# 🧬 CNV Diagnostic Platform — MedFlow AI

> **Détection et interprétation clinique des variants du nombre de copies (CNV)**  
> Basée sur une méta-analyse validée · 25 études · 79 417 patients · 6 indications cliniques

[![medRxiv](https://img.shields.io/badge/medRxiv-Submitted_2026-b31b1b)](https://www.medrxiv.org)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## Présentation

Plateforme de détection et d'interprétation clinique des Copy Number Variants (CNV) basée sur une méta-analyse systématique du rendement diagnostique de la chromosomique sur microarray (CMA) publiée sur medRxiv.

### Indications cliniques couvertes

| Code | Indication | Rendement poolé | I² | k études |
|------|-----------|----------------|-----|---------|
| ID/DD | Déficience intellectuelle / Retard développemental | **15.9%** [15.2–16.6%] | 72% | 7 |
| MCA  | Anomalies congénitales multiples | **24.6%** [22.9–26.4%] | 38% | 4 |
| PSY  | Troubles psychiatriques | **14.9%** [11.9–18.5%] | 75% | 3 |
| EPI  | Épilepsie / crises convulsives | **10.8%** [9.3–12.6%] | 0% | 3 |
| ASD  | Troubles du spectre autistique | **10.3%** [9.3–11.4%] | 0% | 5 |
| PRE  | Prénatal (échographie anormale) | **5.9%** [5.5–6.4%] | 0% | 3 |

---

## Méta-analyse (Phase 1)

**Publication :** medRxiv (soumis avril 2026)  
**Titre :** "Diagnostic Yield of Chromosomal Microarray Analysis for Copy Number Variants Detection: A Systematic Review and Meta-Analysis of 25 Studies across Six Clinical Indications"

### Données clés
- **25 études** publiées (2007–2026)
- **79 417 patients** (range 150–21 698 par étude)
- **18 syndromes génomiques** récurrents référencés (ClinVar / OMIM)
- **9 plateformes** comparées : karyotype → aCGH → SNP array → WGS
- Méthode : DerSimonian-Laird (effets aléatoires, transformation logit)

### Syndromes pathogènes couverts

| Région | Syndrome | Type | Prévalence /10k | Pénétrance |
|--------|---------|------|----------------|-----------|
| 22q11.2 | DiGeorge / 22q11.2DS | DEL | 2.5 | 97% |
| 15q11-q13 | Angelman / Prader-Willi | DEL | 0.7 | 100% |
| 16p11.2 | ASD-associated CNV | DEL/DUP | 3.0 | 27–62% |
| 7q11.23 | Williams-Beuren | DEL | 1.3 | 99% |
| 1p36 | 1p36 deletion | DEL | 2.0 | 98% |
| 17p11.2 | Smith-Magenis / Potocki-Lupski | DEL/DUP | 0.4 | 70–100% |

---

## Structure du projet

```
cnv-diagnostic-platform/
├── meta_analysis/
│   ├── 01_generate_cnv_meta_data.py     # Données de référence (25 études)
│   ├── 02_generate_figures.py            # 6 figures publication
│   ├── 03_generate_manuscript.py         # PDF manuscrit IMRaD
│   └── 04_generate_supplementary.py      # PDF supplémentaire
├── data/meta_analysis_v1/
│   ├── studies_registry.csv              # 25 études
│   ├── meta_analytic_estimates.csv       # Rendements poolés par indication
│   ├── cnv_syndromes.csv                 # 18 syndromes ClinVar/OMIM
│   ├── platform_comparison.csv           # 9 plateformes comparées
│   └── risk_of_bias.csv                  # Scores NOS
├── figures/
│   ├── fig1_forest_plot_overall.png      # Forest plot global
│   ├── fig2_pooled_yield.png             # Rendements poolés lollipop
│   ├── fig3_platform_comparison.png      # Comparaison plateformes
│   ├── fig4_cnv_syndromes_bubble.png     # Syndromes taille vs pénétrance
│   ├── fig5_risk_of_bias.png             # NOS scores
│   └── fig6_prisma_flow.png              # Diagramme PRISMA 2020
├── manuscript/
│   ├── CNV_MetaAnalysis_Manuscript.pdf   # Manuscrit complet (IMRaD)
│   └── CNV_MetaAnalysis_Supplementary.pdf
└── README.md
```

---

## Méthode statistique

### Méta-analyse
- **Modèle** : DerSimonian-Laird (effets aléatoires)
- **Transformation** : Logit des proportions (stabilisation de variance)
- **Hétérogénéité** : Cochran Q · I² · τ²
- **Biais** : Newcastle-Ottawa Scale (NOS, max 9)

### Critères d'inclusion
1. CMA (aCGH ou SNP array) pour détection CNV
2. Rendement diagnostique rapporté (variantes pathogènes/probablement pathogènes)
3. ≥ 100 patients
4. Journal à comité de lecture
5. Période : janvier 2007 – avril 2026

---

## Reproduction

```bash
git clone https://github.com/mamadoulaminetall/D-tection-de-CNV-et-Visualisation-Interactive-.git
cd D-tection-de-CNV-et-Visualisation-Interactive-
pip install pandas numpy matplotlib reportlab

# Générer les données
python3 meta_analysis/01_generate_cnv_meta_data.py

# Générer les figures
python3 meta_analysis/02_generate_figures.py

# Générer le manuscrit PDF
python3 meta_analysis/03_generate_manuscript.py

# Générer le supplément PDF
python3 meta_analysis/04_generate_supplementary.py
```

---

## Publication de référence

> **TALL ML** (2026). Diagnostic Yield of Chromosomal Microarray Analysis for Copy Number Variants Detection:  
> A Systematic Review and Meta-Analysis of 25 Studies across Six Clinical Indications.  
> *medRxiv* (submitted April 2026). MedFlow AI, Aix-Marseille Universite.

---

## Phase 2 — Plateforme Clinique (à venir)

Streamlit multi-pages basée sur les données validées :
- Upload VCF/CSV CNV → annotation ClinVar/OMIM
- Score de pathogénicité ACMG
- Comparaison aux 18 syndromes de référence
- Karyogramme interactif
- Rapport PDF clinicien

---

## Avertissement

> ⚠️ Usage exploratoire et de recherche uniquement. Ne constitue pas un diagnostic médical.  
> Interpréter uniquement par un généticien clinique qualifié.

---

## Auteur

**Dr. Mamadou Lamine TALL, PhD**  
Bioinformatique & Intelligence Artificielle médicale  
MedFlow AI · Aix-Marseille Universite  
📧 mamadoulaminetallgithub@gmail.com  
🐙 [github.com/mamadoulaminetall](https://github.com/mamadoulaminetall)

*MedFlow AI © 2026*
