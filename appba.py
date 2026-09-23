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
    st.write("Pilih station lokasi audit dan unit kerja untuk memuat template Berita Acara yang sesuai.")

    st.divider()

    # Load data otomatis via HTTP Request
    with st.spinner("Memuat struktur template dari Google Drive..."):
        raw_data = fetch_drive_data()

    if not raw_data:
        st.warning("⚠️ Data folder belum dimuat atau folder di Google Drive masih kosong.")
        st.stop()

    # 1. STEP 1: Pilih Unit Kerja (Line Maintenance, GSE, Warehouse, Shop)
    st.subheader("1️⃣ Pilih Unit Kerja")
    unit_list = list(raw_data.keys())
    selected_kategori = st.selectbox(
        "Unit Kerja Tersedia:",
        options=unit_list,
        horizontal=True,
        index=0
    )

    st.markdown("---")

    # 2. STEP 2: Pilih Station (Ditampilkan berupa list ke bawah)
    st.subheader(f"2️⃣ Pilih Station / Lokasi ({selected_kategori})")
    stations_available = raw_data.get(selected_kategori, {})

    if stations_available:
        station_list = list(stations_available.keys())
        
        # Diganti dari selectbox ke radio (list vertikal)
        selected_station = st.radio(
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
        st.warning(f"⚠️ Belum ada divisi yang terdaftar untuk station {selected_kategori}.")
