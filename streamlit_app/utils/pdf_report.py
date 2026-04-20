"""ReportLab clinical PDF report for CNV analysis results."""

from io import BytesIO
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

DARK  = colors.HexColor("#1e3a5f")
RED   = colors.HexColor("#ef4444")
ORANGE= colors.HexColor("#f97316")
YELLOW= colors.HexColor("#eab308")
GRAY  = colors.HexColor("#6b7280")
LITE  = colors.HexColor("#f8fafc")
BORD  = colors.HexColor("#e2e8f0")
TEXT  = colors.HexColor("#1f2937")

ACMG_COLORS_RL = {
    "Pathogenic":        RED,
    "Likely Pathogenic": ORANGE,
    "VUS":               YELLOW,
    "Likely Benign":     GRAY,
    "Benign":            GRAY,
}

styles = getSampleStyleSheet()

def S(name="Normal", **kw):
    return ParagraphStyle(name + str(id(kw)), parent=styles.get(name, styles["Normal"]), **kw)

TITLE  = S("Title",   fontSize=14, leading=18, textColor=DARK, alignment=TA_CENTER, spaceAfter=4)
H1     = S("Heading1",fontSize=11, leading=14, textColor=DARK, fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4)
BODY   = S("Normal",  fontSize=9,  leading=13, textColor=TEXT, spaceAfter=4, alignment=TA_JUSTIFY)
SMALL  = S("Normal",  fontSize=8,  leading=11, textColor=GRAY, spaceAfter=3)
WARN   = S("Normal",  fontSize=8.5,leading=12, textColor=RED,  fontName="Helvetica-Bold", spaceAfter=3)

def hr():
    return HRFlowable(width="100%", thickness=0.4, color=BORD, spaceAfter=4)

def stab(data, widths):
    ts = TableStyle([
        ("BACKGROUND",    (0,0),(-1,0), DARK),
        ("TEXTCOLOR",     (0,0),(-1,0), colors.white),
        ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 8),
        ("LEADING",       (0,0),(-1,-1), 10),
        ("ALIGN",         (0,0),(-1,-1), "CENTER"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [LITE, colors.white]),
        ("GRID",          (0,0),(-1,-1), 0.4, BORD),
        ("TOPPADDING",    (0,0),(-1,-1), 3),
        ("BOTTOMPADDING", (0,0),(-1,-1), 3),
    ])
    return Table(data, colWidths=[w*cm for w in widths], style=ts, repeatRows=1)


