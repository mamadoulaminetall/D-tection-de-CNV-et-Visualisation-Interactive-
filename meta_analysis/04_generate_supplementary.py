"""
CNV Meta-Analysis — Supplementary PDF Generator
Tables S1–S5, Figures S1–S6, Appendix A (search strings)

Author: Dr. Mamadou Lamine TALL, PhD — MedFlow AI
"""

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import pandas as pd

DATA = Path(__file__).parent.parent / "data" / "meta_analysis_v1"
FIGS = Path(__file__).parent.parent / "figures"
OUT  = Path(__file__).parent.parent / "manuscript"

df_stud = pd.read_csv(DATA / "studies_registry.csv")
df_meta = pd.read_csv(DATA / "meta_analytic_estimates.csv")
df_rob  = pd.read_csv(DATA / "risk_of_bias.csv")
df_synd = pd.read_csv(DATA / "cnv_syndromes.csv")
df_plat = pd.read_csv(DATA / "platform_comparison.csv")

styles = getSampleStyleSheet()
def S(name="Normal", **kw):
    return ParagraphStyle(name + str(id(kw)), parent=styles.get(name, styles["Normal"]), **kw)

DARK  = colors.HexColor("#1e3a5f")
GRAY  = colors.HexColor("#6b7280")
TEXT  = colors.HexColor("#1f2937")
BORD  = colors.HexColor("#e2e8f0")
LITE  = colors.HexColor("#f8fafc")

TITLE = S("Title",    fontSize=14, leading=18, textColor=DARK, alignment=TA_CENTER, spaceAfter=4)
H1    = S("Heading1", fontSize=12, leading=15, textColor=DARK, fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=5)
BODY  = S("Normal",   fontSize=9.5, leading=13, textColor=TEXT, spaceAfter=5, alignment=TA_JUSTIFY)
SMALL = S("Normal",   fontSize=8.5, leading=11, textColor=GRAY, spaceAfter=3)
CAP   = S("Normal",   fontSize=8.5, leading=12, textColor=GRAY, alignment=TA_CENTER, fontName="Helvetica-Oblique", spaceAfter=8)
CODE  = S("Normal",   fontSize=8,   leading=11, textColor=colors.HexColor("#1e293b"),
          spaceAfter=2, fontName="Courier", backColor=colors.HexColor("#f1f5f9"), leftIndent=10)

def hr(): return HRFlowable(width="100%", thickness=0.4, color=BORD, spaceAfter=5)

