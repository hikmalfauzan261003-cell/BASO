import os
import subprocess
import tempfile
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Generator BA Stock Opname",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Generator Berita Acara Stock Opname Bandara")
st.write("Isi formulir di bawah ini untuk menghasilkan dokumen Berita Acara dalam format Word (.docx) atau PDF.")

st.divider()

# ---------------------------------------------------------
# DIRECT LINK TEMPLATE MASTER GOOGLE DRIVE
# ---------------------------------------------------------
TEMPLATE_DRIVE_URL = "https://docs.google.com/document/d/1pqxqLCf-N6HxjXI7KZuRMikWEjiMIVlW/edit?usp=drive_link&ouid=112740836268247118661&rtpof=true&sd=true"


@st.cache_data
def fetch_master_template():
    """Mengunduh template master dari Google Drive dan menyimpannya di cache Streamlit."""
    response = requests.get(TEMPLATE_DRIVE_URL)
    response.raise_for_status()
    return io.BytesIO(response.content)

# ==========================================
# 1. FORM INPUT HEADER & METADATA
# ==========================================
with st.expander("📌 Informasi Umum & Header Audit", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        hari = st.selectbox("Hari Audit", ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"])
        tanggal = st.number_input("Tanggal", min_value=1, max_value=31, value=15)
        bulan = st.selectbox("Bulan", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
        tahun = st.number_input("Tahun", min_value=2024, max_value=2030, value=2026)
        lokasi_bandara = st.text_input("Lokasi / Bandara (contoh: PLM / Palembang)", "PLM")
        alamat = st.text_input("Alamat", "Jl. Bandara Sultan Mahmud Badaruddin II")

    with col2:
        tgl_mulai = st.date_input("Tanggal Mulai Audit")
        tgl_selesai = st.date_input("Tanggal Selesai Audit")
        pj_store = st.text_input("Penanggung Jawab Store LM", "Nama PJ Store")
        audit_aset = st.text_input("Nama Pelaksana Audit Aset", "Nama Auditor Aset")
        pic_lm = st.text_input("Nama PIC Line Maintenance", "Nama PIC LM")

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
    df_rekomendasi = st.data_editor(
        pd.DataFrame([
            {"no": 1, "subject": "Not Found", "rekomendasi": "Pemeriksaan ulang fisik & eMRO", "durasi": "3 Hari"},
            {"no": 2, "subject": "Unrecord Parts", "rekomendasi": "Pemeriksaan ulang fisik & eMRO", "durasi": "2 Hari"},
        ]),
        num_rows="dynamic",
        key="editor_rekomendasi",
        use_container_width=True
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
    except Exception as e:
        return None

# ==========================================
# 4. PROSES GENERATE & DOWNLOAD DOKUMEN
# ==========================================
st.divider()
if st.button("🚀 Generate Berita Acara", type="primary", use_container_width=True):
    template_path = "templates/BA_SO_TEMPLATE.docx"

    if not os.path.exists(template_path):
        st.error(f"File template '{template_path}' tidak ditemukan. Pastikan sudah diunggah di folder templates/")
    else:
        doc = DocxTemplate(template_path)

        # Menyiapkan data context untuk dimasukkan ke template Word
        context = {
            "hari": hari,
            "tanggal": tanggal,
            "bulan": bulan,
            "tahun": tahun,
            "lokasi": lokasi_bandara,
            "alamat": alamat,
            "tgl_mulai": tgl_mulai.strftime("%d-%m-%Y"),
            "tgl_selesai": tgl_selesai.strftime("%d-%m-%Y"),
            "pj_store": pj_store,
            "audit_aset": audit_aset,
            "pic_lm": pic_lm,
            
            # Data Tabel
            "rows_serviceable": df_serviceable.to_dict('records'),
            "rows_unserviceable": df_unserviceable.to_dict('records'),
            "rows_unrecorded": df_unrecorded.to_dict('records'),
            "rows_facility": df_facility.to_dict('records'),
            "rows_rekomendasi": df_rekomendasi.to_dict('records'),
        }

        # Render template dengan data dari form
        doc.render(context)

        # Gunakan temporary directory untuk menyimpan file output
        with tempfile.TemporaryDirectory() as tmpdir:
            file_title = f"BA_Stock_Opname_{lokasi_bandara}_{tahun}"
            docx_path = os.path.join(tmpdir, f"{file_title}.docx")
            doc.save(docx_path)

            # Read DOCX ke bytes
            with open(docx_path, "rb") as f:
                docx_bytes = f.read()

            # Konversi DOCX ke PDF
            pdf_path = convert_docx_to_pdf(docx_path, tmpdir)
            pdf_bytes = None
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()

            st.success("✅ Berita Acara berhasil di-generate!")

            # Tombol Download
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
                    st.warning("⚠️ Konversi PDF hanya berfungsi jika LibreOffice terpasang (misal di Streamlit Cloud/Linux).")
