import os
import io
import requests
import subprocess
import tempfile
from datetime import timedelta, date
import pandas as pd
import streamlit as st
from docxtpl import DocxTemplate

st.set_page_config(
    page_title="Generator BA Stock Opname",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Generator Berita Acara Stock Opname Bandara")
st.write("Isi formulir di bawah ini untuk menghasilkan dokumen Berita Acara secara otomatis.")

st.divider()

# ---------------------------------------------------------
# HELPER TERBILANG & FORMAT TANGGAL
# ---------------------------------------------------------
HARI_LIST = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
BULAN_LIST = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni", 
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

def terbilang(n):
    """Mengubah angka menjadi kata-kata Bahasa Indonesia (contoh: 15 -> 'Lima Belas')."""
    satuan = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
    n = int(n)
    if n < 12:
        res = satuan[n]
    elif n < 20:
        res = terbilang(n - 10) + " Belas"
    elif n < 100:
        res = terbilang(n // 10) + " Puluh " + terbilang(n % 10)
    elif n < 200:
        res = "Seratus " + terbilang(n - 100)
    elif n < 1000:
        res = terbilang(n // 100) + " Ratus " + terbilang(n % 100)
    elif n < 2000:
        res = "Seribu " + terbilang(n - 1000)
    elif n < 1000000:
        res = terbilang(n // 1000) + " Ribu " + terbilang(n % 1000)
    else:
        res = str(n)
    return " ".join(res.split())

def format_tgl_simpel(dt):
    """Format tanggal simpel (contoh: '18 Agustus 2026')."""
    if dt is None:
        return ""
    if isinstance(dt, str):
        try:
            dt = pd.to_datetime(dt).date()
        except Exception:
            return dt
    return f"{dt.day} {BULAN_LIST[dt.month - 1]} {dt.year}"

def format_indo_date(dt):
    """Format tanggal lengkap dengan nama hari (contoh: 'Rabu, 18 Februari 2026')."""
    if dt is None:
        return ""
    if isinstance(dt, str):
        try:
            dt = pd.to_datetime(dt).date()
        except Exception:
            return dt
    hari = HARI_LIST[dt.weekday()]
    return f"{hari}, {format_tgl_simpel(dt)}"

# ---------------------------------------------------------
# TEMPLATE MASTER GOOGLE DRIVE
# ---------------------------------------------------------
FILE_ID = "1pqxqLCf-N6HxjXI7KZuRMikWEjiMIVlW"
TEMPLATE_DRIVE_URL = f"https://docs.google.com/document/d/{FILE_ID}/export?format=docx"

@st.cache_data(ttl=3600)
def fetch_master_template(url: str) -> bytes:
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.content

# ==========================================
# 1. FORM INPUT HEADER & METADATA
# ==========================================
with st.expander("📌 Informasi Umum & Header Audit", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        hari = st.selectbox("Hari Audit", HARI_LIST)
        tanggal = st.number_input("Tanggal BA", min_value=1, max_value=31, value=15)
        bulan = st.selectbox("Bulan Berita Acara", BULAN_LIST, index=1)
        tahun = st.number_input("Tahun", min_value=2024, max_value=2030, value=2026)
        lokasi_bandara = st.text_input("Lokasi / Bandara (contoh: PLM / Palembang)", "PLM")
        alamat = st.text_input("Alamat", "Jl. Bandara Sultan Mahmud Badaruddin II")

    with col2:
        tgl_mulai_audit = st.date_input("Tanggal Mulai Audit", value=date(2026, 2, 12))
        tgl_selesai_audit = st.date_input("Tanggal Selesai Audit", value=date(2026, 2, 15))
        audit_aset = st.text_input("Nama Pelaksana Audit Aset", "Nama Auditor Aset")
        pic_lm = st.text_input("Nama PIC Line Maintenance", "Nama PIC LM")

    st.markdown("---")
    st.markdown("##### 👤 Penanggung Jawab (PJ) Store LM")
    col_pj1, col_pj2 = st.columns(2)
    
    with col_pj1:
        bulan_lalu = st.selectbox("Pilih Bulan Sebelumnya", BULAN_LIST, index=0, key="select_bulan_lalu")
        pj_store_lalu = st.text_input(f"Nama PJ Store LM (Periode {bulan_lalu})", "Nama PJ Store Bulan Lalu")

    with col_pj2:
        bulan_ini = st.selectbox("Pilih Bulan Sekarang", BULAN_LIST, index=1, key="select_bulan_ini")
        pj_store_ini = st.text_input(f"Nama PJ Store LM (Periode {bulan_ini})", "Nama PJ Store Bulan Sekarang")

# ==========================================
# 2. INPUT TABEL DATA
# ==========================================
st.subheader("📊 Rekapitulasi Data Audit")
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1. Serviceable Area",
    "2. Unserviceable Area",
    "3. Unrecorded Parts",
    "4. Facility Check",
    "5. Rekomendasi & Timeframe"
])

with tab1:
    df_serviceable = st.data_editor(
        pd.DataFrame([
            {"no": 1, "lokasi": "Rack A1", "deskripsi": "Aircraft Part Serviceable", "batch": "10", "jumlah": "50", "match": "48", "not_match": "2", "akurasi": "96%"},
        ]),
        num_rows="dynamic",
        key="editor_serviceable",
        use_container_width=True
    )

with tab2:
    df_unserviceable = st.data_editor(
        pd.DataFrame([
            {"no": 1, "lokasi": "Scrap Area", "deskripsi": "Aircraft Part Unserviceable", "batch": "2", "jumlah": "5", "match": "5", "not_match": "0", "akurasi": "100%"},
        ]),
        num_rows="dynamic",
        key="editor_unserviceable",
        use_container_width=True
    )

with tab3:
    df_unrecorded = st.data_editor(
        pd.DataFrame([
            {"no": 1, "lokasi": "Bin Store 3", "deskripsi": "Unrecorded Seal Ring", "jumlah": "10"},
        ]),
        num_rows="dynamic",
        key="editor_unrecorded",
        use_container_width=True
    )

with tab4:
    df_facility = st.data_editor(
        pd.DataFrame([
            {"no": 1, "lokasi": "Main Room Store", "deskripsi": "Area Utama", "humidity": "Kondisi Baik", "cctv": "Aktif", "firex": "Ready", "finger_access": "Aktif"},
        ]),
        num_rows="dynamic",
        key="editor_facility",
        use_container_width=True
    )

with tab5:
    st.markdown("**Rekomendasi & Timeframe Pelaksanaan**")
    st.info(f"💡 Tanggal Mulai secara otomatis mengambil dari **Tanggal Selesai Audit ({format_tgl_simpel(tgl_selesai_audit)})**.")

    df_rekom_input = st.data_editor(
        pd.DataFrame([
            {"no": 1, "subject": "Not Found", "rekomendasi": "Pemeriksaan ulang fisik & eMRO", "durasi_hari": 3},
            {"no": 2, "subject": "Unrecord Parts", "rekomendasi": "Pemeriksaan ulang fisik & eMRO", "durasi_hari": 2},
        ]),
        num_rows="dynamic",
        key="editor_rekomendasi",
        use_container_width=True,
        column_config={
            "no": st.column_config.NumberColumn("No", width="small"),
            "subject": st.column_config.TextColumn("Subjek / Masalah"),
            "rekomendasi": st.column_config.TextColumn("Rekomendasi"),
            "durasi_hari": st.column_config.NumberColumn("Durasi (Hari)", min_value=1, max_value=365, step=1, format="%d Hari")
        }
    )

    rows_rekomendasi_processed = []
    for idx, row in df_rekom_input.iterrows():
        try:
            dur = int(row.get("durasi_hari", 1))
        except (ValueError, TypeError):
            dur = 1
        
        dt_start = tgl_selesai_audit
        dt_end = tgl_selesai_audit + timedelta(days=dur)
        
        row_dict = row.to_dict()
        row_dict["no"] = row.get("no", idx + 1)
        row_dict["subject"] = row.get("subject", "")
        row_dict["rekomendasi"] = row.get("rekomendasi", "")
        row_dict["durasi"] = f"{dur} Hari"
        row_dict["durasi_hari"] = dur
        
        # Tanggal simpel untuk tabel
        row_dict["tgl_mulai"] = format_tgl_simpel(dt_start)
        row_dict["tgl_selesai"] = format_tgl_simpel(dt_end)
        row_dict["timeframe"] = f"{format_tgl_simpel(dt_start)} s/d {format_tgl_simpel(dt_end)}"
        
        rows_rekomendasi_processed.append(row_dict)

    df_final_rekomendasi = pd.DataFrame(rows_rekomendasi_processed)

    st.markdown("##### ✅ Tabel Hasil Perhitungan Otomatis (Siap Masuk Word):")
    st.dataframe(
        df_final_rekomendasi[[
            "no", "subject", "rekomendasi", "durasi", "tgl_mulai", "tgl_selesai", "timeframe"
        ]].rename(columns={
            "no": "No",
            "subject": "Subjek",
            "rekomendasi": "Rekomendasi",
            "durasi": "Durasi",
            "tgl_mulai": "Tgl Mulai",
            "tgl_selesai": "Tgl Selesai",
            "timeframe": "Rentang Timeframe"
        }),
        use_container_width=True
    )

# ==========================================
# 3. HELPER KONVERSI PDF
# ==========================================
def convert_docx_to_pdf(docx_path, output_dir):
    try:
        subprocess.run([
            "soffice", "--headless", "--convert-to", "pdf",
            docx_path, "--outdir", output_dir
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        pdf_filename = os.path.basename(docx_path).replace(".docx", ".pdf")
        return os.path.join(output_dir, pdf_filename)
    except Exception:
        return None

# ==========================================
# 4. PROSES GENERATE & DOWNLOAD DOKUMEN
# ==========================================
st.divider()
if st.button("🚀 Generate Berita Acara", type="primary", use_container_width=True):
    with st.spinner("Membaca template & mengisi data..."):
        try:
            template_bytes = fetch_master_template(TEMPLATE_DRIVE_URL)
            doc = DocxTemplate(io.BytesIO(template_bytes))
        except Exception as e:
            st.error(f"❌ Gagal mengambil template dari Google Drive: {e}")
            st.stop()

        # Context LENGKAP dengan Terbilang & Format Tanggal Simpel
        context = {
            # Metadata & Header
            "hari": hari,
            "tanggal": tanggal,
            "tanggal_terbilang": terbilang(tanggal),  # Hasil: "Lima Belas"
            "bulan": bulan,
            "tahun": tahun,
            "tahun_terbilang": terbilang(tahun),      # Hasil: "Dua Ribu Dua Puluh Enam"
            "lokasi": lokasi_bandara,
            "alamat": alamat,
            
            # Tanggal Audit Header (Format Simpel: "12 Februari 2026")
            "tgl_mulai": format_tgl_simpel(tgl_mulai_audit),
            "tgl_selesai": format_tgl_simpel(tgl_selesai_audit),
            
            # Penanggung Jawab & Auditor
            "audit_aset": audit_aset,
            "pic_lm": pic_lm,
            "bulan_lalu": bulan_lalu,
            "pj_store_lalu": pj_store_lalu,
            "bulan_ini": bulan_ini,
            "pj_store_ini": pj_store_ini,
            
            # Data Tabel
            "rows_serviceable": df_serviceable.to_dict('records'),
            "rows_unserviceable": df_unserviceable.to_dict('records'),
            "rows_unrecorded": df_unrecorded.to_dict('records'),
            "rows_facility": df_facility.to_dict('records'),
            "rows_rekomendasi": rows_rekomendasi_processed,
        }

        # Render template
        doc.render(context)

        # Simpan file
        with tempfile.TemporaryDirectory() as tmpdir:
            file_title = f"BA_Stock_Opname_{lokasi_bandara}_{tahun}"
            docx_path = os.path.join(tmpdir, f"{file_title}.docx")
            doc.save(docx_path)

            with open(docx_path, "rb") as f:
                docx_bytes = f.read()

            pdf_path = convert_docx_to_pdf(docx_path, tmpdir)
            pdf_bytes = None
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()

            st.success("✅ Berita Acara berhasil dibuat!")

            c1, c2 = st.columns(2)
            with c1:
                st.download_button(
                    label="📥 Download File DOCX (Word)",
                    data=docx_bytes,
                    file_name=f"{file_title}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            with c2:
                if pdf_bytes:
                    st.download_button(
                        label="📥 Download File PDF",
                        data=pdf_bytes,
                        file_name=f"{file_title}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
