"""RewardsNext - Customer Offer Engagement
ETL: clean raw CSVs, parse event JSON, build star schema + offer journeys.

Usage: python -I etl_rewardsnext.py <raw_data_dir> <output_dir>
"""
import ast
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path(sys.argv[1])
OUT = Path(sys.argv[2])
(OUT / "model").mkdir(parents=True, exist_ok=True)
(OUT / "analysis").mkdir(parents=True, exist_ok=True)

log = []


def note(msg):
    print(msg)
    log.append(msg)


# ---------------------------------------------------------------- customers
cust = pd.read_csv(RAW / "customers.csv")
note(f"customers.csv raw rows: {len(cust):,}")

cust["became_member_on"] = pd.to_datetime(
    cust["became_member_on"], format="%Y%m%d", errors="coerce"
)

# 118 is the documented placeholder for "age unknown"
age_placeholder = (cust["age"] == 118).sum()
cust["age_is_missing"] = cust["age"] == 118
cust.loc[cust["age_is_missing"], "age"] = np.nan
note(f"age placeholder 118 replaced with null: {age_placeholder:,} rows")

note(f"gender missing: {cust['gender'].isna().sum():,}")
note(f"income missing: {cust['income'].isna().sum():,}")

# Profile completeness: the three nulls co-occur in this dataset - flag it.
incomplete = cust["age_is_missing"] & cust["gender"].isna() & cust["income"].isna()
note(f"rows missing age AND gender AND income together: {incomplete.sum():,}")
cust["profile_complete"] = ~incomplete

cust["gender_clean"] = cust["gender"].fillna("Not Disclosed").replace(
    {"M": "Male", "F": "Female", "O": "Other"}
)

age_bins = [17, 25, 35, 45, 55, 65, 75, 120]
age_labels = ["18-25", "26-35", "36-45", "46-55", "56-65", "66-75", "76+"]
cust["age_group"] = pd.cut(cust["age"], bins=age_bins, labels=age_labels)
cust["age_group"] = cust["age_group"].cat.add_categories("Unknown").fillna("Unknown")

inc_bins = [0, 40000, 60000, 80000, 100000, 1e9]
inc_labels = ["<40k", "40-60k", "60-80k", "80-100k", "100k+"]
cust["income_band"] = pd.cut(cust["income"], bins=inc_bins, labels=inc_labels)
cust["income_band"] = cust["income_band"].cat.add_categories("Unknown").fillna("Unknown")

cust["membership_year"] = cust["became_member_on"].dt.year
snapshot = cust["became_member_on"].max()
cust["tenure_days_at_snapshot"] = (snapshot - cust["became_member_on"]).dt.days
ten_bins = [-1, 365, 730, 1095, 100000]
ten_labels = ["<1 yr", "1-2 yr", "2-3 yr", "3+ yr"]
cust["tenure_band"] = pd.cut(cust["tenure_days_at_snapshot"], bins=ten_bins, labels=ten_labels)
note(f"membership dates span {cust['became_member_on'].min():%Y-%m-%d} to {snapshot:%Y-%m-%d}")

# ------------------------------------------------------------------- offers
offers = pd.read_csv(RAW / "offers.csv")
offers["channels_list"] = offers["channels"].apply(ast.literal_eval)
offers["channel_count"] = offers["channels_list"].apply(len)
offers["channels_text"] = offers["channels_list"].apply(lambda x: ", ".join(sorted(x)))
offers["is_informational"] = offers["offer_type"] == "informational"
offers["duration_hours"] = offers["duration"] * 24
offers["reward_per_dollar"] = np.where(
    offers["difficulty"] > 0, offers["reward"] / offers["difficulty"], np.nan
)
# short readable label for charts
offers["offer_label"] = (
    offers["offer_type"].str.title()
    + " "
    + offers["reward"].astype(str)
    + "/"
    + offers["difficulty"].astype(str)
    + " ("
    + offers["duration"].astype(str)
    + "d)"
)
# disambiguate duplicate labels
dupe = offers["offer_label"].duplicated(keep=False)
offers.loc[dupe, "offer_label"] = (
    offers.loc[dupe, "offer_label"] + " #" + (offers.loc[dupe].groupby("offer_label").cumcount() + 1).astype(str)
)
note(f"offers: {len(offers)} ({offers['offer_type'].value_counts().to_dict()})")

bridge = offers[["offer_id", "channels_list"]].explode("channels_list")
bridge = bridge.rename(columns={"channels_list": "channel"}).reset_index(drop=True)
note(f"offer-channel bridge rows: {len(bridge)}")

# ------------------------------------------------------------------- events
events = pd.read_csv(RAW / "events.csv")
note(f"events.csv raw rows: {len(events):,}")


