# Report page specification — 5 pages

Canvas 1280×720, 16:9. One slicer panel on the left of every page (same position, so it does not jump
when you page through), visuals on a 12-column grid.

**Global slicers** (sync across all pages via **View → Sync slicers**): `Offers[offer_type]`,
`Offers[channels_text]`, `Customers[age_group]`, `Customers[income_band]`, `Customers[gender_clean]`,
`Customers[tenure_band]`, and `Customers[profile_complete]` defaulted to **True**.

---

## Page 1 — Overview

Five KPI cards across the top, two charts below.

| Card | Measure | Expected |
| --- | --- | --- |
| Total Customers | `[Customers]` | 17,000 |
| Offers Sent | `[Offers Sent]` | 76,277 |
| Offers Completed | `[Offers Completed]` | 32,710 |
| Redemption Rate | `[Redemption Rate]` | 53.6% |
| Avg Transaction | `[Avg Transaction]` | $12.78 |

Put `[KPI Subtitle]` in a card under the row so the headline always states its own denominator.

- **Line chart** — `FactTransaction[day]` on X, `[Total Spend]` on Y. 30 points. Spend climbs through
  the window and peaks on day 25.
- **Stacked column** — `Offers[offer_type]` on X, `[Offers Sent]` / `[Offers Viewed]` /
  `[Offers Completed]` as three series.
- **Text box, bottom right**, small grey type: *"Redemption excludes informational offers (15,235
  deliveries), which cannot be completed."* Having that sentence on the page, unprompted, is what
  separates a dashboard from a chart dump.

---

## Page 2 — Offer funnel

- **Funnel visual** — `FunnelStages[Stage]` on the axis, `[Funnel Value]` as the value.
  Received 76,277 → Viewed 56,350 (73.9%) → Completed 32,710 (42.9%).
- **Funnel by offer type** — same visual, small-multiplied or with `offer_type` on a slicer. The shape
  differs sharply: discount offers convert far better than bogo at the same reward cost.
- **Waterfall or stacked bar** — completions split into `[Influenced Completions]` (22,971) against
  `[Unviewed Completions]` (9,739).
- **Two cards** — `[Unviewed Completion Share]` (29.8%) and `[Wasted Reward %]`.

This page carries the strongest business message in the project: **nearly three in ten completions
happen without the customer ever opening the offer.** The reward is paid, the margin is gone, and no
marketing influence occurred. Build the page around that number rather than burying it.

---

## Page 3 — Customer segmentation

- **Matrix heatmap** — rows `Customers[age_group]`, columns `Customers[income_band]`, values
  `[Redemption Rate]`, conditional-formatted background. Validated numbers in
  `analysis/heatmap_age_income.csv`.
- **Bar** — `[Redemption Rate]` by `gender_clean`. Female 69.1%, Male 52.4%, Other 68.1%.
- **Bar** — `[Redemption Rate]` by `tenure_band`. 1–2 yr 72.2%, 2–3 yr 71.2%, 3+ yr 52.3%,
  **<1 yr 39.5%**.
- **Scatter** — one dot per customer, X `offers_received`, Y `completion_rate`, size `total_spend`,
  colour `engagement_segment`. Cap it with a Top-N filter if it renders slowly.
- **Donut** — customers by `engagement_segment`: Champion 8,258 / Occasional 4,436 / Browser 4,183 /
  Dormant 117.

Two things to say out loud on this page, because both look like findings and only one is:

1. **Income tracks redemption almost monotonically** — <40k at 42.0% up to 100k+ at 75.8%. Real.
2. **The "Unknown" demographic bucket at 13.6% is not a finding.** It is the 2,175 customers with no
   profile data at all, and they barely transact. Filter them out by default, and keep a toggle so you
   can show the grader you know they exist.

---

## Page 4 — Offer performance

- **Bar, sorted descending** — `[Redemption Rate]` by `Offers[offer_label]`. Top is
  Discount 2/10 (10d) at 68.6%, bottom is Bogo 10/10 (5d) at 42.7%.
- **Scatter** — X `Offers[difficulty]`, Y `[Redemption Rate]`, size `[Offers Sent]`, colour
  `offer_type`. The negative slope is clean: difficulty 7 → 66.1%, 10 → 52.3%, 20 → 42.8%.
- **Bar** — `[Redemption Rate]` by `Offers[channels_text]`. All four channels: 58.1%.
  email+mobile+web: 53.2%. email+web only: 42.8%.
- **Table** — offer label, type, difficulty, reward, duration, sent, view rate, redemption rate,
  `[Avg Hours to Complete]`, `[Reward Cost]`.

The finding worth a slide of its own: **the single best-performing offer is also the cheapest.**
Discount 2/10 pays $2 on a $10 spend and redeems at 68.6%; Bogo 10/10 pays $10 and redeems at 42.7%.
Reward size is inversely related to redemption across the whole set — bigger rewards attach to harder
thresholds, and the threshold is what customers respond to.

Note the **social channel** effect separately: offers carried on social show a 93.9% view rate against
74.7% for web. Some of that is confounded with which offers were put on social, which is why the
channel-combination table is the honest version and the single-channel table is the headline version.
Show both.

---

## Page 5 — Transaction behaviour

- **Line chart, two series** — `FactTransaction[day]` on X, `[Avg Transaction]` for completers against
  non-completers. Use the `Customers[engagement_segment]` field on legend, or a calculation group.
- **Column** — `[Avg Transaction]` by spend context: viewed window $12.90, unviewed window $11.92,
  outside any window $12.64.
- **Before/after card pair** — average transaction before first completion **$7.84**, after **$16.11**.
- **Table** — completers against non-completers: avg total spend $133.66 vs $18.29, avg transaction
  value $16.48 vs $4.52, avg transaction count 9.3 vs 5.0.

**Read the before/after number carefully on the slide.** It is the same customers on both sides, so it
controls for who they are — but a customer's first completion tends to happen early in the window, so
"after" covers more days and more of the natural spend ramp. It is directional evidence, not a causal
estimate. State that in one line. The temptation is to claim offers double spend; the defensible claim
is that completers are a structurally higher-value group and that offers identify them as much as they
create them.

---

## Interactivity (task F.2)

- **Drill-through** from any offer visual to a customer-detail page filtered by `offer_id`.
- **Tooltip page** 320×240 showing demographics, offers received/viewed/completed and total spend;
  attach it to the scatter and heatmap.
- **Bookmarks**: "All customers" / "Complete profiles only" / "Champions only" as scenario snapshots,
  wired to buttons in the slicer panel.
- **Top-N filter** on the customer scatter so Page 3 stays under the 3-minute refresh target.
