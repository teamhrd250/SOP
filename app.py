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
}

PROCESSES = [
    {
        "id": 1, "stage": "LEAD", "name": "Lead Generation", "owner": "Sales",
        "activity": "Mencari prospek, referensi, tender, event, dan informasi awal pelanggan.",
        "gate": "Lead sesuai target dan layak ditindaklanjuti?", "go": "Lead memenuhi kriteria awal; lanjut ke Lead Qualification oleh Sales.",
        "nogo": "REJECT / CLOSE LEAD", "solution": "Lead tidak sesuai target pasar, data tidak valid, tidak relevan, atau tidak layak ditindaklanjuti. Catat alasan di CRM dan tutup lead.",
        "escalation": "Sales Manager", "output": "Lead register dan customer profile awal",
        "documents": "Lead register, call note, customer profile", "sla": "1 hari kerja",
        "kpi": "Jumlah lead baru dan lead response rate", "risk": "Lead tidak relevan atau data tidak valid",
    },
    {
        "id": 2, "stage": "QUALIFICATION", "name": "Lead Qualification", "owner": "Sales",
        "activity": "Kualifikasi BANT: budget, authority, need, timeline, serta identifikasi decision maker.",
        "gate": "BANT minimum terpenuhi?", "go": "Qualified opportunity; lanjut ke Product Development untuk Need Assessment awal dan penyusunan BOQ. BOQ kemudian didistribusikan ke Operation dan Procurement, sementara Legal melakukan verifikasi requirement legal secara paralel.",
        "nogo": "REQUALIFY / NURTURE / CLOSE", "solution": "Jika budget, authority, need, timeline, atau informasi awal belum memadai, kembalikan ke Sales untuk klarifikasi/re-kualifikasi. Nurture bila potensial tetapi belum siap; close bila tidak layak.",
        "escalation": "Sales Manager", "output": "Qualified opportunity yang siap diverifikasi lintas fungsi",
        "documents": "Qualification checklist, CRM opportunity, preliminary requirement, manpower/certification check, device availability check, legal requirement checklist", "sla": "2–3 hari kerja",
        "kpi": "Lead-to-opportunity conversion dan verification turnaround time", "risk": "Opportunity semu, resource tidak tersedia, sertifikasi tidak memenuhi, perangkat tidak available, legalitas/tender requirement tidak terpenuhi, atau request tidak sesuai kemampuan",
    },
    {
        "id": 3, "stage": "NEED, SURVEY & BOQ", "name": "Need Assessment, Survey & BOQ", "owner": "Product Development",
        "activity": "Product Development menggali kebutuhan customer, melakukan survey bila diperlukan, menyusun preliminary solution, dan membuat BOQ sebagai technical owner. BOQ didistribusikan ke Operation dan Procurement untuk verifikasi.",
        "gate": "Requirement, data survey, dan BOQ awal sudah cukup untuk diverifikasi lintas fungsi?", "go": "BOQ diterbitkan oleh Product Development dan didistribusikan ke Operation serta Procurement. Legal melakukan verifikasi requirement legal secara paralel.",
        "nogo": "CLARIFY / RESURVEY / REVISE BOQ", "solution": "Lengkapi requirement, lakukan klarifikasi bersama Sales/customer, survey ulang bila diperlukan, dan revisi BOQ sampai cukup untuk diverifikasi Operation dan Procurement.",
        "escalation": "Sales Manager / Product Development Manager", "output": "Customer requirement, survey report, preliminary solution, dan BOQ awal",
        "documents": "MoM, requirement form, survey report, preliminary solution, BOQ", "sla": "3 hari kerja",
        "kpi": "Kelengkapan requirement, ketepatan survey, dan first-pass BOQ verification", "risk": "Requirement ambigu, survey tidak lengkap, quantity/specification BOQ tidak sesuai, atau asumsi teknis tidak valid",
    },
    {
        "id": 4, "stage": "SOLUTION DESIGN", "name": "Solution Design", "owner": "Product Development",
        "activity": "Analisis teknis, arsitektur solusi, BoM/BoQ, estimasi durasi, kapasitas, dan metode implementasi.",
        "gate": "Solusi technically feasible dan dapat dipenuhi?", "go": "Solusi feasible; lanjut ke Internal Review untuk validasi lintas fungsi dan keputusan bisnis.",
        "nogo": "REVISE DESIGN / NO-GO", "solution": "Revisi arsitektur, BoM/BoQ, metode, kapasitas, atau alternatif perangkat. Bila tetap tidak feasible, kembalikan ke Sales untuk keputusan no-go/close opportunity.",
        "escalation": "Product Development Manager", "output": "Technical solution, BoM/BoQ dan estimasi teknis",
        "documents": "Solution design, topology, BoM, BoQ", "sla": "5 hari kerja",
        "kpi": "Design accuracy dan solution acceptance", "risk": "Solusi tidak kompatibel, kapasitas kurang, atau teknologi tidak tersedia",
    },
    {
        "id": 5, "stage": "INTERNAL REVIEW", "name": "Cross-Functional Internal Review", "owner": "Sales",
        "activity": "Review lintas fungsi atas teknis, harga dan margin, legal, supply/vendor, HSEQ, kapasitas tim, jadwal, serta risiko proyek. Sales bertindak sebagai coordinator process; approval/escalation mengikuti batas kewenangan.",
        "gate": "Teknis, komersial, legal, supply, HSEQ, resource, jadwal, dan risiko disetujui?", "go": "Internal Review disetujui; distribusikan pekerjaan secara paralel ke Sales, Product Development, HSEQ, Legal, Procurement, dan Operation sesuai kewenangan masing-masing.",
        "nogo": "REVISE / HOLD / REJECT", "solution": "Kembalikan temuan ke departemen terkait dengan catatan revisi, PIC, target waktu, dan approval ulang. Hold bila menunggu data/approval; reject bila risiko tidak dapat diterima.",
        "escalation": "Department Head / Director sesuai authority matrix", "output": "Internal approval dan go/no-go record",
        "documents": "Approval sheet, risk register, costing", "sla": "3 hari kerja",
        "kpi": "Approval turnaround time", "risk": "Margin rendah, risiko kontrak, lead time, atau kapasitas resource",
    },
    {
        "id": 6, "stage": "PROPOSAL", "name": "Proposal & Quotation", "owner": "Sales",
        "activity": "Sales mengonsolidasikan hasil pekerjaan paralel dari Sales, Product Development, HSEQ, Legal, Procurement, dan Operation; melakukan review internal; lalu mengirim proposal final kepada customer.",
        "gate": "Proposal dan quotation dapat diterima customer sebagai dasar komersial?", "go": "Customer menerima proposal sebagai basis pembahasan; lanjut ke Negotiation untuk finalisasi harga, scope, SLA, dan term.",
        "nogo": "REVISE / RE-SUBMIT / WITHDRAW", "solution": "Konsolidasikan feedback customer, revisi harga/scope/term/solusi sesuai kewenangan, lalu submit ulang. Withdraw bila requirement tidak dapat dipenuhi.",
        "escalation": "Sales Manager", "output": "Proposal final terintegrasi dan quotation resmi",
        "documents": "Quotation, proposal solution & product, dokumen HSEQ, legal requirement checklist, timeline procurement, material readiness, proposal teknis, portfolio project, timeline project, manpower mapping, proposal managed service", "sla": "2 hari kerja",
        "kpi": "Proposal response time dan proposal acceptance", "risk": "Harga tidak kompetitif atau scope tidak dipahami",
    },
    {
        "id": 7, "stage": "NEGOTIATION", "name": "Negotiation", "owner": "Sales",
        "activity": "Negosiasi harga, SLA, garansi, termin pembayaran, delivery, scope, dan klausul komersial.",
        "gate": "Kesepakatan komersial dan scope tercapai?", "go": "Deal tercapai; lanjut ke Contract / PO Parallel Review oleh Legal dan Finance.",
        "nogo": "DEADLOCK / LOST", "solution": "Lakukan final offer atau eskalasi sesuai kewenangan. Jika tetap tidak tercapai kesepakatan, dokumentasikan lost reason dan tutup opportunity.",
        "escalation": "Sales Director", "output": "Negotiation record dan final commercial terms",
        "documents": "Negotiation note, final quotation", "sla": "Sesuai timeline pelanggan",
        "kpi": "Win rate dan average closing cycle", "risk": "Diskon berlebihan atau klausul tidak seimbang",
    },
    {
        "id": 8, "stage": "CONTRACT / PO", "name": "Contract / PO Parallel Review", "owner": "Legal",
        "activity": "Legal dan Finance melakukan review Contract/PO secara paralel. Legal menilai aspek kontraktual dan kepatuhan; Finance menilai aspek komersial, pembayaran, pajak, invoice, cash flow, dan risiko finansial.",
        "gate": "Legal dan Finance keduanya memberikan clearance?", "go": "ALL GO: Legal dan Finance clear; hasil review digabungkan lalu lanjut ke Kick Off Internal.",
        "nogo": "REVISE CONTRACT / PO / ESCALATE", "solution": "Temuan Legal atau Finance dikembalikan ke Sales/customer untuk revisi kontrak, PO, SLA, payment term, tax, invoice requirement, atau approval risiko Direksi. Tidak boleh lanjut sebelum keduanya clear.",
        "escalation": "Legal Manager / Finance Manager / Director", "output": "Contract/PO tervalidasi secara legal dan finansial",
        "documents": "PO, contract, SLA, NDA, payment term, tax requirement, invoice requirement, bank guarantee (jika ada)", "sla": "3–5 hari kerja",
        "kpi": "Contract/PO review turnaround time dan first-pass approval", "risk": "Klausul berat sebelah, termin pembayaran tidak aman, pajak/invoice tidak sesuai, atau risiko cash flow",
    },
    {
        "id": 9, "stage": "PROJECT KICK OFF", "name": "Kick Off Internal", "owner": "Operation",
        "activity": "Handover Sales ke Project, penetapan PM/tim, project plan, baseline scope, biaya, dan jadwal.",
        "gate": "Project siap dieksekusi?", "go": "Handover lengkap, PM/tim, scope, WBS, jadwal, budget, dan risiko disepakati; lanjut ke Procurement & Logistics.",
        "nogo": "REVISE PROJECT PLAN", "solution": "Lengkapi handover, baseline scope, WBS, resource, jadwal, budget, HSEQ requirement, dan risk register sebelum eksekusi.",
        "escalation": "Project Manager / Operation Manager", "output": "Project charter dan baseline plan",
        "documents": "Kick-off MoM, WBS, project schedule", "sla": "2 hari kerja setelah PO",
        "kpi": "Kick-off readiness", "risk": "Handover tidak lengkap atau baseline tidak disepakati",
    },
    {
        "id": 10, "stage": "PROCUREMENT", "name": "Procurement & Logistics", "owner": "Procurement",
        "activity": "Pengadaan barang/jasa, seleksi vendor, monitoring lead time, inspeksi, dan distribusi material.",
        "gate": "Material/perangkat siap sesuai spesifikasi dan jadwal?", "go": "Material ready dan sesuai requirement; release ke Operation untuk Implementation.",
        "nogo": "ALTERNATIVE / EXPEDITE / RESCHEDULE", "solution": "Cari vendor/perangkat alternatif, lakukan expediting atau partial delivery, koreksi spesifikasi bila diperlukan, dan revisi jadwal dengan approval terkait.",
        "escalation": "Procurement Manager", "output": "Material tersedia sesuai spesifikasi dan jadwal",
        "documents": "PR, PO vendor, delivery note, inspection record", "sla": "Sesuai lead time",
        "kpi": "On-time delivery dan procurement saving", "risk": "Keterlambatan, spesifikasi salah, atau vendor gagal",
    },
    {
        "id": 11, "stage": "IMPLEMENTATION", "name": "Implementation", "owner": "Operation",
        "activity": "Instalasi, konfigurasi, integrasi, quality control, dokumentasi, dan monitoring progres.",
        "gate": "Implementasi selesai sesuai scope dan siap diuji?", "go": "Instalasi, konfigurasi, integrasi, QC, dan dokumentasi siap; lanjut ke Testing & Commissioning oleh Operation.",
        "nogo": "CORRECTIVE ACTION / RE-PLAN", "solution": "Lakukan corrective action, re-plan, percepatan, penambahan resource, atau koordinasi akses/site. Setelah koreksi selesai, verifikasi ulang kesiapan testing.",
        "escalation": "Project Manager", "output": "Pekerjaan terpasang dan siap diuji",
        "documents": "Daily report, checklist, as-built draft", "sla": "Sesuai project schedule",
        "kpi": "On-time completion, quality, HSE compliance", "risk": "Site tidak siap, akses tertunda, kualitas instalasi, atau HSE incident",
    },
    {
        "id": 12, "stage": "TESTING", "name": "Testing & Commissioning", "owner": "Operation",
        "activity": "Operation melaksanakan Testing & Commissioning setelah Implementation atau Managed Service, termasuk SAT/UAT, pengujian fungsi, performance, integrasi, troubleshooting awal, dan penyusunan hasil pengujian.",
        "gate": "Hasil testing memenuhi acceptance criteria?", "go": "Testing lulus dan evidence lengkap; lanjut ke BAST / Acceptance.",
        "nogo": "REPAIR / RECTIFY / RETEST", "solution": "Lakukan troubleshooting dan corrective action pada temuan, update konfigurasi/instalasi bila perlu, lalu retest sampai acceptance criteria terpenuhi.",
        "escalation": "Project Manager / Operation Manager", "output": "Test report lulus dan acceptance evidence",
        "documents": "FAT, SAT, UAT, test report", "sla": "2–5 hari kerja",
        "kpi": "First-pass yield, defect closure time, dan testing completion", "risk": "Fungsi gagal, performa tidak memenuhi, atau integrasi bermasalah",
    },
    {
        "id": 13, "stage": "ACCEPTANCE", "name": "BAST / Acceptance", "owner": "Operation",
        "activity": "Serah terima pekerjaan, finalisasi dokumen, as-built, checklist, training, dan punch list.",
        "gate": "Customer menerima hasil pekerjaan dan dokumen serah terima?", "go": "Customer approve dan BAST ditandatangani; dokumen diserahkan ke Finance untuk proses Invoice.",
        "nogo": "PUNCH LIST / RE-ACCEPTANCE", "solution": "Selesaikan punch list/temuan, lengkapi dokumen, lakukan verifikasi ulang bersama customer, lalu ajukan acceptance/BAST kembali.",
        "escalation": "Project Manager", "output": "BAST ditandatangani dan dokumen final",
        "documents": "BAST, as-built, training record, punch list", "sla": "Maks. 5 hari setelah pekerjaan selesai",
        "kpi": "BAST cycle time dan punch-list closure", "risk": "Dokumen tidak lengkap atau customer menunda acceptance",
    },
    {
        "id": 14, "stage": "INVOICE", "name": "Invoice", "owner": "Finance",
        "activity": "Penerbitan invoice, faktur pajak, verifikasi dokumen pendukung, dan pengiriman ke customer.",
        "gate": "Invoice dan dokumen pendukung diterima customer?", "go": "Invoice accepted dan tercatat customer; lanjut ke Payment & Collection sesuai termin.",
        "nogo": "REVISE / RESUBMIT INVOICE", "solution": "Perbaiki invoice, faktur pajak, data PO/kontrak, BAST, atau persyaratan administrasi, kemudian submit ulang dan konfirmasi penerimaan.",
        "escalation": "Finance Manager", "output": "Invoice diterima dan tercatat customer",
        "documents": "Invoice, tax invoice, BAST, PO", "sla": "1–2 hari kerja",
        "kpi": "Billing accuracy dan billing cycle time", "risk": "Dokumen kurang atau kesalahan data invoice",
    },
    {
        "id": 15, "stage": "PAYMENT", "name": "Payment & Collection", "owner": "Finance",
        "activity": "Monitoring jatuh tempo, reminder, collection, rekonsiliasi, dan pelaporan aging piutang.",
        "gate": "Pembayaran diterima penuh dan ter-rekonsiliasi?", "go": "Pembayaran lunas dan rekonsiliasi selesai; lanjut ke After Sales / Support dan monitoring layanan.",
        "nogo": "COLLECTION / DISPUTE / ESCALATE", "solution": "Lakukan reminder dan collection, selesaikan dispute invoice, negosiasikan penyelesaian sesuai kontrak, atau eskalasi ke manajemen bila overdue.",
        "escalation": "Finance Manager / Director", "output": "Pembayaran diterima dan direkonsiliasi",
        "documents": "Aging report, payment receipt, collection note", "sla": "Sesuai termin kontrak",
        "kpi": "DSO dan overdue ratio", "risk": "Keterlambatan pembayaran atau dispute invoice",
    },
    {
        "id": 16, "stage": "AFTER SALES", "name": "After Sales / Support", "owner": "After Sales",
        "activity": "Warranty, helpdesk, ticketing, preventive/corrective maintenance, dan monitoring SLA.",
        "gate": "Layanan sesuai SLA dan tidak ada complaint terbuka?", "go": "Layanan normal dan SLA terpenuhi; lanjut monitoring berkala dan Customer Satisfaction Review.",
        "nogo": "INCIDENT / COMPLAINT / RCA", "solution": "Klasifikasikan severity, lakukan troubleshooting, RCA dan corrective/preventive action, update customer, verifikasi recovery, lalu close ticket sesuai SLA.",
        "escalation": "After Sales Manager", "output": "Ticket terselesaikan dan SLA tercapai",
        "documents": "Ticket, service report, RCA/CAPA", "sla": "Sesuai SLA",
        "kpi": "SLA compliance, MTTR, repeat incident", "risk": "Gangguan berulang atau respons terlambat",
    },
    {
        "id": 17, "stage": "SATISFACTION", "name": "Customer Satisfaction", "owner": "After Sales",
        "activity": "Survey kepuasan, evaluasi layanan, review performa, dan identifikasi improvement.",
        "gate": "Customer puas terhadap layanan dan hasil pekerjaan?", "go": "Customer puas; lanjut ke Repeat Order / Upselling dan account development.",
        "nogo": "SERVICE RECOVERY / IMPROVEMENT PLAN", "solution": "Susun improvement plan, lakukan service recovery, perbaiki SLA/proses terkait, review dengan customer, dan lakukan pengukuran kepuasan ulang.",
        "escalation": "After Sales Manager / Director", "output": "CSI/NPS dan improvement plan",
        "documents": "Customer survey, service review MoM", "sla": "Maks. 30 hari setelah acceptance",
        "kpi": "CSI/NPS dan complaint recurrence", "risk": "Kepuasan rendah dan churn customer",
    },
    {
        "id": 18, "stage": "REPEAT & GROWTH", "name": "Repeat Order / Upselling", "owner": "Sales",
        "activity": "Identifikasi kebutuhan baru, renewal, upgrade, cross-selling, upselling, dan kontrak maintenance.",
        "gate": "Terdapat opportunity baru, renewal, upgrade, atau upselling?", "go": "Opportunity teridentifikasi; kembali ke Lead Qualification untuk proses opportunity berikutnya.",
        "nogo": "ACCOUNT NURTURE", "solution": "Belum ada opportunity aktif; lakukan account review, relationship management, monitoring kebutuhan, dan follow-up berkala.",
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
        "output": "Quotation",
        "go": "Quotation lengkap dan sesuai approval komersial; serahkan ke Sales untuk konsolidasi proposal final.",
        "nogo": "Revisi bila harga, margin, term, SLA, warranty, atau payment term belum sesuai approval."
    },
    {
        "department": "Product Development",
        "title": "Proposal Solution & Product",
        "detail": "Penyusunan solusi, arsitektur, produk, BoM/BoQ, spesifikasi, dan pendekatan teknis produk.",
        "output": "Proposal Solution & Product",
        "go": "Proposal Solution & Product lengkap dan konsisten dengan requirement/BoM/BoQ; serahkan ke Sales untuk konsolidasi.",
        "nogo": "Revisi bila arsitektur, produk, spesifikasi, BoM/BoQ, atau pendekatan solusi belum memenuhi requirement."
    },
    {
        "department": "HSEQ",
        "title": "Dokumen HSEQ",
        "detail": "CSMS, RKPLH, dan dokumen pra-kualifikasi HSEQ apabila dipersyaratkan oleh customer atau tender.",
        "output": "Dokumen CSMS / RKPLH / Pra-Kualifikasi HSEQ",
        "go": "Dokumen HSEQ yang dipersyaratkan lengkap/valid atau dinyatakan tidak diperlukan; serahkan status ke Sales.",
        "nogo": "Lengkapi atau revisi CSMS, RKPLH, dan dokumen pra-kualifikasi sebelum proposal final dikirim."
    },
    {
        "department": "Legal",
        "title": "Collect Legalitas Requirement Project",
        "detail": "Mengumpulkan dan memverifikasi legalitas yang dipersyaratkan untuk project, termasuk dokumen perusahaan, perizinan, kontrak, NDA, dan kebutuhan legal customer atau tender.",
        "output": "Legal Requirement Checklist",
        "go": "Legal requirement project teridentifikasi dan dokumen tersedia/terverifikasi; serahkan checklist ke Sales.",
        "nogo": "Lengkapi legalitas/perizinan/dokumen perusahaan atau eskalasi gap legal sebelum proposal final."
    },
    {
        "department": "Procurement",
        "title": "Timeline & Material Readiness",
        "detail": "Timeline pengadaan, kesiapan material, lead time vendor, dan alternatif supply bila diperlukan.",
        "output": "Timeline Pengadaan & Material Readiness",
        "go": "Timeline pengadaan, lead time, dan material readiness feasible; serahkan hasil ke Sales untuk konsolidasi.",
        "nogo": "Revisi sourcing plan, lead time, alternatif material/vendor, atau jadwal bila belum feasible."
    },
    {
        "department": "Operation",
        "title": "Proposal Teknis & Project Plan",
        "detail": "Proposal teknis, portfolio project, timeline project, manpower mapping, serta proposal managed service.",
        "output": "Proposal Teknis, Project Plan & Managed Service",
        "go": "Proposal teknis, portfolio, timeline project, manpower mapping, dan managed service plan lengkap; serahkan ke Sales.",
        "nogo": "Revisi scope teknis, timeline, manpower mapping, metode implementasi, atau managed service plan bila belum feasible."
    },
]

