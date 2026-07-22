import streamlit as st
import pandas as pd

st.set_page_config(page_title='Starcom SOP | Sales to After Sales', page_icon='📡', layout='wide', initial_sidebar_state='expanded')

PROCESSES = [
 {'No':1,'Phase':'Pre-Sales','Department':'Sales','Process':'Lead Generation & Registration','Authority':'Mencari, menerima, mencatat, dan menetapkan sumber lead/tender/referral.','Approval':'Sales Manager','Pass':'Identitas customer, kebutuhan awal, PIC, dan peluang tercatat.','Problem':'Data tidak valid, di luar target pasar, atau konflik akun.','Action':'Klarifikasi, alihkan account owner, nurture, atau close lead.','Output':'Lead Register'},
 {'No':2,'Phase':'Pre-Sales','Department':'Sales','Process':'Lead Qualification','Authority':'Menilai kebutuhan, budget, authority, timeline, dan strategic fit.','Approval':'Sales Manager','Pass':'Lead memenuhi kriteria peluang yang dapat dikerjakan.','Problem':'Tidak ada kebutuhan, anggaran, PIC keputusan, atau timeline realistis.','Action':'Nurture, hold, atau reject dengan alasan terdokumentasi.','Output':'Qualified Opportunity'},
 {'No':3,'Phase':'Pre-Sales','Department':'Sales + Product Development','Process':'Customer Discovery','Authority':'Menggali business requirement dan technical requirement pelanggan.','Approval':'Sales Manager / Head of PD','Pass':'Requirement, lokasi, kapasitas, SLA, dan batas scope terdefinisi.','Problem':'Requirement belum jelas atau data customer belum lengkap.','Action':'RFI, meeting lanjutan, dan site survey.','Output':'Requirement Brief'},
 {'No':4,'Phase':'Solution','Department':'Product Development','Process':'Site Survey & Technical Assessment','Authority':'Menentukan kebutuhan survey, metode, parameter teknis, dan hasil assessment.','Approval':'Head of Product Development','Pass':'Data teknis cukup dan kondisi lokasi mendukung.','Problem':'Akses site, LOS, power, rack, jaringan existing, izin, atau data tidak memadai.','Action':'Survey ulang, redesign, alternative technology, atau no-go teknis.','Output':'Survey Report'},
 {'No':5,'Phase':'Solution','Department':'Product Development','Process':'Solution Design & BoM','Authority':'Menetapkan arsitektur, spesifikasi, kapasitas, BoM/BoQ, lisensi, dan technical scope.','Approval':'Head of Product Development','Pass':'Solusi feasible, compliant, scalable, dan dapat diimplementasikan.','Problem':'Tidak kompatibel, kapasitas kurang, produk obsolete, sertifikasi/izin tidak tersedia.','Action':'Revisi desain, substitusi produk, PoC, atau reject.','Output':'Technical Proposal & BoM'},
 {'No':6,'Phase':'Commercial Review','Department':'Procurement & Logistic','Process':'Vendor, Price & Lead-Time Validation','Authority':'Memvalidasi vendor, harga beli, ketersediaan, lead time, warranty, dan delivery.','Approval':'Procurement Manager','Pass':'Quotation vendor valid dan supply sesuai target proyek.','Problem':'Barang kosong, lead time terlalu lama, harga berubah, atau vendor tidak qualified.','Action':'Vendor alternatif, substitusi, renegosiasi, reschedule, atau hold.','Output':'Vendor Validation'},
 {'No':7,'Phase':'Commercial Review','Department':'Operation / Project','Process':'Delivery Feasibility Review','Authority':'Menilai resource, metode kerja, timeline, akses site, HSE, dan acceptance plan.','Approval':'Operation Manager','Pass':'Pekerjaan dapat dilaksanakan sesuai scope, biaya, waktu, dan standar mutu.','Problem':'Resource tidak tersedia, timeline tidak realistis, risiko site tinggi.','Action':'Rebaseline, tambah resource, revisi scope, atau no-go.','Output':'Delivery Plan'},
 {'No':8,'Phase':'Commercial Review','Department':'Finance','Process':'Costing, Margin & Cash-Flow Review','Authority':'Memvalidasi cost, margin, tax, payment term, cash-flow, exposure, dan credit risk.','Approval':'Finance Manager / Director','Pass':'Margin dan cash-flow sesuai threshold serta risiko pembayaran dapat diterima.','Problem':'Margin di bawah batas, negative cash-flow, termin berat, atau credit risk tinggi.','Action':'Reprice, ubah termin, minta DP/jaminan, eskalasi, atau reject.','Output':'Commercial Approval'},
 {'No':9,'Phase':'Commercial Review','Department':'Legal','Process':'Contract, License & Compliance Review','Authority':'Memeriksa NDA, tender terms, kontrak, SLA, liability, penalty, izin, dan compliance.','Approval':'Legal Manager / Director','Pass':'Risiko hukum dan regulasi dapat diterima atau termitigasi.','Problem':'Unlimited liability, penalty tidak proporsional, scope ambigu, izin tidak memadai.','Action':'Redline, legal qualification, risk acceptance Direksi, atau no-go.','Output':'Legal Clearance'},
 {'No':10,'Phase':'Commercial Review','Department':'Management','Process':'Internal Go / No-Go','Authority':'Menetapkan keputusan bisnis akhir berdasarkan technical, commercial, legal, dan delivery review.','Approval':'Direksi sesuai DoA','Pass':'Seluruh critical gate approved atau residual risk diterima.','Problem':'Risiko material tidak dapat dimitigasi atau return tidak layak.','Action':'Revise, hold, reject, atau approve dengan syarat.','Output':'Go/No-Go Decision'},
 {'No':11,'Phase':'Sales Closing','Department':'Sales','Process':'Proposal Submission & Negotiation','Authority':'Menyampaikan proposal, mengendalikan komunikasi komersial, dan mengoordinasikan negosiasi.','Approval':'Sales Manager / Director','Pass':'Customer menyetujui scope, price, schedule, SLA, dan payment term.','Problem':'Harga/spec ditolak, kompetitor unggul, keputusan tertunda.','Action':'Clarification, BAFO, redesign, hold, atau lost analysis.','Output':'Final Proposal / BAFO'},
 {'No':12,'Phase':'Contracting','Department':'Sales + Legal + Finance','Process':'PO / Contract Validation','Authority':'Memastikan PO/kontrak sesuai penawaran final, legal clearance, billing milestone, dan tax requirement.','Approval':'Authorized Signatory','Pass':'Dokumen sah, scope konsisten, dan syarat mulai kerja terpenuhi.','Problem':'PO tidak sesuai, kontrak belum signed, milestone tidak jelas.','Action':'Hold mobilization, koreksi PO, addendum, atau management waiver.','Output':'Effective Contract / PO'},
 {'No':13,'Phase':'Handover','Department':'Sales','Process':'Sales-to-Project Handover','Authority':'Menyerahkan seluruh komitmen customer, baseline scope, assumptions, exclusions, dan contact matrix.','Approval':'Sales Manager + Project Manager','Pass':'Handover checklist lengkap dan diterima project owner.','Problem':'Komitmen lisan, dokumen kurang, scope berbeda, atau margin leakage.','Action':'Clarify dan tutup gap sebelum kickoff.','Output':'Handover Minutes'},
 {'No':14,'Phase':'Project Delivery','Department':'Operation / Project','Process':'Project Kickoff & Baseline','Authority':'Menetapkan WBS, schedule, resource, communication, risk register, quality dan HSE plan.','Approval':'Project Manager / Operation Manager','Pass':'Baseline disetujui internal dan customer.','Problem':'Dependency belum siap, schedule conflict, atau owner tidak jelas.','Action':'Resolve prerequisite, rebaseline, atau escalation.','Output':'Project Management Plan'},
 {'No':15,'Phase':'Project Delivery','Department':'Procurement & Logistic','Process':'Procurement, Warehousing & Delivery','Authority':'Menerbitkan PO vendor, inspeksi barang, inventory, dan pengiriman ke site.','Approval':'Procurement Manager sesuai DoA','Pass':'Barang sesuai spesifikasi, jumlah, kualitas, dan tiba tepat waktu.','Problem':'Delay, damage, mismatch, shortage, atau customs issue.','Action':'Expedite, replacement, claim vendor, atau resequence pekerjaan.','Output':'Material Delivery Record'},
 {'No':16,'Phase':'Project Delivery','Department':'HRGA / HSE','Process':'Resource, Permit & HSE Readiness','Authority':'Memastikan manpower, kompetensi, alat kerja, kendaraan, permit, PPE, dan safety induction.','Approval':'HRGA/HSE Manager','Pass':'Seluruh resource dan safety prerequisite ready.','Problem':'Sertifikasi kurang, permit belum terbit, unsafe condition.','Action':'Stop work, corrective readiness, substitusi personel, atau reschedule.','Output':'Mobilization Readiness'},
 {'No':17,'Phase':'Project Delivery','Department':'Operation + Product Development','Process':'Installation, Integration & Configuration','Authority':'Melaksanakan instalasi, integrasi, konfigurasi, dokumentasi, dan technical escalation.','Approval':'Project Manager / Technical Lead','Pass':'Pekerjaan sesuai approved design, method, dan quality checklist.','Problem':'Design issue, site constraint, configuration fail, atau scope change.','Action':'Troubleshoot, RFI, change request, rollback, atau escalation.','Output':'Installed & Configured System'},
 {'No':18,'Phase':'Testing','Department':'Product Development + Operation','Process':'FAT / SAT / UAT','Authority':'Menetapkan test script, acceptance criteria, pelaksanaan test, dan evidence.','Approval':'Technical Lead + Customer','Pass':'Seluruh critical test case lulus.','Problem':'Test fail, performance kurang, atau evidence tidak diterima.','Action':'Defect fixing, retest, waiver terbatas, atau redesign.','Output':'Test & Acceptance Report'},
 {'No':19,'Phase':'Acceptance','Department':'Operation / Project','Process':'Punch List & BAST','Authority':'Mengendalikan punch list, as-built document, training, handover, dan BAST.','Approval':'Project Manager + Customer','Pass':'Punch list critical closed dan BAST ditandatangani.','Problem':'Customer reject, dokumen kurang, atau outstanding critical.','Action':'Corrective work, verification ulang, partial BAST, atau escalation.','Output':'BAST / Handover Package'},
 {'No':20,'Phase':'Billing','Department':'Finance','Process':'Invoice, Tax & Collection','Authority':'Menerbitkan invoice/faktur pajak, mengontrol due date, aging, collection, dan reconciliation.','Approval':'Finance Manager','Pass':'Dokumen billing lengkap dan pembayaran diterima sesuai jatuh tempo.','Problem':'Invoice reject, disputed amount, overdue, atau deduction.','Action':'Perbaiki dokumen, dispute resolution, reminder, collection escalation.','Output':'Paid / Outstanding Record'},
 {'No':21,'Phase':'After Sales','Department':'After Sales / Customer Support','Process':'Warranty, Helpdesk & Maintenance','Authority':'Menerima tiket, klasifikasi severity, memenuhi SLA, preventive/corrective maintenance.','Approval':'After Sales Manager','Pass':'Layanan pulih dan tiket ditutup dengan konfirmasi customer.','Problem':'SLA breach, repeat incident, spare part delay, atau major outage.','Action':'Escalation matrix, workaround, vendor support, problem management.','Output':'Service Ticket / Maintenance Report'},
 {'No':22,'Phase':'After Sales','Department':'After Sales + Product Development','Process':'RCA & CAPA','Authority':'Menentukan root cause, corrective action, preventive action, owner, dan due date.','Approval':'After Sales / Operation Manager','Pass':'Root cause tervalidasi dan CAPA efektif mencegah recurrence.','Problem':'Root cause belum terbukti atau kejadian berulang.','Action':'Deep-dive, problem review board, redesign, atau management escalation.','Output':'RCA-CAPA Report'},
 {'No':23,'Phase':'Account Growth','Department':'Sales','Process':'Customer Satisfaction, QBR & Renewal','Authority':'Mengelola CSI/NPS, QBR, renewal, upselling, cross-selling, dan account plan.','Approval':'Sales Manager','Pass':'Customer satisfied, renewal plan jelas, dan opportunity baru tercatat.','Problem':'Dissatisfaction, churn risk, atau renewal tidak pasti.','Action':'Service recovery plan, executive engagement, dan retention offer.','Output':'Account Growth Plan'},
]

