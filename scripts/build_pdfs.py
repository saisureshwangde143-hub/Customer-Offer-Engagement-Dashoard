"""Build the two submission PDFs: one-page User Guide, multi-page Technical Document.
Usage: python -I build_pdfs.py <out_dir>
"""
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, PageTemplate,
                                Paragraph, Preformatted, Spacer, Table, TableStyle)

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

INK = colors.HexColor("#16202E")
SOFT = colors.HexColor("#4A5568")
ACCENT = colors.HexColor("#0E7C6B")
FLAG = colors.HexColor("#B45309")
LINE = colors.HexColor("#D6D2C8")
BAND = colors.HexColor("#F0EEE7")


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def styles(base=9):
    s = {}
    s["title"] = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=base + 9,
                                leading=base + 11, textColor=INK, spaceAfter=2)
    s["sub"] = ParagraphStyle("sub", fontName="Helvetica", fontSize=base + 0.5,
                              leading=base + 3, textColor=SOFT, spaceAfter=7)
    s["h2"] = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=base + 1.5,
                             leading=base + 4, textColor=ACCENT, spaceBefore=8, spaceAfter=3)
    s["h3"] = ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=base + 0.5,
                             leading=base + 3, textColor=INK, spaceBefore=5, spaceAfter=2)
    s["body"] = ParagraphStyle("body", fontName="Helvetica", fontSize=base,
                               leading=base + 3.2, textColor=INK, alignment=TA_LEFT, spaceAfter=3)
    s["small"] = ParagraphStyle("small", fontName="Helvetica", fontSize=base - 1,
                                leading=base + 2, textColor=SOFT, spaceAfter=2)
    s["flag"] = ParagraphStyle("flag", fontName="Helvetica", fontSize=base - 0.5,
                               leading=base + 2.4, textColor=INK, spaceAfter=2,
                               leftIndent=5, borderPadding=0)
    s["code"] = ParagraphStyle("code", fontName="Courier", fontSize=base - 1.5,
                               leading=base + 1, textColor=INK)
    return s


def table(data, widths, head=True, font=8, align_right=None):
    t = Table(data, colWidths=widths, repeatRows=1 if head else 0)
    cmds = [
        ("FONT", (0, 0), (-1, -1), "Helvetica", font),
        ("TEXTCOLOR", (0, 0), (-1, -1), INK),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, LINE),
    ]
    if head:
        cmds += [("FONT", (0, 0), (-1, 0), "Helvetica-Bold", font - 0.5),
                 ("TEXTCOLOR", (0, 0), (-1, 0), SOFT),
                 ("LINEBELOW", (0, 0), (-1, 0), 0.8, INK)]
    if align_right:
        for c in align_right:
            cmds.append(("ALIGN", (c, 0), (c, -1), "RIGHT"))
    t.setStyle(TableStyle(cmds))
    return t


def callout(text, st, color=FLAG):
    p = Paragraph(text, st["flag"])
    t = Table([[p]], colWidths=[None])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BAND),
        ("LINEBEFORE", (0, 0), (0, -1), 2.5, color),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def doc_template(path, title, footer_text, margin=14 * mm):
    d = BaseDocTemplate(str(path), pagesize=A4, title=title,
                        author="CPDA B12 Capstone Group 3",
                        leftMargin=margin, rightMargin=margin,
                        topMargin=margin, bottomMargin=margin + 4 * mm)

    def on_page(canvas, docu):
        canvas.saveState()
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.5)
        y = docu.bottomMargin - 5 * mm
        canvas.line(docu.leftMargin, y, A4[0] - docu.rightMargin, y)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(SOFT)
        canvas.drawString(docu.leftMargin, y - 9, footer_text)
        canvas.drawRightString(A4[0] - docu.rightMargin, y - 9, "Page %d" % canvas.getPageNumber())
        canvas.restoreState()

    frame = Frame(d.leftMargin, d.bottomMargin, d.width, d.height, id="f", showBoundary=0)
    d.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=on_page)])
    return d


