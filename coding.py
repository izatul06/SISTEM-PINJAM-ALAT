import streamlit as st
import pandas as pd
from datetime import date, datetime
import os

# Nama fail
DATA_FILE = 'rekod_pinjaman.csv'
ALAT_FILE = 'senarai_alatan.csv'

# --- FUNGSI INVENTORI ---
def tetapkan_alatan_awal():
    if not os.path.isfile(ALAT_FILE):
        senarai_nama = [
            "TOTAL STATION", "TRIPOD", "PRISM", "SETAF", "AUTOMASI EDM", 
            "KAKITIGA PLUMBOB", "GELEMBUNG ARAS", "TUKUL", "PITA UKUR", 
            "KADASTER EDM", "KOMPAS", "KAKITIGA KOMPAS", "KAKI KOMPAS", 
            "UKUR KOMPAS (KOMPAS BERPRISA)", "PANCANG JAJAR", "UKUR LENGKUNG EDM", 
            "PLUMBOB", "SESIKU OPTIK", "ANAK PANAH", "ASTRONOMI EDM", 
            "SUN FILTER", "TEKIMETER EDM", "ALAT ARAS"
        ]
        no_siri_list = []
        nama_alat_list = []
        for nama in senarai_nama:
            for i in range(1, 11):
                singkatan = "".join([w[0] for w in nama.split()])
                no_siri_list.append(f"{singkatan}-{i:02d}")
                nama_alat_list.append(nama)
        data = {"No_Siri": no_siri_list, "Nama_Alat": nama_alat_list, "Status_Alat": ["Sedia"] * len(no_siri_list)}
        df = pd.DataFrame(data)
        df.to_csv(ALAT_FILE, index=False)

tetapkan_alatan_awal()

def save_data(data_df):
    if not os.path.isfile(DATA_FILE):
        data_df.to_csv(DATA_FILE, index=False)
    else:
        df_existing = pd.read_csv(DATA_FILE, dtype={'No_Siri': str})
        df_combined = pd.concat([df_existing, data_df], ignore_index=True)
        df_combined.to_csv(DATA_FILE, index=False)

# --- FUNGSI MASA ASAL ---
def komponen_masa(label_khas):
    st.markdown(f"##### ⏰ {label_khas}")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1: jam = st.selectbox("", [f"{i:02d}" for i in range(1, 13)], key=f"h_{label_khas}", label_visibility="collapsed")
    with c2: minit = st.selectbox("", [f"{i:02d}" for i in range(0, 60)], key=f"m_{label_khas}", label_visibility="collapsed")
    with c3: ampm = st.selectbox("", ["AM", "PM"], key=f"ap_{label_khas}", label_visibility="collapsed")
    st.markdown(f'<div style="background: #1E1E1E; border-radius: 15px; padding: 10px; text-align: center; border: 1px solid #333; margin-bottom: 20px;"><span style="color: #4CAF50; font-size: 24px; font-weight: bold; font-family: monospace;">{jam} : {minit} {ampm}</span></div>', unsafe_allow_html=True)
    return f"{jam}:{minit} {ampm}"

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Sistem Pinjam Alat DGU Pro", layout="wide")

if 'staff_password' not in st.session_state:
    st.session_state.staff_password = "staff123"

st.sidebar.title("🚪 Menu Utama")
peranan = st.sidebar.radio("Sila Pilih Peranan:", ["Pelajar (Student)", "Kakitangan (Staff)"])