df = pd.DataFrame(PROCESSES)

st.markdown('''
<style>
:root{--navy:#0b1f33;--blue:#1667b1;--cyan:#29a8df;--green:#18a36b;--orange:#f59e0b;--red:#dc3d4b;--purple:#7c4dcc;--bg:#f3f7fb}
[data-testid="stAppViewContainer"]{background:linear-gradient(180deg,#eef5fb 0,#f8fafc 320px)}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#071827,#102f4c)}
[data-testid="stSidebar"] *{color:#f5f9fd}
.block-container{padding-top:1rem;max-width:1550px}
.hero{padding:28px 32px;border-radius:22px;background:linear-gradient(115deg,#071827,#124d7b 70%,#167bb2);color:white;box-shadow:0 16px 40px rgba(11,31,51,.2);margin-bottom:18px}
.hero h1{font-size:2.15rem;margin:0}.hero p{margin:.5rem 0 0;color:#d7ebf8;font-size:1.02rem}
.kpi{background:white;border:1px solid #dce7f1;border-radius:16px;padding:16px 18px;box-shadow:0 8px 25px rgba(30,65,95,.07)}
.kpi b{font-size:1.65rem;color:#0b1f33}.kpi span{display:block;color:#667b8f;font-size:.78rem;text-transform:uppercase;letter-spacing:.05em}
.phase-title{font-size:1.15rem;font-weight:800;color:#0b1f33;margin:10px 0}
.scope-card{background:white;border-radius:16px;padding:17px;border:1px solid #dce7f1;box-shadow:0 6px 18px rgba(30,65,95,.06);height:100%}
.scope-card h4{margin:0 0 8px;color:#0b1f33}.tag{display:inline-block;padding:4px 9px;border-radius:999px;background:#e5f2fc;color:#145b91;font-size:.75rem;font-weight:700}
.pass{border-left:5px solid var(--green);background:#eaf8f2;padding:12px;border-radius:10px}.problem{border-left:5px solid var(--red);background:#fff0f1;padding:12px;border-radius:10px}.action{border-left:5px solid var(--orange);background:#fff7e8;padding:12px;border-radius:10px}
.legend{display:flex;gap:10px;flex-wrap:wrap}.legend span{background:white;border:1px solid #dce7f1;border-radius:999px;padding:6px 11px;font-size:.78rem}
</style>''', unsafe_allow_html=True)

