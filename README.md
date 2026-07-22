# Starcom SOP Sales to After Sales

Interactive Streamlit application for a telecommunication services and IT system integrator. It maps departmental authority from lead generation through delivery, billing, after-sales support, and account growth.

## Included
- Interactive Mermaid end-to-end flowchart
- Department scope and authority
- Process detail with inputs, outputs, SLA, evidence, pass, reject, and escalation criteria
- Decision gates
- RACI matrix
- Approval matrix
- Document register
- KPI framework
- Excel-based process master

## Run locally
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy
1. Create a private GitHub repository.
2. Upload the complete folder contents.
3. Connect GitHub to Streamlit Community Cloud.
4. Deploy `app.py` from the `main` branch.

## Maintain the SOP
Edit `data/sop_sales_after_sales.xlsx`. Keep sheet names and column headers unchanged. Commit the updated file to GitHub.

## Governance note
Approval limits and margin thresholds must be aligned with the current Delegation of Authority. Do not publish sensitive customer, pricing, margin, credential, or contract data in a public repository.