if peranan == "Pelajar (Student)":
    st.title("🛠️ Borang Peminjaman Alatan (Student)")
    tab1, tab2, tab3 = st.tabs(["📋 Mohon Pinjaman", "🔄 Pulang Alat", "🔔 Status Kelulusan"])
    
    with tab1:
        df_stok = pd.read_csv(ALAT_FILE, dtype={'No_Siri': str})
        alat_tersedia = df_stok[df_stok['Status_Alat'] == "Sedia"]
        
        st.subheader("👥 Maklumat Kumpulan Peminjam")
        bil_orang = st.number_input("Bilangan Peminjam (Orang)", min_value=1, max_value=10, value=1)
        senarai_nama_pemohon = []
        
        col_n1, col_n2 = st.columns(2)
        for i in range(bil_orang):
            label = f"Nama Peminjam {i+1} (KETUA)" if i == 0 else f"Nama Peminjam {i+1}"
            with col_n1 if i % 2 == 0 else col_n2:
                n = st.text_input(label, key=f"nama_{i}")
                if n: senarai_nama_pemohon.append(n)
        
        nama_gabung = ", ".join(senarai_nama_pemohon)
        
        col1, col2 = st.columns(2)
        with col1:
            id_pelajar = st.text_input("ID Pelajar (Ketua)")
            no_phone = st.text_input("No. Telefon (Ketua)")
        with col2:
            kelas = st.selectbox("Pilih Kelas", ["", "DGU1A", "DGU2A", "DGU2B", "DGU3A", "DGU4A", "DGU4B", "DGU4C"])
            nama_lecturer = st.selectbox("Pensyarah Penyelia", ["", "Encik Asri", "Encik Zahir", "Encik Syed", "Encik Omar", "Encik Hairie", "Puan Laila", "Puan Ila", "Puan Naza", "Puan Nooriza", "Puan Masreta"])
            subjek = st.selectbox("Subjek", ["", "Basic Survey", "Eng Survey 1", "Eng Survey 2", "Eng Survey 3", "Cadas 1", "Cadas 2", "Astronomy"])

        st.markdown("---")
        st.subheader("📋 Pilih Alatan & No Siri")
        
        if 'pilihan_siri' not in st.session_state: 
            st.session_state.pilihan_siri = []
        
        # KEY RESET: Digunakan untuk memaksa checkbox render semula bila reset ditekan
        if 'reset_key' not in st.session_state:
            st.session_state.reset_key = 0

        jenis_alat = sorted(alat_tersedia['Nama_Alat'].unique())
        alat_dipilih = st.selectbox("Pilih Jenis Alat:", ["Sila Pilih..."] + jenis_alat)

        if alat_dipilih != "Sila Pilih...":
            st.info(f"Sila tanda No Siri untuk **{alat_dipilih}**:")
            siri_list = alat_tersedia[alat_tersedia['Nama_Alat'] == alat_dipilih]['No_Siri'].tolist()
            
            cols = st.columns(5)
            for i, siri in enumerate(siri_list):
                with cols[i % 5]:
                    # Guna reset_key supaya widget checkbox di-reset sepenuhnya secara visual
                    ckey = f"cb_{siri}_{st.session_state.reset_key}"
                    if st.checkbox(f"🆔 {siri}", key=ckey, value=(siri in st.session_state.pilihan_siri)):
                        if siri not in st.session_state.pilihan_siri:
                            st.session_state.pilihan_siri.append(siri)
                            st.rerun()
                    else:
                        if siri in st.session_state.pilihan_siri:
                            st.session_state.pilihan_siri.remove(siri)
                            st.rerun()
        
        if st.session_state.pilihan_siri:
            ringkasan_list = [f"{df_stok[df_stok['No_Siri'] == s]['Nama_Alat'].values[0]} ({s})" for s in st.session_state.pilihan_siri]
            st.warning(f"**Senarai Pinjaman Semasa:**\n" + "\n".join([f"- {i}" for i in ringkasan_list]))
            
            if st.button("Kosongkan Semua Pilihan 🗑️"):
                st.session_state.pilihan_siri = []
                st.session_state.reset_key += 1 # Paksa widget checkbox lama dibuang
                st.rerun()

        st.markdown("---")
        st.subheader("⏰ Ketetapan Waktu")
        tarikh_mula = st.date_input("Tarikh Pinjam", min_value=date.today())
        cm1, cm2 = st.columns(2)
        with cm1: masa_mula = komponen_masa("Masa Ambil")
        with cm2: anggaran_pulang = komponen_masa("Masa Pulang")
        tujuan = st.text_area("Tujuan Peminjaman")
        
        if st.button('Hantar Permohonan 🚀', use_container_width=True):
            if senarai_nama_pemohon and id_pelajar and st.session_state.pilihan_siri and kelas != "":
                ringkasan_final = [f"{df_stok[df_stok['No_Siri']==s]['Nama_Alat'].values[0]} ({s})" for s in st.session_state.pilihan_siri]
                data_baru = pd.DataFrame([{
                    "Nama": nama_gabung, "ID": id_pelajar, "No_Phone": no_phone,
                    "Kelas": kelas, "Pensyarah": nama_lecturer, "Subjek": subjek,
                    "No_Siri": ", ".join(st.session_state.pilihan_siri), 
                    "Alatan_Lengkap": ", ".join(ringkasan_final),
                    "Tarikh_Mula": str(tarikh_mula), "Masa_Pinjam": masa_mula, "Anggaran_Pulang": anggaran_pulang,
                    "Status_Pinjam": "Menunggu Kelulusan", "Masa_Pulang": "-", "Tujuan": tujuan
                }])
                for s in st.session_state.pilihan_siri:
                    df_stok.loc[df_stok['No_Siri'] == str(s), 'Status_Alat'] = "Booking"
                df_stok.to_csv(ALAT_FILE, index=False)
                save_data(data_baru)
                
                st.session_state.pilihan_siri = []
                st.session_state.reset_key += 1
                st.success("✅ Permohonan anda telah berjaya dihantar!")
                st.balloons()
            else:
                st.error("⚠️ Sila lengkapkan profil dan alatan!")

    with tab2:
        st.header("🔄 Proses Pemulangan")
        if os.path.isfile(DATA_FILE):
            df_p = pd.read_csv(DATA_FILE, dtype={'No_Siri': str})
            df_boleh_pulang = df_p[df_p['Status_Pinjam'] == "Diluluskan"]
            if not df_boleh_pulang.empty:
                list_pilihan = [f"{r['Nama'].split(',')[0]} (Ketua) - {r['Alatan_Lengkap']}" for _, r in df_boleh_pulang.iterrows()]
                pilihan_p = st.selectbox("Pilih Rekod Anda", [""] + list_pilihan)
                if st.button("Sahkan Pulang") and pilihan_p != "":
                    idx = df_boleh_pulang.index[list_pilihan.index(pilihan_p)-1]
                    siri_pulang = str(df_p.at[idx, 'No_Siri']).split(", ")
                    df_s = pd.read_csv(ALAT_FILE, dtype={'No_Siri': str})
                    for s in siri_pulang: df_s.loc[df_s['No_Siri'] == str(s).strip(), 'Status_Alat'] = "Sedia"
                    df_s.to_csv(ALAT_FILE, index=False)
                    df_p.at[idx, 'Status_Pinjam'] = "Telah Dipulangkan"
                    df_p.at[idx, 'Masa_Pulang'] = datetime.now().strftime("%I:%M %p")
                    df_p.to_csv(DATA_FILE, index=False)
                    st.success("✅ Alat berjaya dipulangkan!")
                    st.rerun()

    with tab3:
        st.header("🔔 Semakan Status Kelulusan")
        id_semak = st.text_input("Masukkan ID Pelajar (Ketua) untuk semak:")
        if id_semak and os.path.isfile(DATA_FILE):
            df_status = pd.read_csv(DATA_FILE)
            hasil = df_status[df_status['ID'] == id_semak].tail(1)
            if not hasil.empty:
                st.write(f"Status Terkini: **{hasil['Status_Pinjam'].values[0]}**")
                if hasil['Status_Pinjam'].values[0] == "Diluluskan":
                    st.balloons()
                    st.success("Permohonan anda DILULUSKAN. Sila ke stor.")
            else: st.info("Tiada rekod ditemui.")