# =====================================================================
#  1. USER GUIDE - exactly one page
# =====================================================================
def build_user_guide():
    st = styles(8.2)
    path = OUT / "User_Guide.pdf"
    d = doc_template(path, "RewardsNext Dashboard - User Guide",
                     "RewardsNext Customer Offer Engagement Dashboard - User Guide - CPDA B12 Capstone, Group 3",
                     margin=13 * mm)
    f = []
    f.append(Paragraph("Customer Offer Engagement Dashboard", st["title"]))
    f.append(Paragraph("User guide for the marketing team &#183; RewardsNext &#183; 17,000 customers, "
                       "76,277 offer deliveries, 138,953 transactions across a 30-day window.", st["sub"]))

    f.append(Paragraph("Refreshing the data", st["h2"]))
    f.append(Paragraph(
        "<b>Power BI Desktop:</b> Home &#8594; Refresh. Takes under three minutes for the full dataset. "
        "<b>Power BI Service:</b> refresh runs on the workspace schedule; to force one, open the workspace, "
        "click &#183;&#183;&#183; next to the semantic model and choose Refresh now. If a refresh fails, the usual "
        "cause is the source folder having moved &#8212; correct the path under Transform data &#8594; Data source settings.",
        st["body"]))

    f.append(Paragraph("The five pages", st["h2"]))
    rows = [["Page", "Use it to answer"],
            ["1 Overview", "How are we doing overall? Redemption, spend, offer volumes."],
            ["2 Offer Funnel", "Where do customers drop out — delivery, opening, or completing?"],
            ["3 Customer Segmentation", "Who responds? By age, income, gender and tenure."],
            ["4 Offer Performance", "Which offers work, at what reward cost, through which channels?"],
            ["5 Transaction Behaviour", "Do customers who complete offers spend differently?"]]
    f.append(table([[Paragraph(f"<b>{esc(r[0])}</b>" if i else f"<b>{esc(r[0])}</b>",
                               ParagraphStyle("c", fontName="Helvetica", fontSize=8, leading=10.5,
                                              textColor=SOFT if i == 0 else INK)),
                     Paragraph(esc(r[1]), ParagraphStyle("c2", fontName="Helvetica", fontSize=8,
                                                         leading=10.5, textColor=SOFT if i == 0 else INK))]
                    for i, r in enumerate(rows)],
                   widths=[42 * mm, None], head=True, font=8))

    f.append(Paragraph("Using the slicers", st["h2"]))
    f.append(Paragraph(
        "The slicer panel sits in the same place on every page and <b>stays applied as you move between "
        "pages</b>. Filter by offer type (bogo, discount, informational), channel, age group, income band, "
        "gender and tenure. Clear everything with the eraser icon at the top of the panel. The bookmark "
        "buttons below the slicers jump to saved views: All customers, Complete profiles only, Champions only. "
        "To see the customers behind any offer, right-click a bar on page 4 and choose Drill through &#8594; "
        "Customer detail.", st["body"]))

    f.append(Paragraph("Two things to know before you quote a number", st["h2"]))
    f.append(callout(
        "<b>1. Redemption rate excludes informational offers.</b> They carry no spend threshold and no reward, "
        "so they can never be completed &#8212; 15,235 of the 76,277 deliveries. The dashboard leaves them out of "
        "the denominator, which is why it reads <b>53.6%</b> and not the 42.9% you get by dividing completions "
        "by every offer sent. If you are comparing against a figure from elsewhere, check which denominator it used.",
        st, FLAG))
    f.append(Spacer(1, 4))
    f.append(callout(
        "<b>2. The Complete profiles only filter is on by default, deliberately.</b> 2,175 customers have no age, "
        "gender or income recorded &#8212; the same rows in all three columns. They redeem at 13.6% against 53.6% "
        "overall, but that reflects dormant accounts rather than any demographic group. Leaving them in drags every "
        "segmentation chart toward a misleading story. Switch the filter off only when you need totals that "
        "reconcile to the full customer base.",
        st, FLAG))

    f.append(Paragraph("What the headline numbers mean", st["h2"]))
    kpi = [["Number", "Reading"],
           ["53.6% redemption", "Just over half of promotional offers get completed."],
           ["73.9% view rate", "Most delivered offers do get opened — delivery is not the bottleneck."],
           ["29.8% of completions unviewed", "Nearly three in ten rewards go to customers who never opened the offer."],
           ["$12.78 average transaction", "Barely moves inside or outside an offer window ($12.90 vs $12.64)."],
           ["79.3% of revenue", "Comes from Champions — 48.6% of customers."]]
    f.append(table([[Paragraph(f"<b>{esc(r[0])}</b>" if i else esc(r[0]),
                               ParagraphStyle("k", fontName="Helvetica", fontSize=8, leading=10.5,
                                              textColor=SOFT if i == 0 else INK)),
                     Paragraph(esc(r[1]), ParagraphStyle("k2", fontName="Helvetica", fontSize=8,
                                                         leading=10.5, textColor=SOFT if i == 0 else INK))]
                    for i, r in enumerate(kpi)],
                   widths=[52 * mm, None], head=True, font=8))

    f.append(Spacer(1, 5))
    f.append(Paragraph(
        "<b>Who to ask</b> &#8212; data refresh and source files: L1 &#183; event parsing and funnel figures: L2 &#183; "
        "segmentation and cohorts: L3 &#183; offer performance and drill-through: L4 &#183; transaction analysis and QA: L5. "
        "<i>Replace the role codes with the Group 3 names before submission.</i>", st["small"]))

    d.build(f)
    return path


