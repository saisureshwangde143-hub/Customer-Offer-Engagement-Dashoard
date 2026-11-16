"""RewardsNext - engagement, segmentation and spend analysis.
Usage: python -I analysis_rewardsnext.py <output_dir>
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(sys.argv[1])
M = OUT / "model"
A = OUT / "analysis"
A.mkdir(parents=True, exist_ok=True)

cust = pd.read_csv(M / "dim_customer.csv")
offer = pd.read_csv(M / "dim_offer.csv")
fact = pd.read_csv(M / "fact_offer_delivery.csv")
txn = pd.read_csv(M / "fact_transaction.csv")
bridge = pd.read_csv(M / "bridge_offer_channel.csv")

f = fact.merge(offer, on="offer_id", how="left")
promo = f[~f["is_informational"]]  # only bogo/discount can be "completed"
lines = []


def h(t):
    lines.append(f"\n## {t}\n")


def _fmt(v):
    if isinstance(v, float):
        return "" if pd.isna(v) else f"{v:,.3f}"
    if isinstance(v, (bool, np.bool_)):
        return str(bool(v))
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v)


def md(df, index=False):
    d = df.reset_index() if index else df
    cols = [str(c) for c in d.columns]
    rows = [[_fmt(v) for v in r] for r in d.itertuples(index=False)]
    w = [max(len(cols[i]), *(len(r[i]) for r in rows)) if rows else len(cols[i]) for i in range(len(cols))]
    out = ["| " + " | ".join(c.ljust(w[i]) for i, c in enumerate(cols)) + " |",
           "| " + " | ".join("-" * w[i] for i in range(len(cols))) + " |"]
    out += ["| " + " | ".join(r[i].ljust(w[i]) for i in range(len(cols))) + " |" for r in rows]
    return "\n".join(out)


def tab(df, name=None, float_fmt="{:.3f}"):
    if name:
        df.to_csv(A / f"{name}.csv", index=False)
    lines.append(md(df))
    lines.append("")


lines.append("# RewardsNext - Customer Offer Engagement: Findings\n")
lines.append(f"Generated from {len(cust):,} customers, {len(fact):,} offer deliveries, {len(txn):,} transactions.\n")

# ------------------------------------------------------------------ headline
h("1. Headline KPIs")
sent = len(fact)
viewed = int(fact["was_viewed"].sum())
completed = int(fact["was_completed"].sum())
promo_sent = len(promo)
promo_completed = int(promo["was_completed"].sum())
influenced = int(promo["viewed_before_completed"].sum())
kpi = pd.DataFrame([
    ("Total customers", f"{len(cust):,}"),
    ("Customers targeted", f"{(cust['offers_received']>0).sum():,}"),
    ("Offers sent (deliveries)", f"{sent:,}"),
    ("Offers viewed", f"{viewed:,}"),
    ("View rate", f"{viewed/sent:.1%}"),
    ("Promotional offers sent (excl. informational)", f"{promo_sent:,}"),
    ("Offers completed", f"{promo_completed:,}"),
    ("Redemption rate (completed / promotional sent)", f"{promo_completed/promo_sent:.1%}"),
    ("Naive redemption rate (completed / all sent)", f"{completed/sent:.1%}"),
    ("Influenced redemption (viewed then completed)", f"{influenced:,} ({influenced/promo_sent:.1%})"),
    ("Completed without viewing", f"{int(promo['completed_unviewed'].sum()):,}"),
    ("Total spend", f"${txn['amount'].sum():,.0f}"),
    ("Transactions", f"{len(txn):,}"),
    ("Average transaction", f"${txn['amount'].mean():.2f}"),
], columns=["Metric", "Value"])
tab(kpi, "kpi_headline")

# -------------------------------------------------------------------- funnel
h("2. Offer funnel")
funnel = pd.DataFrame([
    ("Offer received", sent, 1.0),
    ("Offer viewed", viewed, viewed / sent),
    ("Offer completed", completed, completed / sent),
], columns=["Stage", "Volume", "Pct of received"])
tab(funnel, "funnel_overall")

fn_type = f.groupby("offer_type").agg(
    sent=("was_viewed", "size"),
    viewed=("was_viewed", "sum"),
    completed=("was_completed", "sum"),
).reset_index()
fn_type["view_rate"] = fn_type["viewed"] / fn_type["sent"]
fn_type["redemption_rate"] = np.where(
    fn_type["offer_type"] == "informational", np.nan, fn_type["completed"] / fn_type["sent"]
)
tab(fn_type, "funnel_by_offer_type")

# ----------------------------------------------------------- offer performance
h("3. Offer performance")
perf = promo.groupby(["offer_label", "offer_type", "difficulty", "reward", "duration", "channel_count"]).agg(
    sent=("was_viewed", "size"),
    view_rate=("was_viewed", "mean"),
    redemption_rate=("was_completed", "mean"),
    influenced_rate=("viewed_before_completed", "mean"),
    unviewed_completions=("completed_unviewed", "sum"),
    avg_hours_to_complete=("hours_to_complete", "mean"),
).reset_index().sort_values("redemption_rate", ascending=False)
tab(perf, "offer_performance")

info = f[f["is_informational"]].groupby(["offer_label", "duration", "channel_count"]).agg(
    sent=("was_viewed", "size"), view_rate=("was_viewed", "mean"),
    avg_hours_to_view=("hours_to_view", "mean"),
).reset_index()
tab(info, "informational_offers")

h("4. Effect of difficulty and reward")
diff = promo.groupby("difficulty").agg(
    sent=("was_viewed", "size"), view_rate=("was_viewed", "mean"), redemption_rate=("was_completed", "mean")
).reset_index()
tab(diff, "redemption_by_difficulty")
rew = promo.groupby("reward").agg(
    sent=("was_viewed", "size"), view_rate=("was_viewed", "mean"), redemption_rate=("was_completed", "mean")
).reset_index()
tab(rew, "redemption_by_reward")
dur = promo.groupby("duration").agg(
    sent=("was_viewed", "size"), view_rate=("was_viewed", "mean"), redemption_rate=("was_completed", "mean")
).reset_index()
tab(dur, "redemption_by_duration")

# ------------------------------------------------------------------ channels
h("5. Channel mix")
ch = promo.merge(bridge, on="offer_id")
chan = ch.groupby("channel").agg(
    deliveries=("was_viewed", "size"), view_rate=("was_viewed", "mean"), redemption_rate=("was_completed", "mean")
).reset_index().sort_values("redemption_rate", ascending=False)
tab(chan, "channel_performance")
lines.append("_Channels overlap: one offer uses several, so these are not independent. "
             "The combination column below is the cleaner read._\n")
combo = promo.groupby("channels_text").agg(
    deliveries=("was_viewed", "size"), view_rate=("was_viewed", "mean"), redemption_rate=("was_completed", "mean")
).reset_index().sort_values("redemption_rate", ascending=False)
tab(combo, "channel_combination_performance")

# -------------------------------------------------------------- segmentation
h("6. Customer segmentation")
cf = promo.merge(cust, on="customer_id", how="left")


def seg(col, name):
    s = cf.groupby(col).agg(
        customers=("customer_id", "nunique"),
        offers_sent=("was_viewed", "size"),
        view_rate=("was_viewed", "mean"),
        redemption_rate=("was_completed", "mean"),
    ).reset_index()
    tab(s, name)
    return s


lines.append("### By gender")
seg("gender_clean", "segment_gender")
lines.append("### By age group")
seg("age_group", "segment_age")
lines.append("### By income band")
seg("income_band", "segment_income")
lines.append("### By tenure")
seg("tenure_band", "segment_tenure")
lines.append("### By membership year")
seg("membership_year", "segment_membership_year")

lines.append("### Heatmap: redemption rate by age group x income band")
heat = cf.pivot_table(index="age_group", columns="income_band", values="was_completed", aggfunc="mean")
heat.round(3).to_csv(A / "heatmap_age_income.csv")
lines.append(md(heat.round(3), index=True))
lines.append("")

h("7. Engagement segments")
es = cust.groupby("engagement_segment").agg(
    customers=("customer_id", "size"),
    avg_offers_received=("offers_received", "mean"),
    avg_completion_rate=("completion_rate", "mean"),
    avg_total_spend=("total_spend", "mean"),
    avg_txn_value=("avg_txn", "mean"),
    total_spend=("total_spend", "sum"),
).reset_index().sort_values("total_spend", ascending=False)
es["pct_of_revenue"] = es["total_spend"] / es["total_spend"].sum()
tab(es, "engagement_segments")

# -------------------------------------------------------- spend behaviour
h("8. Transaction behaviour")
sp = pd.DataFrame([
    ("Inside a viewed offer window", txn[txn["in_viewed_offer_window"]]["amount"].mean(),
     txn["in_viewed_offer_window"].sum(), txn[txn["in_viewed_offer_window"]]["amount"].sum()),
    ("Inside an unviewed offer window", txn[txn["in_offer_window"] & ~txn["in_viewed_offer_window"]]["amount"].mean(),
     (txn["in_offer_window"] & ~txn["in_viewed_offer_window"]).sum(),
     txn[txn["in_offer_window"] & ~txn["in_viewed_offer_window"]]["amount"].sum()),
    ("Outside any offer window", txn[~txn["in_offer_window"]]["amount"].mean(),
     (~txn["in_offer_window"]).sum(), txn[~txn["in_offer_window"]]["amount"].sum()),
], columns=["Context", "Avg transaction", "Transactions", "Total spend"])
tab(sp, "spend_by_offer_context")

# before/after first completion, same customers
firstc = promo[promo["was_completed"]].groupby("customer_id")["completed_at"].min().rename("first_completion")
t2 = txn.merge(firstc, on="customer_id", how="inner")
before = t2[t2["txn_time"] < t2["first_completion"]]
after = t2[t2["txn_time"] >= t2["first_completion"]]
ba = pd.DataFrame([
    ("Before first completion", before["amount"].mean(), len(before), before["amount"].sum()),
    ("After first completion", after["amount"].mean(), len(after), after["amount"].sum()),
], columns=["Period", "Avg transaction", "Transactions", "Total spend"])
tab(ba, "spend_before_after_completion")
lines.append("_Same customers on both sides, so the comparison controls for who they are - "
             "but not for time-in-window, so read it as directional, not causal._\n")

# completers vs non-completers
comp_ids = set(promo[promo["was_completed"]]["customer_id"])
cust["is_completer"] = cust["customer_id"].isin(comp_ids)
cn = cust.groupby("is_completer").agg(
    customers=("customer_id", "size"), avg_total_spend=("total_spend", "mean"),
    avg_txn_value=("avg_txn", "mean"), avg_txn_count=("txn_count", "mean"),
).reset_index()
tab(cn, "completers_vs_non")

# daily spend curve
daily = txn.groupby("day")["amount"].agg(["sum", "mean", "size"]).reset_index()
daily.columns = ["day", "total_spend", "avg_transaction", "transactions"]
daily.to_csv(A / "daily_spend.csv", index=False)
lines.append(f"Daily spend curve written to `analysis/daily_spend.csv` "
             f"({len(daily)} days, peak day {int(daily.loc[daily['total_spend'].idxmax(),'day'])}).\n")

# --------------------------------------------------------------- data quality
h("9. Data quality flags")
dq = pd.DataFrame([
    ("Customers with placeholder age 118", f"{int(cust['age_is_missing'].sum()):,}",
     "Same 2,175 rows also lack gender and income - one incomplete-profile cohort, not three separate gaps."),
    ("Completions attributed to no open window", "869",
     "Completion fell outside the offer's validity window; excluded from journey facts."),
    ("Views attributed to no open window", "1,375",
     "Same cause. Both are <2% of their event type."),
    ("Completions without a prior view", f"{int(promo['completed_unviewed'].sum()):,}",
     "Customer met the spend threshold without opening the offer - reward paid, no marketing influence."),
    ("Informational offers", "2 of 10",
     "Cannot be 'completed'. Including them in the denominator understates redemption by ~9pp."),
], columns=["Flag", "Count", "Meaning"])
tab(dq, "data_quality_flags")

(A / "FINDINGS.md").write_text("\n".join(lines), encoding="utf8")
print("Analysis written ->", A / "FINDINGS.md")
print(kpi.to_string(index=False))
