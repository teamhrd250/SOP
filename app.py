import streamlit as st
from dataclasses import dataclass
from typing import List, Dict

st.set_page_config(
    page_title="STARCOM SOP Sales to After Sales",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Data model
# -----------------------------
@dataclass
class ProcessStep:
    no: int
    phase: str
    title: str
    owner: str
    owner_group: str
    activities: List[str]
    decision: str
    yes_label: str
    no_label: str
    no_action: str
    no_status: str
    escalation: str
    output: str

STEPS: List[ProcessStep] = [
    ProcessStep(1, "LEAD", "Lead Generation", "Sales", "sales",
                ["Mencari prospek", "Database, inquiry, referensi", "Cold call, email, event, tender"],
                "Lead potensial?", "YA - lanjut kualifikasi", "TIDAK", "REJECT / CLOSE LEAD", "reject",
                "Sales Manager", "Lead tercatat di CRM"),
    ProcessStep(2, "QUALIFICATION", "Lead Qualification", "Sales", "sales",
                ["Kualifikasi BANT", "Budget, Authority, Need, Timeline", "Identifikasi decision maker"],
                "Qualified?", "YA - lanjut assessment", "TIDAK", "REJECT / CLOSE LEAD", "reject",
                "Sales Manager", "Qualified opportunity"),
    ProcessStep(3, "NEED & SURVEY", "Need Assessment & Survey", "Sales + Product Development", "pd",
                ["Meeting customer", "Gali kebutuhan", "Survei lokasi bila perlu", "Kumpulkan data teknis"],
                "Kebutuhan jelas?", "YA - desain solusi", "TIDAK", "REVISE / KLARIFIKASI", "revise",
                "Head of Product Development", "Requirement & survey report"),
    ProcessStep(4, "SOLUTION DESIGN", "Solution Design", "Product Development", "pd",
                ["Analisis teknis", "Desain solusi & arsitektur", "Bill of Material (BoM)", "Estimasi teknis & durasi"],
                "Solusi feasible?", "YA - review internal", "TIDAK", "REVISE SOLUSI / NO-GO", "reject",
                "Head of Product Development", "Technical proposal & BoM"),
    ProcessStep(5, "INTERNAL REVIEW", "Internal Review", "Sales + PD + Finance + Legal + Procurement + Operation", "review",
                ["Review teknis", "Review harga & margin", "Review risiko kontrak", "Review material & lead time", "Review kapasitas tim"],
                "Semua disetujui?", "YA - proposal", "TIDAK", "REVISE / HOLD / REJECT", "hold",
                "Direktur terkait", "Internal approval record"),
    ProcessStep(6, "PROPOSAL", "Proposal & Quotation", "Sales", "sales",
                ["Susun proposal teknis & komersial", "Quotation, timeline, SLA", "Term of payment & warranty"],
                "Disetujui customer?", "YA - negosiasi", "TIDAK", "REVISE PROPOSAL", "revise",
                "Sales Manager", "Submitted proposal"),
    ProcessStep(7, "NEGOTIATION", "Negotiation", "Sales + Legal + PD", "sales",
                ["Negosiasi harga", "Negosiasi SLA & garansi", "Delivery & scope", "Termin pembayaran"],
                "Deal?", "YA - kontrak / PO", "TIDAK", "NEGOSIASI LANJUT / LOST", "lost",
                "Commercial Director", "Negotiation minutes"),
    ProcessStep(8, "CONTRACT / PO", "Contract & PO Review", "Legal + Finance", "legal",
                ["Review kontrak / PO", "Negosiasi klausul", "Validasi termin pembayaran", "Persetujuan tanda tangan"],
                "PO / Kontrak OK?", "YA - kick off", "TIDAK", "REVISE KONTRAK / REJECT", "reject",
                "Legal Manager / Director", "Signed contract / accepted PO"),
    ProcessStep(9, "PROJECT KICK OFF", "Kick Off Internal", "Operation / Project", "operation",
                ["Handover Sales ke Project", "Kick off meeting internal", "Project plan & timeline", "Risk register"],
                "Kick off complete?", "YA - procurement", "TIDAK", "PENYESUAIAN RENCANA", "revise",
                "Project Manager", "Approved project plan"),
    ProcessStep(10, "PROCUREMENT", "Procurement & Logistics", "Procurement", "procurement",
                ["Pengadaan barang & jasa", "Seleksi vendor", "Monitoring lead time", "Pengiriman material"],
                "Material ready?", "YA - implementasi", "TIDAK", "ALTERNATIF / RESCHEDULE", "hold",
                "Procurement Manager", "Material readiness confirmation"),
    ProcessStep(11, "IMPLEMENTATION", "Implementation", "Operation / Project", "operation",
                ["Instalasi", "Konfigurasi", "Integrasi sistem", "Progress reporting"],
                "On track?", "YA - testing", "TIDAK", "TINDAKAN PERBAIKAN", "escalate",
                "Project Manager / Operation Manager", "Installed & configured solution"),
    ProcessStep(12, "TESTING", "Testing & Commissioning", "PD + Operation", "pd",
                ["FAT", "SAT", "UAT", "Dokumentasi hasil test"],
                "Testing lulus?", "YA - BAST", "TIDAK", "TROUBLESHOOTING & RETEST", "revise",
                "PD Manager", "Signed test report"),
    ProcessStep(13, "ACCEPTANCE", "BAST / Acceptance", "Operation + Customer", "operation",
                ["Serah terima pekerjaan", "BAST ditandatangani", "Dokumentasi final", "Punch list bila ada"],
                "Customer approve?", "YA - invoice", "TIDAK", "PUNCH LIST", "revise",
                "Project Manager", "BAST / acceptance document"),
    ProcessStep(14, "INVOICE", "Invoice", "Finance", "finance",
                ["Penerbitan invoice", "Faktur pajak", "Kirim ke customer", "Verifikasi dokumen pendukung"],
                "Invoice accepted?", "YA - collection", "TIDAK", "REVISI INVOICE", "revise",
                "Finance Manager", "Accepted invoice"),
    ProcessStep(15, "PAYMENT", "Payment & Collection", "Finance", "finance",
                ["Monitoring pembayaran", "Reminder / collection", "Rekonsiliasi", "Aging review"],
                "Pembayaran lunas?", "YA - after sales", "TIDAK", "COLLECTION & ESKALASI", "escalate",
                "Finance Manager / Director", "Payment confirmation"),
    ProcessStep(16, "AFTER SALES", "After Sales / Support", "After Sales", "aftersales",
                ["Warranty support", "Preventive maintenance", "Corrective maintenance", "Helpdesk & ticketing"],
                "Ada complaint?", "TIDAK - lanjut survey", "YA", "RCA & CORRECTIVE ACTION", "escalate",
                "After Sales Manager", "Closed ticket / service report"),
    ProcessStep(17, "SATISFACTION", "Customer Satisfaction", "After Sales + Sales", "aftersales",
                ["Survey kepuasan", "Evaluasi SLA & kualitas", "Review performa proyek", "Action plan"],
                "Customer puas?", "YA - repeat order", "TIDAK", "ACTION PLAN", "escalate",
                "Director / Account Manager", "Customer satisfaction score"),
    ProcessStep(18, "REPEAT & GROWTH", "Repeat Order / Upselling", "Sales", "sales",
                ["Identifikasi kebutuhan baru", "Upselling / cross selling", "Perpanjangan kontrak", "Account development"],
                "Peluang baru?", "YA - kembali ke qualification", "TIDAK", "MAINTAIN RELATIONSHIP", "hold",
                "Sales Manager", "Repeat order / long-term partnership"),
]

DEPT_SCOPE: Dict[str, List[str]] = {
    "Sales": ["Lead generation", "Kualifikasi lead", "Hubungan pelanggan", "Proposal komersial", "Negosiasi", "Repeat order"],
    "Product Development": ["Need assessment teknis", "Survey", "Solution design", "BoM", "Proposal teknis", "Testing support"],
    "Finance": ["Margin & cashflow review", "Termin pembayaran", "Invoice", "Collection", "Rekonsiliasi"],
    "Legal": ["NDA", "Review kontrak/PO", "Negosiasi klausul", "Mitigasi risiko", "Compliance"],
    "Procurement": ["Vendor sourcing", "Pengadaan", "Lead time", "Logistik", "Material readiness"],
    "Operation / Project": ["Kick off", "Project planning", "Implementasi", "Monitoring", "BAST"],
    "After Sales": ["Helpdesk", "Warranty", "Maintenance", "Complaint", "Customer satisfaction"],
}

STATUS_STYLE = {
    "go": ("#1f9d55", "GO / APPROVE"),
    "revise": ("#f59e0b", "REVISE"),
    "hold": ("#f0ad4e", "HOLD / RESCHEDULE"),
    "reject": ("#dc2626", "REJECT / NO-GO"),
    "lost": ("#be123c", "LOST"),
    "escalate": ("#7c3aed", "ESCALATE"),
}

# -----------------------------
# CSS
# -----------------------------
st.markdown("""
<style>
:root {
  --navy:#08233a; --blue:#1269b0; --line:#d8e3ef; --text:#0f2740;
  --sales:#e8f1ff; --pd:#f1eaff; --finance:#e8f8ea; --legal:#f2ebff;
  --proc:#fff1df; --ops:#e7f7f8; --after:#e8fbf8; --review:#eef2f7;
}
[data-testid="stAppViewContainer"] {background:#f4f8fc;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#061b2c 0%,#0b3454 100%);}
[data-testid="stSidebar"] * {color:white;}
.block-container {max-width:1500px;padding-top:1.2rem;padding-bottom:3rem;}
.hero {background:linear-gradient(100deg,#071d31,#1275b4);padding:26px 32px;border-radius:0 0 26px 26px;color:white;margin-bottom:18px;box-shadow:0 16px 40px rgba(4,34,58,.18)}
.hero h1 {margin:0;font-size:34px}.hero p{margin:10px 0 0;font-size:16px}
.kpi {background:white;border:1px solid #dce7f1;border-radius:16px;padding:18px;box-shadow:0 6px 18px rgba(11,50,80,.06)}
.kpi .n {font-size:30px;font-weight:800;color:#0d2a45}.kpi .l{font-size:12px;color:#63809b;letter-spacing:.08em}
.flow-head {display:grid;grid-template-columns:70px 230px 1fr 250px 280px;gap:12px;padding:12px 16px;background:#f9fbfd;border:1px solid var(--line);border-radius:14px 14px 0 0;font-weight:800;color:#173652;position:sticky;top:0;z-index:5}
.flow-row {display:grid;grid-template-columns:70px 230px 1fr 250px 280px;gap:12px;align-items:stretch;padding:14px 16px;background:white;border-left:1px solid var(--line);border-right:1px solid var(--line);border-bottom:1px solid var(--line)}
.flow-row:last-child{border-radius:0 0 14px 14px}
.phase {display:flex;flex-direction:column;align-items:center;justify-content:center;background:#edf5ff;border:1px solid #bdd7f5;border-radius:12px;padding:8px;text-align:center;min-height:125px}.phase .num{font-size:24px;font-weight:900;color:#145da0}.phase .txt{font-size:10px;font-weight:800;color:#274b6d}
.owner-card {border-radius:12px;padding:14px;border:1px solid #c7d9ef;min-height:125px}.owner-title{font-weight:850;font-size:16px;color:#0f3d6d}.owner-name{font-size:13px;margin-top:6px;color:#355b7a}.owner-sales{background:var(--sales)}.owner-pd{background:var(--pd)}.owner-finance{background:var(--finance)}.owner-legal{background:var(--legal)}.owner-procurement{background:var(--proc)}.owner-operation{background:var(--ops)}.owner-aftersales{background:var(--after)}.owner-review{background:var(--review)}
.activities {background:#fbfcfe;border:1px solid #e1e8f0;border-radius:12px;padding:12px 15px;min-height:125px}.activities ul{padding-left:18px;margin:0}.activities li{margin:5px 0;font-size:13px;color:#253f58}
.decision-wrap{display:flex;align-items:center;justify-content:center;min-height:125px}.diamond{width:145px;height:92px;background:#f7faff;border:2px solid #5b8fd1;transform:rotate(45deg);display:flex;align-items:center;justify-content:center;box-shadow:0 5px 14px rgba(38,89,140,.08)}.diamond span{transform:rotate(-45deg);font-weight:800;font-size:12px;text-align:center;color:#173d65;width:105px}
.action-card{border-radius:12px;padding:12px 14px;min-height:125px;border:1px solid #e1e8f0;background:#fff}.action-title{font-weight:900;font-size:14px}.badge{display:inline-block;padding:4px 8px;border-radius:999px;color:white;font-size:10px;font-weight:900;margin-bottom:8px}.action-card p{font-size:12px;margin:5px 0;color:#3d5368}.go-box{background:#ecf9ef;border:1px solid #a8d9b3}.bad-box{background:#fff4e8;border:1px solid #f5c07a}.reject-box{background:#fff0f0;border:1px solid #f1a4a4}
.side-panel {background:white;border:1px solid #dce7f1;border-radius:16px;padding:18px;position:sticky;top:15px}.note{padding:11px 13px;border-radius:10px;margin:8px 0;font-size:13px}.note.info{background:#eaf4ff;border-left:4px solid #2185d0}.note.warn{background:#fff6df;border-left:4px solid #f0a000}.note.danger{background:#ffeded;border-left:4px solid #d72c2c}.note.ok{background:#eaf8ef;border-left:4px solid #209b50}
.legend-pill{display:inline-block;padding:7px 10px;border:1px solid #d5e1ed;border-radius:999px;background:#fff;margin:4px;font-size:12px}
.small-muted{font-size:12px;color:#6c8297}
@media (max-width:1100px){.flow-head,.flow-row{grid-template-columns:58px 200px 1fr}.decision-wrap,.action-card{grid-column:2/4}.flow-head div:nth-child(4),.flow-head div:nth-child(5){display:none}}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown("## 📡 STARCOM SOP")
    st.caption("Telecommunication & IT System Integrator")
    page = st.radio("Navigation", [
        "Executive Flow", "Department Authority", "Process Detail", "Decision Gates", "RACI Matrix", "Presentation Mode"
    ], index=0)
    st.markdown("---")
    st.markdown("### Legend")
    st.markdown("🟢 GO / APPROVE  ")
    st.markdown("🟠 REVISE  ")
    st.markdown("🟡 HOLD / RESCHEDULE  ")
    st.markdown("🔴 REJECT / NO-GO  ")
    st.markdown("🟣 ESCALATE")
    st.markdown("---")
    st.caption("Standalone edition — tanpa Excel atau file data eksternal.")

# -----------------------------
# Header
# -----------------------------
st.markdown("""
<div class="hero">
  <h1>SOP Sales → Delivery → After Sales</h1>
  <p>Flow vertikal end-to-end dengan kewenangan departemen, decision gate, hasil Go / Revise / Hold / Reject, dan jalur eskalasi.</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Helpers
# -----------------------------
def owner_class(group: str) -> str:
    return f"owner-{group}"

def render_step(step: ProcessStep):
    status_color, status_label = STATUS_STYLE.get(step.no_status, ("#f59e0b", step.no_status.upper()))
    action_class = "reject-box" if step.no_status in ["reject", "lost"] else "bad-box"
    acts = "".join(f"<li>{a}</li>" for a in step.activities)
    html = f"""
    <div class="flow-row">
      <div class="phase"><div class="num">{step.no}</div><div class="txt">{step.phase}</div></div>
      <div class="owner-card {owner_class(step.owner_group)}">
        <div class="owner-title">{step.title}</div>
        <div class="owner-name"><b>Owner:</b> {step.owner}</div>
        <div class="owner-name"><b>Output:</b> {step.output}</div>
      </div>
      <div class="activities"><ul>{acts}</ul></div>
      <div class="decision-wrap"><div class="diamond"><span>{step.decision}</span></div></div>
      <div class="action-card {action_class}">
        <span class="badge" style="background:{status_color}">{status_label}</span>
        <div class="action-title">{step.no_action}</div>
        <p><b>Jika YA:</b> {step.yes_label}</p>
        <p><b>Jika TIDAK / masalah:</b> {step.no_label}</p>
        <p><b>Eskalasi:</b> {step.escalation}</p>
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# -----------------------------
# Pages
# -----------------------------
if page in ["Executive Flow", "Presentation Mode"]:
    k1,k2,k3,k4 = st.columns(4)
    for col, n, label in [(k1,18,"CONTROLLED PROCESSES"),(k2,7,"OWNER GROUPS"),(k3,18,"DECISION GATES"),(k4,6,"OUTCOME TYPES")]:
        with col:
            st.markdown(f'<div class="kpi"><div class="n">{n}</div><div class="l">{label}</div></div>', unsafe_allow_html=True)

    st.markdown("### Flowchart Vertikal")
    left, right = st.columns([4.7,1.3], gap="large")
    with left:
        st.markdown("""
        <div class="flow-head">
          <div>TAHAP</div><div>PROSES / OWNER</div><div>KEGIATAN UTAMA</div><div>DECISION GATE</div><div>HASIL & TINDAKAN</div>
        </div>
        """, unsafe_allow_html=True)
        for step in STEPS:
            render_step(step)

    with right:
        st.markdown('<div class="side-panel">', unsafe_allow_html=True)
        st.markdown("#### Panel Pilihan & Notifikasi")
        selected = st.selectbox("Pilih proses", [f"{s.no}. {s.title}" for s in STEPS])
        chosen = STEPS[[f"{s.no}. {s.title}" for s in STEPS].index(selected)]
        result = st.radio("Status keputusan", ["GO / APPROVE", "REVISE", "HOLD", "REJECT / NO-GO", "ESCALATE"], index=0)
        note = st.text_area("Catatan keputusan", placeholder="Tulis alasan, kendala, atau instruksi tindak lanjut...")
        if st.button("Simpan simulasi keputusan", use_container_width=True):
            if result == "GO / APPROVE":
                st.success(f"{chosen.title}: proses dinyatakan lolos dan dapat dilanjutkan.")
            elif result == "REVISE":
                st.warning(f"{chosen.title}: perlu revisi sebelum dilanjutkan.")
            elif result == "HOLD":
                st.info(f"{chosen.title}: ditahan sementara / reschedule.")
            elif result == "REJECT / NO-GO":
                st.error(f"{chosen.title}: ditolak / no-go. Eskalasi ke {chosen.escalation}.")
            else:
                st.warning(f"{chosen.title}: wajib dieskalasikan ke {chosen.escalation}.")
            if note:
                st.caption(f"Catatan: {note}")

        st.markdown("#### Notifikasi Otomatis")
        st.markdown('<div class="note info">Setiap decision gate wajib memiliki bukti keputusan.</div>', unsafe_allow_html=True)
        st.markdown('<div class="note warn">Status Revise/Hold harus memiliki PIC dan target penyelesaian.</div>', unsafe_allow_html=True)
        st.markdown('<div class="note danger">Status Reject/No-Go wajib mencantumkan alasan dan level approval.</div>', unsafe_allow_html=True)
        st.markdown('<div class="note ok">Status Go hanya berlaku bila dokumen output telah lengkap.</div>', unsafe_allow_html=True)
        st.markdown("#### Filter Presentasi")
        st.checkbox("Tampilkan hanya proses bermasalah")
        st.checkbox("Sorot proses Product Development")
        st.checkbox("Sorot proses dengan eskalasi Direksi")
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "Department Authority":
    st.subheader("Department Authority")
    cols = st.columns(2)
    for i,(dept, scopes) in enumerate(DEPT_SCOPE.items()):
        with cols[i%2]:
            st.markdown(f"### {dept}")
            for scope in scopes:
                st.markdown(f"- {scope}")
            st.markdown("---")

elif page == "Process Detail":
    st.subheader("Process Detail")
    selected = st.selectbox("Pilih proses", [f"{s.no}. {s.title}" for s in STEPS])
    s = STEPS[[f"{s.no}. {s.title}" for s in STEPS].index(selected)]
    c1,c2 = st.columns(2)
    with c1:
        st.markdown(f"**Owner:** {s.owner}")
        st.markdown(f"**Phase:** {s.phase}")
        st.markdown(f"**Output:** {s.output}")
        st.markdown("**Aktivitas utama:**")
        for a in s.activities: st.markdown(f"- {a}")
    with c2:
        st.markdown(f"**Decision gate:** {s.decision}")
        st.success(s.yes_label)
        st.warning(s.no_action)
        st.markdown(f"**Eskalasi:** {s.escalation}")

elif page == "Decision Gates":
    st.subheader("Decision Gate Register")
    rows = []
    for s in STEPS:
        rows.append({"No":s.no,"Process":s.title,"Owner":s.owner,"Decision Gate":s.decision,"If Go":s.yes_label,"If Issue":s.no_action,"Status Type":STATUS_STYLE[s.no_status][1],"Escalation":s.escalation})
    st.dataframe(rows, use_container_width=True, hide_index=True)

elif page == "RACI Matrix":
    st.subheader("RACI Matrix")
    raci = [
        {"Process":"Lead Generation","Sales":"R/A","PD":"I","Finance":"I","Legal":"I","Procurement":"I","Operation":"I","After Sales":"I"},
        {"Process":"Need Assessment","Sales":"A","PD":"R","Finance":"I","Legal":"I","Procurement":"I","Operation":"C","After Sales":"I"},
        {"Process":"Solution Design","Sales":"C","PD":"R/A","Finance":"C","Legal":"I","Procurement":"C","Operation":"C","After Sales":"I"},
        {"Process":"Internal Review","Sales":"R","PD":"R","Finance":"R","Legal":"R","Procurement":"R","Operation":"R","After Sales":"I"},
        {"Process":"Contract / PO","Sales":"C","PD":"I","Finance":"R","Legal":"R/A","Procurement":"I","Operation":"I","After Sales":"I"},
        {"Process":"Implementation","Sales":"I","PD":"C","Finance":"I","Legal":"I","Procurement":"C","Operation":"R/A","After Sales":"I"},
        {"Process":"Testing","Sales":"I","PD":"R","Finance":"I","Legal":"I","Procurement":"I","Operation":"R/A","After Sales":"I"},
        {"Process":"After Sales","Sales":"C","PD":"C","Finance":"I","Legal":"I","Procurement":"I","Operation":"C","After Sales":"R/A"},
    ]
    st.dataframe(raci, use_container_width=True, hide_index=True)