CONTRACT_REVIEW_PARALLEL = [
    {
        "department": "Legal",
        "title": "Legal Contract Review",
        "detail": "Review kontrak, SLA, NDA, liability, warranty, acceptance, hak dan kewajiban para pihak, serta legal requirement project.",
        "output": "Legal Review & Contract Comments",
        "go": "Legal memberikan clearance atas kontrak, SLA, NDA, liability, warranty, acceptance, hak/kewajiban, dan legal requirement.",
        "nogo": "Kembalikan ke Sales/customer untuk revisi klausul atau eskalasi risiko legal; tidak boleh merge sebelum Legal clear."
    },
    {
        "department": "Finance",
        "title": "Finance Contract / PO Review",
        "detail": "Review nilai PO/kontrak, payment term, pajak, invoice requirement, cash flow, financial risk, dan bank guarantee apabila dipersyaratkan.",
        "output": "Finance Review & Commercial Clearance",
        "go": "Finance memberikan clearance atas nilai PO/kontrak, payment term, tax, invoice requirement, cash flow, dan financial risk.",
        "nogo": "Kembalikan ke Sales/customer untuk revisi aspek finansial/PO/payment/tax/invoice atau eskalasi risiko; tidak boleh merge sebelum Finance clear."
    },
]

LEAD_QUALIFICATION_VERIFICATION = [
    {
        "department": "Product Development",
        "title": "Need Assessment & BOQ Preparation",
        "detail": "Product Development menjadi technical owner untuk menyusun preliminary solution dan BOQ berdasarkan requirement serta hasil survey.",
        "output": "Preliminary Solution & BOQ",
        "go": "BOQ cukup lengkap untuk didistribusikan ke Operation dan Procurement.",
        "nogo": "Klarifikasi requirement dan revisi BOQ sebelum didistribusikan."
    },
    {
        "department": "Operation",
        "title": "BOQ Operational Verification",
        "detail": "Memverifikasi BOQ terhadap manpower, kompetensi/sertifikasi, tools, metode kerja, akses/site, resource pendukung, kebutuhan instalasi, dan kesesuaian quantity terhadap kebutuhan lapangan.",
        "output": "Operation BOQ Verification & Readiness",
        "go": "Operation menyatakan BOQ dapat dieksekusi dari sisi manpower, tools, metode, sertifikasi, resource, dan kebutuhan implementasi.",
        "nogo": "BOQ dikembalikan ke Product Development untuk revisi jika quantity, resource, metode, sertifikasi, tools, atau asumsi lapangan tidak sesuai."
    },
    {
        "department": "Procurement",
        "title": "BOQ Supply & Availability Verification",
        "detail": "Memverifikasi BOQ terhadap availability perangkat/material, part number/specification, vendor/principal, lead time, alternatif supply, minimum order, dan risiko pengadaan.",
        "output": "Procurement BOQ Verification & Supply Readiness",
        "go": "Procurement menyatakan item BOQ tersedia atau memiliki sourcing plan yang memenuhi spesifikasi, quantity, dan lead time.",
        "nogo": "BOQ dikembalikan ke Product Development untuk revisi jika material/perangkat tidak available, spesifikasi tidak sesuai, lead time tidak memenuhi, atau diperlukan alternatif supply."
    },
    {
        "department": "Legal",
        "title": "Legal Requirement Verification",
        "detail": "Memverifikasi legalitas dan dokumen kepatuhan project/tender, termasuk legalitas perusahaan, perizinan, NDA, persyaratan customer, dokumen tender, dan izin pendukung.",
        "output": "Legal Requirement Verification & Gap List",
        "go": "Legal menyatakan requirement legal sudah teridentifikasi dan dokumen tersedia atau memiliki rencana pemenuhan yang dapat diterima.",
        "nogo": "Kembalikan ke Sales untuk klarifikasi atau pemenuhan dokumen legal yang belum tersedia atau tidak memenuhi."
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
    """Build a conventional horizontal cross-functional SOP swimlane.

    The diagram follows the normal corporate SOP convention: departments are
    horizontal lanes, process sequence runs from left to right, and the canvas
    remains at a readable scale with internal scrolling and fullscreen controls.
    """
    deps = list(DEPARTMENTS.keys())
    left_w = 205
    top_h = 112
    col_w = 205
    lane_h = 132
    right_pad = 80
    width = left_w + len(processes) * col_w + right_pad
    height = top_h + len(deps) * lane_h + 180

    p_json = json.dumps(processes, ensure_ascii=False)
    dep_json = json.dumps(DEPARTMENTS, ensure_ascii=False)
    parallel_json = json.dumps(PARALLEL_AUTHORITY, ensure_ascii=False)
    contract_review_json = json.dumps(CONTRACT_REVIEW_PARALLEL, ensure_ascii=False)
    lead_verification_json = json.dumps(LEAD_QUALIFICATION_VERIFICATION, ensure_ascii=False)

    lane_y = {dep: top_h + i * lane_h for i, dep in enumerate(deps)}
    col_x = {p["id"]: left_w + (i * col_w) for i, p in enumerate(processes)}

    lane_parts = []
    sticky_lane_parts = []
    for i, dep in enumerate(deps):
        cfg = DEPARTMENTS[dep]
        y = lane_y[dep]
        fill = "#FFFFFF" if i % 2 == 0 else "#F8FBFE"
        lane_parts.append(f'<rect x="0" y="{y}" width="{width}" height="{lane_h}" fill="{fill}"/>')
        lane_parts.append(f'<rect x="0" y="{y}" width="{left_w}" height="{lane_h}" fill="{cfg["soft"]}" stroke="{cfg["color"]}" stroke-width="1.2"/>')
        lane_parts.append(f'<rect x="0" y="{y}" width="7" height="{lane_h}" fill="{cfg["color"]}"/>')
        label_lines = split_lines(dep.upper(), 18)[:2]
        for li, line in enumerate(label_lines):
            lane_parts.append(f'<text x="22" y="{y+52+li*18}" class="laneLabel">{escape(line)}</text>')
        lane_parts.append(f'<text x="22" y="{y+96}" class="laneSub">PROCESS OWNER / SUPPORT</text>')
        lane_parts.append(f'<line x1="0" y1="{y+lane_h}" x2="{width}" y2="{y+lane_h}" class="laneLine"/>')

        sticky_lane_parts.append(f'<rect x="0" y="{y}" width="{left_w}" height="{lane_h}" fill="{cfg["soft"]}" stroke="{cfg["color"]}" stroke-width="1.2"/>')
        sticky_lane_parts.append(f'<rect x="0" y="{y}" width="7" height="{lane_h}" fill="{cfg["color"]}"/>')
        for li, line in enumerate(label_lines):
            sticky_lane_parts.append(f'<text x="22" y="{y+52+li*18}" class="laneLabel">{escape(line)}</text>')
        sticky_lane_parts.append(f'<text x="22" y="{y+96}" class="laneSub">PROCESS OWNER / SUPPORT</text>')
        sticky_lane_parts.append(f'<line x1="0" y1="{y+lane_h}" x2="{left_w}" y2="{y+lane_h}" class="laneLine"/>')

    stage_parts = []
    for i, p in enumerate(processes):
        x = col_x[p["id"]]
        stage_parts.append(f'<rect x="{x}" y="0" width="{col_w}" height="{top_h}" fill="{("#F1F6FB" if i%2==0 else "#EAF2F9")}" stroke="#C8D6E4"/>')
        stage_parts.append(f'<text x="{x+col_w/2}" y="24" text-anchor="middle" class="stageNo">{p["id"]:02d}</text>')
        for li, line in enumerate(split_lines(p["stage"], 18)[:3]):
            stage_parts.append(f'<text x="{x+col_w/2}" y="48+{li*16}" text-anchor="middle" class="stageTitle">{escape(line)}</text>')
        stage_parts.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{height-20}" class="colLine"/>')
    stage_parts.append(f'<line x1="{left_w+len(processes)*col_w}" y1="0" x2="{left_w+len(processes)*col_w}" y2="{height-20}" class="colLine"/>')

    nodes = []
    connectors = []
    positions = {}
    box_w, box_h = 154, 58

    for i, p in enumerate(processes):
        x0 = col_x[p["id"]] + (col_w-box_w)/2
        y0 = lane_y[p["owner"]] + 17
        cfg = DEPARTMENTS[p["owner"]]
        positions[p["id"]] = {"x": x0, "y": y0, "cx": x0+box_w/2, "cy": y0+box_h/2}

        nodes.append(f'<rect class="process-box clickable" data-id="{p["id"]}" x="{x0}" y="{y0}" width="{box_w}" height="{box_h}" rx="8" fill="{cfg["soft"]}" stroke="{cfg["color"]}" stroke-width="1.8"/>')
        nodes.append(f'<rect x="{x0}" y="{y0}" width="7" height="{box_h}" rx="4" fill="{cfg["color"]}" pointer-events="none"/>')
        title_lines = split_lines(p["name"], 21)[:3]
        start_y = y0 + 22 - (max(0, len(title_lines)-2)*6)
        for li, line in enumerate(title_lines):
            nodes.append(f'<text x="{x0+box_w/2+3}" y="{start_y+li*16}" text-anchor="middle" class="boxText" pointer-events="none">{escape(line)}</text>')

        # Compact decision diamond and no-go action inside the same lane.
        dcx = x0 + box_w/2
        dcy = y0 + 87
        drx, dry = 31, 18
        nodes.append(f'<polygon class="gate clickable" data-id="{p["id"]}" points="{dcx},{dcy-dry} {dcx+drx},{dcy} {dcx},{dcy+dry} {dcx-drx},{dcy}" fill="#FFFFFF" stroke="#467BA9" stroke-width="1.3"/>')
        gate_short = "YES?" if len(p["gate"]) > 13 else p["gate"]
        nodes.append(f'<text x="{dcx}" y="{dcy+3}" text-anchor="middle" class="gateText" pointer-events="none">{escape(gate_short)}</text>')
        connectors.append(f'<path d="M {dcx} {y0+box_h} L {dcx} {dcy-dry}" class="flow" marker-end="url(#arrowBlue)"/>')

        action_x = x0 + box_w - 55
        action_y = y0 + 81
        nodes.append(f'<rect class="action-box clickable" data-id="{p["id"]}" x="{action_x}" y="{action_y}" width="53" height="31" rx="6" fill="#FFF1EE" stroke="#E05A49"/>')
        nodes.append(f'<text x="{action_x+26.5}" y="{action_y+13}" text-anchor="middle" class="noGo">NO-GO</text>')
        nodes.append(f'<text x="{action_x+26.5}" y="{action_y+24}" text-anchor="middle" class="detailHint">DETAIL</text>')
        connectors.append(f'<path d="M {dcx+drx} {dcy} L {action_x-5} {dcy} L {action_x-5} {action_y+15} L {action_x} {action_y+15}" class="noFlow" marker-end="url(#arrowRed)"/>')

    # Lead Qualification / BOQ verification flow
    lead_verify_cards = []
    lead_verify_connectors = []

    if 2 in positions and 3 in positions and 4 in positions:
        qual_pos = positions[2]
        prodev_pos = positions[3]
        solution_pos = positions[4]

        verify_x = col_x.get(3, left_w) + col_w + 18
        verify_card_w = 166
        verify_card_h = 72
        split_x_q = verify_x - 12
        merge_x_q = verify_x + verify_card_w + 14

        verification_items = [
            (idx, item) for idx, item in enumerate(LEAD_QUALIFICATION_VERIFICATION)
            if item["department"] in ("Operation", "Procurement", "Legal")
        ]
        verify_centers = []

        for vidx, item in verification_items:
            dep = item["department"]
            cfg = DEPARTMENTS[dep]
            vy = lane_y[dep] + (lane_h - verify_card_h) / 2
            vcx = verify_x + verify_card_w / 2
            vcy = vy + verify_card_h / 2
            verify_centers.append((vidx, dep, vcx, vcy))

            lead_verify_cards.append(
                f'<rect class="lead-verify-card process-card" data-lead-verify="{vidx}" '
                f'x="{verify_x}" y="{vy}" width="{verify_card_w}" height="{verify_card_h}" '
                f'rx="8" fill="{cfg["soft"]}" stroke="{cfg["color"]}" stroke-width="1.8"/>'
            )
            lead_verify_cards.append(
                f'<rect x="{verify_x}" y="{vy}" width="7" height="{verify_card_h}" rx="4" fill="{cfg["color"]}" pointer-events="none"/>'
            )
            lead_verify_cards.append(
                f'<text x="{vcx+3}" y="{vy+15}" text-anchor="middle" class="parallelDeptText">{escape(dep)}</text>'
            )
            for li, line in enumerate(split_lines(item["title"], 23)[:3]):
                lead_verify_cards.append(
                    f'<text x="{vcx+3}" y="{vy+31+li*14}" text-anchor="middle" class="parallelProcessText">{escape(line)}</text>'
                )
            lead_verify_cards.append(
                f'<text x="{vcx+3}" y="{vy+verify_card_h-7}" text-anchor="middle" class="parallelClickText">Klik detail</text>'
            )

        # Lead Qualification GO -> Product Development
        qual_go_y = qual_pos["y"] + 105
        lead_verify_connectors.append(
            f'<text x="{qual_pos["cx"]+8}" y="{qual_go_y-6}" class="goText">GO → PRODEV</text>'
        )
        lead_verify_connectors.append(
            f'<path d="M {qual_pos["cx"]} {qual_go_y} L {prodev_pos["x"]-14} {qual_go_y} '
            f'L {prodev_pos["x"]-14} {prodev_pos["cy"]} L {prodev_pos["x"]} {prodev_pos["cy"]}" '
            f'class="boqOwnerFlow" marker-end="url(#arrowGreen)"/>'
        )

        # Product Development BOQ -> Operation & Procurement
        op_proc = [x for x in verify_centers if x[1] in ("Operation", "Procurement")]
        if op_proc:
            prodev_out_x = prodev_pos["x"] + box_w
            prodev_out_y = prodev_pos["cy"]
            min_y = min(x[3] for x in op_proc)
            max_y = max(x[3] for x in op_proc)

            lead_verify_connectors.append(
                f'<text x="{prodev_out_x+8}" y="{prodev_out_y-7}" class="boqText">BOQ DISTRIBUTION</text>'
            )
            lead_verify_connectors.append(
                f'<path d="M {prodev_out_x} {prodev_out_y} L {split_x_q} {prodev_out_y}" '
                f'class="boqOwnerFlow" marker-end="url(#arrowBlue)"/>'
            )
            lead_verify_connectors.append(
                f'<path d="M {split_x_q} {min(min_y,prodev_out_y)} L {split_x_q} {max(max_y,prodev_out_y)}" class="boqSpine"/>'
            )
            for _, dep, _, vcy in op_proc:
                lead_verify_connectors.append(
                    f'<path d="M {split_x_q} {vcy} L {verify_x} {vcy}" class="boqBranch" marker-end="url(#arrowBlue)"/>'
                )

        # Lead Qualification -> Legal verification in parallel
        legal = [x for x in verify_centers if x[1] == "Legal"]
        if legal:
            _, _, _, legal_y = legal[0]
            legal_branch_x = qual_pos["x"] + box_w + 14
            lead_verify_connectors.append(
                f'<path d="M {qual_pos["x"]+box_w} {qual_pos["cy"]} L {legal_branch_x} {qual_pos["cy"]} '
                f'L {legal_branch_x} {legal_y} L {verify_x} {legal_y}" '
                f'class="parallelBranch" marker-end="url(#arrowBlue)"/>'
            )

        # GO merge from Operation, Procurement and Legal
        if verify_centers:
            min_vy = min(x[3] for x in verify_centers)
            max_vy = max(x[3] for x in verify_centers)
            lead_verify_connectors.append(
                f'<path d="M {merge_x_q} {min_vy} L {merge_x_q} {max_vy}" class="parallelMergeSpine"/>'
            )
            for _, dep, _, vcy in verify_centers:
                lead_verify_connectors.append(
                    f'<path d="M {verify_x+verify_card_w} {vcy} L {merge_x_q} {vcy}" '
                    f'class="parallelReturn" marker-end="url(#arrowGreen)"/>'
                )
                lead_verify_cards.append(
                    f'<text x="{verify_x+verify_card_w+5}" y="{vcy-6}" class="goText">GO</text>'
                )

            merge_mid_y = (min_vy + max_vy) / 2
            gate_cx = merge_x_q
            gate_cy = merge_mid_y
            gate_rx = 52
            gate_ry = 26
            lead_verify_cards.append(
                f'<polygon class="mandatory-gate" points="{gate_cx},{gate_cy-gate_ry} '
                f'{gate_cx+gate_rx},{gate_cy} {gate_cx},{gate_cy+gate_ry} '
                f'{gate_cx-gate_rx},{gate_cy}" fill="#FFFFFF" stroke="#258947" stroke-width="1.8"/>'
            )
            lead_verify_cards.append(
                f'<text x="{gate_cx}" y="{gate_cy-3}" text-anchor="middle" class="mandatoryGateText">MANDATORY</text>'
            )
            lead_verify_cards.append(
                f'<text x="{gate_cx}" y="{gate_cy+9}" text-anchor="middle" class="mandatoryGateText">VERIFICATION</text>'
            )
            lead_verify_cards.append(
                f'<text x="{gate_cx}" y="{gate_cy+21}" text-anchor="middle" class="mandatoryGateText">COMPLETE?</text>'
            )

            # YES -> Solution Design
            lead_verify_cards.append(
                f'<text x="{gate_cx+8}" y="{gate_cy+gate_ry+15}" class="goText">YES / ALL CLEAR</text>'
            )
            lead_verify_connectors.append(
                f'<path d="M {gate_cx} {gate_cy+gate_ry} L {gate_cx} {solution_pos["cy"]} '
                f'L {solution_pos["x"]} {solution_pos["cy"]}" class="bothGoFlow" marker-end="url(#arrowGreen)"/>'
            )

            # NO side label: detailed returns remain on each branch.
            lead_verify_cards.append(
                f'<text x="{gate_cx+gate_rx+8}" y="{gate_cy+3}" class="noGoReturnText">NO → RETURN TO OWNER</text>'
            )

        # Operation/Procurement NO-GO -> Product Development to revise BOQ
        if op_proc:
            return_x = verify_x - 18
            for _, dep, _, vcy in op_proc:
                lead_verify_connectors.append(
                    f'<path d="M {verify_x} {vcy+12} L {return_x} {vcy+12} '
                    f'L {return_x} {prodev_pos["y"]+box_h} L {prodev_pos["cx"]} {prodev_pos["y"]+box_h}" '
                    f'class="boqNoGoFlow" marker-end="url(#arrowRed)"/>'
                )
            lead_verify_cards.append(
                f'<text x="{return_x+5}" y="{prodev_pos["y"]+box_h-8}" class="noGoReturnText">NO-GO → PRODEV / REVISE BOQ</text>'
            )

        # Legal NO-GO -> Sales
        if legal:
            _, _, _, legal_y = legal[0]
            legal_return_x = verify_x - 34
            lead_verify_connectors.append(
                f'<path d="M {verify_x} {legal_y+12} L {legal_return_x} {legal_y+12} '
                f'L {legal_return_x} {qual_pos["cy"]} L {qual_pos["x"]+box_w} {qual_pos["cy"]}" '
                f'class="noFlow" marker-end="url(#arrowRed)"/>'
            )
            lead_verify_cards.append(
                f'<text x="{legal_return_x+5}" y="{qual_pos["cy"]-8}" class="noGoReturnText">LEGAL NO-GO → SALES</text>'
            )

    # Main sequential flow, routed orthogonally from each decision to next process.
    for i in range(len(processes)-1):
        p = processes[i]
        nxt = processes[i+1]
        a = positions[p["id"]]
        b = positions[nxt["id"]]
        start_x = a["cx"]
        start_y = a["y"] + 105
        end_x = b["x"]
        end_y = b["cy"]
        mid_x = (start_x + end_x) / 2
        if p["id"] not in (2, 3, 5, 8):
            connectors.append(f'<path class="mainFlow flow-{p["id"]} flow-{nxt["id"]}" d="M {start_x} {start_y} L {mid_x} {start_y} L {mid_x} {end_y} L {end_x} {end_y}" marker-end="url(#arrowGreen)"/>')
            connectors.append(f'<text x="{start_x+8}" y="{start_y-6}" class="goText">GO</text>')

    # Parallel responsibilities after Internal Review are rendered as full process cards.
    # Each card stays inside its own department lane and uses consistent sizing
    # to avoid visual overlap.
    support_cards = []
    parallel_connectors = []

    internal_x = col_x.get(5, left_w)
    proposal_x = col_x.get(6, left_w + col_w)
    parallel_card_w = 158
    parallel_card_h = 70
    parallel_card_x = internal_x + col_w + (col_w - parallel_card_w) / 2

    split_x = internal_x + col_w + 18
    merge_x = proposal_x - 18

    parallel_centers = []

    # Explicit GO path from Internal Review decision gate into the parallel distribution.
    # Internal Review is coordinated from the Sales lane; the path leaves the bottom of the decision gate,
    # moves horizontally to the split corridor, then the corridor distributes upward to all lanes.
    internal_pos = positions.get(5)
    internal_go_y = None
    if internal_pos:
        internal_gate_bottom_y = internal_pos["y"] + 105
        internal_go_y = internal_gate_bottom_y
        parallel_connectors.append(
            f'<text x="{internal_pos["cx"]+8}" y="{internal_gate_bottom_y-6}" class="goText">GO</text>'
        )
        parallel_connectors.append(
            f'<path d="M {internal_pos["cx"]} {internal_gate_bottom_y} '
            f'L {split_x} {internal_gate_bottom_y}" '
            f'class="parallelGoMain" marker-end="url(#arrowGreen)"/>'
        )

    for idx, item in enumerate(PARALLEL_AUTHORITY):
        dep = item["department"]
        cfg = DEPARTMENTS[dep]
        card_x = parallel_card_x
        card_y = lane_y[dep] + (lane_h - parallel_card_h) / 2
        card_cx = card_x + parallel_card_w / 2
        card_cy = card_y + parallel_card_h / 2
        parallel_centers.append((dep, card_cx, card_cy))

        support_cards.append(
            f'<rect class="parallel-card process-card" data-parallel="{idx}" '
            f'x="{card_x}" y="{card_y}" width="{parallel_card_w}" height="{parallel_card_h}" '
            f'rx="8" fill="{cfg["soft"]}" stroke="{cfg["color"]}" stroke-width="1.8"/>'
        )
        support_cards.append(
            f'<rect x="{card_x}" y="{card_y}" width="7" height="{parallel_card_h}" '
            f'rx="4" fill="{cfg["color"]}" pointer-events="none"/>'
        )

        dep_label = dep.replace("Product Development", "Product Dev.")
        support_cards.append(
            f'<text x="{card_cx+3}" y="{card_y+15}" text-anchor="middle" '
            f'class="parallelDeptText" pointer-events="none">{escape(dep_label)}</text>'
        )

        title_lines = split_lines(item["title"], 22)[:3]
        for li, line in enumerate(title_lines):
            support_cards.append(
                f'<text x="{card_cx+3}" y="{card_y+31+li*14}" text-anchor="middle" '
                f'class="parallelProcessText" pointer-events="none">{escape(line)}</text>'
            )

        support_cards.append(
            f'<text x="{card_cx+3}" y="{card_y+parallel_card_h-7}" text-anchor="middle" '
            f'class="parallelClickText" pointer-events="none">Klik detail</text>'
        )

        parallel_connectors.append(
            f'<path d="M {split_x} {card_cy} L {card_x-6} {card_cy} L {card_x} {card_cy}" '
            f'class="parallelBranch" marker-end="url(#arrowBlue)"/>'
        )
        parallel_connectors.append(
            f'<path d="M {card_x+parallel_card_w} {card_cy} L {merge_x} {card_cy}" '
            f'class="parallelReturn"/>'
        )

    if parallel_centers:
        min_y = min(cy for _, _, cy in parallel_centers)
        max_y = max(cy for _, _, cy in parallel_centers)
        # Extend the split spine down to the Internal Review GO entry point.
        if internal_go_y is not None:
            min_y = min(min_y, internal_go_y)
            max_y = max(max_y, internal_go_y)
        parallel_connectors.append(
            f'<path d="M {split_x} {min_y} L {split_x} {max_y}" class="parallelSpine"/>'
        )
        parallel_connectors.append(
            f'<path d="M {merge_x} {min_y} L {merge_x} {max_y}" class="parallelMergeSpine"/>'
        )

    proposal_pos = positions.get(6)
    if proposal_pos:
        proposal_y = proposal_pos["cy"]
        parallel_connectors.append(
            f'<path d="M {merge_x} {proposal_y} L {proposal_pos["x"]-6} {proposal_y} '
            f'L {proposal_pos["x"]} {proposal_y}" class="parallelReturn" marker-end="url(#arrowGreen)"/>'
        )

    # Legal and Finance Contract / PO review are also full process cards.
    contract_x = col_x.get(8, left_w)
    kick_x = col_x.get(9, contract_x + col_w)
    contract_card_w = 158
    contract_card_h = 70
    contract_card_x = contract_x + (col_w - contract_card_w) / 2
    contract_split_x = contract_x + 18
    contract_merge_x = kick_x - 18
    contract_centers = []

    for idx, item in enumerate(CONTRACT_REVIEW_PARALLEL):
        dep = item["department"]
        cfg = DEPARTMENTS[dep]
        card_y = lane_y[dep] + (lane_h - contract_card_h) / 2
        cx = contract_card_x + contract_card_w / 2
        cy = card_y + contract_card_h / 2
        contract_centers.append((dep, cx, cy))

        support_cards.append(
            f'<rect class="contract-review-card process-card" data-contract-review="{idx}" '
            f'x="{contract_card_x}" y="{card_y}" width="{contract_card_w}" height="{contract_card_h}" '
            f'rx="8" fill="{cfg["soft"]}" stroke="{cfg["color"]}" stroke-width="1.8"/>'
        )
        support_cards.append(
            f'<rect x="{contract_card_x}" y="{card_y}" width="7" height="{contract_card_h}" '
            f'rx="4" fill="{cfg["color"]}" pointer-events="none"/>'
        )
        support_cards.append(
            f'<text x="{cx+3}" y="{card_y+15}" text-anchor="middle" '
            f'class="parallelDeptText" pointer-events="none">{escape(dep)}</text>'
        )
        for li, line in enumerate(split_lines(item["title"], 22)[:3]):
            support_cards.append(
                f'<text x="{cx+3}" y="{card_y+31+li*14}" text-anchor="middle" '
                f'class="parallelProcessText" pointer-events="none">{escape(line)}</text>'
            )
        support_cards.append(
            f'<text x="{cx+3}" y="{card_y+contract_card_h-7}" text-anchor="middle" '
            f'class="parallelClickText" pointer-events="none">Klik detail</text>'
        )

    if contract_centers:
        min_cy = min(cy for _, _, cy in contract_centers)
        max_cy = max(cy for _, _, cy in contract_centers)

        # Vertical rails for Legal + Finance parallel review.
        parallel_connectors.append(
            f'<path d="M {contract_split_x} {min_cy} L {contract_split_x} {max_cy}" class="parallelSpine"/>'
        )
        parallel_connectors.append(
            f'<path d="M {contract_merge_x} {min_cy} L {contract_merge_x} {max_cy}" class="parallelMergeSpine"/>'
        )

        # Each function feeds the common merge rail.
        for dep, cx, cy in contract_centers:
            parallel_connectors.append(
                f'<path d="M {contract_split_x} {cy} L {contract_card_x} {cy}" '
                f'class="parallelBranch" marker-end="url(#arrowBlue)"/>'
            )
            parallel_connectors.append(
                f'<path d="M {contract_card_x+contract_card_w} {cy} L {contract_merge_x} {cy}" '
                f'class="parallelReturn" marker-end="url(#arrowGreen)"/>'
            )
            support_cards.append(
                f'<text x="{contract_card_x+contract_card_w+5}" y="{cy-6}" class="goText">GO</text>'
            )

        # ALL GO marker between Legal + Finance before moving to Kick Off Internal.
        contract_merge_mid_y = (min_cy + max_cy) / 2
        support_cards.append(
            f'<rect x="{contract_merge_x-36}" y="{contract_merge_mid_y-12}" width="72" height="24" '
            f'rx="12" fill="#EAF8EF" stroke="#258947" stroke-width="1.3"/>'
        )
        support_cards.append(
            f'<text x="{contract_merge_x}" y="{contract_merge_mid_y+3}" text-anchor="middle" '
            f'class="bothGoText">ALL GO</text>'
        )

    kick_pos = positions.get(9)
    if kick_pos and contract_centers:
        kick_y = kick_pos["cy"]
        contract_merge_mid_y = (min(cy for _, _, cy in contract_centers) + max(cy for _, _, cy in contract_centers)) / 2

        # Explicit GO path from the merged Legal + Finance result to Operation - Kick Off Internal.
        parallel_connectors.append(
            f'<path d="M {contract_merge_x} {contract_merge_mid_y+12} '
            f'L {contract_merge_x} {kick_y} '
            f'L {kick_pos["x"]-8} {kick_y} '
            f'L {kick_pos["x"]} {kick_y}" '
            f'class="contractGoFlow" marker-end="url(#arrowGreen)"/>'
        )
        support_cards.append(
            f'<text x="{contract_merge_x+8}" y="{contract_merge_mid_y+30}" class="goText">GO → KICK OFF</text>'
        )

    html = f"""
<!doctype html><html><head><meta charset='utf-8'/>
<style>
html,body{{margin:0;background:#EEF3F7;font-family:Arial,Helvetica,sans-serif;color:#0B243B;overflow:hidden}}
.toolbar{{height:58px;box-sizing:border-box;display:flex;gap:7px;align-items:center;padding:8px 12px;background:#FFFFFF;border-bottom:1px solid #CCD8E3;box-shadow:0 2px 8px rgba(18,44,68,.08);position:relative;z-index:20}}
.toolbar .title{{font-size:16px;font-weight:800;color:#0A2B46;margin-right:auto;white-space:nowrap}}
.toolbar button,.toolbar select,.toolbar input{{height:36px;border:1px solid #C6D4E1;background:#FFF;border-radius:6px;padding:0 10px;font-size:12px;color:#183B57}}
.toolbar button{{cursor:pointer;font-weight:700}} .toolbar button:hover{{background:#EDF5FC}}
#workspace{{height:calc(100vh - 58px);min-height:1500px;overflow:hidden;background:#EAF0F5;position:relative}}
#viewport{{width:100%;height:100%;min-height:1500px;overflow:auto;background:#EAF0F5;position:relative;scrollbar-gutter:stable both-edges;overscroll-behavior:contain}}
#scrollSurface{{position:relative;min-height:100%;max-width:none!important;overflow:visible;}}
#stickyPane{{position:sticky;left:0;top:0;width:205px;z-index:50;float:left;background:white;border-right:1px solid #B9C9D8;box-shadow:5px 0 12px rgba(16,42,65,.14)}}
#stickyPane svg{{display:block;background:white;border:0;box-shadow:none}}
#canvasWrap{{position:absolute;left:219px;top:14px;transform-origin:top left;will-change:auto;max-width:none!important;overflow:visible}}
#viewport::-webkit-scrollbar{{height:20px;width:14px}}
#viewport::-webkit-scrollbar-track{{background:#DCE5ED}}
#viewport::-webkit-scrollbar-thumb{{background:#8098AD;border-radius:8px;border:3px solid #DCE5ED}}
#viewport::-webkit-scrollbar-thumb:hover{{background:#607D95}}
svg{{display:block;background:white;border:1px solid #B9C9D8;box-shadow:0 5px 18px rgba(16,42,65,.12)}}
.laneLine{{stroke:#CBD7E3;stroke-width:1}} .colLine{{stroke:#D6E0EA;stroke-width:1;stroke-dasharray:4 4}}
.laneLabel{{font-size:14px;font-weight:800;fill:#0A2F4E}} .laneSub{{font-size:8px;font-weight:700;fill:#62788D;letter-spacing:.08em}}
.stageNo{{font-size:12px;font-weight:900;fill:#1970B7}} .stageTitle{{font-size:10px;font-weight:800;fill:#244B68;letter-spacing:.02em}}
.boxText{{font-size:11px;font-weight:800;fill:#0A2F4E}} .gateText{{font-size:7px;font-weight:900;fill:#315F84}}
.flow{{fill:none;stroke:#356C99;stroke-width:1.2}} .mainFlow{{fill:none;stroke:#258947;stroke-width:1.7}} .noFlow{{fill:none;stroke:#D34A3A;stroke-width:1.25}}
.goText{{font-size:8px;font-weight:900;fill:#258947}} .noGo{{font-size:7px;font-weight:900;fill:#B93227}} .detailHint{{font-size:6px;font-weight:800;fill:#6D7F90}}
.supportText{{font-size:7px;font-weight:900;fill:#204866}}
.parallelDeptText{{font-size:8px;font-weight:900;fill:#5D7184;letter-spacing:.03em}}
.parallelProcessText{{font-size:10px;font-weight:800;fill:#0A2F4E}}
.parallelClickText{{font-size:7px;font-weight:800;fill:#5D7184}}
.noGoReturnText{{font-size:7px;font-weight:900;fill:#B93227}}\n.bothGoText{{font-size:8px;font-weight:900;fill:#258947}}\n.mandatoryGateText{{font-size:7px;font-weight:900;fill:#1F5E3A;letter-spacing:.02em}}\n.bothGoFlow{{fill:none;stroke:#258947;stroke-width:2}}\n.contractGoFlow{{fill:none;stroke:#258947;stroke-width:2.2}}\n.boqOwnerFlow{{fill:none;stroke:#356C99;stroke-width:2}}\n.boqSpine{{fill:none;stroke:#356C99;stroke-width:1.5;stroke-dasharray:4 3}}\n.boqBranch{{fill:none;stroke:#356C99;stroke-width:1.5}}\n.boqNoGoFlow{{fill:none;stroke:#D34A3A;stroke-width:1.5}}\n.boqText{{font-size:8px;font-weight:900;fill:#356C99}}
.process-card{{cursor:pointer}}
.parallelGoMain{{fill:none;stroke:#258947;stroke-width:1.8}}
.parallelSpine{{fill:none;stroke:#356C99;stroke-width:1.2;stroke-dasharray:4 3}}
.parallelMergeSpine{{fill:none;stroke:#258947;stroke-width:1.25;stroke-dasharray:4 3}}
.parallelBranch{{fill:none;stroke:#356C99;stroke-width:1.25}}
.parallelReturn{{fill:none;stroke:#258947;stroke-width:1.35}}
.clickable,.parallel-card,.contract-review-card{{cursor:pointer;transition:filter .15s,stroke-width .15s}}
.clickable:hover,.parallel-card:hover,.contract-review-card:hover{{filter:drop-shadow(0 3px 4px rgba(0,0,0,.20));stroke-width:2.3}}
.dim{{opacity:.12}} .highlight{{filter:drop-shadow(0 0 6px #F2B705);stroke:#E5A800!important;stroke-width:3!important}}
#modal{{display:none;position:fixed;inset:0;background:rgba(5,20,33,.62);z-index:60;align-items:center;justify-content:center;padding:18px}}
#modalCard{{width:min(780px,94vw);max-height:84vh;overflow:auto;background:#FFF;border-radius:12px;box-shadow:0 20px 60px rgba(0,0,0,.35);padding:22px}}
#modalCard h2{{margin:7px 0 4px;color:#092A45;font-size:24px}} .badge{{display:inline-block;padding:5px 9px;border-radius:999px;font-size:11px;font-weight:800}}
.detailGrid{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:14px}} .detail{{border:1px solid #D7E1EA;border-radius:8px;padding:10px;background:#F9FBFD}} .detail b{{display:block;font-size:9px;letter-spacing:.08em;color:#61798E;margin-bottom:5px}} .detail span{{font-size:12px;line-height:1.45}}
.close{{float:right;border:0;background:#ECF1F5;border-radius:50%;width:31px;height:31px;cursor:pointer;font-size:18px}}
@media(max-width:900px){{.toolbar .title{{display:none}}.toolbar input{{width:120px}}.detailGrid{{grid-template-columns:1fr}}}}
@media print{{.toolbar{{display:none}}#stickyPane{{display:none}}#viewport{{height:auto;overflow:visible}}#scrollSurface{{width:auto!important;height:auto!important;min-width:0!important;min-height:0!important}}#canvasWrap{{position:static!important;transform:none!important;padding:0}}html,body{{overflow:visible;background:white}}}}
</style></head><body>
<div class='toolbar'>
 <span class='title'>PT STARCOM SOLUSINDO · SOP SALES TO AFTER SALES</span>
 <input id='search' placeholder='Cari proses...' oninput='applyFilters()'/>
 <select id='dept' onchange='applyFilters()'><option value='ALL'>Semua departemen</option>{''.join(f'<option>{d}</option>' for d in deps)}</select>
 <button onclick='zoomOut()'>−</button><button id='zoomLabel' onclick='actualSize()'>100%</button><button onclick='zoomIn()'>+</button>
 <button onclick='fitWidth()'>Fit Width</button><button onclick='fitHeight()'>Fit Height</button><button onclick='actualSize()'>100%</button>
 <button onclick='resetView()'>Reset</button><button onclick='goToStart()'>⇤ Awal</button><button onclick='goToFinalProcess()'>Akhir ⇥</button><button id='edgeInfo' onclick='goToEnd()'>→ FULL KANAN</button><button onclick='fullscreen()'>⛶ Fullscreen</button><button onclick='window.print()'>Print / PDF</button>
</div>
<div id='workspace'>
<div id='viewport'>
<div id='scrollSurface'>
<div id='stickyPane'>
<svg id='stickyChart' width='{left_w}' height='{height}' viewBox='0 0 {left_w} {height}' aria-label='Sticky department column'>
<rect x='0' y='0' width='{left_w}' height='{top_h}' fill='#0B3152'/>
<text x='22' y='43' class='laneLabel' style='fill:white;font-size:16px'>DEPARTEMEN</text>
<text x='22' y='66' class='laneSub' style='fill:#C9D8E5'>CROSS-FUNCTIONAL SWIMLANE</text>
{''.join(sticky_lane_parts)}
</svg>
</div>
<div id='canvasWrap'>
<svg id='chart' width='{width-left_w}' height='{height}' viewBox='0 0 {width-left_w} {height}' aria-label='STARCOM cross-functional SOP swimlane'>
<defs>
 <marker id='arrowBlue' markerWidth='8' markerHeight='8' refX='7' refY='4' orient='auto'><path d='M0,0 L8,4 L0,8 z' fill='#356C99'/></marker>
 <marker id='arrowGreen' markerWidth='8' markerHeight='8' refX='7' refY='4' orient='auto'><path d='M0,0 L8,4 L0,8 z' fill='#258947'/></marker>
 <marker id='arrowRed' markerWidth='8' markerHeight='8' refX='7' refY='4' orient='auto'><path d='M0,0 L8,4 L0,8 z' fill='#D34A3A'/></marker>
</defs>
<g transform='translate(-{left_w},0)'>
<rect x='0' y='0' width='{left_w}' height='{top_h}' fill='#0B3152'/>
<text x='22' y='43' class='laneLabel' style='fill:white;font-size:16px'>DEPARTEMEN</text>
<text x='22' y='66' class='laneSub' style='fill:#C9D8E5'>CROSS-FUNCTIONAL SWIMLANE</text>
{''.join(lane_parts)}
{''.join(stage_parts)}
{''.join(connectors)}
{''.join(lead_verify_connectors)}
{''.join(parallel_connectors)}
{''.join(nodes)}
{''.join(lead_verify_cards)}
{''.join(support_cards)}
</g>
</svg></div>
<div style='clear:both'></div>
</div>
</div>
</div>
<div id='modal' onclick='if(event.target.id==="modal")closeModal()'><div id='modalCard'><button class='close' onclick='closeModal()'>×</button><div id='modalBody'></div></div></div>
<script>
const processes={p_json}; const departments={dep_json}; const parallelAuthority={parallel_json}; const contractReviewParallel={contract_review_json}; const leadQualificationVerification={lead_verification_json};
let zoom=1;
const LEFT_W=205;
const PAD=140;
function updateScrollSurface(){{
  const svg=document.getElementById('chart');
  const surface=document.getElementById('scrollSurface');
  const processW=Math.ceil(svg.width.baseVal.value);
  const processH=Math.ceil(svg.height.baseVal.value);

  // Large explicit right and bottom safety margins so the final stage can always
  // be brought completely into view, regardless of browser width or scrollbar size.
  const RIGHT_BUFFER=Math.max(600, window.innerWidth*0.55);
  const BOTTOM_BUFFER=260;
  const totalW=LEFT_W + 14 + processW + RIGHT_BUFFER;
  const totalH=processH + BOTTOM_BUFFER;

  surface.style.width=totalW+'px';
  surface.style.minWidth=totalW+'px';
  surface.style.maxWidth='none';
  surface.style.height=totalH+'px';
  surface.style.minHeight=totalH+'px';

  const wrap=document.getElementById('canvasWrap');
  wrap.style.left=(LEFT_W+14)+'px';
  wrap.style.width=processW+'px';
  wrap.style.height=processH+'px';
  wrap.style.maxWidth='none';
}}
function setZoom(v){{
  zoom=Math.max(.25,Math.min(2.2,v));
  const svg=document.getElementById('chart');
  const baseW=svg.viewBox.baseVal.width;
  const baseH=svg.viewBox.baseVal.height;
  svg.setAttribute('width',Math.round(baseW*zoom));
  svg.setAttribute('height',Math.round(baseH*zoom));
  document.getElementById('zoomLabel').innerText=Math.round(zoom*100)+'%';
  updateScrollSurface();
}}
function zoomIn(){{setZoom(zoom+.1)}}
function zoomOut(){{setZoom(zoom-.1)}}
function actualSize(){{setZoom(1)}}
function fitWidth(){{
  const vp=document.getElementById('viewport');
  const svg=document.getElementById('chart');
  setZoom(Math.max(.25,(vp.clientWidth-PAD)/svg.width.baseVal.value));
  vp.scrollTo({{left:0,top:0,behavior:'auto'}});
  
}}
function fitHeight(){{
  const vp=document.getElementById('viewport');
  const svg=document.getElementById('chart');
  setZoom(Math.max(.25,(vp.clientHeight-PAD)/svg.height.baseVal.value));
  vp.scrollTo({{left:0,top:0,behavior:'auto'}});
  
}}
function resetView(){{
  setZoom(1);
  document.getElementById('search').value='';
  document.getElementById('dept').value='ALL';
  applyFilters();
  document.getElementById('viewport').scrollTo({{left:0,top:0,behavior:'auto'}});
  
}}
function goToEnd(){{
  const vp=document.getElementById('viewport');
  const maxLeft=Math.max(0,vp.scrollWidth-vp.clientWidth);
  vp.scrollTo({{left:maxLeft,top:vp.scrollTop,behavior:'smooth'}});
}}
function goToFinalProcess(){{
  const vp=document.getElementById('viewport');
  const finalNode=document.querySelector('.process-box[data-id="18"]');
  if(!finalNode){{goToEnd();return;}}
  const finalX=parseFloat(finalNode.getAttribute('x'));
  const finalW=parseFloat(finalNode.getAttribute('width'));
  const target=Math.max(0, LEFT_W + finalX + finalW - vp.clientWidth + 360);
  vp.scrollTo({{left:target,top:vp.scrollTop,behavior:'smooth'}});
}}
function goToStart(){{
  const vp=document.getElementById('viewport');
  vp.scrollTo({{left:0,top:vp.scrollTop,behavior:'smooth'}});
}}
function updateEdgeInfo(){{
  const vp=document.getElementById('viewport');
  const maxLeft=Math.max(1,vp.scrollWidth-vp.clientWidth);
  const pct=Math.min(100,Math.round((vp.scrollLeft/maxLeft)*100));
  const b=document.getElementById('edgeInfo');
  if(b)b.innerText='→ '+pct+'% KANAN';
}}
document.getElementById('viewport').addEventListener('scroll',updateEdgeInfo,{{passive:true}});
window.addEventListener('resize',()=>{{updateScrollSurface();updateEdgeInfo();}},{{passive:true}});

function fullscreen(){{const el=document.getElementById('workspace');if(!document.fullscreenElement&&el.requestFullscreen)el.requestFullscreen();else if(document.exitFullscreen)document.exitFullscreen();}}
function applyFilters(){{const q=document.getElementById('search').value.toLowerCase().trim();const dep=document.getElementById('dept').value;document.querySelectorAll('.process-box,.gate,.action-box').forEach(el=>{{const p=processes.find(x=>x.id===+el.dataset.id);const okQ=!q||JSON.stringify(p).toLowerCase().includes(q);const okD=dep==='ALL'||p.owner===dep;el.classList.toggle('dim',!(okQ&&okD));el.classList.toggle('highlight',okQ&&q.length>1);}})}}
function showDetail(id){{const p=processes.find(x=>x.id===id);const c=departments[p.owner];document.getElementById('modalBody').innerHTML=`<span class='badge' style='background:${{c.soft}};color:${{c.color}}'>${{p.owner}}</span><h2>${{p.id}}. ${{p.name}}</h2><div class='detailGrid'><div class='detail'><b>KEGIATAN UTAMA</b><span>${{p.activity}}</span></div><div class='detail'><b>OUTPUT</b><span>${{p.output}}</span></div><div class='detail'><b>DECISION GATE</b><span>${{p.gate}}</span></div><div class='detail'><b>GO / LOLOS</b><span>${{p.go}}</span></div><div class='detail'><b>NO-GO / TINDAKAN</b><span><strong>${{p.nogo}}</strong><br>${{p.solution}}</span></div><div class='detail'><b>ESKALASI</b><span>${{p.escalation}}</span></div><div class='detail'><b>DOKUMEN</b><span>${{p.documents}}</span></div><div class='detail'><b>SLA</b><span>${{p.sla}}</span></div><div class='detail'><b>KPI</b><span>${{p.kpi}}</span></div><div class='detail'><b>RISIKO</b><span>${{p.risk}}</span></div></div>`;document.getElementById('modal').style.display='flex';}}
function showParallelDetail(index){{const item=parallelAuthority[index];const c=departments[item.department];document.getElementById('modalBody').innerHTML=`<span class='badge' style='background:${{c.soft}};color:${{c.color}}'>${{item.department}}</span><h2>${{item.title}}</h2><div class='detailGrid'><div class='detail'><b>KEWENANGAN / AKTIVITAS</b><span>${{item.detail}}</span></div><div class='detail'><b>OUTPUT</b><span>${{item.output}}</span></div><div class='detail'><b>JIKA GO</b><span>${{item.go}}</span></div><div class='detail'><b>JIKA NO-GO</b><span>${{item.nogo}}</span></div><div class='detail'><b>POLA KERJA</b><span>Dilaksanakan paralel setelah Internal Review berstatus GO. Semua output dikonsolidasikan oleh Sales sebelum proposal final dikirim ke customer.</span></div></div>`;document.getElementById('modal').style.display='flex';}}
function showContractReviewDetail(index){{const item=contractReviewParallel[index];const c=departments[item.department];document.getElementById('modalBody').innerHTML=`<span class='badge' style='background:${{c.soft}};color:${{c.color}}'>${{item.department}}</span><h2>${{item.title}}</h2><div class='detailGrid'><div class='detail'><b>REVIEW SCOPE</b><span>${{item.detail}}</span></div><div class='detail'><b>OUTPUT</b><span>${{item.output}}</span></div><div class='detail'><b>JIKA GO</b><span>${{item.go}}</span></div><div class='detail'><b>JIKA NO-GO</b><span>${{item.nogo}}</span></div><div class='detail'><b>MERGE RULE</b><span>Kick Off Internal hanya dapat dimulai setelah Legal dan Finance keduanya memberikan clearance.</span></div></div>`;document.getElementById('modal').style.display='flex';}}
function showLeadVerificationDetail(index){{
  const item=leadQualificationVerification[index]; const c=departments[item.department];
  document.getElementById('modalBody').innerHTML=`<span class='badge' style='background:${{c.soft}};color:${{c.color}}'>${{item.department}}</span><h2>${{item.title}}</h2><div class='detailGrid'><div class='detail'><b>VERIFICATION SCOPE</b><span>${{item.detail}}</span></div><div class='detail'><b>OUTPUT</b><span>${{item.output}}</span></div><div class='detail'><b>JIKA GO</b><span>${{item.go}}<br><br><strong>Merge rule:</strong> Product Development menjadi owner BOQ. BOQ didistribusikan ke Operation dan Procurement untuk verifikasi, sementara Legal memverifikasi requirement legal. Ketiga mandatory verification harus clear pada gate 'Mandatory Verification Complete?' sebelum lanjut ke Solution Design.</span></div><div class='detail'><b>JIKA NO-GO</b><span>${{item.nogo}}</span></div></div>`; document.getElementById('modal').style.display='flex';
}}
function closeModal(){{document.getElementById('modal').style.display='none'}}
document.querySelectorAll('.process-box,.gate,.action-box').forEach(el=>el.addEventListener('click',()=>showDetail(+el.dataset.id)));
document.querySelectorAll('.parallel-card').forEach(el=>el.addEventListener('click',()=>showParallelDetail(+el.dataset.parallel)));
document.querySelectorAll('.contract-review-card').forEach(el=>el.addEventListener('click',()=>showContractReviewDetail(+el.dataset.contractReview)));
document.querySelectorAll('.lead-verify-card').forEach(el=>el.addEventListener('click',()=>showLeadVerificationDetail(+el.dataset.leadVerify)));
setTimeout(()=>{{setZoom(1);updateScrollSurface();document.getElementById('viewport').scrollTo({{left:0,top:0}});updateEdgeInfo();}},200);
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
        1: [], 2: ["Product Development", "Operation", "Procurement", "Legal"], 3: ["Sales", "Operation", "Procurement"], 4: ["Sales", "Operation", "Procurement"],
        5: ["Product Development", "Finance", "Legal", "Procurement", "HSEQ", "Operation"],
        6: ["Product Development", "Finance", "Legal"], 7: ["Legal", "Finance", "Product Development"],
        8: ["Sales", "Finance", "Legal"], 9: ["Sales", "Product Development", "Procurement", "Finance", "HSEQ"],
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
    {"name":"Opportunity", "ids":[1,2,3], "owner":"Sales + Operation + Procurement + Legal + Product Development"},
    {"name":"Solution & Approval", "ids":[4,5,6], "owner":"Sales + Product Development + HSEQ + Legal + Procurement + Operation"},
    {"name":"Commercial", "ids":[7,8], "owner":"Sales + Legal + Finance (parallel Contract/PO review)"},
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
    components.html(html, height=1900, scrolling=False)

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
    components.html(html,height=1750,scrolling=False)