st.sidebar.markdown('## 📡 STARCOM SOP')
st.sidebar.caption('Telecommunication & IT System Integrator')
page = st.sidebar.radio('Navigation',['Executive Flow','Swimlane Flow','Department Authority','Process Detail','Decision Gates','RACI','Presentation Mode'])
st.sidebar.markdown('---')
st.sidebar.caption('Standalone edition — tidak membutuhkan Excel atau file data eksternal.')

st.markdown('''<div class="hero"><h1>SOP Sales → Delivery → After Sales</h1><p>Visualisasi end-to-end dengan kewenangan departemen, decision gate Go / Revise / Hold / Reject, dan mekanisme eskalasi.</p></div>''',unsafe_allow_html=True)

FLOW = r'''
flowchart LR
 A([Lead / Tender]):::start --> B[Sales<br/>Qualification]:::sales
 B --> C{Qualified?}:::gate
 C -- NO --> C1([CLOSE / NURTURE]):::reject
 C -- YES --> D[Sales + PD<br/>Discovery]:::sales
 D --> E[Product Development<br/>Survey • Design • BoM]:::pd
 E --> F{Technically<br/>Feasible?}:::gate
 F -- REVISE --> E
 F -- NO --> Z([REJECT / NO-GO]):::reject
 F -- YES --> G[Procurement<br/>Vendor • Price • Lead Time]:::proc
 G --> H[Operation<br/>Delivery Feasibility]:::ops
 H --> I[Finance<br/>Cost • Margin • Cash Flow]:::fin
 I --> J[Legal<br/>Contract • License • Risk]:::legal
 J --> K{INTERNAL<br/>GO / NO-GO}:::gate
 K -- REVISE --> E
 K -- NO-GO --> Z
 K -- GO --> L[Sales<br/>Proposal • Negotiation]:::sales
 L --> M{Customer<br/>Award?}:::gate
 M -- LOST / HOLD --> M1([LOST / HOLD]):::reject
 M -- WON --> N[PO / Contract<br/>Validation]:::legal
 N --> O[Sales → Project<br/>Handover]:::sales
 O --> P[Operation<br/>Kickoff • Baseline]:::ops
 P --> Q[Procurement + HRGA/HSE<br/>Readiness]:::proc
 Q --> R[Operation + PD<br/>Install • Integrate • Configure]:::ops
 R --> S{FAT / SAT / UAT<br/>PASS?}:::gate
 S -- FAIL --> R
 S -- PASS --> T[Punch List<br/>BAST]:::ops
 T --> U{Customer<br/>Accepts?}:::gate
 U -- NO --> R
 U -- YES --> V[Finance<br/>Invoice • Collection]:::fin
 V --> W{PAID?}:::gate
 W -- NO --> W1[Reminder • Dispute<br/>Escalation]:::reject
 W1 --> V
 W -- YES --> X[After Sales<br/>Warranty • Helpdesk • PM]:::after
 X --> Y{Complaint /<br/>Major Incident?}:::gate
 Y -- YES --> Y1[RCA • CAPA<br/>Management Escalation]:::after
 Y1 --> X
 Y -- NO --> AA[Sales<br/>CSI • QBR • Renewal • Upsell]:::sales
 AA --> A
 classDef start fill:#0b1f33,color:#fff,stroke:#0b1f33;
 classDef sales fill:#dceeff,color:#0b3557,stroke:#1667b1,stroke-width:2px;
 classDef pd fill:#d8f4ff,color:#063f58,stroke:#1495c5,stroke-width:2px;
 classDef proc fill:#fff0cc,color:#6c4700,stroke:#e69a00,stroke-width:2px;
 classDef ops fill:#ffe8c7,color:#673900,stroke:#e07800,stroke-width:2px;
 classDef fin fill:#dff7e9,color:#0c5134,stroke:#18a36b,stroke-width:2px;
 classDef legal fill:#eee3ff,color:#452278,stroke:#7c4dcc,stroke-width:2px;
 classDef after fill:#d8f7f3,color:#0b514b,stroke:#159c91,stroke-width:2px;
 classDef gate fill:#fff,color:#0b1f33,stroke:#41566a,stroke-width:2px;
 classDef reject fill:#ffe1e4,color:#861c27,stroke:#dc3d4b,stroke-width:2px;
'''

