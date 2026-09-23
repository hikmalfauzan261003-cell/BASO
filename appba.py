import os
import io
import requests
import subprocess
import tempfile
from datetime import timedelta
import pandas as pd
import streamlit as st
from docxtpl import DocxTemplate

st.set_page_config(
    page_title="Generator BA Stock Opname",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Generator Berita Acara Stock Opname Bandara")
st.write("Isi formulir di bawah ini untuk menghasilkan dokumen Berita Acara dalam format Word (.docx) atau PDF.")

st.divider()

# ---------------------------------------------------------
# HELPER FORMAT TANGGAL BAHASA INDONESIA
# ---------------------------------------------------------
HARI_LIST = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
BULAN_LIST = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni", 
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

def format_indo_date(dt):
    """Format tanggal ke Bahasa Indonesia (contoh: 'Senin, 18 Februari 2026')."""
    hari = HARI_LIST[dt.weekday()]
    tgl = dt.day
    bln = BULAN_LIST[dt.month - 1]
    thn = dt.year
    return f"{hari}, {tgl} {bln} {thn}"

# ---------------------------------------------------------
# DIRECT LINK TEMPLATE MASTER GOOGLE DRIVE
# ---------------------------------------------------------
FILE_ID = "1pqxqLCf-N6HxjXI7KZuRMikWEjiMIVlW"
TEMPLATE_DRIVE_URL = f"https://docs.google.com/document/d/{FILE_ID}/export?format=docx"


@st.cache_data(ttl=3600)
def fetch_master_template(url: str) -> bytes:
    """Mengunduh template master dari Google Drive dan menyimpannya di cache Streamlit."""
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
        tanggal = st.number_input("Tanggal", min_value=1, max_value=31, value=15)
        bulan = st.selectbox("Bulan Berita Acara", BULAN_LIST, index=1)
        tahun = st.number_input("Tahun", min_value=2024, max_value=2030, value=2026)
        lokasi_bandara = st.text_input("Lokasi / Bandara (contoh: PLM / Palembang)", "PLM")
        alamat = st.text_input("Alamat", "Jl. Bandara Sultan Mahmud Badaruddin II")

    with col2:
        tgl_mulai = st.date_input("Tanggal Mulai Audit")
        tgl_selesai = st.date_input("Tanggal Selesai Audit")
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
# 2. INPUT TABEL DATA (EDITABLE TABLES)
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
    st.markdown("**Hasil pemeriksaan Part Aircraft, General, Chemical, dan Tools di Serviceable Area**")
    df_serviceable = st.data_editor(
        pd.DataFrame([
            {"no": 1, "lokasi": "Rack A1", "deskripsi": "Aircraft Part Serviceable", "batch": "10", "jumlah": "50", "match": "48", "not_match": "2", "akurasi": "96%"},
        ]),
        num_rows="dynamic",
        key="editor_serviceable",
        use_container_width=True
    )

with tab2:
    st.markdown("**Hasil pemeriksaan Aircraft Part di Unserviceable Area**")
    df_unserviceable = st.data_editor(
        pd.DataFrame([
            {"no": 1, "lokasi": "Scrap Area", "deskripsi": "Aircraft Part Unserviceable", "batch": "2", "jumlah": "5", "match": "5", "not_match": "0", "akurasi": "100%"},
        ]),
        num_rows="dynamic",
        key="editor_unserviceable",
        use_container_width=True
    )

with tab3:
    st.markdown("**Tabel UNRECORDED Parts**")
    df_unrecorded = st.data_editor(
        pd.DataFrame([
            {"no": 1, "lokasi": "Bin Store 3", "deskripsi": "Unrecorded Seal Ring", "jumlah": "10"},
        ]),
        num_rows="dynamic",
        key="editor_unrecorded",
        use_container_width=True
    )

with tab4:
    st.markdown("**Pemeriksaan Fasilitas Store LM/GSE**")
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
    st.caption("ℹ️ Tanggal target penyelesaian akan dihitung otomatis dari Tanggal Selesai Audit berdasarkan durasi hari.")
    df_rekomendasi = st.data_editor(
        pd.DataFrame([
            {"no": 1, "subject": "Not Found", "rekomendasi": "Pemeriksaan ulang fisik & eMRO", "durasi_hari": 3},
            {"no": 2, "subject": "Unrecord Parts", "rekomendasi": "Pemeriksaan ulang fisik & eMRO", "durasi_hari": 2},
        ]),
        num_rows="dynamic",
        key="editor_rekomendasi",
        use_container_width=True,
        column_config={
            "durasi_hari": st.column_config.NumberColumn(
                "Durasi (Hari)",
                help="Jumlah hari pelaksanaan rekomendasi",
                min_value=1,
                max_value=60,
                step=1,
                format="%d Hari"
            )
        }
    )

# ==========================================
# 3. HELPER KONVERSI PDF
# ==========================================
def convert_docx_to_pdf(docx_path, output_dir):
    """Mengonversi dokumen DOCX ke PDF menggunakan LibreOffice di background."""
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
    with st.spinner("Mengunduh template master dari Google Drive & memproses dokumen..."):
        try:
            template_bytes = fetch_master_template(TEMPLATE_DRIVE_URL)
            doc = DocxTemplate(io.BytesIO(template_bytes))
        except Exception as e:
            st.error(f"❌ Gagal mengambil template dari Google Drive: {e}")
            st.info("Pastikan file di Google Drive sudah di-set 'Anyone with the link' / 'Siapa saja yang memiliki link'!")
            st.stop()

        # Proses otomatisasi tanggal timeframe rekomendasi
        rows_rekomendasi_processed = []
        for idx, row in df_rekomendasi.iterrows():
            row_dict = row.to_dict()
            try:
                durasi = int(row_dict.get("durasi_hari", 1))
            except (ValueError, TypeError):
                durasi = 1
                
            start_tf = tgl_selesai
            end_tf = tgl_selesai + timedelta(days=durasi)
            
            # Field siap pakai untuk dimasukkan ke template Word
            row_dict["durasi"] = f"{durasi} Hari"
            row_dict["tgl_mulai_tf"] = start_tf.strftime("%d-%m-%Y")
            row_dict["tgl_selesai_tf"] = end_tf.strftime("%d-%m-%Y")
            row_dict["target_date"] = format_indo_date(end_tf)
            row_dict["timeframe"] = f"{format_indo_date(start_tf)} s/d {format_indo_date(end_tf)}"
            
            rows_rekomendasi_processed.append(row_dict)

        # Context data yang dikirim ke Word Template
        context = {
            "hari": hari,
            "tanggal": tanggal,
            "bulan": bulan,
            "tahun": tahun,
            "lokasi": lokasi_bandara,
            "alamat": alamat,
            "tgl_mulai": tgl_mulai.strftime("%d-%m-%Y"),
            "tgl_selesai": tgl_selesai.strftime("%d-%m-%Y"),
            "tgl_mulai_indo": format_indo_date(tgl_mulai),
            "tgl_selesai_indo": format_indo_date(tgl_selesai),
            
            # Data PJ Store LM
            "bulan_lalu": bulan_lalu,
            "pj_store_lalu": pj_store_lalu,
            "bulan_ini": bulan_ini,
            "pj_store_ini": pj_store_ini,
            
            # Informasi Auditor & PIC
            "audit_aset": audit_aset,
            "pic_lm": pic_lm,
            
            # Data Tabel
            "rows_serviceable": df_serviceable.to_dict('records'),
            "rows_unserviceable": df_unserviceable.to_dict('records'),
            "rows_unrecorded": df_unrecorded.to_dict('records'),
            "rows_facility": df_facility.to_dict('records'),
            "rows_rekomendasi": rows_rekomendasi_processed,
        }

        # Render template
        doc.render(context)

        # Simpan ke temporary directory
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

            st.success("✅ Berita Acara berhasil di-generate!")

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
                else:
                    st.warning("⚠️ Konversi PDF membutuhkan LibreOffice (otomatis aktif di Linux/Streamlit Cloud).")
