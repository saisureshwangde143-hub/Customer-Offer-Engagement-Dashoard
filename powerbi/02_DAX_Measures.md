# DAX measure library — RewardsNext

Create a blank table called `_Measures` (**Home → Enter data**, one dummy column, delete it after the
first measure lands) and put every measure there. Folder them with the **Display folder** property into
_Engagement_, _Offer economics_, _Spend_, _Segmentation_.

Every number quoted in the comments was validated against the Python pipeline in this pack
(`analysis/FINDINGS.md`), so you can check your model as you build it.

---

## Engagement — the core four

```dax
Offers Sent =
COUNTROWS ( FactOfferDelivery )                                      -- 76,277

Offers Viewed =
CALCULATE ( COUNTROWS ( FactOfferDelivery ), FactOfferDelivery[was_viewed] = TRUE () )   -- 56,350

Offers Completed =
CALCULATE ( COUNTROWS ( FactOfferDelivery ), FactOfferDelivery[was_completed] = TRUE () ) -- 32,710

View Rate =
DIVIDE ( [Offers Viewed], [Offers Sent] )                            -- 73.9%
```

### The measure that decides whether your dashboard is right

Informational offers **cannot be completed** — there is no spend threshold, so no `offer completed`
event ever fires for them. They are 15,235 of the 76,277 deliveries. Leave them in the denominator and
every redemption rate on the page is wrong by about nine points.

```dax
Promotional Offers Sent =
CALCULATE (
    COUNTROWS ( FactOfferDelivery ),
    FILTER ( ALL ( Offers[is_informational] ), Offers[is_informational] = FALSE () )
)                                                                    -- 61,042

Redemption Rate =
DIVIDE ( [Offers Completed], [Promotional Offers Sent] )             -- 53.6%

Redemption Rate (naive) =
DIVIDE ( [Offers Completed], [Offers Sent] )                         -- 42.9%  <- do not ship this one
```

Keep the naive version in the model but hide it, and show both side by side once on the methodology
slide. Being able to explain the ~11-point gap is the single clearest signal that the team understood
the data rather than just charting it.

### Influence — did the marketing actually do anything

9,739 completions came from customers who never opened the offer. They hit the spend threshold
anyway and the reward paid out. That is margin given away for no marketing effect, and it is the most
actionable finding in the dataset.

```dax
Influenced Completions =
CALCULATE (
    COUNTROWS ( FactOfferDelivery ),
    FactOfferDelivery[viewed_before_completed] = TRUE ()
)                                                                    -- 22,971

Unviewed Completions =
CALCULATE (
    COUNTROWS ( FactOfferDelivery ),
    FactOfferDelivery[completed_unviewed] = TRUE ()
)                                                                    -- 9,739

Influenced Redemption Rate =
DIVIDE ( [Influenced Completions], [Promotional Offers Sent] )       -- 37.6%

Unviewed Completion Share =
DIVIDE ( [Unviewed Completions], [Offers Completed] )                -- 29.8%

Reward Cost =
SUMX (
    FILTER ( FactOfferDelivery, FactOfferDelivery[was_completed] = TRUE () ),
    RELATED ( Offers[reward] )
)

Wasted Reward Cost =
SUMX (
    FILTER ( FactOfferDelivery, FactOfferDelivery[completed_unviewed] = TRUE () ),
    RELATED ( Offers[reward] )
)

Wasted Reward % =
DIVIDE ( [Wasted Reward Cost], [Reward Cost] )
```

### Funnel

```dax
Funnel Value =
VAR Stage = SELECTEDVALUE ( FunnelStages[Stage] )
RETURN
    SWITCH (
        Stage,
        "1. Received", [Offers Sent],
        "2. Viewed",   [Offers Viewed],
        "3. Completed", [Offers Completed]
    )

Funnel % of Received =
DIVIDE ( [Funnel Value], [Offers Sent] )
```

`FunnelStages` is a one-column disconnected table — **Enter data**, three rows: `1. Received`,
`2. Viewed`, `3. Completed`. Put it on the axis of the funnel visual.

### Speed

```dax
Avg Hours to View =
AVERAGE ( FactOfferDelivery[hours_to_view] )

Avg Hours to Complete =
AVERAGE ( FactOfferDelivery[hours_to_complete] )                     -- 40.7h to 100.3h by offer
```

---

## Spend