SWIM = r'''
flowchart TB
 subgraph S[SALES]
  A1[Lead & Qualification] --> A2[Discovery] --> A3[Proposal & Negotiation] --> A4[Handover] --> A5[CSI • Renewal • Upsell]
 end
 subgraph PD[PRODUCT DEVELOPMENT]
  B1[Survey & Assessment] --> B2[Solution Design & BoM] --> B3[Technical Support & Testing] --> B4[RCA / Redesign]
 end
 subgraph P[PROCUREMENT & LOGISTIC]
  C1[Vendor / Price / Lead Time] --> C2[Purchasing & Delivery]
 end
 subgraph F[FINANCE]
  D1[Cost • Margin • Cash Flow] --> D2[Billing Readiness] --> D3[Invoice & Collection]
 end
 subgraph L[LEGAL]
  E1[NDA / Tender / Contract Review] --> E2[PO / Contract Validation]
 end
 subgraph O[OPERATION / PROJECT]
  F1[Delivery Feasibility] --> F2[Kickoff & Baseline] --> F3[Installation & Integration] --> F4[FAT/SAT/UAT] --> F5[BAST]
 end
 subgraph H[HRGA / HSE]
  G1[Manpower • Permit • PPE • Safety]
 end
 subgraph AS[AFTER SALES]
  H1[Warranty • Helpdesk • Maintenance] --> H2[Incident • RCA • CAPA]
 end
 A1 --> A2
 A2 --> B1
 B2 --> C1
 C1 --> F1
 F1 --> D1
 D1 --> E1
 E1 --> A3
 A3 --> E2
 E2 --> A4
 A4 --> F2
 F2 --> C2
 F2 --> G1
 C2 --> F3
 G1 --> F3
 B3 --> F4
 F3 --> F4
 F4 --> F5
 F5 --> D3
 D3 --> H1
 H1 --> A5
 H2 --> B4
 classDef lane fill:#f8fbfe,stroke:#b7ccdd,color:#0b1f33;
 class A1,A2,A3,A4,A5,B1,B2,B3,B4,C1,C2,D1,D2,D3,E1,E2,F1,F2,F3,F4,F5,G1,H1,H2 lane;
'''

