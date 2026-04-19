"""
CNV Meta-Analysis — Figure Generator
6 publication-quality figures

Author: Dr. Mamadou Lamine TALL, PhD — MedFlow AI
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "meta_analysis_v1"
OUT  = Path(__file__).parent.parent / "figures"
OUT.mkdir(parents=True, exist_ok=True)

df_stud = pd.read_csv(DATA / "studies_registry.csv")
df_meta = pd.read_csv(DATA / "meta_analytic_estimates.csv")
df_synd = pd.read_csv(DATA / "cnv_syndromes.csv")
df_plat = pd.read_csv(DATA / "platform_comparison.csv")
df_rob  = pd.read_csv(DATA / "risk_of_bias.csv")

BG      = "#0f172a"
CARD    = "#1e293b"
BORDER  = "#334155"
TEXT    = "#f1f5f9"
SUBTEXT = "#94a3b8"

IND_COLORS = {
    "ID/DD": "#3b82f6",
    "ASD":   "#10b981",
    "MCA":   "#f59e0b",
    "PRE":   "#8b5cf6",
    "EPI":   "#ef4444",
    "PSY":   "#f97316",
}

IND_LABELS = {
    "ID/DD": "ID/DD",
    "ASD":   "ASD",
    "MCA":   "MCA",
    "PRE":   "Prénatal",
    "EPI":   "Épilepsie",
    "PSY":   "Psychiatrie",
}

plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": CARD,
    "text.color": TEXT, "axes.labelcolor": SUBTEXT,
    "xtick.color": SUBTEXT, "ytick.color": SUBTEXT,
    "axes.edgecolor": BORDER, "grid.color": BORDER,
    "font.family": "DejaVu Sans",
})

# ── Figure 1 — Forest plot overall ────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 10), facecolor=BG)
ax.set_facecolor(CARD)

y = 0
yticks, ylabels = [], []
ind_order = ["ID/DD", "ASD", "MCA", "PRE", "EPI", "PSY"]
prev_ind = None

for ind in ind_order:
    sub = df_stud[df_stud["indication"] == ind].copy()
    meta_row = df_meta[df_meta["indication"] == ind].iloc[0]
    color = IND_COLORS[ind]

    # Section header
    ax.text(-0.5, y + 0.3, f"── {IND_LABELS[ind]}", color=color, fontsize=9, fontweight="bold", ha="left")
    y += 1.0

    for _, row in sub.iterrows():
        p = row["yield_pct"] / 100
        ci_half = np.sqrt(p * (1 - p) / row["n_total"]) * 1.96 * 100
        ax.errorbar(row["yield_pct"], y, xerr=ci_half,
                    fmt="o", color=color, markersize=3 + row["n_total"] / 3000,
                    ecolor=color, elinewidth=0.8, capsize=2.5, alpha=0.85)
        ax.text(-0.5, y, row["id"][:14], va="center", ha="left", color=SUBTEXT, fontsize=7)
        ax.text(42, y, f"{row['yield_pct']:.1f}%", va="center", ha="left", color=TEXT, fontsize=7)
        ax.text(48, y, f"n={row['n_total']:,}", va="center", ha="left", color=SUBTEXT, fontsize=7)
        yticks.append(y); ylabels.append("")
        y += 1.0

    # Pooled diamond
    y_d = y
    ci_l = meta_row["ci_lower"]
    ci_u = meta_row["ci_upper"]
    yp   = meta_row["yield_pooled"]
    dx = [ci_l, yp, ci_u, yp, ci_l]
    dy = [y_d, y_d - 0.35, y_d, y_d + 0.35, y_d]
    ax.fill(dx, dy, color=color, alpha=0.95)
    ax.text(-0.5, y_d, f"Pooled ({ind})", va="center", ha="left", color=color, fontsize=8, fontweight="bold")
    ax.text(42, y_d, f"{yp:.1f}%", va="center", ha="left", color=color, fontsize=8, fontweight="bold")
    ax.text(48, y_d, f"[{ci_l:.1f}–{ci_u:.1f}]", va="center", ha="left", color=SUBTEXT, fontsize=7)
    y += 2.0

ax.axvline(0, color=BORDER, lw=0.8, ls="--")
ax.set_xlim(-1, 58)
ax.set_ylim(-1, y)
ax.set_xlabel("Diagnostic Yield (%)", fontsize=10)
ax.set_title("Figure 1 — Forest Plot: Diagnostic Yield of CMA by Clinical Indication\n(DerSimonian-Laird Random-Effects Model)",
             color=TEXT, fontsize=11, pad=12)
ax.set_yticks([]); ax.yaxis.set_visible(False)
for spine in ax.spines.values(): spine.set_edgecolor(BORDER)
plt.tight_layout()
fig.savefig(OUT / "fig1_forest_plot_overall.png", dpi=180, bbox_inches="tight", facecolor=BG)
plt.close()
print("✅ fig1")

# ── Figure 2 — Pooled yield lollipop ─────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6), facecolor=BG)
ax.set_facecolor(CARD)

df_m = df_meta.sort_values("yield_pooled", ascending=True)
y_pos = range(len(df_m))
colors_bar = [IND_COLORS[ind] for ind in df_m["indication"]]

for i, (_, row) in enumerate(df_m.iterrows()):
    color = IND_COLORS[row["indication"]]
    ax.plot([row["ci_lower"], row["ci_upper"]], [i, i], color=color, lw=2, alpha=0.5)
    ax.scatter(row["yield_pooled"], i, color=color, s=120, zorder=5)
    ax.text(row["ci_upper"] + 0.3, i, f"{row['yield_pooled']:.1f}% [{row['ci_lower']:.1f}–{row['ci_upper']:.1f}]",
            va="center", color=TEXT, fontsize=8.5)
    ax.text(-0.5, i, IND_LABELS[row["indication"]], va="center", ha="right", color=color, fontsize=9, fontweight="bold")

ax.axvline(10, color=SUBTEXT, lw=0.8, ls="--", alpha=0.5, label="10%")
ax.axvline(20, color=SUBTEXT, lw=0.8, ls=":", alpha=0.5, label="20%")
ax.set_xlim(-2, 38)
ax.set_ylim(-0.7, len(df_m) - 0.3)
ax.set_yticks([])
ax.set_xlabel("Pooled Diagnostic Yield (%)", fontsize=10)
ax.set_title("Figure 2 — Pooled Diagnostic Yield with 95% CI by Clinical Indication",
             color=TEXT, fontsize=11, pad=10)
ax.legend(facecolor=CARD, labelcolor=SUBTEXT, fontsize=8)
for spine in ax.spines.values(): spine.set_edgecolor(BORDER)
plt.tight_layout()
fig.savefig(OUT / "fig2_pooled_yield.png", dpi=180, bbox_inches="tight", facecolor=BG)
plt.close()
print("✅ fig2")

# ── Figure 3 — Platform comparison ───────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(15, 6), facecolor=BG)
df_p = df_plat.copy()

for ax, (col, label, color) in zip(axes, [
    ("yield_id_pct",  "ID/DD",       "#3b82f6"),
    ("yield_asd_pct", "ASD",         "#10b981"),
    ("yield_mca_pct", "MCA",         "#f59e0b"),
]):
    ax.set_facecolor(CARD)
    names = [p[:20] for p in df_p["platform"]]
    vals  = df_p[col].values
    bars  = ax.barh(names, vals, color=color, height=0.6, edgecolor=BORDER)
    for bar, val in zip(bars, vals):
        ax.text(val + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%", va="center", color=TEXT, fontsize=8)
    ax.set_xlim(0, 38)
    ax.set_xlabel("Diagnostic Yield (%)", fontsize=9)
    ax.set_title(f"{label}", color=color, fontsize=10, fontweight="bold")
    ax.tick_params(labelsize=7.5)
    for spine in ax.spines.values(): spine.set_edgecolor(BORDER)

plt.suptitle("Figure 3 — Diagnostic Yield by Platform and Clinical Indication",
             color=TEXT, fontsize=11, y=1.01)
plt.tight_layout()
fig.savefig(OUT / "fig3_platform_comparison.png", dpi=180, bbox_inches="tight", facecolor=BG)
plt.close()
print("✅ fig3")

# ── Figure 4 — CNV syndromes bubble chart ────────────────────────────────────
fig, ax = plt.subplots(figsize=(13, 7), facecolor=BG)
ax.set_facecolor(CARD)

type_colors = {"DEL": "#ef4444", "DUP": "#3b82f6"}
for _, row in df_synd.iterrows():
    color = type_colors[row["type"]]
    size  = row["prevalence_per10k"] * 80
    ax.scatter(row["size_mb"], row["penetrance"] * 100,
               s=size, color=color, alpha=0.75, edgecolors=BORDER, linewidth=0.5)
    label = row["region"] if row["name"] != "16p11.2 CNV (ASD) dup" else ""
    ax.annotate(label, (row["size_mb"], row["penetrance"] * 100),
                fontsize=7, color=SUBTEXT, ha="left", va="bottom",
                xytext=(3, 3), textcoords="offset points")

del_patch = mpatches.Patch(color="#ef4444", label="Deletion")
dup_patch = mpatches.Patch(color="#3b82f6", label="Duplication")
ax.legend(handles=[del_patch, dup_patch], facecolor=CARD, labelcolor=TEXT, fontsize=9)
ax.set_xlabel("CNV size (Mb)", fontsize=10)
ax.set_ylabel("Penetrance (%)", fontsize=10)
ax.set_title("Figure 4 — Genomic Syndromes: Size vs Penetrance\n(bubble size ∝ population prevalence per 10,000)",
             color=TEXT, fontsize=11, pad=10)
ax.set_ylim(0, 115)
ax.grid(True, alpha=0.15)
for spine in ax.spines.values(): spine.set_edgecolor(BORDER)
plt.tight_layout()
fig.savefig(OUT / "fig4_cnv_syndromes_bubble.png", dpi=180, bbox_inches="tight", facecolor=BG)
plt.close()
print("✅ fig4")

# ── Figure 5 — Risk of bias ───────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 8), facecolor=BG)
ax.set_facecolor(CARD)

df_r = df_rob.sort_values("total_nos", ascending=True)
colors_rob = [IND_COLORS.get(ct, SUBTEXT) for ct in df_r["indication"]]
bars = ax.barh(df_r["study"], df_r["total_nos"], color=colors_rob, height=0.65, edgecolor=BORDER)
ax.axvline(7, color="#10b981", lw=1.2, ls="--", alpha=0.8, label="High quality (≥7)")
ax.axvline(5, color="#f59e0b", lw=1.2, ls="--", alpha=0.8, label="Moderate (≥5)")
for bar, val in zip(bars, df_r["total_nos"]):
    ax.text(val + 0.05, bar.get_y() + bar.get_height() / 2,
            str(val), va="center", color=TEXT, fontsize=7.5)
ax.set_xlim(0, 11)
ax.set_xlabel("NOS Score (/9)", fontsize=10)
ax.set_title("Figure 5 — Risk of Bias: Newcastle-Ottawa Scale (NOS)\nAll 25 Included Studies",
             color=TEXT, fontsize=11, pad=10)
ax.tick_params(labelsize=7.5)
legend_patches = [mpatches.Patch(color=IND_COLORS[ind], label=IND_LABELS[ind]) for ind in IND_COLORS]
ax.legend(handles=legend_patches, facecolor=CARD, labelcolor=TEXT, fontsize=8, loc="lower right")
ax.legend(handles=legend_patches, facecolor=CARD, labelcolor=TEXT, fontsize=8)
for spine in ax.spines.values(): spine.set_edgecolor(BORDER)
plt.tight_layout()
fig.savefig(OUT / "fig5_risk_of_bias.png", dpi=180, bbox_inches="tight", facecolor=BG)
plt.close()
print("✅ fig5")

# ── Figure 6 — PRISMA flow ────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 12), facecolor=BG)
ax.set_facecolor(BG)
ax.axis("off")

def box(ax, x, y, w, h, text, color="#1e293b", border="#3b82f6", fontsize=9):
    rect = mpatches.FancyBboxPatch((x - w/2, y - h/2), w, h,
                                   boxstyle="round,pad=0.02", linewidth=1.5,
                                   edgecolor=border, facecolor=color)
    ax.add_patch(rect)
    ax.text(x, y, text, ha="center", va="center", color=TEXT,
            fontsize=fontsize, wrap=True, multialignment="center",
            fontweight="bold" if "\n" in text[:20] else "normal")

def arrow(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color=SUBTEXT, lw=1.2))

# Identification
box(ax, 0.5, 0.95, 0.40, 0.06, "PubMed\n423 records", border="#3b82f6")
box(ax, 0.5, 0.87, 0.40, 0.06, "Embase\n312 records", border="#3b82f6")
box(ax, 0.5, 0.79, 0.40, 0.06, "Web of Science\n198 records", border="#3b82f6")

box(ax, 0.5, 0.68, 0.50, 0.07,
    "Total records identified\nn = 933", border="#6366f1")
arrow(ax, 0.5, 0.76, 0.5, 0.715)

box(ax, 0.5, 0.57, 0.50, 0.07,
    "After deduplication\nn = 621 screened", border="#6366f1")
box(ax, 0.82, 0.57, 0.28, 0.06, "Duplicates removed\nn = 312", color="#1c1007", border="#f59e0b")
arrow(ax, 0.5, 0.645, 0.5, 0.605)

box(ax, 0.5, 0.45, 0.50, 0.07,
    "Full-text assessed\nn = 78", border="#6366f1")
box(ax, 0.82, 0.45, 0.28, 0.06, "Excluded (title/abstract)\nn = 543", color="#1c1007", border="#ef4444")
arrow(ax, 0.5, 0.535, 0.5, 0.485)

box(ax, 0.5, 0.33, 0.50, 0.07,
    "Studies included in meta-analysis\nn = 25", border="#10b981")
box(ax, 0.82, 0.35, 0.28, 0.08,
    "Excluded full-text\nn = 53\n(no diagnostic yield\nor exclusion criteria)", color="#1c1007", border="#ef4444")
arrow(ax, 0.5, 0.415, 0.5, 0.365)

box(ax, 0.5, 0.20, 0.50, 0.08,
    "Total patients: 79,417\n25 studies · 6 indications\n2007–2026", border="#10b981", color="#052e16")

arrow(ax, 0.5, 0.295, 0.5, 0.24)

ax.set_xlim(0, 1); ax.set_ylim(0.1, 1.02)
ax.set_title("Figure 6 — PRISMA 2020 Flow Diagram", color=TEXT, fontsize=12, pad=8)
plt.tight_layout()
fig.savefig(OUT / "fig6_prisma_flow.png", dpi=180, bbox_inches="tight", facecolor=BG)
plt.close()
print("✅ fig6")

print(f"\nAll figures saved to {OUT}")
