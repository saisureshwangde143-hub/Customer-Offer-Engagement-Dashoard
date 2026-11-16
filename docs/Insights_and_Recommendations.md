# Insights and recommendations

Every figure here traces to a file in `analysis/`. Numbers exclude informational offers from redemption
denominators and exclude the 2,175 incomplete-profile customers from demographic cuts, both flagged
where they matter.

---

## Finding 1 — Three in ten rewards buy nothing

**9,739 of 32,710 completions (29.8%) came from customers who never opened the offer.**

They met the spend threshold on their own, the system detected it, and the reward paid out. No
marketing influence occurred. This is the clearest margin leak in the dataset, and it concentrates in
the offers with the worst view rates: Bogo 5/5 (7d) has a 53.7% view rate and 2,171 unviewed
completions; Discount 5/20 (10d) has a 34.6% view rate and 1,990.

**Recommendation.** Make reward eligibility conditional on the offer having been viewed, or at minimum
report influenced redemption separately from total redemption. The three offers with view rates below
55% — all of them missing the social channel — should be the first to change.
*Expected impact:* on this 30-day window, roughly 30% of reward cost is attributable to completions with
no view. Even recovering a third of that is material.

---

## Finding 2 — The cheapest offer is the best offer

| Offer | Reward | Threshold | Redemption |
| --- | --- | --- | --- |
| Discount 2/10 (10d) | $2 | $10 | **68.6%** |
| Discount 3/7 (7d) | $3 | $7 | 66.1% |
| Bogo 10/10 (7d) | $10 | $10 | 47.0% |
| Discount 5/20 (10d) | $5 | $20 | 42.8% |
| Bogo 10/10 (5d) | $10 | $10 | **42.7%** |

Redemption falls as reward rises, because larger rewards are attached to harder thresholds, and the
**threshold** is what customers actually respond to. Difficulty $7 redeems at 66.1%; difficulty $20 at
42.8%. The $2-on-$10 discount outperforms the $10 bogo by 26 points at a fifth of the reward cost.

**Recommendation.** Shift budget from high-reward bogo offers toward low-threshold discounts. Test a
$2/$7 discount — below the cheapest threshold currently in market — before assuming the relationship
continues.
*Caveat for the slide:* there are only 8 promotional offers, so reward, threshold and duration co-vary.
The difficulty effect is clear; the independent effect of reward size is not separable at this sample.

---

## Finding 3 — Channel reach drives views, and views drive everything

| Channels | View rate | Redemption |
| --- | --- | --- |
| email + mobile + social + web | 95.6% | 58.1% |
| email + mobile + web | 53.4% | 53.2% |
| email + mobile + social | 87.2% | 47.0% |
| email + web | 34.6% | 42.8% |

Offers on all four channels are viewed by 95.6% of recipients; email-and-web-only offers reach 34.6%.
**Social is the differentiator** — every high-view combination includes it.

**Recommendation.** Put social on every offer. The two offers currently without it carry the worst view
rates in the portfolio and, not coincidentally, the most unviewed completions.
*Caveat:* channel assignment is confounded with offer design — the all-four-channel group also contains
the best-designed offers. Treat the view-rate gap as solid and the redemption gap as suggestive.

---

## Finding 4 — Tenure predicts response better than any demographic

| Tenure | Redemption |
| --- | --- |
| 1–2 yr | **72.2%** |
| 2–3 yr | 71.2% |
| 3+ yr | 52.3% |
| **<1 yr** | **39.5%** |

8,672 customers — over half the base — joined within the last year and redeem at 39.5%, roughly half
the rate of the 1–2 year cohort. By membership year the same pattern: 2016 joiners redeem at 72.4%,
2018 joiners at 33.6%.

**Recommendation.** Build a distinct onboarding offer track for members under one year, using the
low-threshold discount format that performs best overall. The current portfolio is tuned for
established members and is being wasted on the largest segment.

---

## Finding 5 — Income tracks redemption cleanly; the "unknown" bucket does not

<40k: 42.0% · 40–60k: 52.1% · 60–80k: 63.1% · 80–100k: 74.7% · 100k+: 75.8%

Nearly monotonic, and it holds across every age band in the heatmap. Women redeem at 69.1% against
52.4% for men. Response rises with age through the 56–65 band and stays high.

**The trap:** the "Unknown" demographic bucket shows 13.6%. That is the 2,175 customers with no profile
data, who are near-dormant overall. It is not a demographic finding and must not be charted as one.

**Recommendation.** Target the 80k+ bands with the higher-threshold offers they already tolerate, and
move <40k customers onto the $2/$10 format. Separately, run a profile-completion campaign — those 2,175
accounts cannot be targeted at all.

---

## Finding 6 — Offers identify high-value customers more than they create them

| | Completers | Non-completers |
| --- | --- | --- |
| Customers | 12,694 | 4,306 |
| Avg total spend | **$133.66** | $18.29 |
| Avg transaction | $16.48 | $4.52 |
| Avg transactions | 9.3 | 5.0 |

A 7× spend gap. But the honest read is in the window comparison: average transaction **inside** a viewed
offer window is **$12.90**, **outside any window** it is **$12.64**. Being under an active offer barely
changes basket size.

The before/after cut (**$7.84** before first completion, **$16.11** after) looks dramatic, but the same
customers sit on both sides and "after" covers more of the 30-day spend ramp. Directional, not causal.

**Recommendation.** Stop treating redemption as the success metric in isolation. Champions are 48.6% of
customers and 79.3% of revenue — the programme's value is in identifying and retaining them, not in
lifting basket size at the moment of redemption. Report incremental spend against a holdout group;
without one, no uplift claim in this dataset can be defended.

---

## Priority order

| # | Action | Effort | Evidence |
| --- | --- | --- | --- |
| 1 | Gate rewards on offer views | Medium | Finding 1 — 29.8% of completions unviewed |
| 2 | Shift budget to low-threshold discounts | Low | Finding 2 — 26-point gap at 1/5 the cost |
| 3 | Add social to all offers | Low | Finding 3 — 95.6% vs 34.6% view rate |
| 4 | Onboarding track for <1 yr members | Medium | Finding 4 — 39.5% vs 72.2% |
| 5 | Hold out a control group next cycle | Low | Finding 6 — no uplift measurable without one |
| 6 | Profile-completion campaign | Medium | Finding 5 — 2,175 untargetable customers |