# =====================================================================
#  2. TECHNICAL DOCUMENT
# =====================================================================
ERD = """
          +---------------------------+
          |         Customers         |  17,000 rows
          |---------------------------|
          | customer_id        (PK)   |
          | became_member_on_date     |
          | membership_year           |
          | gender_clean, age_group   |
          | income_band, tenure_band  |
          | profile_complete          |
          | engagement_segment        |
          +-------------+-------------+
                        | 1
          +-------------+--------------+
          | *                          | *
+---------+-----------+   +------------+-----------+
|  FactOfferDelivery  |   |    FactTransaction     |
|  76,277 rows        |   |  138,953 rows          |
|---------------------|   |------------------------|
| customer_id   (FK)  |   | txn_id          (PK)   |
| offer_id      (FK)  |   | customer_id     (FK)   |
| delivery_seq        |   | txn_time        (FK)   |
| received_at         |   | amount, day            |
| window_end          |   | in_offer_window        |
| viewed_at           |   | in_viewed_offer_window |
| completed_at        |   +-----------+------------+
| was_viewed          |               | *
| was_completed       |               |
| viewed_before_compl.|   +-----------+------------+
| completed_unviewed  |   |        DimTime         |  720 rows
| hours_to_view       |   |------------------------|
| hours_to_complete   |   | time_hour       (PK)   |
+---------+-----------+   | day, week              |
          | *             +------------------------+
          | 1
+---------+-----------+        +----------------------+
|       Offers        |  1   * | BridgeOfferChannel   |  33 rows
|   10 rows           |--------|----------------------|
|---------------------|        | offer_id       (FK)  |
| offer_id      (PK)  |        | channel              |
| offer_label         |        +----------------------+
| offer_type          |
| difficulty, reward  |        Bidirectional filter on the bridge
| duration            |        only; every other relationship is
| channels_text       |        single-direction.
| is_informational    |
+---------------------+
"""

