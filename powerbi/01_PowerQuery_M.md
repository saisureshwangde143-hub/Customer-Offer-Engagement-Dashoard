# Power Query (M) — RewardsNext data preparation

Paste each block into **Home → Transform data → New Source → Blank Query → Advanced Editor**.

Set a parameter first so the path lives in one place:

- **Home → Manage Parameters → New**, Name `DataFolder`, Type `Text`, Current Value = the folder holding
  `customers.csv`, `events.csv`, `offers.csv`, `data_dictionary.csv`.

---

## 1. Customers

Handles the documented placeholder `age = 118` and the null gender/income. In this dataset those three
gaps are the **same 2,175 rows**, so they are flagged as one incomplete-profile cohort rather than three
independent problems.

```m
let
    Source = Csv.Document(File.Contents(DataFolder & "\customers.csv"),
                [Delimiter=",", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
                {"customer_id", type text}, {"became_member_on", Int64.Type},
                {"gender", type text}, {"age", Int64.Type}, {"income", type number}}),

    // YYYYMMDD integer -> Date
    AddDate = Table.AddColumn(Typed, "became_member_on_date", each
                #date(Number.IntegerDivide([became_member_on], 10000),
                      Number.Mod(Number.IntegerDivide([became_member_on], 100), 100),
                      Number.Mod([became_member_on], 100)), type date),

    // 118 is the documented "age unknown" placeholder
    AgeFlag = Table.AddColumn(AddDate, "age_is_missing", each [age] = 118, type logical),
    AgeNull = Table.AddColumn(AgeFlag, "age_clean", each if [age] = 118 then null else [age], Int64.Type),

    GenderClean = Table.AddColumn(AgeNull, "gender_clean", each
                if [gender] = "M" then "Male"
                else if [gender] = "F" then "Female"
                else if [gender] = "O" then "Other"
                else "Not Disclosed", type text),

    ProfileComplete = Table.AddColumn(GenderClean, "profile_complete", each
                not ([age_is_missing] and [gender] = null and [income] = null), type logical),

    AgeGroup = Table.AddColumn(ProfileComplete, "age_group", each
                if [age_clean] = null then "Unknown"
                else if [age_clean] <= 25 then "18-25"
                else if [age_clean] <= 35 then "26-35"
                else if [age_clean] <= 45 then "36-45"
                else if [age_clean] <= 55 then "46-55"
                else if [age_clean] <= 65 then "56-65"
                else if [age_clean] <= 75 then "66-75"
                else "76+", type text),

    IncomeBand = Table.AddColumn(AgeGroup, "income_band", each
                if [income] = null then "Unknown"
                else if [income] < 40000 then "<40k"
                else if [income] < 60000 then "40-60k"
                else if [income] < 80000 then "60-80k"
                else if [income] < 100000 then "80-100k"
                else "100k+", type text),

    MaxDate = List.Max(AgeGroup[became_member_on_date]),
    Tenure = Table.AddColumn(IncomeBand, "tenure_days", each
                Duration.Days([became_member_on_date] - MaxDate) * -1, Int64.Type),
    TenureBand = Table.AddColumn(Tenure, "tenure_band", each
                if [tenure_days] <= 365 then "<1 yr"
                else if [tenure_days] <= 730 then "1-2 yr"
                else if [tenure_days] <= 1095 then "2-3 yr"
                else "3+ yr", type text),
    MemberYear = Table.AddColumn(TenureBand, "membership_year", each
                Date.Year([became_member_on_date]), Int64.Type),

    Removed = Table.RemoveColumns(MemberYear, {"became_member_on", "age"})
in
    Removed
```

> **Sort order for the bands.** `age_group`, `income_band` and `tenure_band` sort alphabetically by
> default, which puts `<40k` last and `100k+` first. Build a small sort-order column (or a disconnected
> sort table) and apply **Column tools → Sort by column**, or the charts will read wrong.

---

## 2. Offers — and the channel bridge

