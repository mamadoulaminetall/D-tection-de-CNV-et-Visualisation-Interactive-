"""Page 4 — Karyogram: interactive chromosome map of CNV locations."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from utils.cnv_scoring import load_syndromes, demo_cnv, match_cnv, ACMG_COLORS

st.set_page_config(page_title="Karyogram", page_icon="🗺️", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0f172a; }
[data-testid="stSidebar"] { background: #1e293b; }
</style>
""", unsafe_allow_html=True)

st.title("🗺️ Karyogram")
st.caption("Genomic map of CNV locations across chromosomes (GRCh38)")

# Approximate chromosome lengths (GRCh38, Mb)
CHROM_LENGTHS = {
    "1": 248.9, "2": 242.2, "3": 198.3, "4": 190.2, "5": 181.5,
    "6": 170.8, "7": 159.3, "8": 145.1, "9": 138.4, "10": 133.8,
    "11": 135.1, "12": 133.3, "13": 114.4, "14": 107.0, "15": 101.9,
    "16": 90.3,  "17": 83.3,  "18": 80.4,  "19": 58.6,  "20": 64.4,
    "21": 46.7,  "22": 50.8,  "X": 156.0,  "Y": 57.2,
}

st.markdown("### Reference Syndromes Karyogram")
st.markdown("Locations of 18 reference pathogenic CNV syndromes on the genome")

syndromes = load_syndromes()
chroms = [str(c) for c in range(1, 23)] + ["X"]

fig, axes = plt.subplots(1, len(chroms), figsize=(22, 8), sharey=False)
fig.patch.set_facecolor("#0f172a")

for i, chrom in enumerate(chroms):
    ax = axes[i]
    ax.set_facecolor("#0f172a")
    chrom_len = CHROM_LENGTHS.get(chrom, 100)

    # Chromosome body
    ax.barh(0, chrom_len, left=0, height=0.6, color="#334155", edgecolor="#475569", linewidth=0.4)
    ax.set_xlim(0, max(CHROM_LENGTHS.values()))
    ax.set_ylim(-0.6, 0.6)
    ax.axis("off")
    ax.text(chrom_len / 2, -0.55, chrom, ha="center", va="top", fontsize=6.5, color="#94a3b8")

    # Syndrome marks
    syn_chr = syndromes[syndromes["chr"].astype(str) == chrom]
    for _, r in syn_chr.iterrows():
        mid = (r["start"] + r["end"]) / 2 / 1_000_000
        color = "#ef4444" if r["type"] == "DEL" else "#3b82f6" if r["type"] == "DUP" else "#f59e0b"
        ax.barh(0, r["end"]/1e6 - r["start"]/1e6, left=r["start"]/1e6,
                height=0.6, color=color, alpha=0.85, edgecolor="white", linewidth=0.3)

fig.suptitle("Reference CNV Syndromes — Karyogram (GRCh38)", color="#f1f5f9", fontsize=12, y=1.0)
legend = [
    mpatches.Patch(color="#ef4444", label="Deletion (DEL)"),
    mpatches.Patch(color="#3b82f6", label="Duplication (DUP)"),
    mpatches.Patch(color="#f59e0b", label="DEL/DUP"),
]
fig.legend(handles=legend, loc="lower center", ncol=3, fontsize=9,
           facecolor="#1e293b", labelcolor="#f1f5f9", framealpha=0.8)
plt.tight_layout()
st.pyplot(fig)
plt.close()

# ── USER CNV KARYOGRAM ────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Upload CNV file to map on karyogram")

uploaded = st.file_uploader("Upload CNV CSV (chr, start, end, type)", type=["csv"])
use_demo = st.button("Use demo data")

cnv_df = None
if uploaded:
    try:
        cnv_df = pd.read_csv(uploaded)
        cnv_df.columns = cnv_df.columns.str.lower()
    except Exception as e:
        st.error(str(e))
elif use_demo:
    cnv_df = demo_cnv()

if cnv_df is not None:
    results = match_cnv(cnv_df)

    fig2, axes2 = plt.subplots(1, len(chroms), figsize=(22, 8))
    fig2.patch.set_facecolor("#0f172a")

    for i, chrom in enumerate(chroms):
        ax = axes2[i]
        ax.set_facecolor("#0f172a")
        chrom_len = CHROM_LENGTHS.get(chrom, 100)

        # Chromosome body
        ax.barh(0, chrom_len, left=0, height=0.6, color="#1e293b", edgecolor="#334155", linewidth=0.4)
        ax.set_xlim(0, max(CHROM_LENGTHS.values()))
        ax.set_ylim(-0.6, 0.6)
        ax.axis("off")
        ax.text(chrom_len / 2, -0.55, chrom, ha="center", va="top", fontsize=6.5, color="#94a3b8")

        # Reference syndromes (faint)
        syn_chr = syndromes[syndromes["chr"].astype(str) == chrom]
        for _, r in syn_chr.iterrows():
            color = "#ef4444" if r["type"] == "DEL" else "#3b82f6"
            ax.barh(0, r["end"]/1e6 - r["start"]/1e6, left=r["start"]/1e6,
                    height=0.6, color=color, alpha=0.2)

        # User CNVs (bright)
        user_chr = results[results["chr"].astype(str) == chrom]
        for _, r in user_chr.iterrows():
            color = ACMG_COLORS.get(r["acmg"], "#6b7280")
            ax.barh(0, (r["end"] - r["start"]) / 1e6, left=r["start"] / 1e6,
                    height=0.6, color=color, alpha=0.9, edgecolor="white", linewidth=0.5)

    fig2.suptitle("Your CNVs on Karyogram — colored by ACMG classification", color="#f1f5f9", fontsize=12, y=1.0)
    legend2 = [mpatches.Patch(color=c, label=k) for k, c in ACMG_COLORS.items()]
    legend2 += [mpatches.Patch(color="#ef4444", alpha=0.2, label="Ref syndrome (DEL)"),
                mpatches.Patch(color="#3b82f6", alpha=0.2, label="Ref syndrome (DUP)")]
    fig2.legend(handles=legend2, loc="lower center", ncol=4, fontsize=8,
                facecolor="#1e293b", labelcolor="#f1f5f9", framealpha=0.8)
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

    # Table
    st.markdown("#### Your CNVs Summary")
    st.dataframe(
        results[["chr","start","end","type","size_kb","syndrome","acmg"]],
        use_container_width=True, hide_index=True
    )
