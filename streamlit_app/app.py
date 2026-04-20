"""CNV Diagnostic Platform — Home page."""

import streamlit as st

st.set_page_config(
    page_title="CNV Diagnostic Platform",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0f172a; }
[data-testid="stSidebar"] { background: #1e293b; }
.kpi-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 20px 16px;
    text-align: center;
}
.kpi-value { font-size: 2.2rem; font-weight: 800; color: #3b82f6; }
.kpi-label { font-size: 0.82rem; color: #94a3b8; margin-top: 4px; }
.nav-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-left: 4px solid #3b82f6;
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 12px;
}
.nav-title { font-size: 1.05rem; font-weight: 700; color: #f1f5f9; }
.nav-desc  { font-size: 0.85rem; color: #94a3b8; margin-top: 4px; }
.yield-bar {
    background: #0f172a;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 6px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
</style>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 2rem 0 1.5rem;">
  <div style="font-size:3rem; margin-bottom:0.3rem;">🧬</div>
  <h1 style="color:#f1f5f9; font-size:2.4rem; font-weight:800; margin:0;">
    CNV Diagnostic Platform
  </h1>
  <p style="color:#94a3b8; font-size:1.05rem; margin-top:0.5rem;">
    Clinical interpretation of Copy Number Variants &nbsp;|&nbsp;
    Based on validated meta-analysis &nbsp;|&nbsp; MedFlow AI
  </p>
  <div style="margin-top:0.8rem;">
    <span style="background:#1e3a5f; color:#93c5fd; padding:4px 12px; border-radius:20px; font-size:0.8rem; margin:0 4px;">
      medRxiv MEDRXIV/2026/351221
    </span>
    <span style="background:#14532d; color:#86efac; padding:4px 12px; border-radius:20px; font-size:0.8rem; margin:0 4px;">
      PRISMA 2020
    </span>
    <span style="background:#3b0764; color:#d8b4fe; padding:4px 12px; border-radius:20px; font-size:0.8rem; margin:0 4px;">
      DerSimonian-Laird
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── KPIs ──────────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
kpis = [
    (c1, "25",     "Studies included"),
    (c2, "79,417", "Patients"),
    (c3, "6",      "Clinical indications"),
    (c4, "18",     "CNV syndromes"),
    (c5, "9",      "Platforms compared"),
]
for col, val, label in kpis:
    with col:
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-value">{val}</div>
          <div class="kpi-label">{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── YIELDS + NAVIGATION ───────────────────────────────────────────────────────
col_left, col_right = st.columns([1.1, 1])

with col_left:
    st.markdown("### Pooled Diagnostic Yields")
    yields = [
        ("MCA",   "Multiple Congenital Anomalies", 24.6, "#f59e0b"),
        ("ID/DD", "Intellectual Disability / Dev. Delay", 15.9, "#3b82f6"),
        ("PSY",   "Psychiatric Disorders",          14.9, "#f97316"),
        ("EPI",   "Epilepsy",                       10.8, "#ef4444"),
        ("ASD",   "Autism Spectrum Disorder",        10.3, "#10b981"),
        ("PRE",   "Prenatal (abnormal ultrasound)",   5.9, "#8b5cf6"),
    ]
    for code, label, pct, color in yields:
        bar_w = int(pct / 30 * 100)
        st.markdown(f"""
        <div style="margin:6px 0;">
          <div style="display:flex; justify-content:space-between; margin-bottom:3px;">
            <span style="color:#f1f5f9; font-size:0.88rem;">
              <b style="color:{color};">{code}</b> &nbsp; {label}
            </span>
            <span style="color:{color}; font-weight:700; font-size:0.9rem;">{pct}%</span>
          </div>
          <div style="background:#1e293b; border-radius:4px; height:8px;">
            <div style="background:{color}; width:{bar_w}%; height:8px; border-radius:4px;"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

with col_right:
    st.markdown("### Navigation")
    pages = [
        ("🔬", "CNV Analysis",   "Upload your CNV file (CSV/VCF) and match against 18 reference syndromes with ACMG classification", "#3b82f6"),
        ("📊", "Meta-Analysis",  "Forest plots, pooled yields, heterogeneity (I², τ²) across 25 studies", "#10b981"),
        ("🧩", "CNV Syndromes",  "Browser of 18 pathogenic CNV syndromes with bubble chart (size vs penetrance)", "#f59e0b"),
        ("🗺️", "Karyogram",      "Interactive chromosome map of CNV locations", "#8b5cf6"),
        ("📄", "Clinical Report","Generate a PDF clinical report for the geneticist", "#ef4444"),
    ]
    for icon, title, desc, color in pages:
        st.markdown(f"""
        <div class="nav-card" style="border-left-color:{color};">
          <div class="nav-title">{icon} &nbsp; {title}</div>
          <div class="nav-desc">{desc}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#475569; font-size:0.8rem; padding:0.5rem 0;">
  MedFlow AI &nbsp;·&nbsp; Dr. Mamadou Lamine TALL, PhD &nbsp;·&nbsp; Aix-Marseille Universite &nbsp;·&nbsp; 2026<br>
  <span style="color:#64748b;">For research use only — not a medical diagnosis</span>
</div>
""", unsafe_allow_html=True)
