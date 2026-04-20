"""Page 1 — CNV Analysis: upload, match syndromes, ACMG classification."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from utils.cnv_scoring import match_cnv, demo_cnv, ACMG_COLORS

st.set_page_config(page_title="CNV Analysis", page_icon="🔬", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0f172a; }
[data-testid="stSidebar"] { background: #1e293b; }
.acmg-badge {
    display:inline-block; padding:2px 10px; border-radius:12px;
    font-size:0.78rem; font-weight:700;
}
</style>
""", unsafe_allow_html=True)

st.title("🔬 CNV Analysis")
st.caption("Upload a CNV file and match against 18 validated pathogenic syndromes (ClinVar/OMIM)")

# ── INPUT FORMAT INFO ─────────────────────────────────────────────────────────
with st.expander("📋 Expected CSV format", expanded=False):
    st.markdown("""
    **Required columns:** `chr`, `start`, `end`, `type`

    | chr | start | end | type |
    |-----|-------|-----|------|
    | 22 | 18900000 | 21800000 | DEL |
    | 16 | 29600000 | 30200000 | DEL |
    | 15 | 23500000 | 28500000 | DEL |

    - `chr`: chromosome number (with or without "chr" prefix)
    - `start` / `end`: genomic coordinates (GRCh38/hg38)
    - `type`: DEL (deletion) or DUP (duplication)
    """)

# ── UPLOAD ─────────────────────────────────────────────────────────────────────
col_up, col_demo = st.columns([2, 1])
with col_up:
    uploaded = st.file_uploader("Upload CNV file (CSV)", type=["csv", "txt"])
with col_demo:
    st.markdown("<br>", unsafe_allow_html=True)
    use_demo = st.button("▶ Use demo data (6 CNVs)", use_container_width=True)

cnv_df = None
if uploaded:
    try:
        cnv_df = pd.read_csv(uploaded)
        st.success(f"{len(cnv_df)} CNVs loaded from file")
    except Exception as e:
        st.error(f"Error reading file: {e}")
elif use_demo or st.session_state.get("demo_loaded"):
    st.session_state["demo_loaded"] = True
    cnv_df = demo_cnv()
    st.info("Demo data loaded — 6 CNVs including known pathogenic variants")

# ── DOWNLOAD TEST FILE ─────────────────────────────────────────────────────────
test_csv = demo_cnv().to_csv(index=False)
st.download_button("⬇ Download test CSV", test_csv, "test_cnv.csv", "text/csv")

if cnv_df is None:
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; color:#475569; padding:3rem;">
      Upload a CNV file or click <b>Use demo data</b> to start
    </div>""", unsafe_allow_html=True)
    st.stop()

# ── VALIDATE COLUMNS ───────────────────────────────────────────────────────────
required = {"chr", "start", "end", "type"}
missing = required - set(cnv_df.columns.str.lower())
if missing:
    st.error(f"Missing columns: {missing}")
    st.stop()
cnv_df.columns = cnv_df.columns.str.lower()

# ── RUN MATCHING ───────────────────────────────────────────────────────────────
with st.spinner("Matching CNVs against reference syndromes..."):
    results = match_cnv(cnv_df)

st.markdown("---")

# ── SUMMARY METRICS ────────────────────────────────────────────────────────────
n_path = len(results[results["acmg"].isin(["Pathogenic", "Likely Pathogenic"])])
n_vus  = len(results[results["acmg"] == "VUS"])
n_lb   = len(results[results["acmg"].isin(["Likely Benign", "Benign"])])

c1, c2, c3, c4 = st.columns(4)
for col, val, label, color in [
    (c1, len(results), "Total CNVs",      "#3b82f6"),
    (c2, n_path,       "Pathogenic / LP", "#ef4444"),
    (c3, n_vus,        "VUS",             "#eab308"),
    (c4, n_lb,         "Likely Benign",   "#6b7280"),
]:
    with col:
        st.markdown(f"""
        <div style="background:#1e293b; border:1px solid #334155; border-top:3px solid {color};
                    border-radius:10px; padding:16px; text-align:center;">
          <div style="font-size:2rem; font-weight:800; color:{color};">{val}</div>
          <div style="font-size:0.82rem; color:#94a3b8; margin-top:4px;">{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── CHARTS ────────────────────────────────────────────────────────────────────
col_bar, col_overlap = st.columns(2)

with col_bar:
    st.markdown("#### ACMG Classification")
    fig, ax = plt.subplots(figsize=(5, 3.5))
    fig.patch.set_facecolor("#0f172a")
    ax.set_facecolor("#1e293b")
    counts = results["acmg"].value_counts()
    order = ["Pathogenic", "Likely Pathogenic", "VUS", "Likely Benign", "Benign"]
    vals   = [counts.get(k, 0) for k in order]
    clrs   = [ACMG_COLORS[k] for k in order]
    bars   = ax.barh([k for k in order if counts.get(k, 0) > 0],
                     [v for v in vals if v > 0],
                     color=[c for k, c in zip(order, clrs) if counts.get(k, 0) > 0],
                     height=0.5, edgecolor="#0f172a")
    for bar in bars:
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                str(int(bar.get_width())), va="center", color="#f1f5f9", fontsize=10)
    ax.set_xlabel("Count", color="#94a3b8")
    ax.tick_params(colors="#94a3b8")
    for spine in ax.spines.values():
        spine.set_edgecolor("#334155")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col_overlap:
    st.markdown("#### Overlap % with Reference Syndrome")
    matched = results[results["overlap_pct"] > 0]
    if not matched.empty:
        fig2, ax2 = plt.subplots(figsize=(5, 3.5))
        fig2.patch.set_facecolor("#0f172a")
        ax2.set_facecolor("#1e293b")
        colors_list = [ACMG_COLORS[r] for r in matched["acmg"]]
        labels = [f"chr{r['chr']}:{r['type']}" for _, r in matched.iterrows()]
        ax2.bar(range(len(matched)), matched["overlap_pct"].values,
                color=colors_list, edgecolor="#0f172a")
        ax2.set_xticks(range(len(matched)))
        ax2.set_xticklabels(labels, rotation=30, ha="right", fontsize=8, color="#94a3b8")
        ax2.set_ylabel("Overlap %", color="#94a3b8")
        ax2.axhline(80, color="#ef4444", linestyle="--", lw=0.8, alpha=0.6)
        ax2.axhline(50, color="#f97316", linestyle="--", lw=0.8, alpha=0.6)
        ax2.tick_params(colors="#94a3b8")
        for spine in ax2.spines.values():
            spine.set_edgecolor("#334155")
        patches = [mpatches.Patch(color=ACMG_COLORS[k], label=k)
                   for k in ["Pathogenic","Likely Pathogenic","VUS","Likely Benign"] if k in results["acmg"].values]
        ax2.legend(handles=patches, fontsize=7, facecolor="#1e293b", labelcolor="#f1f5f9")
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close()

