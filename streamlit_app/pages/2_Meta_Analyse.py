"""Page 2 — Meta-Analysis: forest plots, pooled yields, heterogeneity."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from utils.cnv_scoring import load_estimates, load_studies, load_rob, INDICATION_COLORS

st.set_page_config(page_title="Meta-Analysis", page_icon="📊", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0f172a; }
[data-testid="stSidebar"] { background: #1e293b; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Meta-Analysis")
st.caption("DerSimonian-Laird random-effects model · 25 studies · 79,417 patients · PRISMA 2020")

estimates = load_estimates()
studies   = load_studies()
rob       = load_rob()

# ── SUMMARY METRICS ───────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
for col, val, lbl, color in [
    (c1, "25",     "Studies",          "#3b82f6"),
    (c2, "79,417", "Patients",         "#10b981"),
    (c3, "6",      "Indications",      "#f59e0b"),
    (c4, "2007–2026", "Period",        "#8b5cf6"),
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
tab1, tab2, tab3, tab4 = st.tabs(["Forest Plot", "Pooled Yields", "Heterogeneity", "Studies & RoB"])

# ── TAB 1: FOREST PLOT ────────────────────────────────────────────────────────
with tab1:
    st.markdown("#### Forest Plot — Diagnostic Yield by Study and Indication")
    ind_filter = st.multiselect(
        "Filter by indication", options=list(INDICATION_COLORS.keys()),
        default=list(INDICATION_COLORS.keys()), key="ff"
    )
    sub = studies[studies["indication"].isin(ind_filter)].sort_values(["indication","yield_pct"])
    if sub.empty:
        st.info("Select at least one indication.")
    else:
        n = len(sub)
        fig, ax = plt.subplots(figsize=(10, max(5, n * 0.38)))
        fig.patch.set_facecolor("#0f172a")
        ax.set_facecolor("#0f172a")

        for i, (_, row) in enumerate(sub.iterrows()):
            color = INDICATION_COLORS.get(row["indication"], "#94a3b8")
            y = row["yield_pct"] / 100
            se = np.sqrt(y * (1 - y) / row["n_total"])
            ci_l = max(0, y - 1.96 * se) * 100
            ci_u = min(100, y + 1.96 * se) * 100
            size = 30 + (row["n_total"] / studies["n_total"].max()) * 120
            ax.scatter(row["yield_pct"], i, color=color, s=size, zorder=3)
            ax.hlines(i, ci_l, ci_u, color=color, alpha=0.5, lw=1.2)
            ax.text(ci_u + 0.3, i, f"{row['yield_pct']:.1f}%", va="center",
                    color="#94a3b8", fontsize=7)

        # Pooled estimates diamonds
        for _, est in estimates[estimates["indication"].isin(ind_filter)].iterrows():
            rows_ind = sub[sub["indication"] == est["indication"]]
            if rows_ind.empty:
                continue
            y_pos = rows_ind.index.get_loc(rows_ind.index[-1]) if len(rows_ind) > 0 else 0
            color = INDICATION_COLORS.get(est["indication"], "#94a3b8")
            mid_y = sub[sub["indication"] == est["indication"]].index
            y_center = list(sub.index).index(mid_y[len(mid_y)//2]) if len(mid_y) else 0
            diamond_x = [est["ci_lower"], est["yield_pooled"], est["ci_upper"], est["yield_pooled"]]
            diamond_y = [y_center, y_center - 0.4, y_center, y_center + 0.4]
            ax.fill(diamond_x, diamond_y, color=color, alpha=0.8, zorder=4)

        ax.set_yticks(range(n))
        ax.set_yticklabels(
            [f"{r['id']}  [{r['indication']}]" for _, r in sub.iterrows()],
            fontsize=7.5, color="#94a3b8"
        )
        ax.set_xlabel("Diagnostic Yield (%)", color="#94a3b8", fontsize=9)
        ax.axvline(0, color="#334155", lw=0.5)
        ax.tick_params(colors="#94a3b8")
        for spine in ax.spines.values():
            spine.set_edgecolor("#334155")
        patches = [mpatches.Patch(color=c, label=k) for k, c in INDICATION_COLORS.items() if k in ind_filter]
        ax.legend(handles=patches, fontsize=8, facecolor="#1e293b", labelcolor="#f1f5f9",
                  loc="lower right")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

# ── TAB 2: POOLED YIELDS ──────────────────────────────────────────────────────
with tab2:
    st.markdown("#### Pooled Diagnostic Yield with 95% CI per Indication")
    est_sorted = estimates.sort_values("yield_pooled", ascending=True)
    fig2, ax2 = plt.subplots(figsize=(9, 5))
    fig2.patch.set_facecolor("#0f172a")
    ax2.set_facecolor("#1e293b")

    for i, (_, r) in enumerate(est_sorted.iterrows()):
        color = INDICATION_COLORS.get(r["indication"], "#94a3b8")
        ax2.hlines(i, r["ci_lower"], r["ci_upper"], color=color, lw=3, alpha=0.4)
        ax2.scatter(r["yield_pooled"], i, color=color, s=160, zorder=3)
        ax2.vlines(r["ci_lower"], i - 0.15, i + 0.15, color=color, lw=1.5)
        ax2.vlines(r["ci_upper"], i - 0.15, i + 0.15, color=color, lw=1.5)
        ax2.text(r["ci_upper"] + 0.3, i,
                 f"{r['yield_pooled']:.1f}% [{r['ci_lower']:.1f}–{r['ci_upper']:.1f}%]  I²={r['i2_pct']:.0f}%",
                 va="center", color="#94a3b8", fontsize=8.5)

    ax2.set_yticks(range(len(est_sorted)))
    ax2.set_yticklabels(
        [f"{r['label']}  (k={r['k']})" for _, r in est_sorted.iterrows()],
        fontsize=9, color="#f1f5f9"
    )
    ax2.set_xlabel("Pooled Diagnostic Yield (%)", color="#94a3b8")
    ax2.tick_params(colors="#94a3b8")
    for spine in ax2.spines.values():
        spine.set_edgecolor("#334155")
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

    # Table
    st.markdown("#### Summary Table")
    tbl = estimates[["indication","label","k","n_total","yield_pooled","ci_lower","ci_upper","i2_pct","tau2"]].copy()
    tbl.columns = ["Code","Indication","k","N","Yield (%)","CI Lower","CI Upper","I² (%)","τ²"]
    st.dataframe(tbl, use_container_width=True, hide_index=True)

# ── TAB 3: HETEROGENEITY ──────────────────────────────────────────────────────
with tab3:
    col_i2, col_tau = st.columns(2)
    with col_i2:
        st.markdown("#### I² Heterogeneity")
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        fig3.patch.set_facecolor("#0f172a")
        ax3.set_facecolor("#1e293b")
        ax3.barh(estimates["indication"], estimates["i2_pct"],
                 color=[INDICATION_COLORS.get(i, "#94a3b8") for i in estimates["indication"]],
                 height=0.5, edgecolor="#0f172a")
        ax3.axvline(25, color="#10b981", linestyle="--", lw=0.8, alpha=0.7, label="Low (25%)")
        ax3.axvline(50, color="#f59e0b", linestyle="--", lw=0.8, alpha=0.7, label="Moderate (50%)")
        ax3.axvline(75, color="#ef4444", linestyle="--", lw=0.8, alpha=0.7, label="High (75%)")
        ax3.set_xlabel("I² (%)", color="#94a3b8")
        ax3.tick_params(colors="#94a3b8")
        for spine in ax3.spines.values():
            spine.set_edgecolor("#334155")
        ax3.legend(fontsize=8, facecolor="#1e293b", labelcolor="#f1f5f9")
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close()

    with col_tau:
        st.markdown("#### τ² (Between-Study Variance)")
        fig4, ax4 = plt.subplots(figsize=(6, 4))
        fig4.patch.set_facecolor("#0f172a")
        ax4.set_facecolor("#1e293b")
        ax4.barh(estimates["indication"], estimates["tau2"],
                 color=[INDICATION_COLORS.get(i, "#94a3b8") for i in estimates["indication"]],
                 height=0.5, edgecolor="#0f172a")
        ax4.set_xlabel("τ²", color="#94a3b8")
        ax4.tick_params(colors="#94a3b8")
        for spine in ax4.spines.values():
            spine.set_edgecolor("#334155")
        plt.tight_layout()
        st.pyplot(fig4)
        plt.close()

# ── TAB 4: STUDIES & ROB ──────────────────────────────────────────────────────
with tab4:
    col_filter, _ = st.columns([1, 3])
    with col_filter:
        ind_sel = st.selectbox("Filter indication", ["All"] + list(studies["indication"].unique()))
    df_show = studies if ind_sel == "All" else studies[studies["indication"] == ind_sel]

    st.dataframe(
        df_show[["id","indication","n_total","n_diagnostic","yield_pct","platform","country","year","nos"]],
        use_container_width=True, hide_index=True
    )

    st.markdown("#### Newcastle-Ottawa Scale (NOS) Scores")
    fig5, ax5 = plt.subplots(figsize=(10, 5))
    fig5.patch.set_facecolor("#0f172a")
    ax5.set_facecolor("#1e293b")
    colors_rob = ["#10b981" if t >= 7 else "#f59e0b" if t >= 5 else "#ef4444"
                  for t in rob["total_nos"]]
    ax5.barh(rob["study"], rob["total_nos"], color=colors_rob, edgecolor="#0f172a")
    ax5.axvline(7, color="#10b981", linestyle="--", lw=1, alpha=0.6, label="Good (>=7)")
    ax5.axvline(5, color="#f59e0b", linestyle="--", lw=1, alpha=0.6, label="Fair (>=5)")
    ax5.set_xlabel("NOS Score (/9)", color="#94a3b8")
    ax5.tick_params(colors="#94a3b8", labelsize=7)
    for spine in ax5.spines.values():
        spine.set_edgecolor("#334155")
    ax5.legend(fontsize=8, facecolor="#1e293b", labelcolor="#f1f5f9")
    plt.tight_layout()
    st.pyplot(fig5)
    plt.close()
