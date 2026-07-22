from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Starcom SOP | Sales to After Sales", page_icon="📡", layout="wide", initial_sidebar_state="expanded")

BASE = Path(__file__).parent
DATA_FILE = BASE / "data" / "sop_sales_after_sales.xlsx"

@st.cache_data(show_spinner=False)
def load_data():
    return {
        "process": pd.read_excel(DATA_FILE, sheet_name="SOP_Process"),
        "raci": pd.read_excel(DATA_FILE, sheet_name="RACI"),
        "approval": pd.read_excel(DATA_FILE, sheet_name="Approval_Matrix"),
        "documents": pd.read_excel(DATA_FILE, sheet_name="Document_Register"),
        "status": pd.read_excel(DATA_FILE, sheet_name="Status_Reference"),
    }

data = load_data()
df = data["process"]

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {background: #f4f7fb;}
[data-testid="stSidebar"] {background: #102a43;}
[data-testid="stSidebar"] * {color: #f8fbff;}
.block-container {padding-top: 1.2rem; padding-bottom: 3rem;}
.hero {background: linear-gradient(120deg,#102a43,#1f5f99); padding: 24px 28px; border-radius: 18px; color: white; margin-bottom: 18px; box-shadow:0 8px 24px rgba(16,42,67,.16)}
.hero h1 {margin:0; font-size:2rem}.hero p{margin:.45rem 0 0;color:#dbeafe}
.card {background:white; border:1px solid #e4ebf3; border-radius:16px; padding:17px; box-shadow:0 4px 16px rgba(16,42,67,.06); min-height:112px}
.card .label{font-size:.78rem;color:#60758a;text-transform:uppercase;letter-spacing:.06em}.card .value{font-size:1.7rem;font-weight:700;color:#102a43}.card .note{font-size:.82rem;color:#60758a}
.section {font-size:1.3rem;font-weight:700;color:#102a43;margin:12px 0 8px}
.owner {display:inline-block;background:#e7f1ff;color:#174d7d;border-radius:999px;padding:4px 10px;font-size:.8rem;font-weight:600}
.warn {background:#fff7e6;border-left:5px solid #f59e0b;padding:12px;border-radius:8px}
.ok {background:#eaf8ef;border-left:5px solid #16a34a;padding:12px;border-radius:8px}
.bad {background:#fdecec;border-left:5px solid #dc2626;padding:12px;border-radius:8px}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("## 📡 STARCOM SOP")
st.sidebar.caption("Telecommunication & IT System Integrator")
page = st.sidebar.radio("Navigation", ["Executive Flow", "Department Scope", "Process Detail", "Decision Gates", "RACI Matrix", "Approval Matrix", "Document Control", "KPI Framework", "Deployment Guide"])
st.sidebar.markdown("---")
st.sidebar.markdown("**Process controls**")
st.sidebar.caption("PASS/GO · REVISE · HOLD · REJECT/NO-GO · ESCALATE")

st.markdown('<div class="hero"><h1>SOP Sales to After Sales</h1><p>End-to-end governance for telecommunication services and IT system integration, with departmental authority and Go/Revise/No-Go controls.</p></div>', unsafe_allow_html=True)

# Executive flow Mermaid
flow = r"""
flowchart LR
    A([Lead / Tender / Referral]) --> B[Sales: Qualification]
    B --> C{Qualified?}
    C -- No --> C1([Close / Nurture])
    C -- Yes --> D[Sales + PD: Discovery]
    D --> E[PD: Assessment, Survey, Design & BoM]
    E --> F{Technically feasible?}
    F -- No --> F1[Revise / Alternative]
    F1 --> F2{Feasible after revision?}
    F2 -- No --> Z([REJECT / NO-GO])
    F2 -- Yes --> G
    F -- Yes --> G[Procurement: Availability & Lead Time]
    G --> H[Operation: Delivery Feasibility]
    H --> I[Finance: Cost, Margin & Cash Flow]
    I --> J[Legal: Contract & Compliance Risk]
    J --> K{Internal Go/No-Go}
    K -- Revise --> E
    K -- No-Go --> Z
    K -- Go --> L[Sales: Proposal & Negotiation]
    L --> M{Customer Award?}
    M -- Lost/Hold --> M1([LOST / HOLD])
    M -- Won --> N[Legal + Finance: PO/Contract & Billing Readiness]
    N --> O[Sales: Project Handover]
    O --> P[Operation: Kickoff & Planning]
    P --> Q[Procurement + HRGA/HSE: Readiness]
    Q --> R[Operation + PD: Install, Configure & Troubleshoot]
    R --> S{FAT / SAT / UAT Pass?}
    S -- No --> R
    S -- Yes --> T[Punch List & BAST]
    T --> U{Customer Accepts?}
    U -- No --> R
    U -- Yes --> V[Finance: Invoice & Collection]
    V --> W{Paid?}
    W -- No --> W1[Reminder / Escalation / Dispute]
    W1 --> V
    W -- Yes --> X[After Sales: Warranty, Support & PM]
    X --> Y{Complaint / Major Incident?}
    Y -- Yes --> Y1[RCA + CAPA + Escalation]
    Y1 --> X
    Y -- No --> AA[Sales: CSI, QBR, Renewal & Upsell]
    AA --> A

    classDef sales fill:#dbeafe,stroke:#2563eb,color:#102a43;
    classDef pd fill:#e0f2fe,stroke:#0284c7,color:#102a43;
    classDef finance fill:#dcfce7,stroke:#16a34a,color:#102a43;
    classDef legal fill:#f3e8ff,stroke:#9333ea,color:#102a43;
    classDef operation fill:#fef3c7,stroke:#d97706,color:#102a43;
    classDef reject fill:#fee2e2,stroke:#dc2626,color:#7f1d1d;
    classDef after fill:#ccfbf1,stroke:#0f766e,color:#102a43;
    class B,D,L,O,AA sales;
    class E,F,F1,F2 pd;
    class I,V,W,W1 finance;
    class J,N legal;
    class H,P,Q,R,S,T,U operation;
    class Z,C1,M1 reject;
    class X,Y,Y1 after;
"""

if page == "Executive Flow":
    c1,c2,c3,c4 = st.columns(4)
    metrics = [(len(df),"Controlled processes"),(df['Department'].nunique(),"Process-owner groups"),(df['Phase'].nunique(),"End-to-end phases"),(df['Document'].nunique(),"Core records")]
    for col,(value,label) in zip([c1,c2,c3,c4],metrics):
        col.markdown(f'<div class="card"><div class="label">{label}</div><div class="value">{value}</div><div class="note">Defined in the Excel master data</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="section">Executive process map</div>',unsafe_allow_html=True)
    st.mermaid_chart(flow, height=830)
    st.info("Use fullscreen in the diagram toolbar for presentation mode. The Excel file is the process master; changes are loaded automatically after app refresh.")

elif page == "Department Scope":
    departments = sorted(df['Department'].dropna().unique().tolist())
    selected = st.selectbox("Select department / process owner", departments)
    view = df[df['Department']==selected].copy()
    st.markdown(f"### {selected}")
    st.caption(f"{len(view)} controlled process(es)")
    for _,r in view.iterrows():
        with st.expander(f"{int(r['No']):02d}. {r['Process']} — {r['Phase']}"):
            a,b = st.columns([1,1])
            with a:
                st.markdown(f"**Responsible:** {r['Responsible']}")
                st.markdown(f"**Approval:** {r['Approval']}")
                st.markdown(f"**Authority / activity:** {r['Activity']}")
                st.markdown(f"**Supporting:** {r['Supporting Department']}")
            with b:
                st.markdown(f"**Input:** {r['Input']}")
                st.markdown(f"**Output:** {r['Output']}")
                st.markdown(f"**SLA:** {r['SLA']}")
                st.markdown(f"**Document:** {r['Document']}")
            st.markdown(f'<div class="ok"><b>PASS:</b> {r["Pass Criteria"]}</div>',unsafe_allow_html=True)
            st.markdown(f'<div class="bad"><b>REJECT / PROBLEM:</b> {r["Reject / Problem Criteria"]}</div>',unsafe_allow_html=True)
            st.markdown(f'<div class="warn"><b>CORRECTIVE / ESCALATION:</b> {r["Corrective / Escalation"]}</div>',unsafe_allow_html=True)

elif page == "Process Detail":
    phase = st.selectbox("Phase", ["All"] + sorted(df['Phase'].unique().tolist()))
    filtered = df if phase == "All" else df[df['Phase']==phase]
    process = st.selectbox("Process", filtered['Process'].tolist())
    r = filtered[filtered['Process']==process].iloc[0]
    st.markdown(f"## {int(r['No']):02d}. {r['Process']}")
    st.markdown(f'<span class="owner">OWNER: {r["Department"]}</span>',unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    c1.metric("Responsible",r['Responsible'])
    c2.metric("Approval",r['Approval'])
    c3.metric("SLA",r['SLA'])
    st.markdown("### Process definition")
    st.write(r['Activity'])
    a,b = st.columns(2)
    with a:
        st.markdown("**Input**")
        st.write(r['Input'])
        st.markdown("**Required document / evidence**")
        st.write(r['Document'])
    with b:
        st.markdown("**Output**")
        st.write(r['Output'])
        st.markdown("**Supporting department**")
        st.write(r['Supporting Department'])
    st.markdown(f'<div class="ok"><b>PASS / GO CRITERIA</b><br>{r["Pass Criteria"]}</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="bad"><b>REJECT / PROBLEM CRITERIA</b><br>{r["Reject / Problem Criteria"]}</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="warn"><b>CORRECTIVE / ESCALATION</b><br>{r["Corrective / Escalation"]}</div>',unsafe_allow_html=True)

elif page == "Decision Gates":
    st.markdown("## Decision-gate governance")
    gate_df = df[df['Reject / Problem Criteria'].notna()][['No','Phase','Department','Process','Pass Criteria','Reject / Problem Criteria','Corrective / Escalation','Approval']]
    status = st.radio("Review focus", ["All gates","Technical","Commercial & Legal","Delivery & Acceptance","Billing & After Sales"], horizontal=True)
    phase_map = {
        'Technical':['Pre-Sales'],
        'Commercial & Legal':['Commercial Review','Sales Closing','Contracting'],
        'Delivery & Acceptance':['Project Delivery','Acceptance'],
        'Billing & After Sales':['Billing','After Sales','Account Growth'],
    }
    if status != 'All gates': gate_df = gate_df[gate_df['Phase'].isin(phase_map[status])]
    st.dataframe(gate_df, use_container_width=True, hide_index=True, height=620)

elif page == "RACI Matrix":
    st.markdown("## RACI matrix")
    st.caption("A = Accountable · R = Responsible · C = Consulted")
    st.dataframe(data['raci'],use_container_width=True,hide_index=True,height=650)

elif page == "Approval Matrix":
    st.markdown("## Approval matrix")
    st.dataframe(data['approval'],use_container_width=True,hide_index=True,height=560)
    st.warning("Approval limits, discount thresholds, and financial authority should be aligned with the company's current Delegation of Authority (DoA).")

elif page == "Document Control":
    st.markdown("## Controlled document register")
    phase_filter = st.multiselect("Filter phase",sorted(data['documents']['Phase'].unique()),default=[])
    d = data['documents'] if not phase_filter else data['documents'][data['documents']['Phase'].isin(phase_filter)]
    st.dataframe(d,use_container_width=True,hide_index=True,height=580)
    st.download_button("Download SOP master Excel", DATA_FILE.read_bytes(), file_name="sop_sales_after_sales.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

elif page == "KPI Framework":
    st.markdown("## Recommended process KPI")
    kpis = pd.DataFrame([
        ['Sales','Qualified Lead Rate','Qualified leads / total leads','Monthly'],
        ['Sales','Proposal Win Rate','Won opportunities / submitted proposals','Monthly'],
        ['Sales','Sales Cycle Time','Average days from qualified lead to award','Monthly'],
        ['Product Development','First-Pass Technical Approval','Design approved without major revision','Monthly'],
        ['Product Development','BoM Accuracy','Actual procurement variance against approved BoM','Per project'],
        ['Finance','Gross Margin Realization','Actual GM versus approved GM','Per project'],
        ['Finance','DSO','Average collection days','Monthly'],
        ['Legal','Contract Review Turnaround','Average review completion time','Monthly'],
        ['Procurement','On-Time Material Availability','Materials available by required date','Per project'],
        ['Operation','On-Time Project Completion','Projects completed by baseline date','Monthly'],
        ['Operation','First-Pass Acceptance Rate','FAT/SAT/UAT pass without major retest','Per project'],
        ['After Sales','SLA Compliance','Tickets resolved within SLA','Monthly'],
        ['After Sales','Repeat Incident Rate','Recurring incidents / total incidents','Monthly'],
        ['Sales / After Sales','Customer Satisfaction Index','Average customer survey score','Quarterly'],
        ['Sales','Renewal / Repeat Order Rate','Renewed or repeat accounts / eligible accounts','Quarterly'],
    ],columns=['Department','KPI','Definition','Frequency'])
    st.dataframe(kpis,use_container_width=True,hide_index=True,height=580)

elif page == "Deployment Guide":
    st.markdown("## GitHub → Streamlit Community Cloud")
    st.markdown("""
1. Create a **private GitHub repository** for internal SOP content.
2. Upload all files in this package while preserving the folders `data/`, `assets/`, and `.streamlit/`.
3. In Streamlit Community Cloud, connect the authorized GitHub account.
4. Select the repository, branch `main`, and entrypoint `app.py`.
5. Deploy. The app will install packages from `requirements.txt`.
6. When the Excel master changes, commit the new file to GitHub; the deployed app will update after the new commit is built.

**Local test**
```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

**Security control**
Do not place customer names, pricing, margin thresholds, credentials, or contract content in a public repository. Use a private repository and restrict workspace access.
""")
