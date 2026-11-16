# Customer Offer Engagement Dashboard — RewardsNext

**CPDA B12 Capstone · Group 3**
Sai Suresh Wangde · Gaurav Thaware · Srikanth S · M S Praveen · Nilanjan Chowdhury · Vipin Kumar

Analysis of 17,000 customers, 306,534 reward-programme events and 10 promotional offers across a
30-day observation window, built into a Power BI dashboard with a parallel web version.

---

## Submission index

| Brief requirement | Where it is | Status |
| --- | --- | --- |
| Interactive Power BI dashboard (`.pbix`) | [`powerbi/RewardsNext.pbip`](powerbi/) + [`00_HOW_TO_GET_THE_PBIX.md`](powerbi/00_HOW_TO_GET_THE_PBIX.md) | Project opens in Desktop → Save As `.pbix` |
| Data ingestion & JSON parsing | [`powerbi/01_PowerQuery_M.md`](powerbi/01_PowerQuery_M.md) | Complete |
| Data modelling (star schema) | [`docs/Technical_Document.pdf`](docs/Technical_Document.pdf) §1 | Complete |
| DAX measures | [`powerbi/02_DAX_Measures.md`](powerbi/02_DAX_Measures.md) — 37 measures | Complete |
| Segmentation & cohort analysis | [`analysis/FINDINGS.md`](analysis/FINDINGS.md) §6–7 | Complete |
| Report pages (5) | [`powerbi/03_Report_Page_Spec.md`](powerbi/03_Report_Page_Spec.md) | Spec complete, visuals to be built |
| Testing & QA | QA measures + [`docs/Technical_Document.pdf`](docs/Technical_Document.pdf) §6 | Complete |
| **User Guide (one-page PDF)** | [`docs/User_Guide.pdf`](docs/User_Guide.pdf) | Complete |
| **Technical Document** | [`docs/Technical_Document.pdf`](docs/Technical_Document.pdf) | Complete |
| Publish to Power BI Service | — | Pending `.pbix` |

---

## Live dashboard

A fully working five-page dashboard over the same data, with no dependencies:
[`dashboard/`](dashboard/) → open `index.html`, or serve the folder and visit it.

It mirrors the Power BI report page for page and every figure reconciles with the pipeline, so it
doubles as the validation reference while the `.pbix` is assembled.

---

## Headline findings

| | |
| --- | --- |
| Offer deliveries | 76,277 to 16,994 customers |
| View rate | 73.9% |
| **Redemption rate** | **53.6%** (completions ÷ promotional offers sent) |
| Completed without ever viewing | 9,739 — **29.8% of all completions**, $47,773 of reward |
| Total spend | $1,775,452 across 138,953 transactions |

1. **Three in ten rewards buy nothing.** 9,739 completions came from customers who never opened the
   offer — they met the threshold anyway and the reward paid out.
2. **The cheapest offer is the best offer.** $2 on a $10 spend redeems at 68.6%; the $10 BOGO at 42.7%.
   Customers respond to the threshold, not the reward.
3. **Social drives reach.** Offers on all four channels are viewed by 95.6% of recipients; email-and-web
   only reaches 34.6%.
4. **Tenure beats demographics.** Members under one year redeem at 39.5% against 72.2% at 1–2 years —
   and they are over half the base.
5. **Offers identify high-value customers more than they create them.** Average basket is $12.90 inside
   a viewed offer window against $12.64 outside one. No holdout group exists, so no uplift is claimed.

Full evidence: [`docs/Insights_and_Recommendations.md`](docs/Insights_and_Recommendations.md).

---

## Repository layout

```
├── dashboard/     interactive web dashboard (HTML/CSS/JS, no build step)
├── docs/          User Guide + Technical Document (PDF and Markdown), findings
├── powerbi/       .pbip project, Power Query M, DAX library, page spec
├── model/         cleaned star-schema CSVs the model loads
├── analysis/      24 result tables + full findings write-up
└── scripts/       Python ETL, analysis and cube build
```

Regenerate everything from the raw course CSVs:

```bash
python scripts/etl_rewardsnext.py <raw_csv_folder> .
python scripts/analysis_rewardsnext.py .
python scripts/build_cube.py . dashboard
```

---

## Three things this build is careful about

**Informational offers cannot be completed.** No spend threshold means no completion event ever fires —
15,235 of 76,277 deliveries. Every redemption denominator excludes them, giving 53.6%. Including them
gives 42.9%.

**The JSON key is spelled two ways.** `'offer id'` for received and viewed, `'offer_id'` for completed.
Parse for one and all 33,579 completions arrive null — the report still renders, showing 0% redemption.

**2,175 incomplete profiles are not a demographic segment.** The same customers are missing age, gender
and income. They redeem at 13.6% because they are dormant. Filtered out of segmentation by default.

---

## Data notes

Event `time` is hours 0–719 inside a 30-day window, **not** a calendar date; membership dates
(2013–2018) run on a separate clock, so no seasonality analysis is possible. A completion is attributed
to a specific delivery only inside that delivery's validity window, which leaves 869 completions (2.6%)
and 1,375 views (2.4%) unattributable — excluded and reported rather than force-fitted.