elif peranan == "Kakitangan (Staff)":
    st.title("📊 Dashboard Staff DGU")
    col_a, col_b = st.columns([2,1])
    with col_a:
        password = st.text_input("Kata Laluan:", type="password")
    with col_b:
        with st.popover("🔑 Lupa Kata Laluan?"):
            id_stf = st.text_input("Masukkan ID Staff (12345):")
            new_pass = st.text_input("Kata Laluan Baru:", type="password")
            if st.button("Reset Kata Laluan"):
                if id_stf == "12345" and new_pass != "":
                    st.session_state.staff_password = new_pass
                    st.success("Berjaya!")
                else: st.error("ID salah.")

    if password == st.session_state.staff_password:
        t1, t2, t3 = st.tabs(["✅ Pengesahan", "📦 Inventori", "📜 Rekod"])
        with t1:
            if os.path.isfile(DATA_FILE):
                df_all = pd.read_csv(DATA_FILE, dtype={'No_Siri': str})
                df_wait = df_all[df_all['Status_Pinjam'] == "Menunggu Kelulusan"]
                if not df_wait.empty:
                    for i, row in df_wait.iterrows():
                        with st.expander(f"🔔 PERMOHONAN: {row['Nama'].split(',')[0]} ({row['Kelas']})"):
                            st.markdown(f"""
                            **Maklumat Lengkap Peminjam:**
                            * 👥 **Nama Ahli:** {row['Nama']}
                            * 🆔 **ID Ketua:** {row['ID']}
                            * 📞 **No. Telefon:** {row['No_Phone']}
                            * 🏫 **Kelas:** {row['Kelas']}
                            * 👨‍🏫 **Pensyarah:** {row['Pensyarah']}
                            * 📚 **Subjek:** {row['Subjek']}
                            * 📝 **Tujuan:** {row['Tujuan']}
                            
                            **Alatan Dimohon:**
                            * 🛠️ `{row['Alatan_Lengkap']}`
                            
                            **Waktu:**
                            * 📅 **Tarikh:** {row['Tarikh_Mula']}
                            * 🕒 **Pinjam:** {row['Masa_Pinjam']}
                            * ⏳ **Anggaran Pulang:** {row['Anggaran_Pulang']}
                            """)
                            c_l, c_t = st.columns(2)
                            if c_l.button(f"Lulus ✅", key=f"l_{i}", use_container_width=True):
                                df_all.at[i, 'Status_Pinjam'] = "Diluluskan"
                                df_s = pd.read_csv(ALAT_FILE, dtype={'No_Siri': str})
                                for s in str(row['No_Siri']).split(", "):
                                    df_s.loc[df_s['No_Siri'] == str(s).strip(), 'Status_Alat'] = "Dipinjam"
                                df_s.to_csv(ALAT_FILE, index=False); df_all.to_csv(DATA_FILE, index=False)
                                st.rerun()
                            if c_t.button(f"Tolak ❌", key=f"t_{i}", use_container_width=True):
                                df_all.at[i, 'Status_Pinjam'] = "Ditolak"
                                df_s = pd.read_csv(ALAT_FILE, dtype={'No_Siri': str})
                                for s in str(row['No_Siri']).split(", "):
                                    df_s.loc[df_s['No_Siri'] == str(s).strip(), 'Status_Alat'] = "Sedia"
                                df_s.to_csv(ALAT_FILE, index=False); df_all.to_csv(DATA_FILE, index=False)
                                st.rerun()
                else: st.info("Tiada permohonan.")
        with t2: st.dataframe(pd.read_csv(ALAT_FILE), use_container_width=True)
        with t3: st.dataframe(pd.read_csv(DATA_FILE), use_container_width=True)