def parse_value(raw):
    """events.value is a python-literal dict. Keys differ by event type:
    'offer id' (received/viewed) vs 'offer_id' (completed), plus 'amount'/'reward'."""
    d = ast.literal_eval(raw)
    return (
        d.get("offer id", d.get("offer_id")),
        d.get("amount"),
        d.get("reward"),
    )


parsed = events["value"].map(parse_value)
events["offer_id"] = [p[0] for p in parsed]
events["amount"] = [p[1] for p in parsed]
events["reward_paid"] = [p[2] for p in parsed]
events["day"] = events["time"] // 24

bad = events[events["event"] != "transaction"]["offer_id"].isna().sum()
note(f"offer events with unparsed offer_id: {bad}")
note(f"transaction events with null amount: {events[events['event']=='transaction']['amount'].isna().sum()}")

# referential integrity
valid_offer_ids = set(offers["offer_id"])
orphan_offers = set(events["offer_id"].dropna()) - valid_offer_ids
orphan_cust = set(events["customer_id"]) - set(cust["customer_id"])
note(f"orphan offer_ids in events: {len(orphan_offers)}")
note(f"orphan customer_ids in events: {len(orphan_cust)}")

for ev, n in events["event"].value_counts().items():
    note(f"event '{ev}': {n:,}")

# ------------------------------------------------- offer journeys (fact grain)
# One row per offer DELIVERY. A view/completion is attributed to a delivery only
# if it falls inside that delivery's validity window, and each event is consumed
# once (earliest matching delivery wins).
dur = offers.set_index("offer_id")["duration_hours"].to_dict()

recv = events[events["event"] == "offer received"][["customer_id", "offer_id", "time"]].copy()
recv = recv.sort_values(["customer_id", "offer_id", "time"]).reset_index(drop=True)
recv["delivery_seq"] = recv.groupby(["customer_id", "offer_id"]).cumcount() + 1
recv["expires_at"] = recv["time"] + recv["offer_id"].map(dur)
recv = recv.rename(columns={"time": "received_at"})

# next delivery of the same offer to the same customer truncates this window
recv["next_recv"] = recv.groupby(["customer_id", "offer_id"])["received_at"].shift(-1)
recv["window_end"] = recv[["expires_at", "next_recv"]].min(axis=1, skipna=True)


def attribute(event_name, col):
    ev = events[events["event"] == event_name][["customer_id", "offer_id", "time"]].copy()
    ev = ev.sort_values(["customer_id", "offer_id", "time"])
    merged = ev.merge(
        recv[["customer_id", "offer_id", "delivery_seq", "received_at", "window_end"]],
        on=["customer_id", "offer_id"],
        how="left",
    )
    merged = merged[
        (merged["time"] >= merged["received_at"]) & (merged["time"] < merged["window_end"])
    ]
    # earliest delivery wins; one event consumed once
    merged = merged.sort_values(["customer_id", "offer_id", "time", "delivery_seq"])
    merged = merged.drop_duplicates(subset=["customer_id", "offer_id", "time"], keep="first")
    first = merged.groupby(["customer_id", "offer_id", "delivery_seq"])["time"].min()
    return first.rename(col)


recv = recv.merge(attribute("offer viewed", "viewed_at"), on=["customer_id", "offer_id", "delivery_seq"], how="left")
recv = recv.merge(attribute("offer completed", "completed_at"), on=["customer_id", "offer_id", "delivery_seq"], how="left")

recv["was_viewed"] = recv["viewed_at"].notna()
recv["was_completed"] = recv["completed_at"].notna()
# "influenced" = customer saw the offer before completing it
recv["viewed_before_completed"] = recv["was_completed"] & recv["was_viewed"] & (
    recv["viewed_at"] <= recv["completed_at"]
)
recv["completed_unviewed"] = recv["was_completed"] & ~recv["viewed_before_completed"]
recv["hours_to_view"] = recv["viewed_at"] - recv["received_at"]
recv["hours_to_complete"] = recv["completed_at"] - recv["received_at"]

journeys = recv.merge(offers, on="offer_id", how="left")
note(f"offer deliveries (fact rows): {len(journeys):,}")
note(f"  viewed: {journeys['was_viewed'].sum():,}")
note(f"  completed: {journeys['was_completed'].sum():,}")
note(f"  completed without viewing: {journeys['completed_unviewed'].sum():,}")

unattributed_views = events["event"].eq("offer viewed").sum() - journeys["was_viewed"].sum()
unattributed_compl = events["event"].eq("offer completed").sum() - journeys["was_completed"].sum()
note(f"views not attributable to an open window: {unattributed_views:,}")
note(f"completions not attributable to an open window: {unattributed_compl:,}")

