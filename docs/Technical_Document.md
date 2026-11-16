# Technical document — Customer Offer Engagement Dashboard

**Project:** RewardsNext · CPDA B12 Capstone, Group 3
**Dataset:** 17,000 customers · 306,534 events · 10 offers · 30-day observation window

---

## 1. Data model (ERD)

```
                    ┌──────────────────────────┐
                    │        Customers         │  17,000 rows
                    │──────────────────────────│
                    │ customer_id      (PK)    │
                    │ became_member_on_date    │
                    │ membership_year          │
                    │ gender_clean, age_group  │
                    │ income_band, tenure_band │
                    │ profile_complete         │
                    │ engagement_segment       │
                    └────────────┬─────────────┘
                                 │ 1
                 ┌───────────────┼────────────────┐
                 │ *                              │ *
    ┌────────────┴─────────────┐    ┌─────────────┴────────────┐
    │   FactOfferDelivery      │    │    FactTransaction        │
    │  76,277 rows             │    │   138,953 rows            │
    │──────────────────────────│    │───────────────────────────│
    │ customer_id       (FK)   │    │ txn_id            (PK)    │
    │ offer_id          (FK)   │    │ customer_id       (FK)    │
    │ delivery_seq             │    │ txn_time          (FK)    │
    │ received_at, window_end  │    │ amount, day               │
    │ viewed_at, completed_at  │    │ in_offer_window           │
    │ was_viewed, was_completed│    │ in_viewed_offer_window    │
    │ viewed_before_completed  │    └───────────┬───────────────┘
    │ completed_unviewed       │                │ *
    │ hours_to_view/complete   │                │
    └────────────┬─────────────┘                │
                 │ *                            │
                 │              ┌───────────────┴──────┐
                 │ 1            │       DimTime        │  720 rows
    ┌────────────┴─────────────┐│──────────────────────│
    │         Offers           ││ time_hour      (PK)  │
    │   10 rows                ││ day, week            │
    │──────────────────────────│└──────────────────────┘
    │ offer_id          (PK)   │
    │ offer_label, offer_type  │          ┌──────────────────────┐
    │ difficulty, reward       │  1    *  │ BridgeOfferChannel   │  33 rows
    │ duration, duration_hours ├──────────│──────────────────────│
    │ channels_text            │          │ offer_id       (FK)  │
    │ channel_count            │          │ channel              │
    │ is_informational         │          └──────────────────────┘
    │ reward_per_dollar        │
    └──────────────────────────┘
```

**Relationships**

| From | To | Cardinality | Direction | Active |
| --- | --- | --- | --- | --- |
| `Customers[customer_id]` | `FactOfferDelivery[customer_id]` | 1 → * | Single | Yes |
| `Customers[customer_id]` | `FactTransaction[customer_id]` | 1 → * | Single | Yes |
| `Offers[offer_id]` | `FactOfferDelivery[offer_id]` | 1 → * | Single | Yes |
| `Offers[offer_id]` | `BridgeOfferChannel[offer_id]` | 1 → * | Both | Yes |
| `DimTime[time_hour]` | `FactTransaction[txn_time]` | 1 → * | Single | Yes |
| `FunnelStages[Stage]` | — | disconnected | — | — |

`BridgeOfferChannel` needs bidirectional filtering so a channel slicer reaches the fact table. It is
the only bidirectional relationship in the model; everything else stays single-direction to keep the
filter flow predictable.

**Grain statement.** `FactOfferDelivery` is one row per *offer delivery*, not per offer and not per
customer. A customer who receives the same offer twice generates two rows. This is the decision that
makes the whole model work, and it should be the first thing said in the demo.

---

## 2. Source-to-target lineage

| Target | Source | Key transformation |
| --- | --- | --- |
| `Customers` | `customers.csv` | YYYYMMDD int → Date; age 118 → null; demographic banding; profile-complete flag |
| `Offers` | `offers.csv` | Python-list `channels` → JSON → list; readable label; informational flag |
| `BridgeOfferChannel` | `Offers` | Expand channel list to rows (10 → 33) |
| `FactTransaction` | `events.csv` where `event = 'transaction'` | Parse `{'amount': n}`; window flags |
| `FactOfferDelivery` | `events.csv`, all four event types | JSON parse + window attribution (below) |
| `DimTime` | generated | 0–719 hours → day, week |

---

## 3. The two parsing traps

**Trap 1 — `value` is not JSON.** It is a Python dict literal with single quotes. `Json.Document` fails
on it. Swap quotes first:

```m
Json.Document ( Text.Replace ( [value], "'", """" ) )
```

**Trap 2 — the key is spelled two different ways.**

| Event | Key | Rows |
| --- | --- | --- |
| offer received | `'offer id'` (space) | 76,277 |
| offer viewed | `'offer id'` (space) | 57,725 |
| **offer completed** | **`'offer_id'` (underscore)** | **33,579** |
| transaction | `'amount'` | 138,953 |

