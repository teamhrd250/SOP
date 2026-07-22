import json
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="STARCOM SOP | Sales to After Sales",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Core data
# -----------------------------
DEPARTMENTS = {
    "Sales": {"color": "#2F80ED", "soft": "#EAF3FF", "icon": "◆"},
    "Product Development": {"color": "#7B61FF", "soft": "#F1EDFF", "icon": "◇"},
    "Finance": {"color": "#27AE60", "soft": "#EAF8EF", "icon": "●"},
    "Legal": {"color": "#8E5CC7", "soft": "#F4EDFA", "icon": "■"},
    "Procurement": {"color": "#F2994A", "soft": "#FFF3E7", "icon": "▲"},
    "Operation": {"color": "#25A8B8", "soft": "#E8F8FA", "icon": "✦"},
    "After Sales": {"color": "#EB5757", "soft": "#FDEEEE", "icon": "●"},
    "Management": {"color": "#D6A11D", "soft": "#FFF8DE", "icon": "◆"},
}

PROCESSES = [
    {
        "id": 1, "stage": "LEAD", "name": "Lead Generation", "owner": "Sales",
        "activity": "Mencari prospek, referensi, tender, event, dan informasi awal pelanggan.",
        "gate": "Lead potensial?", "go": "Lanjut ke Lead Qualification",
        "nogo": "REJECT / CLOSE LEAD", "solution": "Lead tidak sesuai target pasar; dokumentasikan alasan dan tutup di CRM.",
        "escalation": "Sales Manager", "output": "Lead register dan customer profile awal",
        "documents": "Lead register, call note, customer profile", "sla": "1 hari kerja",
        "kpi": "Jumlah lead baru dan lead response rate", "risk": "Lead tidak relevan atau data tidak valid",
    },
    {
        "id": 2, "stage": "QUALIFICATION", "name": "Lead Qualification", "owner": "Sales",
        "activity": "Kualifikasi BANT: budget, authority, need, timeline, serta identifikasi decision maker.",
        "gate": "Qualified?", "go": "Lanjut ke Need Assessment",
        "nogo": "REJECT / NURTURE", "solution": "Tidak memenuhi kriteria; masukkan nurture list atau close opportunity.",
        "escalation": "Sales Manager", "output": "Qualified opportunity",
        "documents": "Qualification checklist, CRM opportunity", "sla": "2 hari kerja",
        "kpi": "Lead-to-opportunity conversion", "risk": "Opportunity semu atau tidak memiliki budget",
    },
    {
        "id": 3, "stage": "NEED & SURVEY", "name": "Need Assessment & Survey", "owner": "Product Development",
        "activity": "Meeting pelanggan, gali kebutuhan, survei lokasi bila perlu, dan kumpulkan data teknis.",
        "gate": "Kebutuhan jelas?", "go": "Lanjut ke Solution Design",
        "nogo": "REVISE / KLARIFIKASI", "solution": "Lengkapi data, lakukan klarifikasi, atau survei ulang bersama Sales.",
        "escalation": "Sales Manager / Product Manager", "output": "Customer requirement dan survey report",
        "documents": "MoM, requirement form, survey report", "sla": "3 hari kerja",
        "kpi": "Kelengkapan requirement dan ketepatan survey", "risk": "Requirement ambigu atau kondisi lapangan tidak lengkap",
    },
    {
        "id": 4, "stage": "SOLUTION DESIGN", "name": "Solution Design", "owner": "Product Development",
        "activity": "Analisis teknis, arsitektur solusi, BoM/BoQ, estimasi durasi, kapasitas, dan metode implementasi.",
        "gate": "Solusi feasible?", "go": "Lanjut ke Internal Review",
        "nogo": "REVISE / NO-GO", "solution": "Revisi desain, gunakan alternatif perangkat/metode; bila tetap tidak feasible tutup opportunity.",
        "escalation": "Product Development Manager", "output": "Technical solution, BoM/BoQ dan estimasi teknis",
        "documents": "Solution design, topology, BoM, BoQ", "sla": "5 hari kerja",
        "kpi": "Design accuracy dan solution acceptance", "risk": "Solusi tidak kompatibel, kapasitas kurang, atau teknologi tidak tersedia",
    },
    {
        "id": 5, "stage": "INTERNAL REVIEW", "name": "Internal Review", "owner": "Management",
        "activity": "Review teknis, harga dan margin, legal, supply/vendor, kapasitas tim, jadwal, serta risiko proyek.",
        "gate": "Semua disetujui?", "go": "Lanjut ke Proposal & Quotation",
        "nogo": "REVISE / HOLD / REJECT", "solution": "Kembalikan ke fungsi terkait dengan catatan revisi, PIC, target waktu, dan approval ulang.",
        "escalation": "Department Head / Director", "output": "Internal approval dan go/no-go record",
        "documents": "Approval sheet, risk register, costing", "sla": "3 hari kerja",
        "kpi": "Approval turnaround time", "risk": "Margin rendah, risiko kontrak, lead time, atau kapasitas resource",
    },
    {
        "id": 6, "stage": "PROPOSAL", "name": "Proposal & Quotation", "owner": "Sales",
        "activity": "Menyusun proposal teknis-komersial, quotation, timeline, SLA, term of payment, dan warranty.",
        "gate": "Disetujui customer?", "go": "Lanjut ke Negotiation",
        "nogo": "REVISE / NEGOTIATE", "solution": "Revisi harga, term, scope, atau alternatif solusi sesuai batas kewenangan.",
        "escalation": "Sales Manager", "output": "Proposal dan quotation resmi",
        "documents": "Proposal, quotation, SLA draft", "sla": "2 hari kerja",
        "kpi": "Proposal response time dan proposal acceptance", "risk": "Harga tidak kompetitif atau scope tidak dipahami",
    },
    {
        "id": 7, "stage": "NEGOTIATION", "name": "Negotiation", "owner": "Sales",
        "activity": "Negosiasi harga, SLA, garansi, termin pembayaran, delivery, scope, dan klausul komersial.",
        "gate": "Deal?", "go": "Lanjut ke Contract / PO",
        "nogo": "LOST / DEADLOCK", "solution": "Lakukan final offer atau eskalasi. Jika tetap deadlock, dokumentasikan lost reason.",
        "escalation": "Sales Director", "output": "Negotiation record dan final commercial terms",
        "documents": "Negotiation note, final quotation", "sla": "Sesuai timeline pelanggan",
        "kpi": "Win rate dan average closing cycle", "risk": "Diskon berlebihan atau klausul tidak seimbang",
    },
    {
        "id": 8, "stage": "CONTRACT / PO", "name": "Contract / PO Review", "owner": "Legal",
        "activity": "Review PO, kontrak, SLA, liability, acceptance, payment, warranty, dan kewajiban para pihak.",
        "gate": "PO / Kontrak OK?", "go": "Lanjut ke Kick Off Internal",
        "nogo": "REVISE CONTRACT", "solution": "Negosiasi klausul, klarifikasi PO, atau minta approval risiko dari Direksi.",
        "escalation": "Legal Manager / Director", "output": "PO/kontrak terverifikasi dan ditandatangani",
        "documents": "PO, contract, SLA, NDA", "sla": "3–5 hari kerja",
        "kpi": "Legal review turnaround time", "risk": "Klausul berat sebelah atau ketidaksesuaian scope dan pembayaran",
    },
    {
        "id": 9, "stage": "PROJECT KICK OFF", "name": "Kick Off Internal", "owner": "Operation",
        "activity": "Handover Sales ke Project, penetapan PM/tim, project plan, baseline scope, biaya, dan jadwal.",
        "gate": "Kick off siap?", "go": "Lanjut ke Procurement",
        "nogo": "REVISE PLAN", "solution": "Lengkapi dokumen, resource, WBS, risiko, dan rencana kerja sebelum eksekusi.",
        "escalation": "Project Manager / Operation Manager", "output": "Project charter dan baseline plan",
        "documents": "Kick-off MoM, WBS, project schedule", "sla": "2 hari kerja setelah PO",
        "kpi": "Kick-off readiness", "risk": "Handover tidak lengkap atau baseline tidak disepakati",
    },
    {
        "id": 10, "stage": "PROCUREMENT", "name": "Procurement & Logistics", "owner": "Procurement",
        "activity": "Pengadaan barang/jasa, seleksi vendor, monitoring lead time, inspeksi, dan distribusi material.",
        "gate": "Material ready?", "go": "Lanjut ke Implementation",
        "nogo": "ALTERNATIVE / RESCHEDULE", "solution": "Cari vendor/perangkat alternatif, lakukan partial delivery, atau revisi jadwal.",
        "escalation": "Procurement Manager", "output": "Material tersedia sesuai spesifikasi dan jadwal",
        "documents": "PR, PO vendor, delivery note, inspection record", "sla": "Sesuai lead time",
        "kpi": "On-time delivery dan procurement saving", "risk": "Keterlambatan, spesifikasi salah, atau vendor gagal",
    },
    {
        "id": 11, "stage": "IMPLEMENTATION", "name": "Implementation", "owner": "Operation",
        "activity": "Instalasi, konfigurasi, integrasi, quality control, dokumentasi, dan monitoring progres.",
        "gate": "On track?", "go": "Lanjut ke Testing & Commissioning",
        "nogo": "CORRECTIVE ACTION", "solution": "Re-plan, percepatan, tambah resource, atau koordinasi akses/site dengan customer.",
        "escalation": "Project Manager", "output": "Pekerjaan terpasang dan siap diuji",
        "documents": "Daily report, checklist, as-built draft", "sla": "Sesuai project schedule",
        "kpi": "On-time completion, quality, HSE compliance", "risk": "Site tidak siap, akses tertunda, kualitas instalasi, atau HSE incident",
    },
    {
        "id": 12, "stage": "TESTING", "name": "Testing & Commissioning", "owner": "Product Development",
        "activity": "FAT/SAT/UAT, testing fungsi, performance, integrasi, dan penyusunan hasil pengujian.",
        "gate": "Testing lulus?", "go": "Lanjut ke BAST / Acceptance",
        "nogo": "REPAIR & RETEST", "solution": "Troubleshooting, corrective action, retest, dan update test report.",
        "escalation": "Project Manager / Product Manager", "output": "Test report lulus dan acceptance evidence",
        "documents": "FAT, SAT, UAT, test report", "sla": "2–5 hari kerja",
        "kpi": "First-pass yield dan defect closure time", "risk": "Fungsi gagal, performa tidak memenuhi, atau integrasi bermasalah",
    },
    {
        "id": 13, "stage": "ACCEPTANCE", "name": "BAST / Acceptance", "owner": "Operation",
        "activity": "Serah terima pekerjaan, finalisasi dokumen, as-built, checklist, training, dan punch list.",
        "gate": "Customer approve?", "go": "Lanjut ke Invoice",
        "nogo": "PUNCH LIST", "solution": "Selesaikan temuan, verifikasi ulang, dan jadwalkan penandatanganan BAST.",
        "escalation": "Project Manager", "output": "BAST ditandatangani dan dokumen final",
        "documents": "BAST, as-built, training record, punch list", "sla": "Maks. 5 hari setelah pekerjaan selesai",
        "kpi": "BAST cycle time dan punch-list closure", "risk": "Dokumen tidak lengkap atau customer menunda acceptance",
    },
    {
        "id": 14, "stage": "INVOICE", "name": "Invoice", "owner": "Finance",
        "activity": "Penerbitan invoice, faktur pajak, verifikasi dokumen pendukung, dan pengiriman ke customer.",
        "gate": "Invoice accepted?", "go": "Lanjut ke Payment & Collection",
        "nogo": "REVISE INVOICE", "solution": "Perbaiki invoice, dokumen pajak, BAST, atau persyaratan administrasi.",
        "escalation": "Finance Manager", "output": "Invoice diterima dan tercatat customer",
        "documents": "Invoice, tax invoice, BAST, PO", "sla": "1–2 hari kerja",
        "kpi": "Billing accuracy dan billing cycle time", "risk": "Dokumen kurang atau kesalahan data invoice",
    },
    {
        "id": 15, "stage": "PAYMENT", "name": "Payment & Collection", "owner": "Finance",
        "activity": "Monitoring jatuh tempo, reminder, collection, rekonsiliasi, dan pelaporan aging piutang.",
        "gate": "Pembayaran lunas?", "go": "Lanjut ke After Sales",
        "nogo": "COLLECTION / ESCALATE", "solution": "Reminder formal, negosiasi termin, suspend sesuai kontrak, atau eskalasi manajemen.",
        "escalation": "Finance Manager / Director", "output": "Pembayaran diterima dan direkonsiliasi",
        "documents": "Aging report, payment receipt, collection note", "sla": "Sesuai termin kontrak",
        "kpi": "DSO dan overdue ratio", "risk": "Keterlambatan pembayaran atau dispute invoice",
    },
    {
        "id": 16, "stage": "AFTER SALES", "name": "After Sales / Support", "owner": "After Sales",
        "activity": "Warranty, helpdesk, ticketing, preventive/corrective maintenance, dan monitoring SLA.",
        "gate": "Ada complaint?", "go": "Tidak: lanjut monitoring dan customer review",
        "nogo": "YA: RCA & CORRECTIVE ACTION", "solution": "Klasifikasi severity, RCA, perbaikan, update customer, dan close ticket.",
        "escalation": "After Sales Manager", "output": "Ticket terselesaikan dan SLA tercapai",
        "documents": "Ticket, service report, RCA/CAPA", "sla": "Sesuai SLA",
        "kpi": "SLA compliance, MTTR, repeat incident", "risk": "Gangguan berulang atau respons terlambat",
    },
    {
        "id": 17, "stage": "SATISFACTION", "name": "Customer Satisfaction", "owner": "After Sales",
        "activity": "Survey kepuasan, evaluasi layanan, review performa, dan identifikasi improvement.",
        "gate": "Customer puas?", "go": "Lanjut ke Repeat Order / Upselling",
        "nogo": "IMPROVEMENT PLAN", "solution": "Susun action plan, perbaiki SLA, lakukan service recovery, dan review manajemen.",
        "escalation": "After Sales Manager / Director", "output": "CSI/NPS dan improvement plan",
        "documents": "Customer survey, service review MoM", "sla": "Maks. 30 hari setelah acceptance",
        "kpi": "CSI/NPS dan complaint recurrence", "risk": "Kepuasan rendah dan churn customer",
    },
    {
        "id": 18, "stage": "REPEAT & GROWTH", "name": "Repeat Order / Upselling", "owner": "Sales",
        "activity": "Identifikasi kebutuhan baru, renewal, upgrade, cross-selling, upselling, dan kontrak maintenance.",
        "gate": "Opportunity baru?", "go": "Kembali ke Lead Qualification",
        "nogo": "ACCOUNT NURTURE", "solution": "Tetap lakukan account review berkala dan relationship management.",
        "escalation": "Sales Manager", "output": "Repeat order, renewal, atau account development plan",
        "documents": "Account plan, renewal proposal", "sla": "Review triwulanan",
        "kpi": "Repeat-order rate dan customer lifetime value", "risk": "Tidak ada engagement atau kehilangan pelanggan",
    },
]

# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
<style>
:root { --navy:#071E33; --navy2:#0B3152; --blue:#1477C9; --bg:#F5F8FC; }
[data-testid="stAppViewContainer"] { background: #F5F8FC; }
[data-testid="stHeader"] { background: rgba(0,0,0,0); }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#061A2D 0%,#0A3558 100%); }
[data-testid="stSidebar"] * { color: #F5FAFF; }
[data-testid="stSidebar"] .stRadio label { padding: 4px 0; }
.block-container { padding-top: 1.0rem; max-width: 1900px; }
.hero { background: linear-gradient(120deg,#071E33,#1477C9); padding:22px 28px; border-radius:0 0 22px 22px; color:white; box-shadow:0 12px 30px rgba(7,30,51,.18); }
.hero h1 { margin:0; font-size:34px; }
.hero p { margin:9px 0 0; opacity:.94; }
.metric-row { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin:16px 0; }
.metric-card { background:white; border:1px solid #D9E3EE; border-radius:14px; padding:15px 17px; box-shadow:0 5px 20px rgba(7,30,51,.06); }
.metric-card b { font-size:26px; color:#071E33; }
.metric-card span { display:block; color:#5F7690; font-size:11px; letter-spacing:.08em; margin-top:3px; }
.section-title { font-size:22px; font-weight:800; color:#071E33; margin:12px 0 8px; }
.legend-chip { display:inline-flex;align-items:center;gap:6px;padding:6px 10px;border:1px solid #D7E3EF;border-radius:999px;background:white;margin:2px;font-size:12px;color:#29435F; }
@media(max-width:900px){.metric-row{grid-template-columns:repeat(2,1fr)}.hero h1{font-size:26px}}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown("## 📡 STARCOM SOP")
    st.caption("Telecommunication & IT System Integrator")
    st.markdown("---")
    page = st.radio(
        "NAVIGATION",
        ["Executive Flow", "Swimlane Flow", "Department Authority", "Process Detail"],
        index=1,
    )

# -----------------------------
# Header
# -----------------------------
st.markdown(
    """
<div class="hero">
  <h1>SOP Sales → Delivery → After Sales</h1>
  <p>Visualisasi end-to-end proses telekomunikasi dan IT system integrator dengan kewenangan departemen, decision gate Go/No-Go, tindakan koreksi, dan jalur eskalasi.</p>
</div>
<div class="metric-row">
  <div class="metric-card"><b>18</b><span>PROSES UTAMA</span></div>
  <div class="metric-card"><b>8</b><span>DEPARTEMEN INTI</span></div>
  <div class="metric-card"><b>18</b><span>DECISION GATE</span></div>
  <div class="metric-card"><b>6</b><span>OUTCOME STATUS</span></div>
</div>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# HTML / SVG builder
# -----------------------------
def build_swimlane_html(processes, presentation=False):
    deps = list(DEPARTMENTS.keys())
    lane_w = 150
    stage_w = 118
    left = 14
    lane_x = {dep: left + stage_w + 8 + i * lane_w for i, dep in enumerate(deps)}
    row_h = 190
    top = 108
    right_pad = 270
    width = left + stage_w + 8 + len(deps) * lane_w + right_pad
    height = top + len(processes) * row_h + 90

    p_json = json.dumps(processes, ensure_ascii=False)
    dep_json = json.dumps(DEPARTMENTS, ensure_ascii=False)

    lane_headers = []
    for dep in deps:
        cfg = DEPARTMENTS[dep]
        x = lane_x[dep]
        label = dep.replace("Product Development", "PRODUCT\nDEVELOPMENT").replace("After Sales", "AFTER SALES")
        lane_headers.append(
            f'<rect x="{x}" y="40" width="{lane_w-8}" height="54" rx="5" fill="{cfg["soft"]}" stroke="{cfg["color"]}" stroke-width="1.2"/>'
            f'<text x="{x+(lane_w-8)/2}" y="59" text-anchor="middle" class="hdr">{label.split(chr(10))[0]}</text>'
            + (f'<text x="{x+(lane_w-8)/2}" y="74" text-anchor="middle" class="hdr">{label.split(chr(10))[1]}</text>' if "\n" in label else "")
        )

    rows = []
    connectors = []
    action_col_x = left + stage_w + 8 + len(deps) * lane_w + 18

    for idx, p in enumerate(processes):
        y = top + idx * row_h
        owner_x = lane_x[p["owner"]]
        cfg = DEPARTMENTS[p["owner"]]
        box_x = owner_x + 8
        box_y = y + 12
        box_w = lane_w - 24
        box_h = 62
        gate_cx = owner_x + lane_w/2 - 4
        gate_cy = y + 116
        gate_rx, gate_ry = 45, 32

        # Stage column
        rows.append(f'<rect x="{left}" y="{y}" width="{stage_w-8}" height="{row_h-12}" rx="8" fill="#F8FBFF" stroke="#BFD0E2"/>')
        rows.append(f'<text x="{left+(stage_w-8)/2}" y="{y+31}" text-anchor="middle" class="num">{p["id"]}</text>')
        rows.append(f'<text x="{left+(stage_w-8)/2}" y="{y+55}" text-anchor="middle" class="stage">{p["stage"]}</text>')

        # Process box
        rows.append(f'<rect class="process-box" data-id="{p["id"]}" x="{box_x}" y="{box_y}" width="{box_w}" height="{box_h}" rx="9" fill="{cfg["soft"]}" stroke="{cfg["color"]}" stroke-width="1.5"/>')
        for li, line in enumerate(split_lines(p["name"], 18)[:3]):
            rows.append(f'<text x="{box_x+box_w/2}" y="{box_y+25+li*15}" text-anchor="middle" class="boxtext">{escape(line)}</text>')

        # Short vertical connector: process -> gate
        connectors.append(f'<path d="M {gate_cx} {box_y+box_h} L {gate_cx} {gate_cy-gate_ry}" class="flow-line" marker-end="url(#arrowBlue)"/>')

        # Decision gate directly under owner process
        rows.append(f'<polygon class="gate" data-id="{p["id"]}" points="{gate_cx},{gate_cy-gate_ry} {gate_cx+gate_rx},{gate_cy} {gate_cx},{gate_cy+gate_ry} {gate_cx-gate_rx},{gate_cy}" fill="#F6FAFF" stroke="#4E89C7" stroke-width="1.5"/>')
        for li, line in enumerate(split_lines(p["gate"], 13)[:3]):
            rows.append(f'<text x="{gate_cx}" y="{gate_cy-7+li*13}" text-anchor="middle" class="gateText">{escape(line)}</text>')

        # GO route to next owner lane. It drops to row boundary, then turns once.
        if idx < len(processes)-1:
            nxt = processes[idx+1]
            next_x = lane_x[nxt["owner"]] + lane_w/2 - 4
            next_y = top + (idx+1) * row_h + 12
            route_y = y + row_h - 12
            rows.append(f'<rect x="{gate_cx-16}" y="{gate_cy+36}" width="32" height="16" rx="8" fill="#E9F8ED"/><text x="{gate_cx}" y="{gate_cy+48}" text-anchor="middle" class="goLabel">GO</text>')
            connectors.append(
                f'<path d="M {gate_cx} {gate_cy+gate_ry} L {gate_cx} {route_y} L {next_x} {route_y} L {next_x} {next_y}" class="go-line" marker-end="url(#arrowGreen)"/>'
            )
        else:
            rows.append(f'<text x="{gate_cx}" y="{gate_cy+51}" text-anchor="middle" class="goLabel">GO / SELESAI</text>')

        # Local No-Go branch: short elbow to right/left of gate, then action on dedicated compact column.
        action_y = y + 82
        action_w = 185
        action_h = 74
        rows.append(f'<text x="{gate_cx+gate_rx+10}" y="{gate_cy-7}" class="noLabel">NO-GO</text>')
        connectors.append(f'<path d="M {gate_cx+gate_rx} {gate_cy} L {action_col_x-10} {gate_cy}" class="no-line" marker-end="url(#arrowRed)"/>')
        rows.append(f'<rect class="action-box" data-id="{p["id"]}" x="{action_col_x}" y="{action_y}" width="{action_w}" height="{action_h}" rx="9" fill="#FFF2EE" stroke="#F06B59" stroke-width="1.3"/>')
        rows.append(f'<text x="{action_col_x+action_w/2}" y="{action_y+21}" text-anchor="middle" class="actionTitle">{escape(p["nogo"])}</text>')
        for li, line in enumerate(split_lines(p["solution"], 29)[:3]):
            rows.append(f'<text x="{action_col_x+action_w/2}" y="{action_y+40+li*13}" text-anchor="middle" class="actionText">{escape(line)}</text>')
        rows.append(f'<text x="{action_col_x+action_w/2}" y="{action_y+action_h+16}" text-anchor="middle" class="escText">Eskalasi: {escape(p["escalation"])}</text>')

    grid_lines = []
    # Vertical swimlane separators only; action column is visually separate.
    grid_lines.append(f'<line x1="{left+stage_w}" y1="35" x2="{left+stage_w}" y2="{height-20}" class="grid"/>')
    for i in range(len(deps)+1):
        x = left + stage_w + 8 + i*lane_w
        grid_lines.append(f'<line x1="{x}" y1="35" x2="{x}" y2="{height-20}" class="grid"/>')
    grid_lines.append(f'<line x1="{action_col_x-18}" y1="35" x2="{action_col_x-18}" y2="{height-20}" class="grid strong"/>')
    for i in range(len(processes)+1):
        yy = top - 4 + i*row_h
        grid_lines.append(f'<line x1="{left}" y1="{yy}" x2="{width-8}" y2="{yy}" class="grid"/>')

    html = f"""
<!doctype html><html><head><meta charset='utf-8'/>
<style>
html,body{{margin:0;background:#F7FAFD;font-family:Inter,Arial,sans-serif;color:#0B243B;overflow:auto}}
.toolbar{{position:sticky;top:0;z-index:20;display:flex;gap:8px;align-items:center;padding:10px 12px;background:rgba(247,250,253,.97);border-bottom:1px solid #D9E4EF;backdrop-filter:blur(8px)}}
.toolbar button,.toolbar select,.toolbar input{{border:1px solid #CAD8E6;background:white;border-radius:8px;padding:8px 10px;font-size:12px;color:#173A59}}
.toolbar button{{cursor:pointer;font-weight:700}} .toolbar .title{{font-weight:800;margin-right:auto;color:#071E33}}
#viewport{{padding:10px;overflow:auto;max-height:{'2200px' if presentation else '1900px'};background:white}}
#canvasWrap{{transform-origin:top left;transition:transform .15s ease;display:inline-block}}
svg{{background:white;border:1px solid #D7E2ED;border-radius:12px;box-shadow:0 8px 25px rgba(7,30,51,.08)}}
.grid{{stroke:#E4EBF3;stroke-width:1}} .grid.strong{{stroke:#CBD8E5;stroke-width:1.3}}
.flow-line{{fill:none;stroke:#2D6596;stroke-width:1.5}} .go-line{{fill:none;stroke:#279647;stroke-width:1.7}} .no-line{{fill:none;stroke:#D94A3B;stroke-width:1.5}}
.hdr{{font-size:10px;font-weight:800;fill:#0B3152}} .num{{font-size:18px;font-weight:800;fill:#0B3152}} .stage{{font-size:8px;font-weight:800;fill:#2E5273}} .boxtext{{font-size:9px;font-weight:700;fill:#0A2F4E}} .gateText{{font-size:8px;font-weight:800;fill:#0B3152}} .goLabel{{font-size:8px;font-weight:900;fill:#21883D}} .noLabel{{font-size:7.5px;font-weight:900;fill:#D73D2D}} .actionTitle{{font-size:8px;font-weight:900;fill:#B52C23}} .actionText{{font-size:7.2px;font-weight:600;fill:#5B2A26}} .escText{{font-size:7px;font-weight:700;fill:#314B64}}
.process-box,.gate,.action-box{{cursor:pointer;transition:filter .15s,stroke-width .15s}} .process-box:hover,.gate:hover,.action-box:hover{{filter:drop-shadow(0 3px 5px rgba(0,0,0,.18));stroke-width:2.4}}
.dim{{opacity:.14}} .highlight{{filter:drop-shadow(0 0 7px #FFD43B);stroke:#E6A900!important;stroke-width:3!important}}
#modal{{display:none;position:fixed;inset:0;background:rgba(4,18,31,.65);z-index:50;align-items:center;justify-content:center;padding:20px}}
#modalCard{{width:min(760px,92vw);max-height:84vh;overflow:auto;background:white;border-radius:16px;box-shadow:0 20px 70px rgba(0,0,0,.35);padding:22px}}
#modalCard h2{{margin:0 0 6px;color:#071E33}} .badge{{display:inline-block;padding:5px 9px;border-radius:999px;background:#EAF3FF;color:#155D9B;font-size:11px;font-weight:800}}
.detailGrid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:14px}} .detail{{border:1px solid #DCE6F0;border-radius:10px;padding:10px;background:#FAFCFE}} .detail b{{display:block;font-size:10px;letter-spacing:.08em;color:#6D8297;margin-bottom:5px}} .detail span{{font-size:13px;line-height:1.45}}
.close{{float:right;border:0;background:#EEF3F7;border-radius:50%;width:32px;height:32px;cursor:pointer;font-size:18px}}
@media(max-width:800px){{.detailGrid{{grid-template-columns:1fr}}}}
</style></head><body>
<div class='toolbar'>
 <span class='title'>Compact Vertical Swimlane</span>
 <input id='search' placeholder='Cari proses…' oninput='applyFilters()'/>
 <select id='dept' onchange='applyFilters()'><option value='ALL'>Semua departemen</option>{''.join(f'<option>{d}</option>' for d in deps)}</select>
 <button onclick='zoomOut()'>−</button><button id='zoomLabel'>100%</button><button onclick='zoomIn()'>+</button>
 <button onclick='fitWidth()'>Fit Width</button><button onclick='actualSize()'>100%</button><button onclick='resetView()'>Reset</button><button onclick='fullscreen()'>⛶ Fullscreen</button><button onclick='window.print()'>Print / PDF</button>
</div>
<div id='viewport'><div id='canvasWrap'>
<svg id='chart' width='{width}' height='{height}' viewBox='0 0 {width} {height}'>
<defs>
 <marker id='arrowBlue' markerWidth='8' markerHeight='8' refX='7' refY='4' orient='auto'><path d='M0,0 L8,4 L0,8 z' fill='#2D6596'/></marker>
 <marker id='arrowGreen' markerWidth='8' markerHeight='8' refX='7' refY='4' orient='auto'><path d='M0,0 L8,4 L0,8 z' fill='#279647'/></marker>
 <marker id='arrowRed' markerWidth='8' markerHeight='8' refX='7' refY='4' orient='auto'><path d='M0,0 L8,4 L0,8 z' fill='#D94A3B'/></marker>
</defs>
<rect x='{left}' y='35' width='{width-left-8}' height='{height-55}' rx='10' fill='white' stroke='#BFCFDF'/>
<rect x='{left}' y='40' width='{stage_w-8}' height='54' rx='5' fill='#F1F6FB' stroke='#9CB2C7'/><text x='{left+(stage_w-8)/2}' y='72' text-anchor='middle' class='hdr'>TAHAP</text>
{''.join(lane_headers)}
<rect x='{action_col_x}' y='40' width='185' height='54' rx='5' fill='#FFF2EE' stroke='#F06B59'/><text x='{action_col_x+92.5}' y='60' text-anchor='middle' class='hdr'>NO-GO: SOLUSI</text><text x='{action_col_x+92.5}' y='75' text-anchor='middle' class='hdr'>& ESKALASI</text>
{''.join(grid_lines)}{''.join(connectors)}{''.join(rows)}
</svg></div></div>
<div id='modal' onclick='if(event.target.id==="modal")closeModal()'><div id='modalCard'><button class='close' onclick='closeModal()'>×</button><div id='modalBody'></div></div></div>
<script>
const processes={p_json}; const departments={dep_json}; let zoom=1;
function setZoom(v){{zoom=Math.max(.55,Math.min(2.2,v));document.getElementById('canvasWrap').style.transform=`scale(${{zoom}})`;document.getElementById('zoomLabel').innerText=Math.round(zoom*100)+'%';}}
function zoomIn(){{setZoom(zoom+.1)}} function zoomOut(){{setZoom(zoom-.1)}}
function actualSize(){{setZoom(1)}}
function fitWidth(){{const vp=document.getElementById('viewport');const svg=document.getElementById('chart');setZoom((vp.clientWidth-30)/svg.width.baseVal.value)}}
function resetView(){{setZoom(1);document.getElementById('search').value='';document.getElementById('dept').value='ALL';applyFilters();document.getElementById('viewport').scrollTo(0,0)}}
function fullscreen(){{const el=document.getElementById('viewport');if(el.requestFullscreen)el.requestFullscreen();}}
function applyFilters(){{const q=document.getElementById('search').value.toLowerCase();const dep=document.getElementById('dept').value;document.querySelectorAll('.process-box,.gate,.action-box').forEach(el=>{{const id=+el.dataset.id;const p=processes.find(x=>x.id===id);const okQ=!q||JSON.stringify(p).toLowerCase().includes(q);const okD=dep==='ALL'||p.owner===dep;el.classList.toggle('dim',!(okQ&&okD));el.classList.toggle('highlight',okQ&&q.length>1);}})}}
function showDetail(id){{const p=processes.find(x=>x.id===id);const c=departments[p.owner];document.getElementById('modalBody').innerHTML=`<span class='badge' style='background:${{c.soft}};color:${{c.color}}'>${{p.owner}}</span><h2>${{p.id}}. ${{p.name}}</h2><div class='detailGrid'><div class='detail'><b>KEGIATAN UTAMA</b><span>${{p.activity}}</span></div><div class='detail'><b>OUTPUT</b><span>${{p.output}}</span></div><div class='detail'><b>DECISION GATE</b><span>${{p.gate}}</span></div><div class='detail'><b>GO / LOLOS</b><span>${{p.go}}</span></div><div class='detail'><b>NO-GO / TINDAKAN</b><span><strong>${{p.nogo}}</strong><br>${{p.solution}}</span></div><div class='detail'><b>ESKALASI</b><span>${{p.escalation}}</span></div><div class='detail'><b>DOKUMEN</b><span>${{p.documents}}</span></div><div class='detail'><b>SLA</b><span>${{p.sla}}</span></div><div class='detail'><b>KPI</b><span>${{p.kpi}}</span></div><div class='detail'><b>RISIKO</b><span>${{p.risk}}</span></div></div>`;document.getElementById('modal').style.display='flex';}}
function closeModal(){{document.getElementById('modal').style.display='none'}}
document.querySelectorAll('.process-box,.gate,.action-box').forEach(el=>el.addEventListener('click',()=>showDetail(+el.dataset.id)));
setZoom(1);
</script></body></html>
"""
    return html, height

def split_lines(text, max_chars):
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = word if not current else current + " " + word
        if len(trial) <= max_chars:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def escape(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def infer_support(p):
    mapping = {
        1: [], 2: ["Product Development"], 3: ["Sales", "Operation"], 4: ["Sales", "Operation", "Procurement"],
        5: ["Sales", "Product Development", "Finance", "Legal", "Procurement", "Operation"],
        6: ["Product Development", "Finance", "Legal"], 7: ["Legal", "Finance", "Product Development"],
        8: ["Sales", "Finance"], 9: ["Sales", "Product Development", "Procurement", "Finance"],
        10: ["Operation", "Finance", "Product Development"], 11: ["Product Development", "Procurement", "After Sales"],
        12: ["Operation", "After Sales"], 13: ["Sales", "Product Development", "Legal"],
        14: ["Sales", "Operation"], 15: ["Sales", "Legal"], 16: ["Operation", "Product Development"],
        17: ["Sales", "Operation"], 18: ["After Sales", "Product Development"],
    }
    return mapping.get(p["id"], [])

# -----------------------------
# Pages
# -----------------------------
if page == "Swimlane Flow":
    st.markdown('<div class="section-title">Swimlane Flow — End-to-End</div>', unsafe_allow_html=True)
    st.caption("Klik kotak proses, decision gate, atau tindakan No-Go untuk membuka detail. Jalur GO kembali ke swimlane pemilik proses berikutnya; jalur NO-GO menuju solusi dan eskalasi.")
    html, h = build_swimlane_html(PROCESSES)
    components.html(html, height=1820, scrolling=True)

elif page == "Executive Flow":
    st.markdown('<div class="section-title">Executive Flow</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    phases = [
        ("1. Opportunity", "Lead → Qualification → Need Assessment", "Sales + Product Development"),
        ("2. Solution & Approval", "Solution Design → Internal Review → Proposal", "PD + Finance + Legal + Procurement"),
        ("3. Commercial", "Negotiation → Contract / PO", "Sales + Legal + Finance"),
        ("4. Delivery", "Kick Off → Procurement → Implementation", "Operation + Procurement"),
        ("5. Acceptance & Cash", "Testing → BAST → Invoice → Payment", "PD + Operation + Finance"),
        ("6. Customer Growth", "After Sales → Satisfaction → Repeat Order", "After Sales + Sales"),
    ]
    for i, (title, flow, owner) in enumerate(phases):
        with cols[i % 3]:
            st.markdown(f"<div class='metric-card' style='min-height:145px'><b style='font-size:18px'>{title}</b><p style='color:#29435F'>{flow}</p><span>OWNER: {owner}</span></div>", unsafe_allow_html=True)
    st.success("Prinsip pengendalian: setiap gate harus menghasilkan keputusan terdokumentasi—Go, Revise, Hold, Reject, Lost, atau Escalate.")

elif page == "Department Authority":
    st.markdown('<div class="section-title">Department Authority</div>', unsafe_allow_html=True)
    selected = st.selectbox("Pilih departemen", list(DEPARTMENTS.keys()))
    owned = [p for p in PROCESSES if p["owner"] == selected]
    st.markdown(f"### {selected}")
    for p in owned:
        with st.expander(f"{p['id']}. {p['name']}", expanded=True):
            c1, c2 = st.columns(2)
            c1.markdown(f"""**Kewenangan utama**  
{p['activity']}  

**Output**  
{p['output']}""")
            c2.markdown(f"""**Decision gate**  
{p['gate']}  

**Eskalasi**  
{p['escalation']}""")

elif page == "Process Detail":
    st.markdown('<div class="section-title">Process Detail</div>', unsafe_allow_html=True)
    label = st.selectbox("Pilih proses", [f"{p['id']}. {p['name']}" for p in PROCESSES])
    p = PROCESSES[int(label.split('.')[0]) - 1]
    st.markdown(f"## {p['id']}. {p['name']}")
    st.caption(f"Process owner: {p['owner']} · SLA: {p['sla']}")
    left, right = st.columns(2)
    with left:
        st.markdown(f"""**Kegiatan utama**  
{p['activity']}""")
        st.markdown(f"""**Input/Output utama**  
{p['output']}""")
        st.markdown(f"""**Dokumen**  
{p['documents']}""")
        st.markdown(f"""**KPI**  
{p['kpi']}""")
    with right:
        st.markdown(f"""**Decision gate**  
{p['gate']}""")
        st.success(p['go'])
        st.error(f"{p['nogo']} — {p['solution']}")
        st.warning(f"Eskalasi: {p['escalation']}")
        st.markdown(f"""**Risiko utama**  
{p['risk']}""")
