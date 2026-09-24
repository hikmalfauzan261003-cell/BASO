import io
import os
import subprocess
import tempfile
import pandas as pd
import requests
import streamlit as st
from docxtpl import DocxTemplate

st.set_page_config(
    page_title="Generator BA Stock Opname Suki",
    page_icon="📋",
    layout="wide"
)

# ---------------------------------------------------------
# DIRECT LINK TEMPLATE MASTER GOOGLE DRIVE (BERITA ACARA)
# ---------------------------------------------------------
TEMPLATE_DRIVE_URL = "https://drive.google.com/uc?export=download"
FILE_ID_BA = "1sY3cQpEMLdCzDm5M1OkvwjandKiQE5ty"

@st.cache_data
def fetch_master_template():
    """Mengunduh template master Berita Acara dari Google Drive dengan penanganan konfirmasi virus scan."""
    session = requests.Session()
    response = session.get(TEMPLATE_DRIVE_URL, params={"id": FILE_ID_BA}, stream=True)
    
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            response = session.get(TEMPLATE_DRIVE_URL, params={"id": FILE_ID_BA, "confirm": value}, stream=True)
            break
            
    response.raise_for_status()
    return io.BytesIO(response.content)

# ---------------------------------------------------------
# DATA STATION & UNIT KERJA (LOKAL)
# ---------------------------------------------------------
DATA_STATION = {
    "Bandar Udara Internasional Sultan Mahmud Badaruddin II - PLM": ["Line Maintenance", "GSE"],
    "Bandar Udara Internasional Soekarno–Hatta - CGK": ["Line Maintenance", "GSE"],
    "Bandar Udara Internasional Juanda - SUB": ["Line Maintenance & Scheduled Maintenance", "GSE"],
    "Bandar Udara Internasional Kualanamu - KNO": ["Line Maintenance", "GSE"],
    "Bandar Udara Internasional Hang Nadim - BTH": ["Line Maintenance", "GSE", "Warehouse", "Base Maintenance", "Shop"],
    "Maintenance Shop Tangerang - MST": ["Warehouse", "Shop"],
}

