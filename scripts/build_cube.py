"""Build the compact data cube the dashboard filters client-side.
Usage: python -I build_cube.py <pack_dir> <dashboard_dir>
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PACK = Path(sys.argv[1])
DASH = Path(sys.argv[2])
(DASH / "data").mkdir(parents=True, exist_ok=True)

cust = pd.read_csv(PACK / "model" / "dim_customer.csv")
offer = pd.read_csv(PACK / "model" / "dim_offer.csv")
fact = pd.read_csv(PACK / "model" / "fact_offer_delivery.csv")
txn = pd.read_csv(PACK / "model" / "fact_transaction.csv")
bridge = pd.read_csv(PACK / "model" / "bridge_offer_channel.csv")

AGE = ["18-25", "26-35", "36-45", "46-55", "56-65", "66-75", "76+", "Unknown"]
INC = ["<40k", "40-60k", "60-80k", "80-100k", "100k+", "Unknown"]
GEN = ["Female", "Male", "Other", "Not Disclosed"]
TEN = ["<1 yr", "1-2 yr", "2-3 yr", "3+ yr"]
SEG = ["Champion", "Occasional", "Browser", "Dormant", "Not Targeted"]

idx = lambda lst: {v: i for i, v in enumerate(lst)}
AI, II, GI, TI, SI = idx(AGE), idx(INC), idx(GEN), idx(TEN), idx(SEG)

offer = offer.reset_index(drop=True)
offer["oi"] = offer.index
OID = dict(zip(offer["offer_id"], offer["oi"]))

cust["ai"] = cust["age_group"].map(AI)
cust["ii"] = cust["income_band"].map(II)
cust["gi"] = cust["gender_clean"].map(GI)
cust["ti"] = cust["tenure_band"].map(TI)
cust["si"] = cust["engagement_segment"].map(SI)
cust["pc"] = cust["profile_complete"].astype(int)

dims = cust[["customer_id", "ai", "ii", "gi", "ti", "si", "pc"]]

# ---- offer cube: one row per (demographics x offer x viewed x completed)
f = fact.merge(dims, on="customer_id", how="left")
f["oi"] = f["offer_id"].map(OID)
f["v"] = f["was_viewed"].astype(int)
f["c"] = f["was_completed"].astype(int)
f["iv"] = f["viewed_before_completed"].astype(int)
f["uc"] = f["completed_unviewed"].astype(int)

cube = f.groupby(["ai", "ii", "gi", "ti", "pc", "oi", "v", "c"]).agg(
    n=("v", "size"),
    iv=("iv", "sum"),
    uc=("uc", "sum"),
    htc=("hours_to_complete", "sum"),
    htv=("hours_to_view", "sum"),
).reset_index()
cube["htc"] = cube["htc"].fillna(0).round(1)
cube["htv"] = cube["htv"].fillna(0).round(1)
print("offer cube rows:", len(cube))

# ---- customer cube: one row per demographic combination
ccube = cust.groupby(["ai", "ii", "gi", "ti", "pc", "si"]).agg(
    n=("customer_id", "size"),
    spend=("total_spend", "sum"),
    txns=("txn_count", "sum"),
).reset_index()
ccube["spend"] = ccube["spend"].round(2)
print("customer cube rows:", len(ccube))

# ---- transaction cube: demographics x day x context
t = txn.merge(dims, on="customer_id", how="left")
t["ctx"] = np.where(t["in_viewed_offer_window"], 2, np.where(t["in_offer_window"], 1, 0))
tcube = t.groupby(["ai", "ii", "gi", "ti", "pc", "day", "ctx"]).agg(
    n=("amount", "size"), amt=("amount", "sum"),
).reset_index()
tcube["amt"] = tcube["amt"].round(2)
print("txn cube rows:", len(tcube))

# ---- before/after first completion, by demographics
firstc = fact[fact["was_completed"]].groupby("customer_id")["completed_at"].min().rename("fc")
t2 = t.merge(firstc, on="customer_id", how="inner")
t2["after"] = (t2["txn_time"] >= t2["fc"]).astype(int)
ba = t2.groupby(["ai", "ii", "gi", "ti", "pc", "after"]).agg(
    n=("amount", "size"), amt=("amount", "sum")
).reset_index()
ba["amt"] = ba["amt"].round(2)

# ---- completer flag per demographic cell
comp_ids = set(fact[fact["was_completed"]]["customer_id"])
cust["isc"] = cust["customer_id"].isin(comp_ids).astype(int)
cc = cust.groupby(["ai", "ii", "gi", "ti", "pc", "isc"]).agg(
    n=("customer_id", "size"), spend=("total_spend", "sum"), txns=("txn_count", "sum")
).reset_index()
cc["spend"] = cc["spend"].round(2)

offers_out = offer[[
    "oi", "offer_label", "offer_type", "difficulty", "reward", "duration",
    "channels_text", "channel_count", "is_informational"
]].copy()
offers_out["is_informational"] = offers_out["is_informational"].astype(int)
offers_out["channels"] = offers_out["oi"].map(
    bridge.assign(oi=bridge["offer_id"].map(OID)).groupby("oi")["channel"].apply(list)
)

def recs(df):
    return [[int(v) if isinstance(v, (np.integer, bool, np.bool_)) else
             (round(float(v), 2) if isinstance(v, (float, np.floating)) else v)
             for v in row] for row in df.itertuples(index=False)]

data = {
    "dims": {"age": AGE, "income": INC, "gender": GEN, "tenure": TEN, "segment": SEG},
    "offers": json.loads(offers_out.to_json(orient="records")),
    "cubeCols": list(cube.columns),
    "cube": recs(cube),
    "custCols": list(ccube.columns),
    "cust": recs(ccube),
    "txnCols": list(tcube.columns),
    "txn": recs(tcube),
    "baCols": list(ba.columns),
    "ba": recs(ba),
    "compCols": list(cc.columns),
    "comp": recs(cc),
}

out = DASH / "data" / "data.js"
out.write_text("window.RN_DATA = " + json.dumps(data, separators=(",", ":")) + ";\n", encoding="utf8")
print("wrote", out, f"{out.stat().st_size/1024:.0f} KB")