def generate_pdf(results_df, patient_id: str, sample_id: str, indication: str) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        leftMargin=2.2*cm, rightMargin=2.2*cm,
        topMargin=2.2*cm, bottomMargin=2.2*cm)
    story = []

    story.append(Paragraph("CNV Diagnostic Report", TITLE))
    story.append(Paragraph("Chromosomal Microarray Analysis - Clinical Interpretation",
        S("Normal", fontSize=10, alignment=TA_CENTER, textColor=GRAY, spaceAfter=2)))
    story.append(Paragraph(f"MedFlow AI - CNV Platform | Generated: {date.today().strftime('%B %d, %Y')}",
        S("Normal", fontSize=8.5, alignment=TA_CENTER, textColor=GRAY, spaceAfter=6)))
    story.append(hr())

    # Patient info
    story.append(Paragraph("Patient Information", H1))
    info = [
        ["Patient ID", patient_id, "Sample ID", sample_id],
        ["Indication", indication, "Date", date.today().isoformat()],
        ["CNVs analyzed", str(len(results_df)), "Platform", "CMA (aCGH/SNP array)"],
    ]
    story.append(stab(info, [3.5, 3.5, 3.5, 3.5]))
    story.append(Spacer(1, 0.4*cm))

    # Summary
    pathogenic = len(results_df[results_df["acmg"].isin(["Pathogenic", "Likely Pathogenic"])])
    vus = len(results_df[results_df["acmg"] == "VUS"])
    story.append(Paragraph("Summary", H1))
    summary = [
        ["Total CNVs", "Pathogenic/LP", "VUS", "Likely Benign"],
        [str(len(results_df)), str(pathogenic), str(vus),
         str(len(results_df) - pathogenic - vus)],
    ]
    story.append(stab(summary, [3.5, 3.5, 3.5, 3.5]))
    story.append(Spacer(1, 0.4*cm))

    # Results table
    story.append(hr())
    story.append(Paragraph("CNV Results - Syndrome Matching", H1))
    headers = ["Chr", "Start", "End", "Type", "Size(kb)", "Syndrome", "Overlap%", "ACMG"]
    rows = [headers]
    for _, r in results_df.iterrows():
        rows.append([
            str(r["chr"]),
            f"{int(r['start']):,}",
            f"{int(r['end']):,}",
            str(r["type"]),
            str(r["size_kb"]),
            str(r["syndrome"])[:30],
            f"{r['overlap_pct']:.0f}%",
            str(r["acmg"]),
        ])
    t = stab(rows, [0.8, 2.0, 2.0, 1.0, 1.5, 4.5, 1.4, 2.8])
    # Color ACMG column
    for i, (_, r) in enumerate(results_df.iterrows(), start=1):
        c = ACMG_COLORS_RL.get(r["acmg"], GRAY)
        t._argH  # trigger layout
        t._tblStyle.add("BACKGROUND", (7, i), (7, i), c)
        t._tblStyle.add("TEXTCOLOR",  (7, i), (7, i), colors.white)
    story.append(t)
    story.append(Spacer(1, 0.4*cm))

    # Pathogenic details
    path_df = results_df[results_df["acmg"].isin(["Pathogenic", "Likely Pathogenic"])]
    if not path_df.empty:
        story.append(hr())
        story.append(Paragraph("Pathogenic / Likely Pathogenic Variants - Details", H1))
        for _, r in path_df.iterrows():
            story.append(Paragraph(
                f"<b>{r['syndrome']}</b> ({r['region']}) - {r['acmg']}",
                S("Normal", fontSize=10, textColor=DARK, fontName="Helvetica-Bold", spaceAfter=2)))
            story.append(Paragraph(
                f"Location: chr{r['chr']}:{int(r['start']):,}-{int(r['end']):,} ({r['type']}, {r['size_kb']} kb) | "
                f"Overlap: {r['overlap_pct']:.0f}% | Penetrance: {r['penetrance']:.0f}% | OMIM: {r['omim']}", BODY))
            story.append(Paragraph(f"Key genes: {r['genes']}", SMALL))
            story.append(Paragraph(f"Associated indications: {r['indications']}", SMALL))
            story.append(Spacer(1, 0.2*cm))

    # Scientific basis
    story.append(PageBreak())
    story.append(hr())
    story.append(Paragraph("Scientific Basis", H1))
    story.append(Paragraph(
        "This report is based on a systematic review and meta-analysis of 25 studies including 79,417 patients "
        "across six clinical indications (MEDRXIV/2026/351221). CNV matching uses reciprocal overlap against "
        "18 validated pathogenic syndromes from ClinVar/OMIM. ACMG-like classification follows: "
        "Pathogenic (>=80% overlap, penetrance >=80%), Likely Pathogenic (>=50%), VUS (>=20%), Likely Benign (<20%).",
        BODY))
    story.append(Paragraph(
        "Pooled diagnostic yields: MCA 24.6% [22.9-26.4%], ID/DD 15.9% [15.2-16.6%], "
        "PSY 14.9% [11.9-18.5%], EPI 10.8% [9.3-12.6%], ASD 10.3% [9.3-11.4%], PRE 5.9% [5.5-6.4%].",
        BODY))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "DISCLAIMER: This report is for research and exploratory purposes only. "
        "Clinical interpretation must be performed by a qualified clinical geneticist. "
        "This tool does not constitute a medical diagnosis.", WARN))

    doc.build(story)
    return buf.getvalue()