# -------------------------------------------------------------- transactions
txn = events[events["event"] == "transaction"][["customer_id", "time", "amount", "day"]].copy()
txn = txn.rename(columns={"time": "txn_time"}).reset_index(drop=True)
txn["txn_id"] = np.arange(1, len(txn) + 1)
note(f"transactions: {len(txn):,}  total spend ${txn['amount'].sum():,.0f}")

# spend inside an open, viewed offer window vs outside any offer window
win = journeys[["customer_id", "received_at", "window_end", "was_viewed"]].copy()
tx_small = txn[["txn_id", "customer_id", "txn_time"]]
j = tx_small.merge(win, on="customer_id", how="left")
inwin = j[(j["txn_time"] >= j["received_at"]) & (j["txn_time"] < j["window_end"])]
in_any = set(inwin["txn_id"])
in_viewed = set(inwin[inwin["was_viewed"]]["txn_id"])
txn["in_offer_window"] = txn["txn_id"].isin(in_any)
txn["in_viewed_offer_window"] = txn["txn_id"].isin(in_viewed)
note(f"transactions inside an open offer window: {txn['in_offer_window'].sum():,}")
note(f"transactions inside a VIEWED offer window: {txn['in_viewed_offer_window'].sum():,}")

# ------------------------------------------------------------- customer roll-up
agg = journeys.groupby("customer_id").agg(
    offers_received=("delivery_seq", "size"),
    offers_viewed=("was_viewed", "sum"),
    offers_completed=("was_completed", "sum"),
)
tagg = txn.groupby("customer_id").agg(
    txn_count=("amount", "size"),
    total_spend=("amount", "sum"),
    avg_txn=("amount", "mean"),
)
cust = cust.merge(agg, on="customer_id", how="left").merge(tagg, on="customer_id", how="left")
for c in ["offers_received", "offers_viewed", "offers_completed", "txn_count", "total_spend"]:
    cust[c] = cust[c].fillna(0)
cust["view_rate"] = np.where(cust["offers_received"] > 0, cust["offers_viewed"] / cust["offers_received"], np.nan)
cust["completion_rate"] = np.where(cust["offers_received"] > 0, cust["offers_completed"] / cust["offers_received"], np.nan)


def engagement(r):
    if r["offers_received"] == 0:
        return "Not Targeted"
    if r["offers_completed"] == 0 and r["offers_viewed"] == 0:
        return "Dormant"
    if r["offers_completed"] == 0:
        return "Browser"
    if r["completion_rate"] >= 0.5:
        return "Champion"
    return "Occasional"


cust["engagement_segment"] = cust.apply(engagement, axis=1)
note("engagement segments: " + str(cust["engagement_segment"].value_counts().to_dict()))

# ------------------------------------------------------------------- outputs
dim_customer = cust[[
    "customer_id", "became_member_on", "membership_year", "tenure_days_at_snapshot", "tenure_band",
    "gender", "gender_clean", "age", "age_group", "age_is_missing", "income", "income_band",
    "profile_complete", "offers_received", "offers_viewed", "offers_completed",
    "view_rate", "completion_rate", "txn_count", "total_spend", "avg_txn", "engagement_segment",
]]
dim_offer = offers[[
    "offer_id", "offer_label", "offer_type", "difficulty", "reward", "duration", "duration_hours",
    "channels_text", "channel_count", "reward_per_dollar", "is_informational",
]]
fact_offer = journeys[[
    "customer_id", "offer_id", "delivery_seq", "received_at", "window_end", "viewed_at", "completed_at",
    "was_viewed", "was_completed", "viewed_before_completed", "completed_unviewed",
    "hours_to_view", "hours_to_complete",
]].copy()
fact_offer["received_day"] = fact_offer["received_at"] // 24

dim_customer.to_csv(OUT / "model" / "dim_customer.csv", index=False)
dim_offer.to_csv(OUT / "model" / "dim_offer.csv", index=False)
bridge.to_csv(OUT / "model" / "bridge_offer_channel.csv", index=False)
fact_offer.to_csv(OUT / "model" / "fact_offer_delivery.csv", index=False)
txn.to_csv(OUT / "model" / "fact_transaction.csv", index=False)

dim_time = pd.DataFrame({"time_hour": range(0, 720)})
dim_time["day"] = dim_time["time_hour"] // 24
dim_time["week"] = dim_time["day"] // 7 + 1
dim_time.to_csv(OUT / "model" / "dim_time.csv", index=False)

(OUT / "analysis" / "etl_log.txt").write_text("\n".join(log), encoding="utf8")
print("\nETL complete ->", OUT)
