# STARCOM SOP Enterprise

Aplikasi Streamlit standalone untuk visualisasi SOP Sales → Delivery → After Sales pada perusahaan telekomunikasi dan IT system integrator.

## Fitur
- Swimlane vertikal per departemen
- Decision gate Go / No-Go
- Tindakan koreksi dan tujuan eskalasi
- Search, filter departemen, zoom, fullscreen, Print/PDF
- Klik proses untuk melihat detail SOP
- Executive Flow, Department Authority, Process Detail, Decision Gates, RACI, Presentation Mode
- Tidak membutuhkan Excel atau file data eksternal

## Deploy ke Streamlit Cloud
1. Upload seluruh isi folder ke root repository GitHub.
2. Main file path: `app.py`
3. Deploy.

## Lokal
```bash
pip install -r requirements.txt
streamlit run app.py
```
