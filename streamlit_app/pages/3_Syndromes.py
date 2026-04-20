"""Page 3 — CNV Syndromes browser: 18 pathogenic syndromes, bubble chart, table."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from utils.cnv_scoring import load_syndromes, INDICATION_COLORS

st.set_page_config(page_title="CNV Syndromes", page_icon="🧩", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0f172a; }
[data-testid="stSidebar"] { background: #1e293b; }
</style>
""", unsafe_allow_html=True)

st.title("🧩 CNV Syndromes")
st.caption("18 recurrent pathogenic CNV syndromes referenced in ClinVar / OMIM")

df = load_syndromes()

# ── KPIs ──────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
for col, val, lbl, color in [
    (c1, "18",   "Syndromes",         "#3b82f6"),
    (c2, str(len(df[df["type"]=="DEL"])), "Deletions", "#ef4444"),
    (c3, str(len(df[df["type"]!="DEL"])), "Dups / Del+Dup", "#10b981"),
    (c4, f"{df['penetrance'].mean()*100:.0f}%", "Avg penetrance", "#f59e0b"),
]:
    with col:
        st.markdown(f"""
        <div style="background:#1e293b; border:1px solid #334155;
                    border-top:3px solid {color}; border-radius:10px;
                    padding:16px; text-align:center;">
          <div style="font-size:1.8rem; font-weight:800; color:{color};">{val}</div>
          <div style="font-size:0.82rem; color:#94a3b8; margin-top:4px;">{lbl}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
tab1, tab2 = st.tabs(["Bubble Chart", "Syndromes Table"])

# ── TAB 1: BUBBLE CHART ───────────────────────────────────────────────────────
with tab1:
    st.markdown("#### CNV Size (Mb) vs Penetrance — bubble size = prevalence (/10k)")
    fig, ax = plt.subplots(figsize=(11, 6))
    fig.patch.set_facecolor("#0f172a")
    ax.set_facecolor("#1e293b")

    for _, r in df.iterrows():
        color = "#ef4444" if r["type"] == "DEL" else "#3b82f6" if r["type"] == "DUP" else "#f59e0b"
        size  = r["prevalence_per10k"] * 400
        ax.scatter(r["size_mb"], r["penetrance"] * 100, s=size, color=color, alpha=0.75,
                   edgecolors="white", linewidth=0.5, zorder=3)
        ax.annotate(r["region"], (r["size_mb"], r["penetrance"] * 100),
                    textcoords="offset points", xytext=(5, 5),
                    fontsize=7.5, color="#f1f5f9", alpha=0.9)

    ax.set_xlabel("CNV Size (Mb)", color="#94a3b8", fontsize=10)
    ax.set_ylabel("Penetrance (%)", color="#94a3b8", fontsize=10)
    ax.tick_params(colors="#94a3b8")
    for spine in ax.spines.values():
        spine.set_edgecolor("#334155")
    legend = [
        mpatches.Patch(color="#ef4444", label="Deletion (DEL)"),
        mpatches.Patch(color="#3b82f6", label="Duplication (DUP)"),
        mpatches.Patch(color="#f59e0b", label="DEL/DUP"),
    ]
    ax.legend(handles=legend, fontsize=9, facecolor="#1e293b", labelcolor="#f1f5f9")
    ax.set_title("Pathogenic CNV Syndromes — Size vs Penetrance", color="#f1f5f9", fontsize=11)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # Prevalence ranking
    st.markdown("#### Prevalence Ranking (/10,000 births)")
    top = df.sort_values("prevalence_per10k", ascending=False)
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    fig2.patch.set_facecolor("#0f172a")
    ax2.set_facecolor("#1e293b")
    colors_bar = ["#ef4444" if t == "DEL" else "#3b82f6" if t == "DUP" else "#f59e0b"
                  for t in top["type"]]
    ax2.barh(top["region"], top["prevalence_per10k"], color=colors_bar, edgecolor="#0f172a")
    ax2.set_xlabel("Prevalence /10,000 births", color="#94a3b8")
    ax2.tick_params(colors="#94a3b8", labelsize=8)
    for spine in ax2.spines.values():
        spine.set_edgecolor("#334155")
    for i, (_, r) in enumerate(top.iterrows()):
        ax2.text(r["prevalence_per10k"] + 0.02, i, f"{r['prevalence_per10k']:.1f}",
                 va="center", color="#94a3b8", fontsize=8)
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

# ── TAB 2: TABLE ─────────────────────────────────────────────────────────────
with tab2:
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        type_filter = st.multiselect("Type", ["DEL","DUP","DEL/DUP"], default=["DEL","DUP","DEL/DUP"])
    with col_f2:
        ind_filter = st.multiselect("Indication", list(INDICATION_COLORS.keys()),
                                    default=list(INDICATION_COLORS.keys()))

    filt = df[df["type"].isin(type_filter)]
    filt = filt[filt["indications"].apply(lambda x: any(i in str(x) for i in ind_filter))]

    display = filt[["region","name","type","size_mb","penetrance","prevalence_per10k","omim","genes","indications"]].copy()
    display["penetrance"] = (display["penetrance"] * 100).round(0).astype(int).astype(str) + "%"
    display.columns = ["Region","Syndrome","Type","Size(Mb)","Penetrance","Prev./10k","OMIM","Key genes","Indications"]

    def color_type(val):
        if val == "DEL":   return "background-color:#ef444422; color:#ef4444; font-weight:700;"
        if val == "DUP":   return "background-color:#3b82f622; color:#3b82f6; font-weight:700;"
        return "background-color:#f59e0b22; color:#f59e0b; font-weight:700;"

    st.dataframe(
        display.style.applymap(color_type, subset=["Type"]),
        use_container_width=True, hide_index=True, height=500
    )

    # Syndrome cards for pathogenic ones
    st.markdown("---")
    st.markdown("#### Top Syndromes — Clinical Overview")
    top5 = df.sort_values("prevalence_per10k", ascending=False).head(6)
    cols = st.columns(3)
    for i, (_, r) in enumerate(top5.iterrows()):
        color = "#ef4444" if r["type"] == "DEL" else "#3b82f6" if r["type"] == "DUP" else "#f59e0b"
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:#1e293b; border:1px solid #334155;
                        border-top:3px solid {color}; border-radius:10px;
                        padding:14px; margin-bottom:12px;">
              <div style="font-size:0.95rem; font-weight:700; color:#f1f5f9;">{r['name']}</div>
              <div style="color:{color}; font-size:0.8rem; margin-top:2px;">{r['region']} · {r['type']}</div>
              <div style="color:#94a3b8; font-size:0.8rem; margin-top:6px;">
                Size: {r['size_mb']} Mb &nbsp;|&nbsp; Penetrance: {r['penetrance']*100:.0f}%<br>
                Prevalence: {r['prevalence_per10k']}/10k &nbsp;|&nbsp; OMIM: {r['omim']}<br>
                <span style="color:#64748b;">Genes: {r['genes'][:40]}</span>
              </div>
            </div>""", unsafe_allow_html=True)