DAX = [
    ("Offers Sent", "COUNTROWS ( FactOfferDelivery )", "76,277"),
    ("Offers Viewed", "CALCULATE ( COUNTROWS ( FactOfferDelivery ), FactOfferDelivery[was_viewed] = TRUE () )", "56,350"),
    ("Offers Completed", "CALCULATE ( COUNTROWS ( FactOfferDelivery ), FactOfferDelivery[was_completed] = TRUE () )", "32,710"),
    ("View Rate", "DIVIDE ( [Offers Viewed], [Offers Sent] )", "73.9%"),
    ("Promotional Offers Sent", "CALCULATE ( COUNTROWS ( FactOfferDelivery ), FILTER ( ALL ( Offers[is_informational] ), Offers[is_informational] = FALSE () ) )", "61,042"),
    ("Redemption Rate", "DIVIDE ( [Offers Completed], [Promotional Offers Sent] )", "53.6%"),
    ("Redemption Rate (naive)", "DIVIDE ( [Offers Completed], [Offers Sent] )   -- hidden; methodology slide only", "42.9%"),
    ("Influenced Completions", "CALCULATE ( COUNTROWS ( FactOfferDelivery ), FactOfferDelivery[viewed_before_completed] = TRUE () )", "22,971"),
    ("Unviewed Completions", "CALCULATE ( COUNTROWS ( FactOfferDelivery ), FactOfferDelivery[completed_unviewed] = TRUE () )", "9,739"),
    ("Influenced Redemption Rate", "DIVIDE ( [Influenced Completions], [Promotional Offers Sent] )", "37.6%"),
    ("Unviewed Completion Share", "DIVIDE ( [Unviewed Completions], [Offers Completed] )", "29.8%"),
    ("Reward Cost", "SUMX ( FILTER ( FactOfferDelivery, FactOfferDelivery[was_completed] = TRUE () ), RELATED ( Offers[reward] ) )", ""),
    ("Wasted Reward Cost", "SUMX ( FILTER ( FactOfferDelivery, FactOfferDelivery[completed_unviewed] = TRUE () ), RELATED ( Offers[reward] ) )", "$47,773"),
    ("Wasted Reward %", "DIVIDE ( [Wasted Reward Cost], [Reward Cost] )", ""),
    ("Funnel Value", "VAR Stage = SELECTEDVALUE ( FunnelStages[Stage] ) RETURN SWITCH ( Stage, \"1. Received\", [Offers Sent], \"2. Viewed\", [Offers Viewed], \"3. Completed\", [Offers Completed] )", ""),
    ("Funnel % of Received", "DIVIDE ( [Funnel Value], [Offers Sent] )", ""),
    ("Avg Hours to View", "AVERAGE ( FactOfferDelivery[hours_to_view] )", ""),
    ("Avg Hours to Complete", "AVERAGE ( FactOfferDelivery[hours_to_complete] )", "40.7-100.3"),
    ("Total Spend", "SUM ( FactTransaction[amount] )", "$1,775,452"),
    ("Transactions", "COUNTROWS ( FactTransaction )", "138,953"),
    ("Avg Transaction", "AVERAGE ( FactTransaction[amount] )", "$12.78"),
    ("Spend in Viewed Offer Window", "CALCULATE ( [Total Spend], FactTransaction[in_viewed_offer_window] = TRUE () )", ""),
    ("Spend Outside Offer Window", "CALCULATE ( [Total Spend], FactTransaction[in_offer_window] = FALSE () )", ""),
    ("Avg Transaction in Viewed Window", "CALCULATE ( [Avg Transaction], FactTransaction[in_viewed_offer_window] = TRUE () )", "$12.90"),
    ("Avg Transaction Outside Window", "CALCULATE ( [Avg Transaction], FactTransaction[in_offer_window] = FALSE () )", "$12.64"),
    ("Spend per Customer", "DIVIDE ( [Total Spend], DISTINCTCOUNT ( FactTransaction[customer_id] ) )", ""),
    ("Customers", "DISTINCTCOUNT ( Customers[customer_id] )", "17,000"),
    ("Targeted Customers", "DISTINCTCOUNT ( FactOfferDelivery[customer_id] )", "16,994"),
    ("Customer Redemption Rate", "AVERAGEX ( VALUES ( Customers[customer_id] ), CALCULATE ( DIVIDE ( [Offers Completed], [Promotional Offers Sent] ) ) )", ""),
    ("Profile Complete %", "DIVIDE ( CALCULATE ( [Customers], Customers[profile_complete] = TRUE () ), [Customers] )", "87.2%"),
    ("Redemption Rate (complete profiles only)", "CALCULATE ( [Redemption Rate], Customers[profile_complete] = TRUE () )", ""),
    ("Offer Rank by Redemption", "RANKX ( ALL ( Offers[offer_label] ), [Redemption Rate],, DESC )", ""),
    ("Best Offer Label", "VAR T = TOPN ( 1, ALL ( Offers[offer_label] ), [Redemption Rate], DESC ) RETURN CONCATENATEX ( T, Offers[offer_label], \", \" )", "Discount 2/10"),
    ("KPI Subtitle", "\"Across \" & FORMAT ( [Promotional Offers Sent], \"#,0\" ) & \" promotional offers to \" & FORMAT ( [Targeted Customers], \"#,0\" ) & \" customers\"", ""),
    ("QA Row Count Check", "IF ( [Offers Sent] = 76277, \"PASS\", \"FAIL: \" & FORMAT ( [Offers Sent], \"#,0\" ) )", "PASS"),
    ("QA Completion Check", "IF ( [Offers Completed] = 32710, \"PASS\", \"FAIL: \" & FORMAT ( [Offers Completed], \"#,0\" ) )", "PASS"),
    ("QA Spend Check", "IF ( ROUND ( [Total Spend], 0 ) = 1775452, \"PASS\", \"FAIL: \" & FORMAT ( [Total Spend], \"#,0\" ) )", "PASS"),
]