`channels` is a Python-style list (`['email', 'mobile']`), not valid JSON: single quotes have to be
swapped for double quotes before `Json.Document` will parse it.

```m
let
    Source = Csv.Document(File.Contents(DataFolder & "\offers.csv"),
                [Delimiter=",", Columns=6, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
                {"offer_id", type text}, {"offer_type", type text}, {"difficulty", Int64.Type},
                {"reward", Int64.Type}, {"duration", Int64.Type}, {"channels", type text}}),

    // ['email','mobile'] -> ["email","mobile"] -> list
    ChannelList = Table.AddColumn(Typed, "channel_list", each
                Json.Document(Text.Replace([channels], "'", """"))),
    ChannelText = Table.AddColumn(ChannelList, "channels_text", each
                Text.Combine(List.Sort([channel_list]), ", "), type text),
    ChannelCount = Table.AddColumn(ChannelText, "channel_count", each
                List.Count([channel_list]), Int64.Type),

    IsInfo = Table.AddColumn(ChannelCount, "is_informational", each
                [offer_type] = "informational", type logical),
    DurHours = Table.AddColumn(IsInfo, "duration_hours", each [duration] * 24, Int64.Type),
    RewardPerDollar = Table.AddColumn(DurHours, "reward_per_dollar", each
                if [difficulty] = 0 then null else [reward] / [difficulty], type number),

    // readable axis label - the raw GUIDs are useless on a chart
    Label = Table.AddColumn(RewardPerDollar, "offer_label", each
                Text.Proper([offer_type]) & " " & Text.From([reward]) & "/" & Text.From([difficulty])
                & " (" & Text.From([duration]) & "d)", type text),
    Removed = Table.RemoveColumns(Label, {"channels"})
in
    Removed
```

Two offers share a label (`Bogo 10/10` at 5d and 7d differ, but `Discount 2/10` appears at 7d and 10d —
the duration in the label separates them). If any collision remains, add an index suffix.

**Channel bridge** — reference the Offers query, then expand the list to rows:

```m
let
    Source = Offers,
    Kept = Table.SelectColumns(Source, {"offer_id", "channel_list"}),
    Expanded = Table.ExpandListColumn(Kept, "channel_list"),
    Renamed = Table.RenameColumns(Expanded, {{"channel_list", "channel"}}),
    Typed = Table.TransformColumnTypes(Renamed, {{"channel", type text}})
in
    Typed
```

This is a many-to-many bridge: 10 offers → 33 rows. Relationship is `Offers[offer_id] 1 → * BridgeOfferChannel[offer_id]`.

---

## 3. Events — the JSON parse

**The trap in this dataset:** the key is `'offer id'` (with a space) for *received* and *viewed*, but
`'offer_id'` (with an underscore) for *completed*. Parse for only one and you silently lose all 33,579
completions. `offer completed` also carries a `'reward'` key the other events do not have.

```m
let
    Source = Csv.Document(File.Contents(DataFolder & "\events.csv"),
                [Delimiter=",", Columns=4, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
                {"customer_id", type text}, {"event", type text},
                {"value", type text}, {"time", Int64.Type}}),

    // single quotes -> double quotes, then parse as JSON record
    AsJson = Table.AddColumn(Typed, "value_record", each
                Json.Document(Text.Replace([value], "'", """"))),

    // handle BOTH key spellings
    OfferId = Table.AddColumn(AsJson, "offer_id", each
                Record.FieldOrDefault([value_record], "offer id",
                Record.FieldOrDefault([value_record], "offer_id", null)), type text),
    Amount = Table.AddColumn(OfferId, "amount", each
                Record.FieldOrDefault([value_record], "amount", null), type number),
    RewardPaid = Table.AddColumn(Amount, "reward_paid", each
                Record.FieldOrDefault([value_record], "reward", null), type number),

    Day = Table.AddColumn(RewardPaid, "day", each Number.IntegerDivide([time], 24), Int64.Type),
    Removed = Table.RemoveColumns(Day, {"value", "value_record"})
in
    Removed
```

