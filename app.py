import streamlit as st
from dataclasses import dataclass
from typing import List

st.set_page_config(
    page_title="STARCOM SOP Swimlane",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

@dataclass
class Step:
    no: int
    phase: str
    title: str
    owner: str
    support: str
    activities: List[str]
    decision: str
    go: str
    issue: str
    status: str
    escalation: str
    output: str

STEPS = [
    Step(1,"LEAD","Lead Generation","Sales","-",["Mencari prospek","Database, inquiry, referensi","Cold call, email, event, tender"],"Lead potensial?","Lanjut ke kualifikasi","Close lead di CRM","REJECT","Sales Manager","Lead tercatat di CRM"),
    Step(2,"QUALIFICATION","Lead Qualification","Sales","Product Development",["Kualifikasi BANT","Validasi budget dan authority","Identifikasi kebutuhan dan timeline"],"Qualified?","Lanjut need assessment","Close / nurture lead","REJECT","Sales Manager","Qualified opportunity"),
    Step(3,"NEED & SURVEY","Need Assessment & Survey","Product Development","Sales, Operation",["Meeting customer","Gali kebutuhan bisnis dan teknis","Site survey bila diperlukan","Dokumentasikan requirement"],"Kebutuhan jelas?","Lanjut desain solusi","Klarifikasi / survey ulang","REVISE","Head of Product Development","Requirement dan survey report"),
    Step(4,"SOLUTION","Solution Design","Product Development","Operation, Procurement",["Desain arsitektur solusi","Penyusunan BoM","Estimasi durasi dan resource","Validasi kompatibilitas"],"Solusi feasible?","Lanjut internal review","Revisi solusi; jika tetap tidak feasible: No-Go","REVISE / REJECT","Head of Product Development","Technical proposal dan BoM"),
    Step(5,"REVIEW","Internal Review","Management","Sales, PD, Finance, Legal, Procurement, Operation",["Review teknis dan kapasitas","Review harga, margin, cashflow","Review kontrak dan risiko","Review material dan lead time"],"Semua disetujui?","Lanjut proposal","Revisi, hold, atau reject sesuai temuan","HOLD / REJECT","Direktur terkait","Internal approval record"),
    Step(6,"PROPOSAL","Proposal & Quotation","Sales","PD, Finance, Legal",["Susun proposal teknis-komersial","Quotation, timeline, SLA","Term of payment dan warranty"],"Proposal diterima?","Lanjut negosiasi","Revisi proposal / klarifikasi","REVISE","Sales Manager","Submitted proposal"),
    Step(7,"NEGOTIATION","Negotiation","Sales","Legal, PD, Finance",["Negosiasi harga dan ruang lingkup","Negosiasi SLA dan garansi","Finalisasi delivery dan termin"],"Deal?","Lanjut kontrak / PO","Negosiasi lanjut atau opportunity lost","LOST","Commercial Director","Negotiation minutes"),
    Step(8,"CONTRACT","Contract & PO Review","Legal","Finance, Sales",["Review kontrak / PO","Negosiasi klausul","Validasi termin pembayaran","Approval tanda tangan"],"Kontrak / PO acceptable?","Lanjut kick off","Revisi klausul atau reject","REVISE / REJECT","Legal Manager / Director","Signed contract / accepted PO"),
    Step(9,"KICK OFF","Project Kick Off","Operation","Sales, PD, Procurement, Finance",["Handover Sales ke Project","Kick off meeting","Project plan, timeline, risk register","Penetapan PIC"],"Kick off lengkap?","Lanjut procurement","Lengkapi data / revisi rencana","REVISE","Project Manager","Approved project plan"),
    Step(10,"PROCUREMENT","Procurement & Logistics","Procurement","PD, Operation, Finance",["Pengadaan barang dan jasa","Seleksi vendor","Monitoring lead time","Pengiriman material"],"Material ready?","Lanjut implementasi","Vendor alternatif / reschedule","HOLD","Procurement Manager","Material readiness confirmation"),
    Step(11,"IMPLEMENTATION","Implementation","Operation","PD, HSE, Procurement",["Instalasi","Konfigurasi","Integrasi sistem","Progress report dan quality control"],"On track?","Lanjut testing","Corrective plan dan eskalasi","ESCALATE","Project / Operation Manager","Installed solution"),
    Step(12,"TESTING","Testing & Commissioning","Product Development","Operation, Customer",["FAT","SAT","UAT","Dokumentasi hasil pengujian"],"Testing lulus?","Lanjut acceptance","Troubleshooting dan retest","REVISE","PD Manager","Signed test report"),
    Step(13,"ACCEPTANCE","BAST / Acceptance","Operation","Customer, Sales, Legal",["Serah terima pekerjaan","Penyelesaian punch list","Dokumentasi final","Tanda tangan BAST"],"Customer approve?","Lanjut invoice","Punch list dan verifikasi ulang","REVISE","Project Manager","BAST / acceptance document"),
    Step(14,"INVOICE","Invoice","Finance","Operation, Sales",["Verifikasi dokumen pendukung","Penerbitan invoice dan faktur pajak","Pengiriman invoice ke customer"],"Invoice accepted?","Lanjut collection","Perbaiki invoice / dokumen","REVISE","Finance Manager","Accepted invoice"),
    Step(15,"PAYMENT","Payment & Collection","Finance","Sales, Management",["Monitoring jatuh tempo","Reminder dan collection","Rekonsiliasi pembayaran","Aging review"],"Pembayaran lunas?","Lanjut after sales","Collection dan eskalasi","ESCALATE","Finance Manager / Director","Payment confirmation"),
    Step(16,"AFTER SALES","Warranty & Support","After Sales","PD, Operation",["Helpdesk dan ticketing","Warranty support","Preventive maintenance","Corrective maintenance"],"Ada complaint?","Jika tidak: survey kepuasan","RCA, corrective action, close ticket","ESCALATE","After Sales Manager","Closed ticket / service report"),
    Step(17,"SATISFACTION","Customer Satisfaction","After Sales","Sales, Management",["Survey kepuasan","Evaluasi SLA dan kualitas","Review performa proyek","Susun improvement plan"],"Customer puas?","Lanjut repeat order","Action plan dan management review","ESCALATE","Director / Account Manager","Customer satisfaction score"),
    Step(18,"GROWTH","Repeat Order / Upselling","Sales","PD, After Sales",["Identifikasi kebutuhan baru","Upselling / cross selling","Renewal kontrak","Account development"],"Ada peluang baru?","Kembali ke qualification","Maintain relationship","HOLD","Sales Manager","Repeat order / partnership"),
]

LANES = ["Sales","Product Development","Finance","Legal","Procurement","Operation","After Sales","Management"]
STATUS_COLOR = {
    "REJECT":"#dc2626", "REVISE":"#f59e0b", "REVISE / REJECT":"#ef4444",
    "HOLD / REJECT":"#d97706", "LOST":"#be123c", "HOLD":"#ca8a04", "ESCALATE":"#7c3aed"
}
LANE_CLASS = {
    "Sales":"sales", "Product Development":"pd", "Finance":"finance", "Legal":"legal",
    "Procurement":"proc", "Operation":"ops", "After Sales":"after", "Management":"mgmt"
}

st.markdown("""
<style>
:root{--navy:#08233a;--line:#cbd8e5;--bg:#eef4f9;--text:#102c46}
[data-testid="stAppViewContainer"]{background:var(--bg)}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#061a2b,#0b3556)}
[data-testid="stSidebar"] *{color:white}
.block-container{max-width:1900px;padding-top:.7rem;padding-bottom:3rem}
.hero{background:linear-gradient(100deg,#071d31,#1477b4);color:white;padding:24px 30px;border-radius:0 0 24px 24px;box-shadow:0 14px 34px rgba(8,35,58,.18);margin-bottom:18px}
.hero h1{margin:0;font-size:34px}.hero p{margin:8px 0 0;font-size:15px}
.kpi{background:white;border:1px solid #d8e3ed;border-radius:14px;padding:15px;box-shadow:0 5px 14px rgba(8,35,58,.06)}
.kpi b{font-size:25px;color:#0c3151}.kpi span{display:block;font-size:11px;color:#668096;letter-spacing:.06em}
.swim-wrap{overflow-x:auto;background:white;border:1px solid var(--line);border-radius:16px;box-shadow:0 8px 24px rgba(8,35,58,.08)}
.swim{min-width:1700px}
.swim-head,.swim-row{display:grid;grid-template-columns:82px repeat(8,1fr) 430px}
.swim-head{position:sticky;top:0;z-index:10;background:#0b2d49;color:white;font-weight:800}
.swim-head>div{padding:13px 8px;text-align:center;border-right:1px solid #31516b;font-size:12px}
.swim-row{position:relative;min-height:190px;border-top:1px solid var(--line)}
.swim-row>div{border-right:1px solid var(--line);padding:10px;min-width:0}
.stepno{background:#edf5fd;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.stepno strong{font-size:25px;color:#145e9c}.stepno span{font-size:9px;font-weight:800;color:#41627e;margin-top:5px}
.lane-cell{background:#fafcfe;position:relative}
.lane-cell.owner{background:#f7fbff}
.process-card{height:100%;border-radius:11px;padding:12px;border:1px solid #bcd0e3;box-shadow:0 3px 10px rgba(13,53,83,.06);display:flex;flex-direction:column;justify-content:center}
.process-card h4{margin:0 0 6px;font-size:14px}.process-card p{font-size:11px;margin:3px 0;color:#38546d}.process-card ul{margin:5px 0 0;padding-left:17px}.process-card li{font-size:11px;margin:3px 0;color:#29465f}
.sales{background:#e8f1ff;border-color:#9ec2ee}.pd{background:#f1eaff;border-color:#c3a8eb}.finance{background:#e8f8ea;border-color:#a7d5ac}.legal{background:#f3ebff;border-color:#c7acec}.proc{background:#fff1df;border-color:#efc180}.ops{background:#e5f7f8;border-color:#9ed5da}.after{background:#e8fbf8;border-color:#9ddbd3}.mgmt{background:#fff3d9;border-color:#e8c66e}
.support-tag{display:inline-block;background:white;border:1px solid #cbd8e5;border-radius:999px;padding:3px 7px;font-size:9px;margin-top:5px;color:#526d83}
.decision-cell{background:#f9fbfd;display:grid;grid-template-columns:105px 1fr;gap:10px;align-items:center}
.diamond-wrap{display:flex;align-items:center;justify-content:center}.diamond{width:76px;height:76px;transform:rotate(45deg);border:2px solid #5c8cc3;background:#f3f8fe;display:flex;align-items:center;justify-content:center}.diamond span{transform:rotate(-45deg);font-size:9px;font-weight:800;text-align:center;width:68px;color:#173d61}
.result{font-size:11px}.go{background:#e8f7ec;border-left:4px solid #22a35a;padding:8px;border-radius:8px;margin-bottom:7px}.bad{background:#fff0e7;border-left:4px solid #ea6a1f;padding:8px;border-radius:8px}.status{display:inline-block;color:white;font-size:9px;font-weight:900;padding:3px 7px;border-radius:999px;margin-bottom:4px}.escalate{margin-top:6px;background:#eef0ff;border:1px dashed #6875d6;padding:5px;border-radius:6px;color:#39468c;font-size:9px}
.down-arrow{text-align:center;font-size:22px;color:#3f7bad;line-height:22px;margin:-2px 0}
.panel{background:white;border:1px solid #d7e3ee;border-radius:15px;padding:17px;position:sticky;top:12px;box-shadow:0 6px 20px rgba(8,35,58,.07)}
.note{padding:10px 12px;border-radius:9px;margin:8px 0;font-size:12px}.info{background:#eaf4ff;border-left:4px solid #2383d0}.warn{background:#fff5df;border-left:4px solid #e99b00}.danger{background:#ffeded;border-left:4px solid #db3030}.ok{background:#eaf8ef;border-left:4px solid #1e9b50}
@media(max-width:900px){.swim{min-width:1500px}.block-container{padding-left:.5rem;padding-right:.5rem}}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 📡 STARCOM SOP")
    st.caption("Telecommunication & IT System Integrator")
    page = st.radio("Navigation",["Swimlane SOP","Process Detail","Department Authority","Decision Register"],index=0)
    st.markdown("---")
    st.markdown("### Status")
    st.markdown("🟢 GO / APPROVE")
    st.markdown("🟠 REVISE")
    st.markdown("🟡 HOLD")
    st.markdown("🔴 REJECT / LOST")
    st.markdown("🟣 ESCALATE")
    st.markdown("---")
    st.caption("Standalone: tidak memerlukan Excel atau file eksternal.")

st.markdown("""
<div class="hero"><h1>SOP Sales → Delivery → After Sales</h1>
<p>Swimlane vertikal berdasarkan kewenangan departemen, dengan decision gate, status, tindakan koreksi, dan jalur eskalasi.</p></div>
""", unsafe_allow_html=True)


def render_swimlane():
    st.markdown('<div class="swim-wrap"><div class="swim">',unsafe_allow_html=True)
    head = '<div class="swim-head"><div>TAHAP</div>' + ''.join(f'<div>{x}</div>' for x in LANES) + '<div>DECISION & NOTIFICATION</div></div>'
    st.markdown(head,unsafe_allow_html=True)
    for i,s in enumerate(STEPS):
        cells=[]
        cells.append(f'<div class="stepno"><strong>{s.no}</strong><span>{s.phase}</span></div>')
        for lane in LANES:
            if lane==s.owner:
                acts=''.join(f'<li>{a}</li>' for a in s.activities)
                cls=LANE_CLASS[lane]
                cells.append(f'''<div class="lane-cell owner"><div class="process-card {cls}">
                    <h4>{s.title}</h4><p><b>Owner:</b> {s.owner}</p><ul>{acts}</ul>
                    <p><b>Output:</b> {s.output}</p><span class="support-tag">Support: {s.support}</span></div></div>''')
            else:
                cells.append('<div class="lane-cell"></div>')
        color=STATUS_COLOR.get(s.status,"#f59e0b")
        cells.append(f'''<div class="decision-cell"><div class="diamond-wrap"><div class="diamond"><span>{s.decision}</span></div></div>
            <div class="result"><div class="go"><b>✓ GO / LOLOS</b><br>{s.go}</div>
            <div class="bad"><span class="status" style="background:{color}">NO-GO: {s.status}</span><br><b>Solusi / tindakan:</b> {s.issue}
            <div class="escalate">🔔 Eskalasi: {s.escalation}</div></div></div></div>''')
        st.markdown('<div class="swim-row">'+''.join(cells)+'</div>',unsafe_allow_html=True)
        if i < len(STEPS)-1:
            st.markdown('<div class="down-arrow">↓</div>',unsafe_allow_html=True)
    st.markdown('</div></div>',unsafe_allow_html=True)

if page=="Swimlane SOP":
    c1,c2,c3,c4=st.columns(4)
    for c,n,l in [(c1,18,"CONTROLLED PROCESSES"),(c2,8,"DEPARTMENT LANES"),(c3,18,"DECISION GATES"),(c4,5,"OUTCOME TYPES")]:
        with c: st.markdown(f'<div class="kpi"><b>{n}</b><span>{l}</span></div>',unsafe_allow_html=True)
    st.markdown("### Swimlane End-to-End")
    st.info("Alur utama bergerak dari atas ke bawah. Pada setiap decision gate, jalur GO menuju proses berikutnya, sedangkan jalur NO-GO langsung menunjukkan solusi, tindakan koreksi, dan tujuan eskalasi.")
    render_swimlane()

elif page=="Process Detail":
    labels=[f"{s.no}. {s.title}" for s in STEPS]
    selected=st.selectbox("Pilih proses",labels)
    s=STEPS[labels.index(selected)]
    a,b=st.columns(2)
    with a:
        st.subheader(s.title)
        st.write("**Tahap:**",s.phase)
        st.write("**Owner:**",s.owner)
        st.write("**Support:**",s.support)
        st.write("**Output:**",s.output)
        st.write("**Aktivitas:**")
        for x in s.activities: st.write("•",x)
    with b:
        st.subheader("Decision Control")
        st.write("**Decision gate:**",s.decision)
        st.success(s.go)
        st.error(s.issue)
        st.write("**Status masalah:**",s.status)
        st.write("**Eskalasi:**",s.escalation)

elif page=="Department Authority":
    for lane in LANES:
        owned=[s for s in STEPS if s.owner==lane]
        with st.expander(f"{lane} — {len(owned)} proses",expanded=True):
            for s in owned:
                st.markdown(f"**{s.no}. {s.title}** — {s.output}")

else:
    rows=[]
    for s in STEPS:
        rows.append({"No":s.no,"Proses":s.title,"Owner":s.owner,"Decision Gate":s.decision,"Go":s.go,"Masalah":s.issue,"Status":s.status,"Eskalasi":s.escalation})
    st.dataframe(rows,use_container_width=True,hide_index=True)
