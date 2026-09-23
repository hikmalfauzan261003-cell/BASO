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

 # Step 1: Pilih Station / Lokasi
    st.subheader("1️⃣ Pilih Station / Lokasi Bandara")
    all_stations = list(station_config.keys())
    selected_station = st.selectbox(
        "Daftar Station Tersedia:",
        options=all_stations
    )

    st.markdown("---")

    # Step 2: Pilih Unit Kerja berdasarkan Station yang dipilih
    st.subheader(f"2️⃣ Pilih Unit Kerja di {selected_station}")
    units_available = station_config.get(selected_station, {})

    if units_available:
        unit_list = list(units_available.keys())
        selected_kategori = st.radio(
            "Unit Kerja Tersedia:",
            options=unit_list,
            horizontal=True,
            index=0
        )

        station_info = units_available[selected_kategori]

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
        st.warning("⚠️ Belum ada unit kerja yang terdaftar untuk station ini.")
