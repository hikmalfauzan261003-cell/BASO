import streamlit as st
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Generator BA Stock Opname", page_icon="📋", layout="wide")

# ID Folder Utama "Master Templates BA" di Google Drive kamu
ROOT_FOLDER_ID = "1m7Z7KNngFRvYn9lpPfnVfeNaM-BJLdKi"

@st.cache_resource
def get_drive_service():
    """Inisialisasi koneksi ke Google Drive API pake Service Account."""
    scopes = ["https://www.googleapis.com/auth/drive.readonly"]
    # Credentials disimpan aman di Streamlit Secrets (.streamlit/secrets.toml)
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], 
        scopes=scopes
    )
    return build("drive", "v3", credentials=creds)

@st.cache_data(ttl=300) # Cache 5 menit biar aplikasi cepet & enggak boncos API request
def fetch_subfolders(parent_id):
    """Narik daftar folder (Unit Kerja) di dalam folder utama."""
    service = get_drive_service()
    query = f"'{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    return {f["name"]: f["id"] for f in results.get("files", [])}

@st.cache_data(ttl=300)
def fetch_template_files(folder_id):
    """Narik daftar file template (.docx) di dalam folder unit kerja."""
    service = get_drive_service()
    query = f"'{folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    return {f["name"].replace(".docx", ""): f["id"] for f in results.get("files", [])}

# ---------------------------------------------------------
# LANDING PAGE UI
# ---------------------------------------------------------
st.title("📋 Generator Berita Acara Stock Opname")
st.write("Pilih unit kerja dan station lokasi audit yang otomatis terhubung dari Google Drive.")

st.divider()

# Step 1: Scan Folder Kategori / Unit Kerja
try:
    categories = fetch_subfolders(ROOT_FOLDER_ID)
    
    if not categories:
        st.warning("⚠️ Enggak ada folder unit kerja yang ditemukan di Google Drive.")
        st.stop()
        
    st.subheader("1️⃣ Pilih Unit Kerja")
    selected_kategori_name = st.radio(
        "Unit Kerja:",
        options=list(categories.keys()),
        horizontal=True
    )
    selected_kategori_id = categories[selected_kategori_name]

    st.markdown("---")

    # Step 2: Scan File Template / Station di dalam Folder Unit Kerja yang dipilih
    st.subheader(f"2️⃣ Pilih Station / Template ({selected_kategori_name})")
    templates = fetch_template_files(selected_kategori_id)

    if templates:
        selected_template_name = st.selectbox(
            "Daftar Template / Station Tersedia:",
            options=list(templates.keys())
        )
        selected_file_id = templates[selected_template_name]

        st.info(f"📌 **Template Terpilih:** `{selected_template_name}`\n\n🆔 **File ID Drive:** `{selected_file_id}`")

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("➡️ Lanjut ke Form Audit", type="primary", use_container_width=True):
                st.session_state["kategori"] = selected_kategori_name
                st.session_state["station"] = selected_template_name
                st.session_state["file_id"] = selected_file_id
                st.session_state["page"] = "form_input"
                st.rerun()
    else:
        st.warning(f"⚠️ Belum ada file template di dalam folder **{selected_kategori_name}**.")

except Exception as e:
    st.error(f"❌ Gagal mengambil data dari Google Drive API: {e}")
