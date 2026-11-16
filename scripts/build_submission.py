"""Submission sheet PDF - one page, plain.
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
LINE = colors.HexColor("#D6D2C8")
BAND = colors.HexColor("#F0EEE7")

REPO = "https://github.com/saisureshwangde143-hub/Customer-Offer-Engagement-Dashoard"
PAGES = "https://saisureshwangde143-hub.github.io/Customer-Offer-Engagement-Dashoard/"

title = ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=INK, spaceAfter=2)
sub = ParagraphStyle("s", fontName="Helvetica", fontSize=10.5, leading=14, textColor=SOFT, spaceAfter=16)
h2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=ACCENT,
                    spaceBefore=16, spaceAfter=6)
lab = ParagraphStyle("lab", fontName="Helvetica", fontSize=9.5, leading=13, textColor=SOFT)
val = ParagraphStyle("val", fontName="Helvetica", fontSize=9.5, leading=13, textColor=INK)
item = ParagraphStyle("it", fontName="Helvetica", fontSize=9.5, leading=14, textColor=INK)
note = ParagraphStyle("n", fontName="Helvetica", fontSize=8.5, leading=11.5, textColor=SOFT)


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


path = OUT / "Submission_Sheet.pdf"
d = BaseDocTemplate(str(path), pagesize=A4,
                    title="Capstone Submission - Customer Offer Engagement Dashboard",
                    author="Sai Suresh Wangde",
                    leftMargin=22 * mm, rightMargin=22 * mm, topMargin=20 * mm, bottomMargin=20 * mm)
d.addPageTemplates([PageTemplate(id="m", frames=[Frame(d.leftMargin, d.bottomMargin, d.width, d.height, id="f")])])

f = []
f.append(Paragraph("Capstone Project Submission", title))
f.append(Paragraph("Certificate Program in Data Analytics with Specialization &#183; Batch 12", sub))

details = [
    ("Project", "Customer Offer Engagement Dashboard"),
    ("Submitted by", "Sai Suresh Wangde"),
    ("Group", "Group 3"),
    ("Group members", "Sai Suresh Wangde, Gaurav Thaware, Srikanth S,<br/>M S Praveen, Nilanjan Chowdhury, Vipin Kumar"),
    ("Tool", "Microsoft Power BI"),
    ("Dataset", "RewardsNext &#8212; 17,000 customers, 306,534 events, 10 offers"),
    ("Date", "16 November 2026"),
]
t = Table([[Paragraph(esc(a), lab), Paragraph(b, val)] for a, b in details],
          colWidths=[36 * mm, None])
t.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ("LINEBELOW", (0, 0), (-1, -2), 0.4, LINE),
]))
f.append(t)

f.append(Paragraph("Repository", h2))
box = Table([[Paragraph(
    f'<b>GitHub</b><br/><link href="{REPO}" color="#0E7C6B">{REPO}</link>'
    f'<br/><br/><b>Live dashboard</b><br/><link href="{PAGES}" color="#0E7C6B">{PAGES}</link>',
    ParagraphStyle("bx", fontName="Helvetica", fontSize=9.5, leading=14, textColor=INK))]],
    colWidths=[None])
box.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), BAND),
    ("LINEBEFORE", (0, 0), (0, -1), 2.5, ACCENT),
    ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ("TOPPADDING", (0, 0), (-1, -1), 9),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
]))
f.append(box)
f.append(Spacer(1, 6))
f.append(Paragraph(
    "GitHub displays .html files as source code. To view the dashboard, use the live link above, or "
    "download the repository and open <font face='Courier' size='8.5'>dashboard/index.html</font> in any "
    "browser &#8212; it needs no installation.", note))

f.append(Paragraph("Contents of the repository", h2))
contents = [
    ("docs/", "User Guide (one page) and Technical Document, both PDF"),
    ("powerbi/", "Power BI project, Power Query M code, 37 DAX measures, page specification"),
    ("dashboard/", "Interactive five-page dashboard"),
    ("model/", "Cleaned datasets used by the model"),
    ("analysis/", "Result tables and full findings"),
    ("scripts/", "Python pipeline that reproduces everything"),
]
t2 = Table([[Paragraph(f"<font face='Courier' size='9'>{esc(a)}</font>", val), Paragraph(esc(b), item)]
            for a, b in contents], colWidths=[30 * mm, None])
t2.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
]))
f.append(t2)

f.append(Paragraph("Key results", h2))
res = [("Offers delivered", "76,277"), ("View rate", "73.9%"),
       ("Redemption rate", "53.6%"), ("Total spend", "$1,775,452")]
t3 = Table([[Paragraph(esc(a), lab) for a, _ in res],
            [Paragraph(f"<b>{esc(b)}</b>", ParagraphStyle(
                "big", fontName="Helvetica-Bold", fontSize=15, leading=19, textColor=INK)) for _, b in res]],
           colWidths=[None] * 4)
t3.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 2),
    ("BOTTOMPADDING", (0, 0), (-1, 0), 1),
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("LINEABOVE", (0, 0), (-1, 0), 0.8, INK),
    ("TOPPADDING", (0, 0), (-1, 0), 7),
]))
f.append(t3)
f.append(Spacer(1, 10))
f.append(Paragraph(
    "Redemption is measured against promotional offers only; informational offers carry no spend threshold "
    "and cannot be completed. Full method in the Technical Document.", note))

d.build(f)
print(path, f"{path.stat().st_size/1024:.0f} KB")