def stab(data, widths, header_bg="#1e3a5f"):
    ts = TableStyle([
        ("BACKGROUND",    (0,0),(-1,0), colors.HexColor(header_bg)),
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

def add_fig(path, caption, w=15):
    elems = []
    p = Path(path)
    if p.exists():
        elems.append(Image(str(p), width=w*cm, height=w*cm*0.52))
        elems.append(Paragraph(caption, CAP))
    return elems

doc = SimpleDocTemplate(
    str(OUT / "CNV_MetaAnalysis_Supplementary.pdf"),
    pagesize=A4,
    leftMargin=2.2*cm, rightMargin=2.2*cm,
    topMargin=2.2*cm, bottomMargin=2.2*cm,
)
story = []

story.append(Paragraph("Supplementary Data", TITLE))
story.append(Paragraph(
    "Diagnostic Yield of Chromosomal Microarray Analysis for Copy Number Variants Detection:<br/>"
    "A Systematic Review and Meta-Analysis", TITLE))
story.append(Paragraph("Mamadou Lamine TALL, PhD · MedFlow AI · April 2026",
    S("Normal", fontSize=9, alignment=TA_CENTER, textColor=GRAY)))
story.append(Spacer(1, 0.4*cm))

# ── TABLE S1 — Studies ────────────────────────────────────────────────────────
story.append(hr())
story.append(Paragraph("Table S1 — Characteristics of All 25 Included Studies", H1))
h1 = ["Study ID", "Indication", "N", "N diag.", "Yield%", "Platform", "Res.", "Country", "Year", "NOS"]
rows1 = [h1]
for _, r in df_stud.iterrows():
    rows1.append([r["id"], r["indication"], f"{r['n_total']:,}", f"{r['n_diagnostic']:,}",
                  f"{r['yield_pct']:.1f}", r["platform"].replace("_", " "),
                  r["resolution"], r["country"][:12], str(r["year"]), str(r["nos"])])
story.append(stab(rows1, [2.4, 1.2, 1.3, 1.3, 1.2, 1.8, 0.9, 1.5, 0.8, 0.8]))
story.append(Spacer(1, 0.4*cm))

# ── TABLE S2 — Meta estimates ─────────────────────────────────────────────────
story.append(hr())
story.append(Paragraph("Table S2 — Meta-Analytic Estimates (DerSimonian-Laird, logit-transformed proportions)", H1))
h2 = ["Indication", "k", "N", "Yield pooled (%)", "95% CI lower", "95% CI upper", "I² (%)", "τ²", "Q", "df"]
rows2 = [h2]
for _, r in df_meta.iterrows():
    rows2.append([r["indication"], str(r["k"]), f"{r['n_total']:,}",
                  f"{r['yield_pooled']:.2f}", f"{r['ci_lower']:.2f}", f"{r['ci_upper']:.2f}",
                  f"{r['i2_pct']:.1f}", f"{r['tau2']:.5f}", f"{r['Q']:.2f}", str(r["Q_df"])])
story.append(stab(rows2, [2.0, 0.6, 1.4, 1.8, 1.8, 1.8, 1.0, 1.0, 0.9, 0.7]))
story.append(Spacer(1, 0.4*cm))

# ── TABLE S3 — Risk of bias ───────────────────────────────────────────────────
story.append(hr())
story.append(Paragraph("Table S3 — Risk of Bias: Newcastle-Ottawa Scale (NOS)", H1))
h3 = ["Study", "Indication", "Selection (/4)", "Comparability (/2)", "Outcome (/3)", "Total (/9)", "Quality"]
rows3 = [h3]
for _, r in df_rob.iterrows():
    rows3.append([r["study"], r["indication"],
                  str(r["selection"]), str(r["comparability"]), str(r["outcome"]),
                  str(r["total_nos"]), r["quality"]])
story.append(stab(rows3, [2.6, 1.2, 1.8, 2.0, 1.7, 1.2, 1.2]))
story.append(Spacer(1, 0.4*cm))

# ── TABLE S4 — CNV syndromes ──────────────────────────────────────────────────
story.append(hr())
story.append(Paragraph("Table S4 — Recurrent Pathogenic CNV Syndromes (ClinVar / OMIM)", H1))
h4 = ["Region", "Syndrome", "Type", "Size (Mb)", "Prevalence /10k", "Penetrance (%)", "OMIM", "Indications"]
rows4 = [h4]
for _, r in df_synd.sort_values("prevalence_per10k", ascending=False).iterrows():
    rows4.append([r["region"], r["name"][:28], r["type"],
                  f"{r['size_mb']:.1f}", f"{r['prevalence_per10k']:.1f}",
                  f"{r['penetrance']*100:.0f}", str(r["omim"]), r["indications"]])
story.append(stab(rows4, [1.4, 4.0, 0.9, 1.2, 1.7, 1.7, 1.2, 2.0]))
story.append(Spacer(1, 0.4*cm))

# ── TABLE S5 — Platform comparison ───────────────────────────────────────────
story.append(hr())
story.append(Paragraph("Table S5 — Diagnostic Platform Comparison", H1))
h5 = ["Platform", "Resolution (kb)", "Yield ID/DD (%)", "Yield ASD (%)", "Yield MCA (%)", "LOH", "Cost (USD)"]
rows5 = [h5]
for _, r in df_plat.iterrows():
    rows5.append([r["platform"], str(r["resolution_kb"]),
                  f"{r['yield_id_pct']:.1f}", f"{r['yield_asd_pct']:.1f}", f"{r['yield_mca_pct']:.1f}",
                  "Yes" if r["loh_detection"] else "No", f"~{r['cost_usd']:,}"])
story.append(stab(rows5, [3.8, 1.8, 1.8, 1.8, 1.8, 1.0, 1.5]))
story.append(PageBreak())

# ── FIGURES ───────────────────────────────────────────────────────────────────
story.append(Paragraph("Supplementary Figures", H1))
for fname, caption in [
    ("fig1_forest_plot_overall.png",
     "Figure S1. Forest plot of diagnostic yield by clinical indication (DerSimonian-Laird random-effects). "
     "Circle size proportional to study sample size. Diamonds = pooled estimates."),
    ("fig2_pooled_yield.png",
     "Figure S2. Pooled diagnostic yield with 95% CI per clinical indication. Sorted by yield."),
    ("fig3_platform_comparison.png",
     "Figure S3. Diagnostic yield by CMA platform across three major indications (ID/DD, ASD, MCA)."),
    ("fig4_cnv_syndromes_bubble.png",
     "Figure S4. Genomic syndromes: CNV size (Mb) vs penetrance (%). Bubble size = population prevalence. "
     "Red = deletion, Blue = duplication."),
    ("fig5_risk_of_bias.png",
     "Figure S5. Newcastle-Ottawa Scale (NOS) scores for all 25 included studies."),
    ("fig6_prisma_flow.png",
     "Figure S6. PRISMA 2020 flow diagram — study selection process."),
]:
    story += add_fig(str(FIGS / fname), caption)
    story.append(Spacer(1, 0.3*cm))

story.append(PageBreak())

# ── APPENDIX A — Search strings ───────────────────────────────────────────────
story.append(hr())
story.append(Paragraph("Appendix A — Full Database Search Strings", H1))
story.append(Paragraph("<b>PubMed (January 2007 – April 2026):</b>", BODY))
for line in [
    '("chromosomal microarray"[MeSH] OR "array CGH"[tiab] OR "aCGH"[tiab]',
    ' OR "SNP array"[tiab] OR "comparative genomic hybridization"[tiab])',
    'AND ("copy number variant"[tiab] OR "CNV"[tiab] OR "copy number variation"[MeSH])',
    'AND ("diagnostic yield"[tiab] OR "detection rate"[tiab]',
    ' OR "intellectual disability"[MeSH] OR "autism spectrum disorder"[MeSH]',
    ' OR "congenital abnormalities"[MeSH] OR "prenatal diagnosis"[MeSH]',
    ' OR "epilepsy"[MeSH] OR "schizophrenia"[MeSH])',
    'AND ("2007/01/01"[PDat]:"2026/04/01"[PDat])',
    '→ 423 records retrieved',
]:
    story.append(Paragraph(line, CODE))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("<b>Embase (OVID, January 2007 – April 2026):</b>", BODY))
for line in [
    "(chromosomal microarray/ OR 'array comparative genomic hybridization':ab,ti",
    " OR 'SNP array':ab,ti OR 'copy number variation'/)",
    "AND ('diagnostic yield':ab,ti OR 'detection rate':ab,ti)",
    "AND (intellectual disability/ OR autism/ OR 'congenital malformation/'",
    "     OR epilepsy/ OR schizophrenia/ OR 'prenatal diagnosis/')",
    "AND [2007-2026]/py",
    "→ 312 records retrieved",
]:
    story.append(Paragraph(line, CODE))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("<b>Web of Science (January 2007 – April 2026):</b>", BODY))
for line in [
    'TS=("chromosomal microarray" OR "array CGH" OR "aCGH" OR "SNP array")',
    'AND TS=("copy number variant*" OR "CNV" OR "copy number variation")',
    'AND TS=("diagnostic yield" OR "detection rate" OR "intellectual disability"',
    '       OR "autism" OR "congenital anomal*" OR "epilepsy" OR "schizophrenia")',
    'AND PY=2007-2026',
    "→ 198 records retrieved",
]:
    story.append(Paragraph(line, CODE))

story.append(Spacer(1, 0.5*cm))
story.append(Paragraph(
    "Total records before deduplication: 933. After removing 312 duplicates: 621 screened.",
    BODY))

doc.build(story)
print(f"✅ Supplementary PDF → {OUT / 'CNV_MetaAnalysis_Supplementary.pdf'}")
