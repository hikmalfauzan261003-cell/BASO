import streamlit as st
import requests

st.set_page_config(
    page_title="Generator BA Stock Opname",
    page_icon="📋",
    layout="wide"
)

# ---------------------------------------------------------
# LINK WEB APP GOOGLE APPS SCRIPT
# ---------------------------------------------------------
GAS_URL = "https://script.google.com/macros/s/AKfycbw3wvEcbiN44YSoSZ97ZiGVKRPT1uq-ZYvCnhmlZ7mJFxrjGjGcwHbxxlIXUj44PTL7OQ/exec"

@st.cache_data(ttl=60) # Auto refresh tiap 60 detik jika ada folder baru di Drive
def fetch_drive_data():
    try:
        response = requests.get(GAS_URL, timeout=10)
        return response.json()
    except Exception as e:
        st.error(f"Gagal mengambil data dari Drive: {e}")
        return {}

# Inisialisasi Session State
if "page" not in st.session_state:
    st.session_state["page"] = "landing"

# ---------------------------------------------------------
# PAGE 1: LANDING PAGE
# ---------------------------------------------------------
if st.session_state["page"] == "landing":
    st.title("📋 Generator Berita Acara Stock Opname")
    st.write("Pilih unit kerja dan station lokasi audit untuk memuat template Berita Acara yang sesuai.")

    st.divider()

    # Load data otomatis via HTTP Request biasa
    with st.spinner("Memuat struktur template dari Google Drive..."):
        template_config = fetch_drive_data()

    if not template_config:
        st.warning("⚠️ Data folder belum dimuat atau folder di Google Drive masih kosong.")
        st.stop()

    # Step 1: Pilih Unit Kerja / Kategori
    st.subheader("1️⃣ Pilih Unit Kerja")
    kategori_list = list(template_config.keys())
    selected_kategori = st.radio(
        "Unit Kerja:",
        options=kategori_list,
        horizontal=True,
        index=0
    )

    st.markdown("---")

    # Step 2: Pilih Station
    st.subheader(f"2️⃣ Pilih Station / Lokasi ({selected_kategori})")
    stations_available = template_config.get(selected_kategori, {})

    if stations_available:
        station_list = list(stations_available.keys())
        selected_station = st.selectbox(
            "Daftar Station Tersedia:",
            options=station_list
        )

        station_info = stations_available[selected_station]

        st.info(f"📌 **Template Terhubung:** `{station_info['file_name']}`\n\n🆔 **Drive File ID:** `{station_info['file_id']}`")

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("➡️ Lanjut ke Form Audit", type="primary", use_container_width=True):
                st.session_state["kategori"] = selected_kategori
                st.session_state["station"] = selected_station
                st.session_state["file_id"] = station_info['file_id']
                st.session_state["web_link"] = station_info['web_link']
                st.session_state["page"] = "form_input"
                st.rerun()
    else:
        st.warning("⚠️ Belum ada folder station untuk unit kerja ini di Drive.")

# ---------------------------------------------------------
# PAGE 2: FORM INPUT AUDIT
# ---------------------------------------------------------
elif st.session_state["page"] == "form_input":
    st.title("📝 Form Input Berita Acara")
    st.caption(f"Lokasi Audit: **{st.session_state['kategori']} - {st.session_state['station']}**")

    st.divider()
    
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

    if submit_btn:
        st.success("✅ Data berhasil tersimpan!")
        st.markdown(f"👉 [Buka File Template di Google Drive]({st.session_state['web_link']})")

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

        # Ekstraksi lokasi unik dari tabel Serviceable
        if "lokasi" in df_serviceable.columns and not df_serviceable["lokasi"].empty:
            loc_s_list = df_serviceable["lokasi"].dropna().astype(str).str.strip().unique().tolist()
            lokasi_serviceable_str = ", ".join([loc for loc in loc_s_list if loc])
        else:
            lokasi_serviceable_str = lokasi_bandara

        # Ekstraksi lokasi unik dari tabel Unserviceable
        if "lokasi" in df_unserviceable.columns and not df_unserviceable["lokasi"].empty:
            loc_u_list = df_unserviceable["lokasi"].dropna().astype(str).str.strip().unique().tolist()
            lokasi_unserviceable_str = ", ".join([loc for loc in loc_u_list if loc])
        else:
            lokasi_unserviceable_str = lokasi_bandara

        # Context LENGKAP dengan Terbilang, Format Tanggal Simpel, & Lokasi Otomatis
        context = {
            # Metadata & Header
            "hari": hari,
            "tanggal": tanggal,
            "tanggal_terbilang": terbilang(tanggal),
            "bulan": bulan,
            "tahun": tahun,
            "tahun_terbilang": terbilang(tahun),
            "lokasi": lokasi_bandara,
            "alamat": alamat,
            
            # Lokasi spesifik otomatis dari tabel
            "lokasi_serviceable": lokasi_serviceable_str if lokasi_serviceable_str else lokasi_bandara,
            "lokasi_unserviceable": lokasi_unserviceable_str if lokasi_unserviceable_str else lokasi_bandara,
            
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