Validation step before you move on — add a temporary group-by on `event` and confirm:

| event | rows | offer_id nulls | amount nulls |
| --- | --- | --- | --- |
| transaction | 138,953 | 138,953 | 0 |
| offer received | 76,277 | 0 | 138,953 |
| offer viewed | 57,725 | 0 | — |
| offer completed | 33,579 | 0 | — |

If `offer completed` shows 33,579 nulls in `offer_id`, the underscore key was missed.

---

## 4. Fact tables

**FactTransaction** — reference Events, keep transactions:

```m
let
    Source = Events,
    Txn = Table.SelectRows(Source, each [event] = "transaction"),
    Kept = Table.SelectColumns(Txn, {"customer_id", "time", "amount", "day"}),
    Renamed = Table.RenameColumns(Kept, {{"time", "txn_time"}}),
    Indexed = Table.AddIndexColumn(Renamed, "txn_id", 1, 1, Int64.Type)
in
    Indexed
```

**FactOfferDelivery** — one row per offer *delivery*, with the view and completion attributed to it.

This is the hard one, and it is where most of the analytical value sits. A customer can receive the
same offer more than once, so a completion has to be tied to the delivery whose validity window it
falls inside — not just to the offer id. Doing this in M is slow over 306k rows (nested table scans);
the practical options are:

1. **Recommended:** do this step once in Python (`etl_rewardsnext.py` in this pack) and load the
   resulting `fact_offer_delivery.csv`. The brief asks for Power Query JSON parsing, which steps 1–3
   satisfy; this step is a modelling decision, not an ingestion one, and documenting it that way is
   defensible.
2. Do it in M with `Table.Buffer` and a merge on `customer_id` + `offer_id`, then filter rows where
   `time >= received_at and time < window_end`, then de-duplicate to the earliest delivery.

The attribution rule, stated for the technical document:

- `window_end = MIN(received_at + duration_hours, next received_at for the same customer+offer)`
- a view or completion belongs to a delivery if `received_at <= event_time < window_end`
- each raw event is consumed once; where windows overlap, the earliest delivery wins

Applied to this dataset that leaves **1,375 views (2.4%)** and **869 completions (2.6%)** unattributable
— they fall outside any open window. They are excluded from the fact table and reported as a data
quality flag rather than silently dropped.

---

## 5. Supporting tables

**DimTime** (the dataset has no real dates — `time` is hours 0–719 from the start of the observation window):

```m
let
    Hours = {0..719},
    Table = Table.FromList(Hours, Splitter.SplitByNothing(), {"time_hour"}),
    Typed = Table.TransformColumnTypes(Table, {{"time_hour", Int64.Type}}),
    Day = Table.AddColumn(Typed, "day", each Number.IntegerDivide([time_hour], 24), Int64.Type),
    Week = Table.AddColumn(Day, "week", each Number.IntegerDivide([day], 7) + 1, Int64.Type)
in
    Week
```

Do **not** build a normal calendar table off `became_member_on` and try to relate it to `time`. They are
different clocks: one is a real signup date between 2013 and 2018, the other is an elapsed-hour counter
inside a 30-day window. Keep them separate.

**DataDictionary** — load `data_dictionary.csv` as-is, mark it **Hidden** in report view, and surface it
on an information page if you want. It is reference material, not model data; leave it out of the
relationship diagram.

---

## 6. Optimisation before you publish

- `Table.RemoveColumns` on `value`, `value_record`, the raw `channels`, the original `age` and
  `became_member_on` — all replaced by cleaned versions.
- Set `offer_id` and `customer_id` to text and leave them; do not add an index key on 17,000 customers,
  it buys nothing at this size.
- **Disable load** on the Events staging query once FactTransaction and FactOfferDelivery are derived
  from it — otherwise 306k rows import twice.
- Cardinality: `channels_text` has 4 distinct values, `offer_label` has 10. Both are cheap. The
  expensive column is `customer_id` at 17,000 distinct — unavoidable, it is the key.
