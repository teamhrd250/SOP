import json
import csv
import io
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="STARCOM SOP | Sales to After Sales",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
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
    "HSEQ": {"color": "#17A2B8", "soft": "#E8F7FA", "icon": "✚"},
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
        "gate": "Semua disetujui?", "go": "Lanjut ke pembagian kewenangan paralel lintas departemen",
        "nogo": "REVISE / HOLD / REJECT", "solution": "Kembalikan ke fungsi terkait dengan catatan revisi, PIC, target waktu, dan approval ulang.",
        "escalation": "Department Head / Director", "output": "Internal approval dan go/no-go record",
        "documents": "Approval sheet, risk register, costing", "sla": "3 hari kerja",
        "kpi": "Approval turnaround time", "risk": "Margin rendah, risiko kontrak, lead time, atau kapasitas resource",
    },
    {
        "id": 6, "stage": "PROPOSAL", "name": "Proposal & Quotation", "owner": "Sales",
        "activity": "Sales mengonsolidasikan hasil pekerjaan paralel dari Sales, Product Development, HSEQ, Legal, Procurement, dan Operation; melakukan review internal; lalu mengirim proposal final kepada customer.",
        "gate": "Disetujui customer?", "go": "Lanjut ke Negotiation",
        "nogo": "REVISE / NEGOTIATE", "solution": "Revisi harga, term, scope, atau alternatif solusi sesuai batas kewenangan.",
        "escalation": "Sales Manager", "output": "Proposal final terintegrasi dan quotation resmi",
        "documents": "Quotation, proposal solution & product, dokumen HSEQ, legal requirement checklist, timeline procurement, material readiness, proposal teknis, portfolio project, timeline project, manpower mapping, proposal managed service", "sla": "2 hari kerja",
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

PARALLEL_AUTHORITY = [
    {
        "department": "Sales",
        "title": "Quotation",
        "detail": "Harga, term komersial, SLA, warranty, payment term, dan ketentuan komersial lainnya.",
        "output": "Quotation"
    },
    {
        "department": "Product Development",
        "title": "Proposal Solution & Product",
        "detail": "Penyusunan solusi, arsitektur, produk, BoM/BoQ, spesifikasi, dan pendekatan teknis produk.",
        "output": "Proposal Solution & Product"
    },
    {
        "department": "HSEQ",
        "title": "Dokumen HSEQ",
        "detail": "CSMS, RKPLH, dan dokumen pra-kualifikasi HSEQ apabila dipersyaratkan oleh customer atau tender.",
        "output": "Dokumen CSMS / RKPLH / Pra-Kualifikasi HSEQ"
    },
    {
        "department": "Legal",
        "title": "Collect Legalitas Requirement Project",
        "detail": "Mengumpulkan dan memverifikasi legalitas yang dipersyaratkan untuk project, termasuk dokumen perusahaan, perizinan, kontrak, NDA, dan kebutuhan legal customer atau tender.",
        "output": "Legal Requirement Checklist"
    },
    {
        "department": "Procurement",
        "title": "Timeline & Material Readiness",
        "detail": "Timeline pengadaan, kesiapan material, lead time vendor, dan alternatif supply bila diperlukan.",
        "output": "Timeline Pengadaan & Material Readiness"
    },
    {
        "department": "Operation",
        "title": "Proposal Teknis & Project Plan",
        "detail": "Proposal teknis, portfolio project, timeline project, manpower mapping, serta proposal managed service.",
        "output": "Proposal Teknis, Project Plan & Managed Service"
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
[data-testid="stHeader"] { background: rgba(0,0,0,0); height: 2.2rem; }
[data-testid="stToolbar"] { top: 0.1rem; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#061A2D 0%,#0A3558 100%); }
[data-testid="stSidebar"] * { color: #F5FAFF; }
[data-testid="stSidebar"] .stRadio label { padding: 4px 0; }
.block-container { padding: 0.15rem 0.35rem 0.35rem !important; max-width: 100% !important; }
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
    theme = st.toggle("Dark Mode", value=False)
    page = st.radio(
        "NAVIGATION",
        [
            "Executive Flow", "Swimlane Flow", "Department Authority",
            "Process Detail", "KPI Dashboard", "Approval Workflow",
            "SOP Search", "Export Center", "Presentation Mode"
        ],
        index=1,
    )

if theme:
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"]{background:#071522;color:#EAF3FA}
        .block-container{color:#EAF3FA}
        .metric-card{background:#10283A;border-color:#29475D;box-shadow:none}
        .metric-card b,.section-title{color:#F5FAFF}
        .metric-card p,.metric-card span{color:#B9CAD8!important}
        .hero{background:linear-gradient(120deg,#020B13,#0B4E78)}
        [data-testid="stExpander"], [data-testid="stDataFrame"], [data-testid="stMetric"]{background:#0D2232}
        </style>
        """, unsafe_allow_html=True
    )

# -----------------------------
# Header removed for full-canvas diagram view
# -----------------------------

# -----------------------------
# HTML / SVG builder
# -----------------------------
def build_swimlane_html(processes, presentation=False):
    deps = list(DEPARTMENTS.keys())
    lane_w = 220
    stage_w = 150
    left = 14
    lane_x = {dep: left + stage_w + 8 + i * lane_w for i, dep in enumerate(deps)}
    row_h = 250
    top = 125
    right_pad = 40
    width = left + stage_w + 8 + len(deps) * lane_w + right_pad
    extra_parallel_h = 230
    height = top + len(processes) * row_h + extra_parallel_h + 90

    def row_y(index):
        return top + index * row_h + (extra_parallel_h if index > 4 else 0)

    p_json = json.dumps(processes, ensure_ascii=False)
    dep_json = json.dumps(DEPARTMENTS, ensure_ascii=False)
    parallel_json = json.dumps(PARALLEL_AUTHORITY, ensure_ascii=False)

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

    for idx, p in enumerate(processes):
        y = row_y(idx)
        owner_x = lane_x[p["owner"]]
        cfg = DEPARTMENTS[p["owner"]]
        box_x = owner_x + 12
        box_y = y + 16
        box_w = lane_w - 32
        box_h = 82
        gate_cx = owner_x + lane_w/2 - 4
        gate_cy = y + 156
        gate_rx, gate_ry = 62, 42

        # Stage column
        rows.append(f'<rect x="{left}" y="{y}" width="{stage_w-8}" height="{row_h-12}" rx="8" fill="#F8FBFF" stroke="#BFD0E2"/>')
        rows.append(f'<text x="{left+(stage_w-8)/2}" y="{y+31}" text-anchor="middle" class="num">{p["id"]}</text>')
        rows.append(f'<text x="{left+(stage_w-8)/2}" y="{y+55}" text-anchor="middle" class="stage">{p["stage"]}</text>')

        # Process box
        rows.append(f'<rect class="process-box" data-id="{p["id"]}" x="{box_x}" y="{box_y}" width="{box_w}" height="{box_h}" rx="9" fill="{cfg["soft"]}" stroke="{cfg["color"]}" stroke-width="1.5"/>')
        for li, line in enumerate(split_lines(p["name"], 23)[:3]):
            rows.append(f'<text x="{box_x+box_w/2}" y="{box_y+31+li*19}" text-anchor="middle" class="boxtext">{escape(line)}</text>')

        # Short vertical connector: process -> gate
        connectors.append(f'<path d="M {gate_cx} {box_y+box_h} L {gate_cx} {gate_cy-gate_ry}" class="flow-line" marker-end="url(#arrowBlue)"/>')

        # Decision gate directly under owner process
        rows.append(f'<polygon class="gate" data-id="{p["id"]}" points="{gate_cx},{gate_cy-gate_ry} {gate_cx+gate_rx},{gate_cy} {gate_cx},{gate_cy+gate_ry} {gate_cx-gate_rx},{gate_cy}" fill="#F6FAFF" stroke="#4E89C7" stroke-width="1.5"/>')
        for li, line in enumerate(split_lines(p["gate"], 18)[:3]):
            rows.append(f'<text x="{gate_cx}" y="{gate_cy-10+li*17}" text-anchor="middle" class="gateText">{escape(line)}</text>')

        # Special parallel authority flow after Internal Review (process 5).
        if p["id"] == 5:
            parallel_y = y + 268
            rows.append(f'<rect x="{lane_x["Sales"]-8}" y="{parallel_y-38}" width="{lane_x["Operation"]+lane_w-lane_x["Sales"]+16}" height="150" rx="12" fill="#FBFDFF" stroke="#79AFFF" stroke-width="1.2" stroke-dasharray="5 4"/>')
            rows.append(f'<text x="{(lane_x["Sales"]+lane_x["Operation"]+lane_w)/2}" y="{parallel_y-18}" text-anchor="middle" class="parallelGroupTitle">PEMBAGIAN KEWENANGAN PARALEL · KLIK KARTU UNTUK DETAIL</text>')
            card_w = 170
            card_h = 92
            join_y = y + row_h + extra_parallel_h - 18
            start_y = gate_cy + gate_ry
            rows.append(f'<text x="{gate_cx}" y="{start_y+18}" text-anchor="middle" class="goLabel">GO · PARALLEL</text>')
            connectors.append(f'<path d="M {gate_cx} {start_y} L {gate_cx} {parallel_y-18}" class="go-line" marker-end="url(#arrowGreen)"/>')
            card_centers = []
            for item in PARALLEL_AUTHORITY:
                dep = item["department"]
                x0 = lane_x[dep] + 20
                cx = x0 + card_w/2
                card_centers.append(cx)
                cfg2 = DEPARTMENTS[dep]
                rows.append(f'<rect class="parallel-card" data-parallel="{PARALLEL_AUTHORITY.index(item)}" x="{x0}" y="{parallel_y}" width="{card_w}" height="{card_h}" rx="10" fill="{cfg2["soft"]}" stroke="{cfg2["color"]}" stroke-width="1.5"/>')
                dept_label = dep.replace("Product Development", "Product Dev.")
                rows.append(f'<text x="{cx}" y="{parallel_y+17}" text-anchor="middle" class="parallelDept">{escape(dept_label)}</text>')
                title_lines = split_lines(item["title"], 20)[:3]
                title_start_y = parallel_y + 37
                for li, line in enumerate(title_lines):
                    rows.append(f'<text x="{cx}" y="{title_start_y+li*14}" text-anchor="middle" class="parallelTitle">{escape(line)}</text>')
                rows.append(f'<text x="{cx}" y="{parallel_y+card_h-9}" text-anchor="middle" class="parallelHint">Klik untuk detail ›</text>')
                connectors.append(f'<path d="M {gate_cx} {parallel_y-18} L {cx} {parallel_y-18} L {cx} {parallel_y}" class="parallel-line" marker-end="url(#arrowBlue)"/>')
                connectors.append(f'<path d="M {cx} {parallel_y+card_h} L {cx} {join_y}" class="parallel-return"/>')
            review_x = lane_x["Sales"] + lane_w/2 - 4
            review_y = row_y(idx+1) + 16
            min_c, max_c = min(card_centers), max(card_centers)
            connectors.append(f'<path d="M {min_c} {join_y} L {max_c} {join_y}" class="parallel-return"/>')
            connectors.append(f'<path d="M {review_x} {join_y} L {review_x} {review_y}" class="go-line" marker-end="url(#arrowGreen)"/>')
        # GO route to next owner lane. It drops to row boundary, then turns once.
        elif idx < len(processes)-1:
            nxt = processes[idx+1]
            next_x = lane_x[nxt["owner"]] + lane_w/2 - 4
            next_y = row_y(idx+1) + 12
            route_y = y + row_h - 12
            rows.append(f'<rect x="{gate_cx-16}" y="{gate_cy+36}" width="32" height="16" rx="8" fill="#E9F8ED"/><text x="{gate_cx}" y="{gate_cy+48}" text-anchor="middle" class="goLabel">GO</text>')
            connectors.append(
                f'<path d="M {gate_cx} {gate_cy+gate_ry} L {gate_cx} {route_y} L {next_x} {route_y} L {next_x} {next_y}" class="go-line" marker-end="url(#arrowGreen)"/>'
            )
        else:
            rows.append(f'<text x="{gate_cx}" y="{gate_cy+51}" text-anchor="middle" class="goLabel">GO / SELESAI</text>')

        # Compact NO-GO card stays inside the process owner's swimlane.
        # The full corrective action and escalation remain available in the click modal.
        action_w = 94
        action_h = 50
        action_x = owner_x + lane_w - action_w - 10
        action_y = gate_cy + gate_ry + 7
        branch_start_x = gate_cx + gate_rx
        branch_mid_y = action_y - 6
        branch_target_x = action_x + action_w / 2

        rows.append(f'<text x="{branch_start_x+8}" y="{gate_cy-9}" text-anchor="start" class="noLabel">NO-GO</text>')
        connectors.append(
            f'<path d="M {branch_start_x} {gate_cy} L {branch_start_x+10} {gate_cy} '
            f'L {branch_start_x+10} {branch_mid_y} L {branch_target_x} {branch_mid_y} '
            f'L {branch_target_x} {action_y}" class="no-line" marker-end="url(#arrowRed)"/>'
        )
        rows.append(f'<rect class="action-box" data-id="{p["id"]}" x="{action_x}" y="{action_y}" width="{action_w}" height="{action_h}" rx="9" fill="#FFF2EE" stroke="#F06B59" stroke-width="1.5"/>')
        compact_lines = split_lines(p["nogo"], 14)[:2]
        for li, line in enumerate(compact_lines):
            rows.append(f'<text x="{action_x+action_w/2}" y="{action_y+17+li*13}" text-anchor="middle" class="actionTitle">{escape(line)}</text>')
        rows.append(f'<text x="{action_x+action_w/2}" y="{action_y+43}" text-anchor="middle" class="actionHint">Klik untuk detail ›</text>')

    grid_lines = []
    # Vertical swimlane separators.
    grid_lines.append(f'<line x1="{left+stage_w}" y1="35" x2="{left+stage_w}" y2="{height-20}" class="grid"/>')
    for i in range(len(deps)+1):
        x = left + stage_w + 8 + i*lane_w
        grid_lines.append(f'<line x1="{x}" y1="35" x2="{x}" y2="{height-20}" class="grid"/>')
    for i in range(len(processes)+1):
        yy = (top - 4 + i*row_h + (extra_parallel_h if i > 5 else 0))
        grid_lines.append(f'<line x1="{left}" y1="{yy}" x2="{width-8}" y2="{yy}" class="grid"/>')

    html = f"""
<!doctype html><html><head><meta charset='utf-8'/>
<style>
html,body{{margin:0;background:#F7FAFD;font-family:Inter,Arial,sans-serif;color:#0B243B;overflow:auto}}
.toolbar{{position:sticky;top:0;z-index:20;display:flex;flex-wrap:wrap;gap:10px;align-items:center;padding:12px 14px;background:rgba(247,250,253,.98);border-bottom:1px solid #D9E4EF;backdrop-filter:blur(8px)}}
.toolbar button,.toolbar select,.toolbar input{{border:1px solid #CAD8E6;background:white;border-radius:9px;padding:10px 12px;font-size:14px;color:#173A59}}
.toolbar button{{cursor:pointer;font-weight:800}} .toolbar .title{{font-weight:900;font-size:18px;margin-right:auto;color:#071E33}}
#viewport{{padding:14px;overflow:auto;height:calc(100vh - 74px);min-height:760px;background:white;position:relative}}
#stickyHeader{{position:sticky;top:0;z-index:30;height:0;overflow:visible;pointer-events:none}}
#stickyHeaderWrap{{transform-origin:top left;transition:transform .15s ease;display:inline-block}}
#stickyHeader svg{{background:white;border:1px solid #D7E2ED;border-radius:12px 12px 0 0;box-shadow:0 5px 14px rgba(7,30,51,.10)}}
#canvasWrap{{transform-origin:top left;transition:transform .15s ease;display:inline-block}}
svg{{background:white;border:1px solid #D7E2ED;border-radius:12px;box-shadow:0 8px 25px rgba(7,30,51,.08)}}
.grid{{stroke:#E4EBF3;stroke-width:1}} .grid.strong{{stroke:#CBD8E5;stroke-width:1.3}}
.flow-line{{fill:none;stroke:#2D6596;stroke-width:1.5}} .go-line{{fill:none;stroke:#279647;stroke-width:1.7}} .no-line{{fill:none;stroke:#D94A3B;stroke-width:1.5}}
.parallel-line{{fill:none;stroke:#2F80ED;stroke-width:1.35}} .parallel-return{{fill:none;stroke:#279647;stroke-width:1.35}} .parallel-card{{cursor:pointer}}
.parallelGroupTitle{{font-size:11px;font-weight:900;fill:#274C70}} .parallelDept{{font-size:9px;font-weight:900;fill:#60788F;letter-spacing:.04em}} .parallelTitle{{font-size:10px;font-weight:900;fill:#0B3152}} .parallelHint{{font-size:8px;font-weight:800;fill:#4B6680}}
.hdr{{font-size:14px;font-weight:900;fill:#0B3152}} .num{{font-size:25px;font-weight:900;fill:#0B3152}} .stage{{font-size:11px;font-weight:900;fill:#2E5273}} .boxtext{{font-size:14px;font-weight:800;fill:#0A2F4E}} .gateText{{font-size:12px;font-weight:900;fill:#0B3152}} .goLabel{{font-size:11px;font-weight:900;fill:#21883D}} .noLabel{{font-size:11px;font-weight:900;fill:#D73D2D}} .actionTitle{{font-size:9px;font-weight:900;fill:#B52C23}} .actionHint{{font-size:7.5px;font-weight:800;fill:#A64A42}}
.process-box,.gate,.action-box{{cursor:pointer;transition:filter .15s,stroke-width .15s}} .process-box:hover,.gate:hover,.action-box:hover,.parallel-card:hover{{filter:drop-shadow(0 3px 5px rgba(0,0,0,.18));stroke-width:2.4}}
.dim{{opacity:.14}} .highlight{{filter:drop-shadow(0 0 7px #FFD43B);stroke:#E6A900!important;stroke-width:3!important}}
#modal{{display:none;position:fixed;inset:0;background:rgba(4,18,31,.65);z-index:50;align-items:center;justify-content:center;padding:20px}}
#modalCard{{width:min(760px,92vw);max-height:84vh;overflow:auto;background:white;border-radius:16px;box-shadow:0 20px 70px rgba(0,0,0,.35);padding:22px}}
#modalCard h2{{margin:0 0 6px;color:#071E33}} .badge{{display:inline-block;padding:5px 9px;border-radius:999px;background:#EAF3FF;color:#155D9B;font-size:11px;font-weight:800}}
.detailGrid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:14px}} .detail{{border:1px solid #DCE6F0;border-radius:10px;padding:10px;background:#FAFCFE}} .detail b{{display:block;font-size:10px;letter-spacing:.08em;color:#6D8297;margin-bottom:5px}} .detail span{{font-size:13px;line-height:1.45}}
.close{{float:right;border:0;background:#EEF3F7;border-radius:50%;width:32px;height:32px;cursor:pointer;font-size:18px}}
@media(max-width:800px){{.detailGrid{{grid-template-columns:1fr}}}}
</style></head><body>
<div class='toolbar'>
 <span class='title'>Presentation Swimlane · Compact NO-GO</span>
 <input id='search' placeholder='Cari proses…' oninput='applyFilters()'/>
 <select id='dept' onchange='applyFilters()'><option value='ALL'>Semua departemen</option>{''.join(f'<option>{d}</option>' for d in deps)}</select>
 <button onclick='zoomOut()'>−</button><button id='zoomLabel'>100%</button><button onclick='zoomIn()'>+</button>
 <button onclick='fitWidth()'>Fit Width</button><button onclick='actualSize()'>100%</button><button onclick='presentationView()'>▶ Presentasi</button><button onclick='resetView()'>Reset</button><button onclick='fullscreen()'>⛶ Fullscreen</button><button onclick='window.print()'>Print / PDF</button>
</div>
<div id='viewport'>
<div id='stickyHeader'><div id='stickyHeaderWrap'>
<svg width='{width}' height='104' viewBox='0 0 {width} 104' aria-label='Sticky department header'>
<rect x='{left}' y='0' width='{width-left-8}' height='104' fill='white'/>
<rect x='{left}' y='6' width='{stage_w-8}' height='54' rx='5' fill='#F1F6FB' stroke='#9CB2C7'/>
<text x='{left+(stage_w-8)/2}' y='38' text-anchor='middle' class='hdr'>TAHAP</text>
{''.join(lane_headers).replace('y="40"','y="6"').replace('y="59"','y="25"').replace('y="74"','y="40"')}
</svg></div></div>
<div id='canvasWrap'>
<svg id='chart' width='{width}' height='{height}' viewBox='0 0 {width} {height}'>
<defs>
 <marker id='arrowBlue' markerWidth='8' markerHeight='8' refX='7' refY='4' orient='auto'><path d='M0,0 L8,4 L0,8 z' fill='#2D6596'/></marker>
 <marker id='arrowGreen' markerWidth='8' markerHeight='8' refX='7' refY='4' orient='auto'><path d='M0,0 L8,4 L0,8 z' fill='#279647'/></marker>
 <marker id='arrowRed' markerWidth='8' markerHeight='8' refX='7' refY='4' orient='auto'><path d='M0,0 L8,4 L0,8 z' fill='#D94A3B'/></marker>
</defs>
<rect x='{left}' y='35' width='{width-left-8}' height='{height-55}' rx='10' fill='white' stroke='#BFCFDF'/>
<rect x='{left}' y='40' width='{stage_w-8}' height='54' rx='5' fill='#F1F6FB' stroke='#9CB2C7'/><text x='{left+(stage_w-8)/2}' y='72' text-anchor='middle' class='hdr'>TAHAP</text>
{''.join(lane_headers)}
{''.join(grid_lines)}{''.join(connectors)}{''.join(rows)}
</svg></div></div>
<div id='modal' onclick='if(event.target.id==="modal")closeModal()'><div id='modalCard'><button class='close' onclick='closeModal()'>×</button><div id='modalBody'></div></div></div>
<script>
const processes={p_json}; const departments={dep_json}; const parallelAuthority={parallel_json}; let zoom=1;
function setZoom(v){{zoom=Math.max(.55,Math.min(2.2,v));document.getElementById('canvasWrap').style.transform=`scale(${{zoom}})`;document.getElementById('stickyHeaderWrap').style.transform=`scale(${{zoom}})`;document.getElementById('zoomLabel').innerText=Math.round(zoom*100)+'%';}}
function zoomIn(){{setZoom(zoom+.1)}} function zoomOut(){{setZoom(zoom-.1)}}
function actualSize(){{setZoom(1)}}
function fitWidth(){{const vp=document.getElementById('viewport');const svg=document.getElementById('chart');setZoom((vp.clientWidth-30)/svg.width.baseVal.value)}}
function resetView(){{setZoom(1.12);document.getElementById('search').value='';document.getElementById('dept').value='ALL';applyFilters();document.getElementById('viewport').scrollTo(0,0)}}
function fullscreen(){{const el=document.getElementById('viewport');if(el.requestFullscreen)el.requestFullscreen();}}
function presentationView(){{setZoom(1.25);const el=document.getElementById('viewport');if(el.requestFullscreen)el.requestFullscreen();}}
function applyFilters(){{const q=document.getElementById('search').value.toLowerCase();const dep=document.getElementById('dept').value;document.querySelectorAll('.process-box,.gate,.action-box').forEach(el=>{{const id=+el.dataset.id;const p=processes.find(x=>x.id===id);const okQ=!q||JSON.stringify(p).toLowerCase().includes(q);const okD=dep==='ALL'||p.owner===dep;el.classList.toggle('dim',!(okQ&&okD));el.classList.toggle('highlight',okQ&&q.length>1);}})}}
function showDetail(id){{const p=processes.find(x=>x.id===id);const c=departments[p.owner];document.getElementById('modalBody').innerHTML=`<span class='badge' style='background:${{c.soft}};color:${{c.color}}'>${{p.owner}}</span><h2>${{p.id}}. ${{p.name}}</h2><div class='detailGrid'><div class='detail'><b>KEGIATAN UTAMA</b><span>${{p.activity}}</span></div><div class='detail'><b>OUTPUT</b><span>${{p.output}}</span></div><div class='detail'><b>DECISION GATE</b><span>${{p.gate}}</span></div><div class='detail'><b>GO / LOLOS</b><span>${{p.go}}</span></div><div class='detail'><b>NO-GO / TINDAKAN</b><span><strong>${{p.nogo}}</strong><br>${{p.solution}}</span></div><div class='detail'><b>ESKALASI</b><span>${{p.escalation}}</span></div><div class='detail'><b>DOKUMEN</b><span>${{p.documents}}</span></div><div class='detail'><b>SLA</b><span>${{p.sla}}</span></div><div class='detail'><b>KPI</b><span>${{p.kpi}}</span></div><div class='detail'><b>RISIKO</b><span>${{p.risk}}</span></div></div>`;document.getElementById('modal').style.display='flex';}}
function showParallelDetail(index){{const item=parallelAuthority[index];const c=departments[item.department];document.getElementById('modalBody').innerHTML=`<span class='badge' style='background:${{c.soft}};color:${{c.color}}'>${{item.department}}</span><h2>${{item.title}}</h2><div class='detailGrid'><div class='detail'><b>KEWENANGAN / AKTIVITAS</b><span>${{item.detail}}</span></div><div class='detail'><b>OUTPUT</b><span>${{item.output}}</span></div><div class='detail'><b>ALUR BERIKUTNYA</b><span>Dikonsolidasikan kembali oleh Sales untuk review internal dan penyusunan proposal final sebelum dikirim kepada customer.</span></div><div class='detail'><b>POLA KERJA</b><span>Dilaksanakan paralel bersama departemen terkait setelah Internal Review berstatus GO.</span></div></div>`;document.getElementById('modal').style.display='flex';}}
function closeModal(){{document.getElementById('modal').style.display='none'}}
document.querySelectorAll('.process-box,.gate,.action-box').forEach(el=>el.addEventListener('click',()=>showDetail(+el.dataset.id)));
document.querySelectorAll('.parallel-card').forEach(el=>el.addEventListener('click',()=>showParallelDetail(+el.dataset.parallel)));
setZoom(1.12);
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
        5: ["Sales", "Product Development", "Finance", "Legal", "Procurement", "HSEQ", "Operation"],
        6: ["Product Development", "Finance", "Legal"], 7: ["Legal", "Finance", "Product Development"],
        8: ["Sales", "Finance"], 9: ["Sales", "Product Development", "Procurement", "Finance", "HSEQ"],
        10: ["Operation", "Finance", "Product Development", "HSEQ"], 11: ["Product Development", "Procurement", "HSEQ", "After Sales"],
        12: ["Operation", "HSEQ", "After Sales"], 13: ["Sales", "Product Development", "Legal", "HSEQ"],
        14: ["Sales", "Operation"], 15: ["Sales", "Legal"], 16: ["Operation", "Product Development"],
        17: ["Sales", "Operation"], 18: ["After Sales", "Product Development"],
    }
    return mapping.get(p["id"], [])

# -----------------------------
# Extended application helpers
# -----------------------------
PHASES = [
    {"name":"Opportunity", "ids":[1,2,3], "owner":"Sales + Product Development"},
    {"name":"Solution & Approval", "ids":[4,5,6], "owner":"Management + Sales + PD + HSEQ + Legal + Procurement + Operation"},
    {"name":"Commercial", "ids":[7,8], "owner":"Sales + Legal + Finance"},
    {"name":"Delivery", "ids":[9,10,11], "owner":"Operation + Procurement + HSEQ"},
    {"name":"Acceptance & Cash", "ids":[12,13,14,15], "owner":"PD + Operation + HSEQ + Finance"},
    {"name":"Customer Growth", "ids":[16,17,18], "owner":"After Sales + Sales"},
]

def process_dataframe():
    return pd.DataFrame([{
        "ID":p["id"], "Stage":p["stage"], "Process":p["name"], "Owner":p["owner"],
        "Decision Gate":p["gate"], "GO":p["go"], "NO-GO":p["nogo"],
        "Corrective Action":p["solution"], "Escalation":p["escalation"],
        "Output":p["output"], "Documents":p["documents"], "SLA":p["sla"],
        "KPI":p["kpi"], "Risk":p["risk"]
    } for p in PROCESSES])

def sop_html_document():
    rows=[]
    for p in PROCESSES:
        rows.append(f"""<section><h2>{p['id']}. {escape(p['name'])}</h2>
        <p><b>Owner:</b> {escape(p['owner'])} | <b>SLA:</b> {escape(p['sla'])}</p>
        <table><tr><th>Kegiatan</th><td>{escape(p['activity'])}</td></tr>
        <tr><th>Output</th><td>{escape(p['output'])}</td></tr>
        <tr><th>Decision Gate</th><td>{escape(p['gate'])}</td></tr>
        <tr><th>GO</th><td>{escape(p['go'])}</td></tr>
        <tr><th>NO-GO</th><td>{escape(p['nogo'])}: {escape(p['solution'])}</td></tr>
        <tr><th>Eskalasi</th><td>{escape(p['escalation'])}</td></tr>
        <tr><th>Dokumen</th><td>{escape(p['documents'])}</td></tr>
        <tr><th>KPI</th><td>{escape(p['kpi'])}</td></tr>
        <tr><th>Risiko</th><td>{escape(p['risk'])}</td></tr></table></section>""")
    return ("""<!doctype html><html><head><meta charset='utf-8'><title>STARCOM SOP</title>
    <style>body{font-family:Arial;margin:34px;color:#10283a}h1{color:#071e33}h2{margin-top:28px;border-bottom:2px solid #1477c9;padding-bottom:5px}table{border-collapse:collapse;width:100%}th,td{border:1px solid #ccd8e3;padding:8px;vertical-align:top}th{width:180px;background:#eef5fb;text-align:left}@media print{section{page-break-inside:avoid}}</style>
    </head><body><h1>PT Starcom Solusindo — SOP Sales to After Sales</h1>""" + ''.join(rows) + "</body></html>")

def render_process_detail(p):
    st.markdown(f"## {p['id']}. {p['name']}")
    st.caption(f"Process owner: {p['owner']} · SLA: {p['sla']}")
    left, right = st.columns(2)
    with left:
        st.markdown(f"**Kegiatan utama**  \n{p['activity']}")
        st.markdown(f"**Output utama**  \n{p['output']}")
        st.markdown(f"**Dokumen**  \n{p['documents']}")
        st.markdown(f"**KPI**  \n{p['kpi']}")
    with right:
        st.markdown(f"**Decision gate**  \n{p['gate']}")
        st.success(p['go'])
        st.error(f"{p['nogo']} — {p['solution']}")
        st.warning(f"Eskalasi: {p['escalation']}")
        st.markdown(f"**Risiko utama**  \n{p['risk']}")

# -----------------------------
# Pages
# -----------------------------
if page == "Swimlane Flow":
    html, h = build_swimlane_html(PROCESSES)
    components.html(html, height=1120, scrolling=False)

elif page == "Executive Flow":
    st.markdown('<div class="section-title">Executive Flow — Drill-down</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    for i, phase in enumerate(PHASES):
        items=[p for p in PROCESSES if p["id"] in phase["ids"]]
        with cols[i % 3]:
            st.markdown(f"<div class='metric-card' style='min-height:145px'><b style='font-size:18px'>{i+1}. {phase['name']}</b><p style='color:#29435F'>{' → '.join(x['name'] for x in items)}</p><span>OWNER: {phase['owner']}</span></div>", unsafe_allow_html=True)
    selected_phase=st.selectbox("Drill-down tahapan", [x["name"] for x in PHASES])
    phase=next(x for x in PHASES if x["name"]==selected_phase)
    for p in [x for x in PROCESSES if x["id"] in phase["ids"]]:
        with st.expander(f"{p['id']}. {p['name']} — {p['owner']}", expanded=True):
            c1,c2,c3=st.columns(3)
            c1.markdown(f"**Aktivitas**  \n{p['activity']}")
            c2.markdown(f"**Gate**  \n{p['gate']}  \n\n**GO:** {p['go']}")
            c3.markdown(f"**No-Go / Eskalasi**  \n{p['nogo']}  \n\n{p['solution']}  \n\n{p['escalation']}")

elif page == "Department Authority":
    st.markdown('<div class="section-title">Department Authority</div>', unsafe_allow_html=True)
    selected = st.selectbox("Pilih departemen", list(DEPARTMENTS.keys()))
    owned = [p for p in PROCESSES if p["owner"] == selected]
    support = [p for p in PROCESSES if selected in infer_support(p)]
    m1,m2=st.columns(2)
    m1.metric("Process owner", len(owned))
    m2.metric("Consulted/support", len(support))
    st.markdown(f"### {selected}")
    for p in owned:
        with st.expander(f"{p['id']}. {p['name']}", expanded=True):
            render_process_detail(p)

elif page == "Process Detail":
    st.markdown('<div class="section-title">Process Detail</div>', unsafe_allow_html=True)
    label = st.selectbox("Pilih proses", [f"{p['id']}. {p['name']}" for p in PROCESSES])
    p = PROCESSES[int(label.split('.')[0]) - 1]
    render_process_detail(p)

elif page == "KPI Dashboard":
    st.markdown('<div class="section-title">KPI Dashboard</div>', unsafe_allow_html=True)
    st.caption("Nilai awal dapat diubah pada panel input. Dashboard menghubungkan KPI operasional dengan setiap proses SOP.")
    selected_dep=st.selectbox("Filter departemen", ["Semua"]+list(DEPARTMENTS.keys()))
    filtered=PROCESSES if selected_dep=="Semua" else [p for p in PROCESSES if p["owner"]==selected_dep]
    default_scores={p['id']: max(62, 94-(p['id']%6)*4) for p in PROCESSES}
    scores=[]
    with st.expander("Input realisasi KPI", expanded=False):
        for p in filtered:
            scores.append({"Process":p["name"],"Owner":p["owner"],"Achievement":st.slider(p["name"],0,100,default_scores[p['id']],key=f"kpi_{p['id']}"),"KPI":p["kpi"]})
    if not scores:
        scores=[{"Process":p["name"],"Owner":p["owner"],"Achievement":default_scores[p['id']],"KPI":p["kpi"]} for p in filtered]
    df=pd.DataFrame(scores)
    avg=float(df["Achievement"].mean()) if not df.empty else 0
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Rata-rata capaian",f"{avg:.1f}%")
    c2.metric("Proses sesuai target",int((df["Achievement"]>=85).sum()))
    c3.metric("Perlu perhatian",int(((df["Achievement"]>=70)&(df["Achievement"]<85)).sum()))
    c4.metric("Kritis",int((df["Achievement"]<70).sum()))
    st.bar_chart(df.set_index("Process")["Achievement"], horizontal=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

elif page == "Approval Workflow":
    st.markdown('<div class="section-title">Approval Workflow</div>', unsafe_allow_html=True)
    st.caption("Alur persetujuan berjenjang Manager → Department Head → Director, dengan pengembalian revisi ke process owner.")
    approval_steps=[
        ("1", "Process Owner", "Menyiapkan data, dokumen, dan rekomendasi"),
        ("2", "Manager", "Validasi kelengkapan, feasibility, dan risiko fungsi"),
        ("3", "Department Head", "Menilai dampak lintas fungsi, biaya, resource, dan SLA"),
        ("4", "Director", "Persetujuan risiko strategis, komersial, dan deviasi material"),
        ("5", "Execution", "Keputusan GO terdokumentasi dan diserahkan ke PIC eksekusi"),
    ]
    for no,title,desc in approval_steps:
        st.markdown(f"<div class='metric-card'><b style='font-size:18px'>{no}. {title}</b><p>{desc}</p></div>", unsafe_allow_html=True)
        if no!="5": st.markdown("<div style='text-align:center;font-size:28px'>↓</div>", unsafe_allow_html=True)
    st.warning("Jika ditolak atau perlu revisi, dokumen dikembalikan ke Process Owner dengan catatan, PIC, target waktu, dan batas eskalasi yang jelas.")
    st.markdown("### Matriks batas kewenangan")
    approval_df=pd.DataFrame([
        ["Operasional rutin / sesuai budget","Manager","Department Head"],
        ["Lintas departemen / deviasi SLA","Department Head","Director"],
        ["Diskon, margin, liability, atau risiko material","Director","Direksi terkait"],
        ["No-Go strategis / penghentian opportunity atau proyek","Director","Direktur Utama"],
    ],columns=["Jenis keputusan","Approver minimum","Eskalasi"])
    st.dataframe(approval_df,use_container_width=True,hide_index=True)

elif page == "SOP Search":
    st.markdown('<div class="section-title">Enterprise SOP Search</div>', unsafe_allow_html=True)
    q=st.text_input("Cari proses, departemen, dokumen, KPI, risiko, atau kata kunci", placeholder="Contoh: BAST, Legal, invoice, survey, SLA...")
    dep=st.selectbox("Departemen",["Semua"]+list(DEPARTMENTS.keys()))
    results=[]
    for p in PROCESSES:
        hay=json.dumps(p,ensure_ascii=False).lower()
        if (not q or q.lower() in hay) and (dep=="Semua" or p["owner"]==dep): results.append(p)
    st.caption(f"{len(results)} proses ditemukan")
    for p in results:
        with st.expander(f"{p['id']}. {p['name']} — {p['owner']}", expanded=bool(q)):
            render_process_detail(p)

elif page == "Export Center":
    st.markdown('<div class="section-title">Export Center</div>', unsafe_allow_html=True)
    st.caption("Unduh register SOP untuk pengolahan lanjutan atau dokumen HTML siap cetak menjadi PDF.")
    df=process_dataframe()
    c1,c2=st.columns(2)
    with c1:
        st.markdown("### Register SOP")
        st.download_button("Download CSV", data=df.to_csv(index=False).encode("utf-8-sig"), file_name="STARCOM_SOP_Register.csv", mime="text/csv", use_container_width=True)
        output=io.BytesIO()
        with pd.ExcelWriter(output,engine="openpyxl") as writer: df.to_excel(writer,index=False,sheet_name="SOP Register")
        st.download_button("Download Excel", data=output.getvalue(), file_name="STARCOM_SOP_Register.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    with c2:
        st.markdown("### Dokumen SOP")
        html_doc=sop_html_document().encode("utf-8")
        st.download_button("Download HTML siap cetak PDF",data=html_doc,file_name="STARCOM_SOP_Print.html",mime="text/html",use_container_width=True)
        st.info("Buka file HTML, lalu gunakan Print → Save as PDF untuk menghasilkan PDF berformat SOP perusahaan.")
    st.dataframe(df,use_container_width=True,hide_index=True)

elif page == "Presentation Mode":
    st.markdown('<div class="section-title">Presentation Mode</div>', unsafe_allow_html=True)
    st.info("Gunakan fullscreen pada toolbar. Pilih satu tahapan untuk presentasi ringkas atau tampilkan seluruh alur.")
    mode=st.selectbox("Materi presentasi",["Seluruh alur"]+[x["name"] for x in PHASES])
    shown=PROCESSES if mode=="Seluruh alur" else [p for p in PROCESSES if p["id"] in next(x for x in PHASES if x["name"]==mode)["ids"]]
    html,h=build_swimlane_html(shown,presentation=True)
    components.html(html,height=2050,scrolling=True)
