"""Submission sheet PDF.
Usage: python -I build_submission.py <out_dir>
"""
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle)

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

INK = colors.HexColor("#16202E")
SOFT = colors.HexColor("#4A5568")
ACCENT = colors.HexColor("#0E7C6B")
FLAG = colors.HexColor("#B45309")
LINE = colors.HexColor("#D6D2C8")
BAND = colors.HexColor("#F0EEE7")

REPO = "https://github.com/saisureshwangde143-hub/Customer-Offer-Engagement-Dashoard"
PAGES = "https://saisureshwangde143-hub.github.io/Customer-Offer-Engagement-Dashoard/"

B = 9
title = ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=19, leading=22, textColor=INK, spaceAfter=1)
sub = ParagraphStyle("s", fontName="Helvetica", fontSize=10, leading=13, textColor=SOFT, spaceAfter=10)
h2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=10.5, leading=13, textColor=ACCENT,
                    spaceBefore=10, spaceAfter=4)
body = ParagraphStyle("b", fontName="Helvetica", fontSize=B, leading=12.4, textColor=INK, spaceAfter=3)
small = ParagraphStyle("sm", fontName="Helvetica", fontSize=8, leading=11, textColor=SOFT, spaceAfter=2)
cell = ParagraphStyle("c", fontName="Helvetica", fontSize=8.2, leading=10.8, textColor=INK)
cellh = ParagraphStyle("ch", fontName="Helvetica-Bold", fontSize=7.8, leading=10, textColor=SOFT)
cellb = ParagraphStyle("cb", fontName="Helvetica-Bold", fontSize=8.2, leading=10.8, textColor=INK)
link = ParagraphStyle("lk", fontName="Helvetica-Bold", fontSize=9.5, leading=13, textColor=ACCENT)


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def table(rows, widths, font=8.2, head=True, zebra=False):
    t = Table(rows, colWidths=widths, repeatRows=1 if head else 0)
    cmds = [("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("LINEBELOW", (0, 0), (-1, -2), 0.4, LINE)]
    if head:
        cmds.append(("LINEBELOW", (0, 0), (-1, 0), 0.9, INK))
    if zebra:
        for i in range(1, len(rows)):
            if i % 2 == 0:
                cmds.append(("BACKGROUND", (0, i), (-1, i), BAND))
    t.setStyle(TableStyle(cmds))
    return t


def callout(text, color=ACCENT):
    t = Table([[Paragraph(text, ParagraphStyle("co", fontName="Helvetica", fontSize=8.4,
                                               leading=11.4, textColor=INK))]], colWidths=[None])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), BAND),
                           ("LINEBEFORE", (0, 0), (0, -1), 2.5, color),
                           ("LEFTPADDING", (0, 0), (-1, -1), 8),
                           ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                           ("TOPPADDING", (0, 0), (-1, -1), 6),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return t


path = OUT / "Submission_Sheet.pdf"
d = BaseDocTemplate(str(path), pagesize=A4, title="Capstone Submission - Customer Offer Engagement Dashboard",
                    author="Sai Suresh Wangde", leftMargin=15 * mm, rightMargin=15 * mm,
                    topMargin=14 * mm, bottomMargin=18 * mm)


def on_page(canvas, docu):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    y = docu.bottomMargin - 5 * mm
    canvas.line(docu.leftMargin, y, A4[0] - docu.rightMargin, y)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(SOFT)
    canvas.drawString(docu.leftMargin, y - 9,
                      "Capstone Submission - Customer Offer Engagement Dashboard - Sai Suresh Wangde, Group 3")
    canvas.drawRightString(A4[0] - docu.rightMargin, y - 9, "Page %d" % canvas.getPageNumber())
    canvas.restoreState()


d.addPageTemplates([PageTemplate(id="m", frames=[Frame(d.leftMargin, d.bottomMargin, d.width, d.height, id="f")],
                                 onPage=on_page)])

