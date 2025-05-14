import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
# Fungsi untuk menyimpan data ke file CSV
def save_data(data, filename="Save_Data.csv"):
    data.to_csv(filename, index=False)
    st.success(f"Data berhasil diupload.")

def homepage():
    st.header("Selamat Datang! 👋🏻")
    st.write("Aplikasi ini dirancang untuk membantu Anda menganalisis data beban puncak dan memprediksi tren yang akan datang. Dengan wawasan yang tepat, Anda dapat mengambil keputusan yang lebih baik dalam pengelolaan sumber daya listrik.")
    st.write("Kami berharap aplikasi ini akan memberikan informasi yang berguna dan mendukung Anda dalam merencanakan kebutuhan energi yang lebih efisien. Selamat menggunakan aplikasi ini!")
    st.subheader("Data yang digunakan per hari ini di Nusa Penida:  📊")

    # Tampilkan data default atau yang telah diunggah pengguna
    if st.session_state['data'] is not None:
        st.write("Saat ini, kami menampilkan data yang dihasilkan dari input Anda. Jika Anda ingin mengeksplorasi data lainnya, jangan ragu untuk mengunggah file baru di bawah ini.")
        st.dataframe(st.session_state['data'].head())
    else:
        st.error("Tidak ada data yang tersedia.")

    # Unggah file untuk mengganti data
    st.subheader("Cek ketentuan datanya dulu, yuk! 📋")
    st.markdown(
        """
        <ul>
            <li><strong>Kolom 1:</strong> Tanggal dengan format <em>dd-mm-yyyy</em>, pastikan untuk mengikuti format ini agar data dapat diproses dengan benar.</li>
            <li><strong>Kolom 2:</strong> Beban Puncak (BP) dengan format numerik/angka, harap masukkan angka tanpa simbol atau karakter lain.</li>
        </ul>
        """,
        unsafe_allow_html=True
    )
    uploaded_file = st.file_uploader("Upload data Anda (format CSV)", type="csv")
    if uploaded_file is not None:
        # Load data dari file yang diunggah
        st.session_state['data'] = pd.read_csv(uploaded_file)
        st.write("Berikut adalah data yang Anda upload:")
        st.dataframe(st.session_state['data'].head())

    # Tombol untuk menyimpan data
    if st.button("Simpan Data"):
        save_data(st.session_state['data'])
        
    st.subheader("Lokasi Data 📍")
    
    # Koordinat Nusa Penida
    nusa_penida_coords = [-8.675239286389026, 115.55320582997335]

    # Membuat peta dengan folium
    map_nusa_penida = folium.Map(location=nusa_penida_coords, zoom_start=12)

    # Link ke Google Maps
    google_maps_link = "https://maps.app.goo.gl/Zuq9yziHAMmnzHGh6"

    # Tambahkan marker dengan link ke Google Maps di popup
    folium.Marker(
        nusa_penida_coords,
        popup=f'<a href="{google_maps_link}" target="_blank">PT.PLN Nusa Penida</a>',
        icon=folium.Icon(color="red")
    ).add_to(map_nusa_penida)

    # Tampilkan peta di Streamlit
    st_folium(map_nusa_penida, width=700, height=500)