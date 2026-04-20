"""Page 5 — Clinical PDF Report generator."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
from utils.cnv_scoring import match_cnv, demo_cnv
from utils.pdf_report import generate_pdf

st.set_page_config(page_title="Clinical Report", page_icon="📄", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0f172a; }
[data-testid="stSidebar"] { background: #1e293b; }
</style>
""", unsafe_allow_html=True)

st.title("📄 Clinical Report")
st.caption("Generate a PDF report for the clinical geneticist")

col_form, col_preview = st.columns([1, 1.4])

with col_form:
    st.markdown("#### Patient Information")
    patient_id  = st.text_input("Patient ID", value="PAT-2026-001")
    sample_id   = st.text_input("Sample ID",  value="DNA-CMA-001")
    indication  = st.selectbox("Clinical Indication", [
        "ID/DD — Intellectual Disability / Developmental Delay",
        "ASD — Autism Spectrum Disorder",
        "MCA — Multiple Congenital Anomalies",
        "PRE — Prenatal (abnormal ultrasound)",
        "EPI — Epilepsy",
        "PSY — Psychiatric Disorders",
    ])

    st.markdown("#### CNV Data")
    uploaded = st.file_uploader("Upload CNV CSV", type=["csv"])
    use_demo = st.button("Use demo data (6 CNVs)", use_container_width=True)

    cnv_df = None
    if uploaded:
        try:
            cnv_df = pd.read_csv(uploaded)
            cnv_df.columns = cnv_df.columns.str.lower()
            st.success(f"{len(cnv_df)} CNVs loaded")
        except Exception as e:
            st.error(str(e))
    elif use_demo or st.session_state.get("report_demo"):
        st.session_state["report_demo"] = True
        cnv_df = demo_cnv()
        st.info("Demo data loaded")

    generate_btn = st.button("🖨️ Generate PDF Report", type="primary",
                             use_container_width=True, disabled=(cnv_df is None))

with col_preview:
    st.markdown("#### Preview")

    if cnv_df is not None:
        results = match_cnv(cnv_df)
        n_path = len(results[results["acmg"].isin(["Pathogenic","Likely Pathogenic"])])
        n_vus  = len(results[results["acmg"] == "VUS"])

        st.markdown(f"""
        <div style="background:#1e293b; border:1px solid #334155; border-radius:12px; padding:20px;">
          <div style="color:#94a3b8; font-size:0.8rem;">CNV DIAGNOSTIC REPORT</div>
          <div style="color:#f1f5f9; font-size:1.2rem; font-weight:700; margin:6px 0;">
            {patient_id} &nbsp;|&nbsp; {sample_id}
          </div>
          <div style="color:#64748b; font-size:0.85rem;">{indication}</div>
          <hr style="border-color:#334155; margin:14px 0;">
          <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px; text-align:center;">
            <div>
              <div style="font-size:1.6rem; font-weight:800; color:#3b82f6;">{len(results)}</div>
              <div style="font-size:0.75rem; color:#94a3b8;">Total CNVs</div>
            </div>
            <div>
              <div style="font-size:1.6rem; font-weight:800; color:#ef4444;">{n_path}</div>
              <div style="font-size:0.75rem; color:#94a3b8;">Pathogenic/LP</div>
            </div>
            <div>
              <div style="font-size:1.6rem; font-weight:800; color:#eab308;">{n_vus}</div>
              <div style="font-size:0.75rem; color:#94a3b8;">VUS</div>
            </div>
          </div>
          <hr style="border-color:#334155; margin:14px 0;">
        """, unsafe_allow_html=True)

        for _, r in results.iterrows():
            from utils.cnv_scoring import ACMG_COLORS
            color = ACMG_COLORS.get(r["acmg"], "#6b7280")
            st.markdown(f"""
          <div style="display:flex; justify-content:space-between; align-items:center;
                      padding:6px 0; border-bottom:1px solid #1e293b;">
            <span style="color:#94a3b8; font-size:0.82rem;">
              chr{r['chr']}:{int(r['start']):,} ({r['type']})
            </span>
            <span style="color:#f1f5f9; font-size:0.82rem;">{r['syndrome'][:25]}</span>
            <span style="background:{color}22; color:{color}; padding:2px 8px;
                         border-radius:10px; font-size:0.75rem; font-weight:700;">
              {r['acmg']}
            </span>
          </div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        if generate_btn:
            with st.spinner("Generating PDF..."):
                try:
                    pdf_bytes = generate_pdf(results, patient_id, sample_id, indication)
                    st.success("Report generated!")
                    st.download_button(
                        label="⬇ Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"CNV_Report_{patient_id}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"PDF generation error: {e}")
    else:
        st.markdown("""
        <div style="background:#1e293b; border:1px dashed #334155; border-radius:12px;
                    padding:3rem; text-align:center; color:#475569;">
          Upload a CNV file or use demo data<br>to preview and generate report
        </div>""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="color:#475569; font-size:0.78rem; text-align:center;">
  ⚠️ For research and exploratory use only — not a medical diagnosis.
  Clinical interpretation must be performed by a qualified clinical geneticist.
</div>""", unsafe_allow_html=True)