f = []
f.append(Paragraph("Capstone Project Submission", title))
f.append(Paragraph("Certificate Program in Data Analytics with Specialization &#183; Batch 12", sub))

# ---- submission details
f.append(Paragraph("Submission details", h2))
det = [
    ["Project title", "Customer Offer Engagement Dashboard (RewardsNext)"],
    ["Programme", "Certificate Program in Data Analytics with Specialization, Batch 12 (CPDA B12)"],
    ["Group", "Group 3"],
    ["Submitted by", "Sai Suresh Wangde"],
    ["Group members", "Sai Suresh Wangde, Gaurav Thaware, Srikanth S, M S Praveen, "
                      "Nilanjan Chowdhury, Vipin Kumar"],
    ["Primary tool", "Microsoft Power BI (Power Query M, star-schema model, DAX)"],
    ["Dataset", "RewardsNext: customers.csv, events.csv, offers.csv, data_dictionary.csv"],
    ["Scope", "17,000 customers &#183; 306,534 events &#183; 10 offers &#183; 30-day observation window"],
    ["Date of submission", "16 November 2026"],
]
f.append(table([[Paragraph(esc(a), cellh), Paragraph(b if "&#183;" in b else esc(b), cell)] for a, b in det],
               widths=[38 * mm, None], head=False))

# ---- repository
f.append(Paragraph("Repository and live dashboard", h2))
f.append(callout(
    f'<b>GitHub repository</b><br/><link href="{REPO}" color="#0E7C6B">{REPO}</link><br/><br/>'
    f'<b>Live dashboard (GitHub Pages)</b><br/><link href="{PAGES}" color="#0E7C6B">{PAGES}</link><br/>'
    '<font size="7.6" color="#4A5568">Clone URL: '
    f'{REPO}.git &#183; the repository is public and needs no account to view.</font>'))
f.append(Spacer(1, 4))
f.append(Paragraph(
    "<b>Note for the reviewer:</b> GitHub shows .html files as source code, not as rendered pages. "
    "To view the dashboard, use the GitHub Pages link above, or clone the repository and open "
    "<font face='Courier' size='8'>dashboard/index.html</font> in any browser &#8212; it runs from disk with no "
    "server and no dependencies.", small))

# ---- deliverables
f.append(Paragraph("Deliverables", h2))
rows = [[Paragraph("Deliverable", cellh), Paragraph("Location in repository", cellh), Paragraph("Status", cellh)]]
deliv = [
    ("User Guide (one-page PDF)", "docs/User_Guide.pdf", "Complete"),
    ("Technical Document (ERD, DAX, M steps, new offers)", "docs/Technical_Document.pdf", "Complete"),
    ("Power Query M - data ingestion and JSON parsing", "powerbi/01_PowerQuery_M.md", "Complete"),
    ("DAX measure library (37 measures)", "powerbi/02_DAX_Measures.md", "Complete"),
    ("Data model - star schema", "docs/Technical_Document.pdf, section 1", "Complete"),
    ("Segmentation and cohort analysis", "analysis/FINDINGS.md, sections 6-7", "Complete"),
    ("Insights and business recommendations", "docs/Insights_and_Recommendations.md", "Complete"),
    ("Interactive dashboard (web build, 5 pages)", "dashboard/", "Complete"),
    ("Cleaned star-schema datasets", "model/ (6 CSV files)", "Complete"),
    ("Reproducible pipeline (Python)", "scripts/ (3 scripts)", "Complete"),
    ("Power BI project file", "powerbi/RewardsNext.pbip", "Opens in Desktop"),
    ("Report page specification (5 pages)", "powerbi/03_Report_Page_Spec.md", "Spec complete"),
    ("Power BI .pbix", "to be saved from the .pbip project", "In progress"),
    ("Publish to Power BI Service", "workspace upload, permissions, refresh", "In progress"),
]
for a, b, c in deliv:
    col = "#0E7C6B" if c == "Complete" else "#B45309"
    rows.append([Paragraph(esc(a), cell),
                 Paragraph(f"<font face='Courier' size='7.6'>{esc(b)}</font>", cell),
                 Paragraph(f'<font color="{col}"><b>{esc(c)}</b></font>', cell)])