`offer completed` additionally carries a `'reward'` key the others do not. Parse for one spelling only
and all 33,579 completions come through as null — the dashboard then shows a 0% redemption rate and
looks plausible enough to ship. Both spellings are handled with nested `Record.FieldOrDefault`.

---

## 4. Offer-window attribution

A completion event says *which offer* and *when*, but not *which delivery of it*. Since a customer can
receive the same offer more than once, completions have to be matched to a delivery window.

**Rule**

```
window_end  = MIN( received_at + duration × 24 ,  next received_at for same customer+offer )
attributed  = received_at ≤ event_time < window_end
tie-break   = earliest delivery wins; each raw event consumed once
```

**Result**

| | Raw events | Attributed | Unattributable | % lost |
| --- | --- | --- | --- | --- |
| Views | 57,725 | 56,350 | 1,375 | 2.4% |
| Completions | 33,579 | 32,710 | 869 | 2.6% |

The unattributable events fall outside any open window — a completion logged after the offer expired.
They are excluded from the fact table and reported as a data-quality flag rather than dropped silently
or force-fitted to the nearest delivery.

---

## 5. Measure dependency map

```
Offers Sent ──┬─► View Rate ◄── Offers Viewed
              │
              └─► Redemption Rate (naive)        [hidden]

Promotional Offers Sent ──┬─► Redemption Rate            ◄── Offers Completed
                          └─► Influenced Redemption Rate ◄── Influenced Completions
                                                              │
Unviewed Completions ──► Unviewed Completion Share ◄──────────┘
       └──► Wasted Reward Cost ──► Wasted Reward % ◄── Reward Cost

Total Spend ──┬─► Avg Transaction ──┬─► Avg Transaction in Viewed Window
              │                     └─► Avg Transaction Outside Window
              └─► Spend per Customer ──► Completer Avg Spend
```

Full code in `powerbi/02_DAX_Measures.md`.

---

## 6. Validation

Every model number was independently reproduced by the Python pipeline in this pack
(`etl_rewardsnext.py` → `analysis_rewardsnext.py`), which reads the raw CSVs and applies the same rules
through a different engine. Agreement between the two is the validation evidence for task G.1.

| Check | Expected | Where |
| --- | --- | --- |
| Offer deliveries | 76,277 | `QA Row Count Check` |
| Completions attributed | 32,710 | `QA Completion Check` |
| Total spend | $1,775,452 | `QA Spend Check` |
| Transactions | 138,953 | QA page table |
| Redemption rate | 53.6% | KPI card vs `analysis/kpi_headline.csv` |

For the 50–100 customer manual reconciliation the brief asks for, filter the QA page table to any
sample and compare against `model/fact_offer_delivery.csv` in Excel.

**Referential integrity:** zero orphan `offer_id` values and zero orphan `customer_id` values across
306,534 events. All ten offers appear in the event stream; 16,994 of 17,000 customers received at least
one offer.

---

## 7. Performance

| Step | Action | Effect |
| --- | --- | --- |
| Events staging | **Disable load** after the two facts are derived | avoids importing 306k rows twice |
| Column pruning | drop `value`, `value_record`, raw `channels`, raw `age`, raw `became_member_on` | smaller model |
| Cardinality | `channels_text` 4 distinct, `offer_label` 10 | negligible |
| Visual limits | Top-N on the customer scatter (17,000 points) | the only visual at risk |
| Window attribution | done once in Python, loaded as CSV | avoids a nested-scan join in M over 306k rows |

Refresh on a laptop lands comfortably inside the 3-minute target; the model is under 60 MB.

---

## 8. Adding a new offer

1. Append the row to `offers.csv` — `offer_id`, `offer_type`, `difficulty`, `reward`, `duration`,
   `channels` as a quoted Python list.
2. Refresh. `Offers` and `BridgeOfferChannel` pick it up with no edit, since the channel expansion is
   generic.
3. If `offer_type` is a new value, extend the `is_informational` test and check the colour mapping on
   Page 4.
4. Re-run the ETL so `FactOfferDelivery` covers the new offer's deliveries, then re-run the QA page —
   the hard-coded expected counts in the QA measures must be updated to the new totals.

---

## 9. Known limitations

- `time` is hours since the start of the observation window, **not** a real date. There is no calendar
  table and no seasonality analysis is possible. Membership dates (2013–2018) are a separate clock.
- No control group. Every customer in the data received offers, so no true uplift can be computed —
  only comparisons between customers who did and did not complete, which conflate behaviour with
  selection.
- Transactions carry no offer id, so spend is linked to offers by time window, not by attribution.
- The 2,175 incomplete profiles cannot be imputed credibly; they are flagged and filtered, not filled.
- `difficulty`, `reward` and `duration` co-vary across only 8 promotional offers. The negative
  difficulty–redemption relationship is clear, but with 8 design points the individual effects of
  reward and duration cannot be separated.