def convert_docx_to_pdf(docx_path, output_dir):
    """Mengonversi dokumen DOCX ke PDF menggunakan LibreOffice."""
    try:
        subprocess.run([
            "soffice", "--headless", "--convert-to", "pdf",
            docx_path, "--outdir", output_dir
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        pdf_filename = os.path.basename(docx_path).replace(".docx", ".pdf")
        return os.path.join(output_dir, pdf_filename)
    except Exception as e:
        return None

# Inisialisasi Session State Halaman
if "page" not in st.session_state:
    st.session_state["page"] = "landing"

# =========================================================
# PAGE 1: LANDING PAGE (SELEKSI STATION & UNIT KERJA)
# =========================================================
if st.session_state["page"] == "landing":
    st.title("📋 Generator Berita Acara Stock Opname Suki")
    st.write("Pilih station lokasi audit dan unit kerja untuk memulai pembuatan Berita Acara.")

    st.divider()

    st.subheader("1️⃣ Pilih Station / Lokasi Bandara")
    selected_station = st.selectbox(
        "Daftar Station Tersedia:",
        options=list(DATA_STATION.keys())
    )

    st.markdown("---")

    st.subheader(f"2️⃣ Pilih Unit Kerja di {selected_station}")
    unit_list = DATA_STATION.get(selected_station, [])

    selected_kategori = st.radio(
        "Unit Kerja Tersedia:",
        options=unit_list,
        horizontal=True,
        index=0
    )

    st.success(f"📍 Terpilih: **{selected_station}** — **{selected_kategori}**")

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("➡️ Lanjut ke Form Audit", type="primary", use_container_width=True):
            st.session_state["station"] = selected_station
            st.session_state["kategori"] = selected_kategori
            st.session_state["page"] = "form_input"
            st.rerun()

# =========================================================
# PAGE 2: FORM INPUT AUDIT & DOKUMEN GENERATOR
# =========================================================
elif st.session_state["page"] == "form_input":
    col_nav1, col_nav2 = st.columns([1, 5])
    with col_nav1:
        if st.button("⬅️ Kembali", use_container_width=True):
            st.session_state["page"] = "landing"
            st.rerun()

    st.title("📝 Form Data Stock Opname Berita Acara")
    st.caption(f"📍 **Station:** `{st.session_state.get('station', '-')}` | 🏭 **Unit Kerja:** `{st.session_state.get('kategori', '-')}`")
    st.divider()

    # 1. FORM INPUT HEADER & METADATA
    with st.expander("📌 Informasi Umum & Header Audit", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            hari = st.selectbox("Hari Audit", ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"])
            tanggal = st.number_input("Tanggal", min_value=1, max_value=31, value=15)
            LIST_BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
            bulan = st.selectbox("Bulan", LIST_BULAN)

            idx_bln = LIST_BULAN.index(bulan)
            bulan_lalu = LIST_BULAN[idx_bln - 1]
            tahun = st.number_input("Tahun", min_value=2024, max_value=2030, value=2026)
            
            lokasi_bandara = st.text_input("Lokasi / Bandara", value=st.session_state.get('station', 'selected_station'))
            alamat = st.text_input("Alamat", "Jl. Bandara Sultan Mahmud Badaruddin II")

        with col2:
            tgl_mulai = st.date_input("Tanggal Mulai Audit")
            tgl_selesai = st.date_input("Tanggal Selesai Audit")
            pj_store_sekarang = st.text_input(f"PJ Store LM (Bulan {bulan})", "Nama PJ Store Bulan Ini")
            pj_store_lalu = st.text_input(f"PJ Store LM (Bulan {bulan_lalu})", "Nama PJ Store Bulan Lalu")
            audit_aset = st.text_input("Nama Pelaksana Audit Aset", "Nama Auditor Aset")
            pic_lm = st.text_input("Nama PIC Line Maintenance", "Nama PIC LM")

    # 2. INPUT TABEL DATA (EDITABLE TABLES)
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
                {"no": 1, "lokasi": "Rack A1", "deskripsi": "Aircraft Part Serviceable", "batch": "10", "jumlah": "50", "match": "48", "not_match": "2", "akurasi": "96"},
            ]),
            num_rows="dynamic",
            key="editor_serviceable",
            use_container_width=True
        )

    with tab2:
        st.markdown("**Hasil pemeriksaan Aircraft Part di Unserviceable Area**")
        df_unserviceable = st.data_editor(
            pd.DataFrame([
                {"no": 1, "lokasi": "Scrap Area", "deskripsi": "Aircraft Part Unserviceable", "batch": "2", "jumlah": "5", "match": "5", "not_match": "0", "akurasi": "100"},
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

    # 3. PROSES GENERATE & DOWNLOAD DOKUMEN
    st.divider()
    if st.button("🚀 Generate Berita Acara", type="primary", use_container_width=True):
        with st.spinner("Suki lagi merakit & membersihkan Berita Acara... 😹"):
            try:
                template_bytes = fetch_master_template()
                doc = DocxTemplate(template_bytes)
                
                # --- PEMBERSIH PAKSA KARAKTER SETAN '%' DI TEMPLATE ---
                for paragraph in doc.paragraphs:
                    if "%" in paragraph.text:
                        paragraph.text = paragraph.text.replace("{%", "").replace("%}", "").replace("{{%", "{{")

                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            for paragraph in cell.paragraphs:
                                if "%" in paragraph.text:
                                    paragraph.text = paragraph.text.replace("{%", "").replace("%}", "").replace("{{%", "{{")
                # ----------------------------------------------------

                context = {
                    "hari": hari,
                    "tanggal": tanggal,
                    "bulan": bulan,
                    "bulan_lalu": bulan_lalu,
                    "tahun": tahun,
                    "lokasi": lokasi_bandara,
                    "alamat": alamat,
                    "tgl_mulai": tgl_mulai.strftime("%d-%m-%Y"),
                    "tgl_selesai": tgl_selesai.strftime("%d-%m-%Y"),
                    "pj_store": pj_store_sekarang,
                    "pj_store_lalu": pj_store_lalu,
                    "audit_aset": audit_aset,
                    "pic_lm": pic_lm,
                    "station": st.session_state.get("station", ""),
                    "unit_kerja": st.session_state.get("kategori", ""),
                }

                doc.render(context)

                with tempfile.TemporaryDirectory() as tmpdir:
                    file_title = f"BA_Stock_Opname_{st.session_state.get('station', 'LOC')}_{tahun}"
                    out_docx_path = os.path.join(tmpdir, f"{file_title}.docx")
                    doc.save(out_docx_path)

                    with open(out_docx_path, "rb") as f:
                        docx_bytes = f.read()

                    pdf_path = convert_docx_to_pdf(out_docx_path, tmpdir)
                    pdf_bytes = None
                    if pdf_path and os.path.exists(pdf_path):
                        with open(pdf_path, "rb") as f:
                            pdf_bytes = f.read()

                    st.success("✅ Berita Acara Berhasil Dihitamkan & Dibersihkan! 😹")

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
                            st.warning("⚠️ Konversi PDF hanya berfungsi jika LibreOffice terpasang di server.")

            except Exception as e:
                st.error(f"❌ Gagal memproses Berita Acara: {e}")