f.append(table(rows, widths=[68 * mm, 68 * mm, None], zebra=True))

# ---- headline results
f.append(Paragraph("Headline results", h2))
kp = [[Paragraph("Metric", cellh), Paragraph("Value", cellh), Paragraph("Metric", cellh), Paragraph("Value", cellh)]]
pairs = [("Offer deliveries", "76,277"), ("View rate", "73.9%"),
         ("Redemption rate", "53.6%"), ("Completions never viewed", "29.8%"),
         ("Total spend", "$1,775,452"), ("Average transaction", "$12.78"),
         ("Customers targeted", "16,994 of 17,000"), ("Reward paid with no view", "$47,773")]
for i in range(0, len(pairs), 2):
    kp.append([Paragraph(esc(pairs[i][0]), cell), Paragraph(esc(pairs[i][1]), cellb),
               Paragraph(esc(pairs[i + 1][0]), cell), Paragraph(esc(pairs[i + 1][1]), cellb)])
f.append(table(kp, widths=[48 * mm, 32 * mm, 50 * mm, None], zebra=True))

f.append(Spacer(1, 6))
f.append(Paragraph("Principal findings", h2))
f.append(Paragraph(
    "<b>1. Three in ten rewards buy nothing.</b> 9,739 of 32,710 completions came from customers who never "
    "opened the offer; they met the spend threshold on their own and the reward paid out with no marketing "
    "influence.<br/>"
    "<b>2. The cheapest offer performs best.</b> $2 on a $10 spend redeems at 68.6%; the $10 BOGO at 42.7%. "
    "Customers respond to the spend threshold, not the reward size.<br/>"
    "<b>3. Channel reach drives views.</b> Offers carried on all four channels are opened by 95.6% of "
    "recipients; email-and-web-only offers reach 34.6%.<br/>"
    "<b>4. Tenure outperforms demographics as a predictor.</b> Members of under one year redeem at 39.5% "
    "against 72.2% at one to two years, and they are over half the customer base.<br/>"
    "<b>5. Offers identify high-value customers more than they create them.</b> Average basket is $12.90 "
    "inside a viewed offer window against $12.64 outside any window. No holdout group exists in the data, "
    "so no uplift is claimed.", body))

f.append(Paragraph("Methodology notes", h2))
f.append(callout(
    "<b>Redemption excludes informational offers.</b> They carry no spend threshold, so no completion event "
    "can fire for them &#8212; 15,235 of 76,277 deliveries. Including them in the denominator gives 42.9% "
    "instead of 53.6%.<br/><br/>"
    "<b>The event JSON uses two key spellings.</b> 'offer id' for received and viewed, 'offer_id' for "
    "completed. Parsing for one spelling alone discards all 33,579 completion events while the report still "
    "renders.<br/><br/>"
    "<b>Completions are attributed to a specific delivery</b> only within that delivery's validity window. "
    "This leaves 869 completions (2.6%) and 1,375 views (2.4%) unattributable; these are excluded and "
    "reported rather than reassigned.<br/><br/>"
    "<b>2,175 customers have no age, gender or income.</b> The same rows are missing all three. They redeem "
    "at 13.6% because the accounts are dormant, not for any demographic reason, and are filtered out of "
    "segmentation by default.", FLAG))

f.append(Spacer(1, 6))
f.append(Paragraph(
    "All figures in this submission were produced twice through independent engines &#8212; the Power BI model "
    "and a Python pipeline reading the raw CSVs &#8212; and agree exactly. The reconciliation is documented in "
    "the Technical Document, section 6.", small))

d.build(f)
print(path, f"{path.stat().st_size/1024:.0f} KB")