if page == 'Executive Flow':
 c=st.columns(4)
 for col,(v,l) in zip(c,[(len(df),'Controlled Processes'),(df.Department.nunique(),'Owner Groups'),(df.Phase.nunique(),'Process Phases'),(5,'Primary Decision Outcomes')]):
  col.markdown(f'<div class="kpi"><b>{v}</b><span>{l}</span></div>',unsafe_allow_html=True)
 st.markdown('### Executive process map')
 st.markdown('<div class="legend"><span>🔵 Sales/Business</span><span>🔷 Product Development</span><span>🟢 Finance</span><span>🟣 Legal</span><span>🟠 Delivery</span><span>🔴 Reject/Escalate</span></div>',unsafe_allow_html=True)
 st.mermaid_chart(FLOW, width="stretch")

elif page == 'Swimlane Flow':
 st.markdown('### Cross-department swimlane')
 st.caption('Menunjukkan perpindahan ownership dan koordinasi lintas fungsi.')
 st.mermaid_chart(SWIM, width="stretch")

elif page == 'Department Authority':
 dep=st.selectbox('Pilih departemen',sorted(df.Department.unique()))
 view=df[df.Department==dep]
 st.markdown(f'## {dep}')
 st.caption(f'{len(view)} proses berada dalam ownership atau joint ownership departemen ini.')
 for _,r in view.iterrows():
  with st.expander(f"{r['No']:02d}. {r['Process']} — {r['Phase']}",expanded=False):
   x,y=st.columns(2)
   x.markdown(f"**Kewenangan**  \n{r['Authority']}")
   x.markdown(f"**Approval**  \n{r['Approval']}")
   y.markdown(f"**Output wajib**  \n{r['Output']}")
   y.markdown(f"**Fase**  \n{r['Phase']}")
   st.markdown(f'<div class="pass"><b>LOLOS / GO</b><br>{r["Pass"]}</div>',unsafe_allow_html=True)
   st.markdown(f'<div class="problem"><b>REJECT / MASALAH</b><br>{r["Problem"]}</div>',unsafe_allow_html=True)
   st.markdown(f'<div class="action"><b>TINDAKAN / ESKALASI</b><br>{r["Action"]}</div>',unsafe_allow_html=True)