# ── RESULTS TABLE ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### Results Table")

display = results[[
    "chr","start","end","type","size_kb","syndrome","region","overlap_pct","penetrance","acmg","omim"
]].copy()
display.columns = ["Chr","Start","End","Type","Size(kb)","Syndrome","Region","Overlap%","Penetrance%","ACMG","OMIM"]

def color_acmg(val):
    c = ACMG_COLORS.get(val, "#6b7280")
    return f"background-color:{c}22; color:{c}; font-weight:700;"

st.dataframe(
    display.style.map(color_acmg, subset=["ACMG"]),
    use_container_width=True, height=300
)

# ── PATHOGENIC DETAILS ────────────────────────────────────────────────────────
path_df = results[results["acmg"].isin(["Pathogenic", "Likely Pathogenic"])]
if not path_df.empty:
    st.markdown("---")
    st.markdown("#### Pathogenic Variants — Clinical Details")
    for _, r in path_df.iterrows():
        color = ACMG_COLORS[r["acmg"]]
        with st.container():
            st.markdown(f"""
            <div style="background:#1e293b; border:1px solid #334155;
                        border-left:4px solid {color}; border-radius:10px;
                        padding:16px; margin-bottom:12px;">
              <div style="font-size:1.05rem; font-weight:700; color:#f1f5f9;">
                {r['syndrome']} &nbsp;
                <span style="background:{color}22; color:{color};
                             padding:2px 10px; border-radius:12px; font-size:0.8rem;">
                  {r['acmg']}
                </span>
              </div>
              <div style="color:#94a3b8; font-size:0.85rem; margin-top:6px;">
                chr{r['chr']}:{int(r['start']):,}-{int(r['end']):,} &nbsp;|&nbsp;
                {r['type']} &nbsp;|&nbsp; {r['size_kb']} kb &nbsp;|&nbsp;
                Overlap: <b style="color:{color};">{r['overlap_pct']:.0f}%</b> &nbsp;|&nbsp;
                Penetrance: {r['penetrance']:.0f}% &nbsp;|&nbsp; OMIM: {r['omim']}
              </div>
              <div style="color:#64748b; font-size:0.82rem; margin-top:4px;">
                Genes: {r['genes']} &nbsp;|&nbsp; Indications: {r['indications']}
              </div>
            </div>""", unsafe_allow_html=True)

# ── DOWNLOAD ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.download_button(
    "⬇ Download results CSV",
    results.drop(columns=["acmg_color"]).to_csv(index=False),
    "cnv_results.csv", "text/csv",
    use_container_width=True
)
