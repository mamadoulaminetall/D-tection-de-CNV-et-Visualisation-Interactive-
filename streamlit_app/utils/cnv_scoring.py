"""CNV matching and ACMG-like pathogenicity scoring against reference syndromes."""

from pathlib import Path
import pandas as pd
import numpy as np

DATA = Path(__file__).parent.parent.parent / "data" / "meta_analysis_v1"

ACMG_COLORS = {
    "Pathogenic":         "#ef4444",
    "Likely Pathogenic":  "#f97316",
    "VUS":                "#eab308",
    "Likely Benign":      "#6b7280",
    "Benign":             "#6b7280",
}

INDICATION_COLORS = {
    "ID/DD": "#3b82f6",
    "ASD":   "#10b981",
    "MCA":   "#f59e0b",
    "PRE":   "#8b5cf6",
    "EPI":   "#ef4444",
    "PSY":   "#f97316",
}


def load_syndromes() -> pd.DataFrame:
    return pd.read_csv(DATA / "cnv_syndromes.csv")


def load_estimates() -> pd.DataFrame:
    return pd.read_csv(DATA / "meta_analytic_estimates.csv")


def load_studies() -> pd.DataFrame:
    return pd.read_csv(DATA / "studies_registry.csv")


def load_rob() -> pd.DataFrame:
    return pd.read_csv(DATA / "risk_of_bias.csv")


def load_platforms() -> pd.DataFrame:
    return pd.read_csv(DATA / "platform_comparison.csv")


def _overlap_pct(s1: int, e1: int, s2: int, e2: int) -> float:
    """Reciprocal overlap: intersection / min(size1, size2)."""
    intersection = max(0, min(e1, e2) - max(s1, s2))
    if intersection == 0:
        return 0.0
    return intersection / min(e1 - s1, e2 - s2)


def classify_acmg(overlap: float, penetrance: float, cnv_type: str, ref_type: str) -> str:
    type_match = (cnv_type.upper() == ref_type.upper()) or ref_type.upper() == "DEL/DUP"
    if not type_match:
        return "Likely Benign"
    if overlap >= 0.80 and penetrance >= 0.80:
        return "Pathogenic"
    if overlap >= 0.50 and penetrance >= 0.50:
        return "Likely Pathogenic"
    if overlap >= 0.20:
        return "VUS"
    return "Likely Benign"


def match_cnv(cnv_df: pd.DataFrame) -> pd.DataFrame:
    """
    Match uploaded CNVs against reference syndromes.
    Input columns: chr, start, end, type (DEL/DUP).
    Returns enriched DataFrame with best match per CNV.
    """
    syndromes = load_syndromes()
    results = []

    for _, cnv in cnv_df.iterrows():
        try:
            chrom = str(cnv["chr"]).replace("chr", "").replace("Chr", "")
            start = int(cnv["start"])
            end   = int(cnv["end"])
            ctype = str(cnv.get("type", "DEL")).upper()
            size_kb = round((end - start) / 1000, 1)
        except Exception:
            continue

        best_overlap = 0.0
        best_match   = None

        for _, syn in syndromes.iterrows():
            if str(syn["chr"]) != chrom:
                continue
            ov = _overlap_pct(start, end, int(syn["start"]), int(syn["end"]))
            if ov > best_overlap:
                best_overlap = ov
                best_match = syn

        if best_match is not None and best_overlap > 0.10:
            acmg = classify_acmg(best_overlap, best_match["penetrance"], ctype, best_match["type"])
            results.append({
                "chr":          chrom,
                "start":        start,
                "end":          end,
                "type":         ctype,
                "size_kb":      size_kb,
                "syndrome":     best_match["name"],
                "region":       best_match["region"],
                "overlap_pct":  round(best_overlap * 100, 1),
                "penetrance":   round(best_match["penetrance"] * 100, 0),
                "omim":         best_match["omim"],
                "genes":        best_match["genes"],
                "indications":  best_match["indications"],
                "acmg":         acmg,
                "acmg_color":   ACMG_COLORS[acmg],
            })
        else:
            results.append({
                "chr":         chrom,
                "start":       start,
                "end":         end,
                "type":        ctype,
                "size_kb":     size_kb,
                "syndrome":    "No match",
                "region":      "-",
                "overlap_pct": 0.0,
                "penetrance":  0.0,
                "omim":        "-",
                "genes":       "-",
                "indications": "-",
                "acmg":        "Likely Benign",
                "acmg_color":  ACMG_COLORS["Likely Benign"],
            })

    return pd.DataFrame(results)


def demo_cnv() -> pd.DataFrame:
    """Demo CNV file with known pathogenic variants."""
    return pd.DataFrame([
        {"chr": "22", "start": 18900000, "end": 21800000, "type": "DEL"},
        {"chr": "15", "start": 23500000, "end": 28500000, "type": "DEL"},
        {"chr": "16", "start": 29600000, "end": 30200000, "type": "DEL"},
        {"chr": "7",  "start": 72700000, "end": 74200000, "type": "DEL"},
        {"chr": "1",  "start": 146500000, "end": 147500000, "type": "DUP"},
        {"chr": "3",  "start": 50000000, "end": 51000000,  "type": "DEL"},
    ])