elif page == 'Process Detail':
 phase=st.selectbox('Fase',['Semua']+sorted(df.Phase.unique()))
 view=df if phase=='Semua' else df[df.Phase==phase]
 name=st.selectbox('Proses',view.Process.tolist())
 r=view[view.Process==name].iloc[0]
 st.markdown(f"## {r['No']:02d}. {r['Process']}")
 st.markdown(f'<span class="tag">OWNER: {r["Department"]}</span>',unsafe_allow_html=True)
 a,b,c=st.columns(3)
 a.info('**Fase**\n\n'+r['Phase'])
 b.info('**Approval**\n\n'+r['Approval'])
 c.info('**Output**\n\n'+r['Output'])
 st.markdown('### Scope kewenangan')
 st.write(r['Authority'])
 st.markdown(f'<div class="pass"><b>LOLOS / GO</b><br>{r["Pass"]}</div>',unsafe_allow_html=True)
 st.markdown(f'<div class="problem"><b>REJECT / MASALAH</b><br>{r["Problem"]}</div>',unsafe_allow_html=True)
 st.markdown(f'<div class="action"><b>TINDAKAN / ESKALASI</b><br>{r["Action"]}</div>',unsafe_allow_html=True)

elif page == 'Decision Gates':
 st.markdown('## Decision Gate Register')
 st.caption('Setiap gate harus menghasilkan keputusan terdokumentasi: GO, REVISE, HOLD, REJECT/NO-GO, atau ESCALATE.')
 show=df[['No','Phase','Department','Process','Approval','Pass','Problem','Action']]
 st.dataframe(show,use_container_width=True,hide_index=True,height=650)

