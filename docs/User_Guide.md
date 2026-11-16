# User guide — Customer Offer Engagement Dashboard

*One page, for the marketing team. No technical knowledge assumed.*

---

## What this dashboard answers

Which promotional offers earn their cost, which customers respond to them, and where reward spend is
being given away to people who would have bought anyway.

It covers **17,000 customers**, **76,277 offer deliveries** and **138,953 transactions** across a
30-day window.

---

## Refreshing the data

**In Power BI Desktop:** Home → Refresh. Takes under three minutes.

**In the Power BI Service:** refresh runs automatically on the schedule set for the workspace. To force
one, open the workspace → ⋯ next to the dataset → Refresh now. If it fails, the usual cause is the
source folder having moved — update the `DataFolder` parameter under Settings → Parameters.

---

## The five pages

| Page | Use it to answer |
| --- | --- |
| **Overview** | How are we doing overall? Headline redemption, spend, offer volumes. |
| **Offer Funnel** | Where do customers drop out — delivery, opening, or completing? |
| **Customer Segmentation** | Who responds? By age, income, gender, tenure. |
| **Offer Performance** | Which offers work, at what reward cost, through which channels? |
| **Transaction Behaviour** | Do offer completers spend differently? |

---

## Using the filters

The slicer panel on the left is the same on every page and **stays applied as you move between pages**.

- **Offer type** — bogo, discount, informational
- **Channel** — the combination an offer was sent through
- **Age group / Income band / Gender / Tenure** — customer demographics
- **Complete profiles only** — see the warning below

Clear everything with the eraser icon at the top of the panel. The three bookmark buttons at the bottom
jump to saved views: *All customers*, *Complete profiles only*, *Champions only*.

**To see detail behind any offer:** right-click a bar on the Offer Performance page → Drill through →
Customer detail.

---

## Two things to know before you quote a number

**1. "Redemption rate" excludes informational offers.**
Informational offers have nothing to complete — no spend threshold, no reward. They are 15,235 of the
76,277 deliveries. The dashboard leaves them out of the redemption denominator, which is why the figure
reads **53.6%** and not the 42.9% you would get by dividing completions by every offer sent. If you are
comparing against a number from elsewhere, check which denominator it used.

**2. The "Complete profiles only" filter is on by default, deliberately.**
2,175 customers have no age, gender or income recorded. They redeem at 13.6% against 53.6% overall —
but that is a fact about dormant accounts, not about any demographic group. Leaving them in drags every
segmentation chart toward a misleading story. Switch the filter off if you need totals that reconcile
to the full customer base; leave it on for any demographic comparison.

---

## What the headline numbers mean

| Number | Reading |
| --- | --- |
| **53.6%** redemption | Just over half of promotional offers get completed. |
| **73.9%** view rate | Most delivered offers do get opened. Delivery is not the bottleneck. |
| **29.8%** of completions unviewed | Nearly three in ten rewards go to customers who never opened the offer. |
| **$12.78** average transaction | Barely moves inside or outside an offer window ($12.90 vs $12.64). |
| **79.3%** of revenue from Champions | 48.6% of customers generate four-fifths of the spend. |

---

## Who to ask

| Topic | Owner |
| --- | --- |
| Data refresh failures, source files | Sai Suresh Wangde |
| Event parsing, funnel figures | Gaurav Thaware |
| Segmentation and cohort definitions | Srikanth S |
| Offer performance, drill-through, tooltips | M S Praveen |
| Transaction analysis, QA validation | Nilanjan Chowdhury and Vipin Kumar |
