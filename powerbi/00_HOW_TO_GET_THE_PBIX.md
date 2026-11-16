# How to produce `RewardsNext.pbix`

A `.pbix` is a compiled binary — it contains a built Analysis Services tabular model that only Power BI
Desktop can generate. Nobody can hand you a finished `.pbix` from outside the application.

What is in this folder instead is a **Power BI Project (`.pbip`)**: the same model written as text, which
Power BI Desktop opens natively and then saves as a `.pbix`. The model, all six relationships and all
**38 DAX measures** are already defined. You do not build them by hand.

---

## The 5-minute path

1. **Check the data path.** Every table loads from
   `D:\Users\Ravindra\Desktop\RewardsNext_Capstone\model\`. If the folder has moved, open
   `RewardsNext.SemanticModel\definition\tables\*.tmdl` in Notepad and update the path — it appears once
   per table in the `partition` block.

2. **Turn the preview on, once.** Power BI Desktop → File → Options and settings → Options → Preview
   features → tick **Power BI Project (.pbip) save option** (and **Store semantic model using TMDL
   format** if listed). Restart Desktop.

3. **Open `RewardsNext.pbip`** — double-click it, or File → Open → browse to it.

4. **Refresh.** Home → Refresh. Roughly 215,000 rows across five tables; well inside the 3-minute target.

5. **Save as `.pbix`.** File → Save As → change *Save as type* to **Power BI files (\*.pbix)** →
   name it `RewardsNext.pbix`.

That file is deliverable 1.

---

## Then build the pages

The report opens with six **named but empty** pages: Overview, Offer Funnel, Customer Segmentation,
Offer Performance, Transaction Behaviour, QA. Page layouts are the one part not scripted here — report
JSON is brittle to hand-author, and a malformed visual breaks the whole file.

Build them from `03_Report_Page_Spec.md`, which names every visual, the fields to drop on it, and the
number it should produce. Dragging them out takes an hour or two, and it is the part of the work your
group should be seen to have done.

Check as you go: every KPI card has a documented expected value. If a card disagrees, the model is
wrong, not the measure.

---

## What to verify first

Put a card on the QA page with `[QA Row Count Check]`, `[QA Completion Check]` and `[QA Spend Check]`.
All three should read **PASS**. They hard-code 76,277 deliveries, 32,710 completions and $1,775,452 of
spend — the figures the Python pipeline produced independently.

If one reads FAIL, the refresh picked up something unexpected; check the file paths before building
anything else.

---

## If the project will not open

The `.pbip` format needs a reasonably current Power BI Desktop (2024 or later) with the preview feature
enabled. If Desktop refuses the project, fall back to the manual route, which has no version
dependency:

1. New file → Get Data → Text/CSV → load the five CSVs from `..\model\`.
2. Build relationships per the ERD in `..\docs\Technical_Document.md` §1.
3. Paste the measures from `02_DAX_Measures.md`.

That is a slower path to the same place. `01_PowerQuery_M.md` additionally shows the parse done from the
**raw** event file — worth reading whichever route you take, since the JSON-parsing traps it documents
are what the brief's task B.1 is actually testing.

---

## Honest status

The model definition here was written to the TMDL specification but has **not been opened in Power BI
Desktop** — there is no Power BI on this machine to test it with. Expect to verify it rather than trust
it. The measures and the M queries are the parts that carry the real value, and both are reproduced in
`02_DAX_Measures.md` and `01_PowerQuery_M.md` so nothing is lost if the project file needs fixing.