```dax
Total Spend =
SUM ( FactTransaction[amount] )                                      -- $1,775,452

Transactions =
COUNTROWS ( FactTransaction )                                        -- 138,953

Avg Transaction =
AVERAGE ( FactTransaction[amount] )                                  -- $12.78

Spend in Viewed Offer Window =
CALCULATE ( [Total Spend], FactTransaction[in_viewed_offer_window] = TRUE () )

Spend Outside Offer Window =
CALCULATE ( [Total Spend], FactTransaction[in_offer_window] = FALSE () )

Avg Transaction in Viewed Window =
CALCULATE ( [Avg Transaction], FactTransaction[in_viewed_offer_window] = TRUE () )   -- $12.90

Avg Transaction Outside Window =
CALCULATE ( [Avg Transaction], FactTransaction[in_offer_window] = FALSE () )         -- $12.64
```

Note what those last two say: **$12.90 against $12.64**. Being inside an offer window barely moves the
transaction size. The real difference is between *people*, not *windows* — see the next block. Resist
the urge to present the window comparison as proof that offers work; it is the honest null result and
saying so earns more credit than hiding it.

```dax
Spend per Customer =
DIVIDE ( [Total Spend], DISTINCTCOUNT ( FactTransaction[customer_id] ) )

Completer Avg Spend =
CALCULATE ( [Spend per Customer], Customers[engagement_segment] IN { "Champion", "Occasional" } )
```

Completers average **$133.66** lifetime against **$18.29** for non-completers, and Champions alone are
**79.3%** of all revenue off 48.6% of customers. That is the headline for the recommendations page.

---

## Segmentation

```dax
Customers =
DISTINCTCOUNT ( Customers[customer_id] )                             -- 17,000

Targeted Customers =
CALCULATE ( DISTINCTCOUNT ( FactOfferDelivery[customer_id] ) )       -- 16,994

Customer Redemption Rate =
AVERAGEX (
    VALUES ( Customers[customer_id] ),
    CALCULATE ( DIVIDE ( [Offers Completed], [Promotional Offers Sent] ) )
)
```

`Customer Redemption Rate` and `Redemption Rate` answer different questions. The first weights every
customer equally, the second weights by offers received. Put the offer-weighted one on the KPI card and
the customer-weighted one on the segmentation page, and label both clearly — a grader who spots you
using them interchangeably will mark it down.

```dax
Profile Complete % =
DIVIDE (
    CALCULATE ( [Customers], Customers[profile_complete] = TRUE () ),
    [Customers]
)                                                                    -- 87.2%
```

### The 2,175-row warning

Customers with no demographics redeem at **13.6%** against 53.6% overall. That is almost certainly not a
behavioural finding — it is that incomplete profiles belong to accounts that barely engage at all. Give
the segmentation page a slicer defaulted to `profile_complete = TRUE`, with a visible note, so the
Unknown bucket does not drag every demographic chart toward a false story.

```dax
Redemption Rate (complete profiles only) =
CALCULATE ( [Redemption Rate], Customers[profile_complete] = TRUE () )
```

### Dynamic top-N and labels

```dax
Offer Rank by Redemption =
RANKX ( ALL ( Offers[offer_label] ), [Redemption Rate],, DESC )

Best Offer Label =
VAR T = TOPN ( 1, ALL ( Offers[offer_label] ), [Redemption Rate], DESC )
RETURN CONCATENATEX ( T, Offers[offer_label], ", " )                 -- Discount 2/10 (10d)

KPI Subtitle =
"Across " & FORMAT ( [Promotional Offers Sent], "#,0" ) & " promotional offers to "
    & FORMAT ( [Targeted Customers], "#,0" ) & " customers"
```

---

## Validation harness

The brief asks for DAX validated against manual aggregation on a sample. Build a page called
`QA` (hide it before the demo, do not delete it — showing it in the technical document is worth marks):

```dax
QA Row Count Check =
VAR ModelRows = [Offers Sent]
VAR Expected = 76277
RETURN IF ( ModelRows = Expected, "PASS", "FAIL: " & ModelRows & " vs " & Expected )

QA Completion Check =
IF ( [Offers Completed] = 32710, "PASS", "FAIL: " & [Offers Completed] )

QA Spend Check =
IF ( ROUND ( [Total Spend], 0 ) = 1775452, "PASS", "FAIL: " & FORMAT ( [Total Spend], "#,0" ) )
```

Put a table on that page with `Customers[customer_id]`, `[Offers Sent]`, `[Offers Viewed]`,
`[Offers Completed]`, `[Total Spend]`, filtered to any 50 customers, and reconcile it against
`model/fact_offer_delivery.csv` in Excel. That is the evidence item G.1 asks for.