M_EVENTS = """let
    Source = Csv.Document(File.Contents(DataFolder & "\\events.csv"),
                [Delimiter=",", Columns=4, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
                {"customer_id", type text}, {"event", type text},
                {"value", type text}, {"time", Int64.Type}}),

    // value is a PYTHON dict literal, not JSON: single quotes must be swapped first
    AsJson = Table.AddColumn(Typed, "value_record", each
                Json.Document(Text.Replace([value], "'", @Q@))),

    // the key is spelled BOTH ways - 'offer id' and 'offer_id'
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
    Removed"""

QUAD = chr(34) * 4
M_CHANNELS = """let
    Source = Csv.Document(File.Contents(DataFolder & "\\offers.csv"),
                [Delimiter=",", Columns=6, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),

    // ['email','mobile'] -> ["email","mobile"] -> a real list
    ChannelList = Table.AddColumn(Promoted, "channel_list", each
                Json.Document(Text.Replace([channels], "'", @Q@))),
    Expanded = Table.ExpandListColumn(
                Table.SelectColumns(ChannelList, {"offer_id", "channel_list"}), "channel_list"),
    Renamed = Table.RenameColumns(Expanded, {{"channel_list", "channel"}})
in
    Renamed"""


M_EVENTS = M_EVENTS.replace("@Q@", QUAD)
M_CHANNELS = M_CHANNELS.replace("@Q@", QUAD)


