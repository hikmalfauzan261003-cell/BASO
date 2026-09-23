import os
import tempfile
import subprocess
import pandas as pd
import streamlit as st
from docxtpl import DocxTemplate

st.set_page_config(
    page_title="Generator BA Stock Opname",
    page_icon="📋",
    layout="wide"
)

# ---------------------------------------------------------
# DATA STATION & UNIT KERJA (LOKAL)
# ---------------------------------------------------------
# Lu bisa sesuaikan daftar station & unit kerja di bawah ini
DATA_STATION = {
    "PLM": ["Line Maintenance", "GSE"],
    "CGK": ["Line Maintenance", "GSE"],
    "SUB": ["Line Maintenance & Scheduled Maintenance", "GSE"],
    "KNO": ["Line Maintenance", "GSE"],
    "BTH": ["Line Maintenance", "GSE", "Warehouse", "Base Maintenance", "Shop"],
    "MST": ["Warehouse", "Shop"],
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
    st.title("📋 Generator Berita Acara Stock Opname")
    st.write("Pilih station lokasi audit dan unit kerja untuk memulai pembuatan Berita Acara.")

    st.divider()

    # 1. STEP 1: Pilih Station
    st.subheader("1️⃣ Pilih Station / Lokasi Bandara")
    selected_station = st.selectbox(
        "Daftar Station Tersedia:",
        options=list(DATA_STATION.keys())
    )

    st.markdown("---")

    # 2. STEP 2: Pilih Unit Kerja
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
    # Header Navigasi Halaman
    col_nav1, col_nav2 = st.columns([1, 5])
    with col_nav1:
        if st.button("⬅️ Kembali", use_container_width=True):
            st.session_state["page"] = "landing"
            st.rerun()

    st.title("📝 Form Data Stock Opname")
    st.caption(f"📍 **Station:** `{st.session_state.get('station', '-')}` | 🏭 **Unit Kerja:** `{st.session_state.get('kategori', '-')}`")
    st.divider()

    # ---------------------------------------------------------
    # 1. FORM INPUT HEADER & METADATA
    # ---------------------------------------------------------
    with st.expander("📌 Informasi Umum & Header Audit", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            hari = st.selectbox("Hari Audit", ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"])
            tanggal = st.number_input("Tanggal", min_value=1, max_value=31, value=15)
            LIST_BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
            bulan = st.selectbox("Bulan", LIST_BULAN)

            # Hitung otomatis bulan lalu berdasarkan pilihan user
            idx_bln = LIST_BULAN.index(bulan)
            bulan_lalu = LIST_BULAN[idx_bln - 1]  # Otomatis mundur 1 bulan (Januari -> Desember)
            tahun = st.number_input("Tahun", min_value=2024, max_value=2030, value=2026)
            lokasi_bandara = st.text_input("Lokasi / Bandara", value=st.session_state.get('station', 'PLM'))
            alamat = st.text_input("Alamat", "Jl. Bandara Sultan Mahmud Badaruddin II")

        with col2:
            tgl_mulai = st.date_input("Tanggal Mulai Audit")
            tgl_selesai = st.date_input("Tanggal Selesai Audit")
            pj_store_sekarang = st.text_input(f"PJ Store LM (Bulan {bulan})", "Nama PJ Store Bulan Ini")
            pj_store_lalu = st.text_input(f"PJ Store LM (Bulan {bulan_lalu})", "Nama PJ Store Bulan Lalu")
            audit_aset = st.text_input("Nama Pelaksana Audit Aset", "Nama Auditor Aset")
            pic_lm = st.text_input("Nama PIC Line Maintenance", "Nama PIC LM")

    # ---------------------------------------------------------
    # 2. INPUT TABEL DATA (EDITABLE TABLES)
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # 3. PROSES GENERATE & DOWNLOAD DOKUMEN (PAKAI TEMPLATE MASTER)
    # ---------------------------------------------------------
    st.divider()
    if st.button("🚀 Generate Berita Acara", type="primary", use_container_width=True):
        template_path = "TEMPLATE MASTER BERITA ACARA STOCK OPNAME AUDIT ASSET.docx"

        if not os.path.exists(template_path):
            st.error(f"❌ Template master tidak ditemukan di `{template_path}`. Pastikan file `.docx` sudah ada di folder `templates/` repo GitHub lu.")
        else:
            with st.spinner("Menyusun Berita Acara..."):
                doc = DocxTemplate(template_path)
                context = {
                "hari": hari,
                "tanggal": tanggal,
                "bulan": bulan,
                "bulan_lalu": bulan_lalu,                  # Tag nama bulan lalu (misal: "Desember")
                "tahun": tahun,
                "lokasi": lokasi_bandara,
                "alamat": alamat,
                "tgl_mulai": tgl_mulai.strftime("%d-%m-%Y"),
                "tgl_selesai": tgl_selesai.strftime("%d-%m-%Y"),
    
                # Tag PJ Store
                "pj_store": pj_store_sekarang,             # PJ Store bulan ini
                "pj_store_lalu": pj_store_lalu,           # PJ Store 1 bulan lalu
                "audit_aset": audit_aset,
                "pic_lm": pic_lm,
                "station": st.session_state.get("station", ""),
                "unit_kerja": st.session_state.get("kategori", ""),
    
                # Data Tabel
                    "rows_serviceable": df_serviceable.to_dict('records'),
                    "rows_unserviceable": df_unserviceable.to_dict('records'),
                    "rows_unrecorded": df_unrecorded.to_dict('records'),
                    "rows_facility": df_facility.to_dict('records'),
                    "rows_rekomendasi": df_rekomendasi.to_dict('records'),
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
                            st.warning("⚠️ Konversi PDF hanya berfungsi jika LibreOffice terpasang di server.")
