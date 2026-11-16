# RewardsNext — Customer Offer Engagement Dashboard

An interactive dashboard over 17,000 customers, 306,534 reward-programme events and 10 promotional
offers. No build step, no framework, no dependencies — open `index.html` and it runs.

**CPDA B12 Capstone · Group 3**

---

## Run it

```bash
python -m http.server 8000
```

Then open <http://localhost:8000>. Opening `index.html` directly from disk works too, since the data is
loaded as a script rather than fetched.

**GitHub Pages:** push this folder, then Settings → Pages → deploy from branch → `/root` (or `/docs` if
you move it there). No configuration needed.

---

## Pages

| Page | Question it answers |
| --- | --- |
| **Overview** | Headline redemption, spend across the window, engagement by offer type |
| **Offer Funnel** | Where customers drop out, and how much reward is paid with no marketing influence |
| **Segmentation** | Who responds — age × income heatmap, income, tenure, age, gender, engagement segments |
| **Offer Performance** | Which offers work, at what reward cost, through which channels |
| **Transaction Behaviour** | Whether offers change spending, and how far that claim can be pushed |

Every chart responds to the filter rail: offer type, channel, age group, income band, gender, tenure,
and a profile-completeness toggle. Filters persist as you move between pages.

---

## Three things the dashboard is careful about

**Informational offers cannot be completed.** They carry no spend threshold, so no completion event
ever fires for them — 15,235 of 76,277 deliveries. Every redemption denominator here excludes them,
giving **53.6%**. Dividing by all offers sent instead gives 42.9%, which understates performance by
nearly eleven points.

**29.8% of completions were never viewed.** 9,739 customers met the spend threshold without opening the
offer. The reward paid out and no marketing influence occurred. This is surfaced as a headline metric
rather than buried, because it is the clearest actionable finding in the data.

**Incomplete profiles are filtered out by default.** 2,175 customers have no age, gender or income —
the same rows in all three columns. They redeem at ~14% against ~54% overall, but that reflects dormant
accounts, not a demographic effect. The toggle in the rail shows them; the note explains why they are
hidden.

---

## Structure

```
dashboard/
├── index.html      markup and page shell
├── styles.css      design tokens, light + dark, responsive to phone width
├── app.js          filtering, aggregation, hand-rolled SVG charts
├── data/data.js    pre-aggregated cube (~725 KB)
└── README.md
```

`data/data.js` is a compact cube, not raw rows: offer deliveries grouped by demographics × offer ×
viewed × completed (7,015 rows), customers by demographic cell (847), and transactions by demographic
cell × day × offer context (17,834). All filtering and aggregation then runs in the browser with no
server. Regenerate it with `scripts/build_cube.py` from the parent pack.

---

## Validation

Every figure the dashboard renders was independently reproduced by the Python pipeline in the parent
folder, which reads the raw CSVs through a different engine:

| Metric | Dashboard | Pipeline |
| --- | --- | --- |
| Offer deliveries | 76,277 | 76,277 |
| Completions attributed | 32,710 | 32,710 |
| Redemption rate | 53.6% | 53.6% |
| Total spend | $1,775,452 | $1,775,452 |
| Average transaction | $12.78 | $12.78 |

---

## Data notes

Event `time` is hours 0–719 inside a 30-day observation window — **not** a calendar date. Membership
dates (2013–2018) are a separate clock, so no seasonality analysis is possible and none is claimed.

A completion is attributed to a specific offer *delivery* only if it falls inside that delivery's
validity window (`received_at ≤ event < min(received_at + duration, next delivery)`). That leaves 869
completions (2.6%) and 1,375 views (2.4%) unattributable; they are excluded and reported rather than
force-fitted.

There is no control group in the data, so no uplift can be computed. Comparisons between completers and
non-completers conflate behaviour with selection, and the dashboard says so where it matters.