elif page == 'RACI':
 roles=['Sales','Product Development','Procurement','Finance','Legal','Operation','HRGA/HSE','After Sales','Management']
 rows=[]
 mapping={
 'Lead Generation & Registration':{'Sales':'A/R'},'Lead Qualification':{'Sales':'A/R','Product Development':'C'},
 'Customer Discovery':{'Sales':'A/R','Product Development':'R','Operation':'C'},'Site Survey & Technical Assessment':{'Product Development':'A/R','Operation':'C','Sales':'C'},
 'Solution Design & BoM':{'Product Development':'A/R','Procurement':'C','Operation':'C'},'Vendor, Price & Lead-Time Validation':{'Procurement':'A/R','Product Development':'C','Finance':'C'},
 'Delivery Feasibility Review':{'Operation':'A/R','Product Development':'C','HRGA/HSE':'C'},'Costing, Margin & Cash-Flow Review':{'Finance':'A/R','Sales':'C','Procurement':'C'},
 'Contract, License & Compliance Review':{'Legal':'A/R','Sales':'C','Finance':'C'},'Internal Go / No-Go':{'Management':'A','Sales':'R','Product Development':'C','Finance':'C','Legal':'C','Operation':'C'},
 'Proposal Submission & Negotiation':{'Sales':'A/R','Product Development':'C','Finance':'C','Legal':'C'},'PO / Contract Validation':{'Legal':'A/R','Sales':'R','Finance':'C'},
 'Sales-to-Project Handover':{'Sales':'A/R','Operation':'R','Product Development':'C','Finance':'C','Legal':'C'},'Project Kickoff & Baseline':{'Operation':'A/R','Sales':'C','Product Development':'C'},
 'Procurement, Warehousing & Delivery':{'Procurement':'A/R','Operation':'C','Finance':'C'},'Resource, Permit & HSE Readiness':{'HRGA/HSE':'A/R','Operation':'C'},
 'Installation, Integration & Configuration':{'Operation':'A/R','Product Development':'R','Procurement':'C'},'FAT / SAT / UAT':{'Operation':'A','Product Development':'R','Sales':'C'},
 'Punch List & BAST':{'Operation':'A/R','Sales':'C','Product Development':'C'},'Invoice, Tax & Collection':{'Finance':'A/R','Sales':'C','Legal':'C'},
 'Warranty, Helpdesk & Maintenance':{'After Sales':'A/R','Operation':'C','Product Development':'C'},'RCA & CAPA':{'After Sales':'A','Product Development':'R','Operation':'R'},
 'Customer Satisfaction, QBR & Renewal':{'Sales':'A/R','After Sales':'C','Management':'C'}}
 for p in df.Process:
  row={'Process':p}; row.update({r:mapping.get(p,{}).get(r,'') for r in roles}); rows.append(row)
 st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True,height=680)
 st.caption('A = Accountable · R = Responsible · C = Consulted')

elif page == 'Presentation Mode':
 st.markdown('## Presentation Mode')
 st.info('Gunakan tombol fullscreen pada diagram. Halaman ini menyederhanakan informasi untuk dipresentasikan kepada Direksi atau lintas departemen.')
 st.mermaid_chart(FLOW, width="stretch")
 st.markdown('### Pesan utama')
 st.write('1. Sales tetap menjadi pemilik relasi customer, tetapi tidak boleh menjanjikan solusi, harga, timeline, atau klausul tanpa approval fungsi terkait.')
 st.write('2. Product Development menjadi pemilik kelayakan dan baseline teknis; Operation menjadi pemilik delivery setelah handover.')
 st.write('3. Finance dan Legal memiliki hak menghentikan proses apabila risiko komersial, pembayaran, kontraktual, atau regulasi tidak dapat diterima.')
 st.write('4. Reject bukan kegagalan administratif; reject adalah kontrol tata kelola untuk mencegah proyek rugi, tidak feasible, atau tidak compliant.')