def build_technical():
    st = styles(9)
    path = OUT / "Technical_Document.pdf"
    d = doc_template(path, "RewardsNext - Technical Document",
                     "RewardsNext Customer Offer Engagement Dashboard - Technical Document - CPDA B12 Capstone, Group 3")
    f = []
    f.append(Paragraph("Customer Offer Engagement Dashboard", st["title"]))
    f.append(Paragraph("Technical document &#183; RewardsNext &#183; CPDA B12 Capstone, Group 3 &#183; "
                       "17,000 customers, 306,534 events, 10 offers, 30-day observation window.", st["sub"]))

    # 1 ERD
    f.append(Paragraph("1. Data model (ERD)", st["h2"]))
    f.append(Preformatted(ERD.strip("\n"), ParagraphStyle(
        "erd", fontName="Courier", fontSize=5.9, leading=7.1, textColor=INK)))
    f.append(Spacer(1, 4))
    rel = [["From", "To", "Cardinality", "Direction"],
           ["Customers[customer_id]", "FactOfferDelivery[customer_id]", "1 to many", "Single"],
           ["Customers[customer_id]", "FactTransaction[customer_id]", "1 to many", "Single"],
           ["Offers[offer_id]", "FactOfferDelivery[offer_id]", "1 to many", "Single"],
           ["Offers[offer_id]", "BridgeOfferChannel[offer_id]", "1 to many", "Both"],
           ["DimTime[time_hour]", "FactTransaction[txn_time]", "1 to many", "Single"],
           ["FunnelStages[Stage]", "(disconnected)", "-", "-"]]
    f.append(table(rel, widths=[48 * mm, 58 * mm, 26 * mm, None], font=7.6))
    f.append(Spacer(1, 5))
    f.append(callout(
        "<b>Grain statement.</b> FactOfferDelivery is one row per offer <i>delivery</i> &#8212; not per offer and "
        "not per customer. A customer who receives the same offer twice generates two rows. This is the decision "
        "that makes the whole model work.", st, ACCENT))

    # 2 lineage
    f.append(Paragraph("2. Source-to-target lineage", st["h2"]))
    lin = [["Target table", "Source", "Key transformation"],
           ["Customers", "customers.csv", "YYYYMMDD integer to Date; age 118 to null; demographic banding; profile-complete flag"],
           ["Offers", "offers.csv", "Python-list channels to JSON to list; readable label; informational flag"],
           ["BridgeOfferChannel", "Offers", "Expand channel list to rows (10 offers to 33 rows)"],
           ["FactTransaction", "events.csv (transaction)", "Parse {'amount': n}; offer-window flags"],
           ["FactOfferDelivery", "events.csv (all types)", "JSON parse plus window attribution (section 4)"],
           ["DimTime", "generated", "Hours 0-719 to day and week"]]
    f.append(table([[Paragraph(f"<b>{esc(r[0])}</b>" if i else esc(r[0]),
                               ParagraphStyle("l0", fontName="Helvetica", fontSize=7.6, leading=9.6,
                                              textColor=SOFT if i == 0 else INK)),
                     Paragraph(esc(r[1]), ParagraphStyle("l1", fontName="Courier" if i else "Helvetica",
                                                         fontSize=7.2 if i else 7.6, leading=9.6,
                                                         textColor=SOFT if i == 0 else INK)),
                     Paragraph(esc(r[2]), ParagraphStyle("l2", fontName="Helvetica", fontSize=7.6,
                                                         leading=9.6, textColor=SOFT if i == 0 else INK))]
                    for i, r in enumerate(lin)],
                   widths=[33 * mm, 36 * mm, None], font=7.6))

    # 3 M steps
    f.append(Paragraph("3. Power Query M steps for JSON extraction", st["h2"]))
    f.append(Paragraph("The events.value field hides two traps, and both are silent failures.", st["body"]))
    f.append(Paragraph("<b>Trap 1 &#8212; value is not JSON.</b> It is a Python dict literal with single quotes, "
                       "so Json.Document rejects it until the quotes are swapped.", st["body"]))
    f.append(Paragraph("<b>Trap 2 &#8212; the key is spelled two different ways.</b> "
                       "'offer id' (with a space) for <i>offer received</i> and <i>offer viewed</i>, but "
                       "'offer_id' (with an underscore) for <i>offer completed</i>. Parse for one spelling only and "
                       "all 33,579 completions arrive as null &#8212; the report still renders, showing a 0% "
                       "redemption rate, which is why this is the most dangerous defect in the build.", st["body"]))
    f.append(Spacer(1, 3))
    f.append(Paragraph("Query: Events", st["h3"]))
    f.append(Preformatted(M_EVENTS, st["code"]))
    f.append(Spacer(1, 5))
    f.append(Paragraph("Query: BridgeOfferChannel (the same quote-swap on the channels array)", st["h3"]))
    f.append(Preformatted(M_CHANNELS, st["code"]))
    f.append(Spacer(1, 5))
    f.append(Paragraph("Validation after parsing &#8212; group by event and confirm these counts:", st["body"]))
    f.append(table([["event", "rows", "offer_id nulls", "amount nulls"],
                    ["transaction", "138,953", "138,953", "0"],
                    ["offer received", "76,277", "0", "138,953"],
                    ["offer viewed", "57,725", "0", "-"],
                    ["offer completed", "33,579", "0", "-"]],
                   widths=[38 * mm, 28 * mm, 32 * mm, None], font=8, align_right=[1, 2, 3]))

    # 4 attribution
    f.append(Paragraph("4. Offer-window attribution", st["h2"]))
    f.append(Paragraph(
        "A completion event names the offer and the time, but not <i>which delivery</i> of it. Since a customer "
        "can receive the same offer more than once, completions must be matched to a delivery window:", st["body"]))
    f.append(Preformatted(
        "window_end = MIN( received_at + duration x 24 , next received_at for same customer+offer )\n"
        "attributed = received_at <= event_time < window_end\n"
        "tie-break  = earliest delivery wins; each raw event is consumed once", st["code"]))
    f.append(Spacer(1, 4))
    f.append(table([["", "Raw events", "Attributed", "Unattributable", "% lost"],
                    ["Views", "57,725", "56,350", "1,375", "2.4%"],
                    ["Completions", "33,579", "32,710", "869", "2.6%"]],
                   widths=[30 * mm, 30 * mm, 30 * mm, 33 * mm, None], font=8, align_right=[1, 2, 3, 4]))
    f.append(Spacer(1, 4))
    f.append(Paragraph("Unattributable events fall outside any open window (a completion logged after the offer "
                       "expired). They are excluded from the fact table and reported as a data-quality flag rather "
                       "than dropped silently or force-fitted to the nearest delivery.", st["small"]))

    # 5 DAX
    f.append(Paragraph("5. DAX formulas", st["h2"]))
    f.append(Paragraph("All 37 measures live on a dedicated _Measures table, foldered by theme. The expected "
                       "column is the value each measure returns on the unfiltered dataset &#8212; if your model "
                       "disagrees, the model is wrong, not the measure.", st["small"]))
    f.append(Spacer(1, 3))
    hdr = ParagraphStyle("dh", fontName="Helvetica-Bold", fontSize=7.4, leading=9, textColor=SOFT)
    nm = ParagraphStyle("dn", fontName="Helvetica-Bold", fontSize=7.3, leading=8.8, textColor=INK)
    cd = ParagraphStyle("dc", fontName="Courier", fontSize=6.5, leading=8, textColor=INK)
    ex = ParagraphStyle("de", fontName="Helvetica", fontSize=7.3, leading=8.8, textColor=ACCENT)
    rows = [[Paragraph("Measure", hdr), Paragraph("Definition", hdr), Paragraph("Expected", hdr)]]
    for name, code, expect in DAX:
        rows.append([Paragraph(esc(name), nm), Paragraph(esc(code), cd), Paragraph(esc(expect), ex)])
    f.append(table(rows, widths=[33 * mm, None, 19 * mm], font=7))

    # 6 validation
    f.append(Paragraph("6. Validation", st["h2"]))
    f.append(Paragraph(
        "Every model figure was independently reproduced by a Python pipeline that reads the raw CSVs through a "
        "different engine and applies the same rules. Agreement between the two engines is the validation evidence.", st["body"]))
    f.append(table([["Check", "Expected", "Where"],
                    ["Offer deliveries", "76,277", "[QA Row Count Check]"],
                    ["Completions attributed", "32,710", "[QA Completion Check]"],
                    ["Total spend", "$1,775,452", "[QA Spend Check]"],
                    ["Transactions", "138,953", "QA page table"],
                    ["Redemption rate", "53.6%", "KPI card vs kpi_headline.csv"]],
                   widths=[55 * mm, 35 * mm, None], font=8))
    f.append(Spacer(1, 4))
    f.append(Paragraph("<b>Referential integrity:</b> zero orphan offer_id values and zero orphan customer_id "
                       "values across all 306,534 events. All ten offers appear in the event stream; 16,994 of "
                       "17,000 customers received at least one offer.", st["small"]))

    # 7 adding offers
    f.append(Paragraph("7. Adding a new offer", st["h2"]))
    f.append(Paragraph(
        "1. Append the row to offers.csv &#8212; offer_id, offer_type, difficulty, reward, duration, and channels "
        "as a quoted Python list, e.g. \"['email', 'mobile', 'social']\".<br/>"
        "2. Refresh. Offers and BridgeOfferChannel pick it up with no edit, because the channel expansion is generic.<br/>"
        "3. If offer_type is a new value, extend the is_informational test and check the colour mapping on page 4.<br/>"
        "4. Re-run the ETL so FactOfferDelivery covers the new offer's deliveries.<br/>"
        "5. Update the hard-coded totals in the three QA measures to the new expected counts, then confirm all "
        "three read PASS.", st["body"]))

    # 8 limitations
    f.append(Paragraph("8. Known limitations", st["h2"]))
    f.append(Paragraph(
        "&#183; <b>No calendar.</b> time is hours since the start of the observation window, not a date. Membership "
        "dates (2013-2018) are a separate clock, so no seasonality analysis is possible.<br/>"
        "&#183; <b>No control group.</b> Every customer in the data received offers, so no true uplift can be "
        "computed &#8212; only comparisons that conflate behaviour with selection.<br/>"
        "&#183; <b>Transactions carry no offer id.</b> Spend is linked to offers by time window, not by attribution.<br/>"
        "&#183; <b>2,175 incomplete profiles cannot be imputed credibly.</b> They are flagged and filtered, not filled.<br/>"
        "&#183; <b>Only 8 promotional design points.</b> difficulty, reward and duration co-vary, so the negative "
        "difficulty-redemption relationship is clear but the independent effect of reward size is not separable.",
        st["body"]))

    d.build(f)
    return path


p1 = build_user_guide()
p2 = build_technical()
for p in (p1, p2):
    print(p, f"{p.stat().st_size/1024:.0f} KB")
