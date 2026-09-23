import streamlit as st

st.set_page_config(
    page_title="Generator BA Stock Opname",
    page_icon="📋",
    layout="wide"
)

# ---------------------------------------------------------
# DATABASE / MAPPING TEMPLATE GOOGLE DRIVE (DINAMIS)
# Tambah station/kategori baru di sini, menu akan otomatis update!
# ---------------------------------------------------------
TEMPLATE_CONFIG = {
    "Line Maintenance": {
        "PLM - Palembang (Sultan Mahmud Badaruddin II)": "1pqxqLCf-N6HxjXI7KZuRMikWEjiMIVlW",
        "CGK - Jakarta (Soekarno-Hatta)": "FILE_ID_CGK_LM",
        "SUB - Surabaya (Juanda)": "FILE_ID_SUB_LM",
    },
    "GSE": {
        "PLM - Palembang (Sultan Mahmud Badaruddin II)": "FILE_ID_PLM_GSE",
        "CGK - Jakarta (Soekarno-Hatta)": "FILE_ID_CGK_GSE",
    },
    "Warehouse": {
        "Central Warehouse BSM01": "FILE_ID_WAREHOUSE_BSM01",
        "Warehouse K200": "FILE_ID_WAREHOUSE_K200",
    },
    "Shop": {
        "Avionics Shop": "FILE_ID_SHOP_AVIONICS",
    }
}

# ---------------------------------------------------------
# LANDING PAGE UI
# ---------------------------------------------------------
st.title("📋 Generator Berita Acara Stock Opname")
st.write("Pilih unit kerja dan station lokasi audit untuk memuat template Berita Acara yang sesuai.")

st.divider()

# Step 1: Pilih Unit Kerja
st.subheader("1️⃣ Pilih Unit Kerja")
kategori_list = list(TEMPLATE_CONFIG.keys())
selected_kategori = st.radio(
    "Unit Kerja:",
    options=kategori_list,
    horizontal=True,
    index=0
)

st.markdown("---")

# Step 2: Pilih Station berdasarkan Unit Kerja yang dipilih
st.subheader(f"2️⃣ Pilih Station / Lokasi ({selected_kategori})")

stations_available = TEMPLATE_CONFIG.get(selected_kategori, {})

if stations_available:
    station_list = list(stations_available.keys())
    selected_station = st.selectbox(
        "Daftar Station Tersedia:",
        options=station_list
    )
    
    # Ambil File ID Drive otomatis
    file_id_template = stations_available[selected_station]
    
    st.info(f"📌 **Template Terhubung:** `{selected_station}`\n\n🆔 **Drive File ID:** `{file_id_template}`")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("➡️ Lanjut ke Form Audit", type="primary", use_container_width=True):
            st.session_state["kategori"] = selected_kategori
            st.session_state["station"] = selected_station
            st.session_state["file_id"] = file_id_template
            st.session_state["page"] = "form_input"
            st.rerun()
else:
    st.warning("⚠️ Belum ada template station yang terdaftar untuk unit kerja ini.")

# Visualisasi jika sudah berpindah halaman (state management)
if st.session_state.get("page") == "form_input":
    st.divider()
    st.success(f"🎯 Kamu masuk ke halaman input form untuk **{st.session_state['kategori']} - {st.session_state['station']}**")
