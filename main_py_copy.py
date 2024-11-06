import streamlit as st
import pandas as pd
import plotly.graph_objs as go

from utils.prophet_model import prepare_prophet_data, predict_future
from utils.visualizer import visualize_data, visualize_forecast
from components.option_menu import create_option_menu
import plotly.express as px
import folium
from streamlit_folium import st_folium
from utils import machine_state
import streamlit_authenticator as stauth
import streamlit as st

import yaml
from yaml.loader import SafeLoader

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Pre-hashing all plain text passwords once
stauth.Hasher.hash_passwords(config['credentials'])

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Data awal mesin dan tenaga yang dihasilkan
machines = {
    "MDU #01": 1.1, "MDU #02": 1.1, "MDU #03": 1.1, "MDU #04": 1.1, "MDU #05": 1.1, 
    "MDU #06": 1.1, "MDU #07": 1.1, "GND #01": 0.5, "GND #02": 0.5, "GND #03": 0.6, 
    "GND #04": 0.6, "GND #05": 0.6, "GND #06": 0.6, "MTS EDG": 0.5, "PNC #01": 1.0, 
    "PNC #02": 1.0, "PNC #03": 1.0, "PNC #04": 1.0, "PNC #05": 0.7, "PNC #06": 0.3
}

# Memuat state mesin dari file CSV jika ada
loaded_machine_status, loaded_total_capacity = machine_state.load_state_from_csv()

# Jika data sudah tersimpan di file, gunakan data tersebut, jika tidak inisialisasi state baru
if loaded_machine_status and loaded_total_capacity:
    st.session_state['machine_status'] = loaded_machine_status
    st.session_state['total_capacity'] = loaded_total_capacity
else:
    if 'machine_status' not in st.session_state:
        st.session_state['machine_status'] = {name: True for name in machines}

    # Hitung total kapasitas awal
    total_power = machine_state.calculate_total_power(st.session_state['machine_status'], machines)
    st.session_state['total_capacity'] = round(total_power * 1000)




def create_toc(sections):
    """
    Membuat daftar isi dinamis berdasarkan heading yang diberikan.
    """
    st.markdown("## Daftar Isi")
    for section in sections:
        st.markdown(f"- [{section}](#{section.lower().replace(' ', '-')})")

def plot_stacked_chart(data):
    # Resampling data
    weekly_data = data['BP'].resample('W').mean()
    monthly_data = data['BP'].resample('ME').mean()
    yearly_data = data['BP'].resample('YE').mean()

    # Membuat figure baru
    fig = go.Figure()

    # Menambahkan trace untuk rata-rata mingguan
    fig.add_trace(go.Scatter(x=weekly_data.index, y=weekly_data, mode='lines', name='Rata-rata Mingguan'))

    # Menambahkan trace untuk rata-rata bulanan
    fig.add_trace(go.Scatter(x=monthly_data.index, y=monthly_data, mode='lines', name='Rata-rata Bulanan'))

    # Menambahkan trace untuk rata-rata tahunan
    fig.add_trace(go.Scatter(x=yearly_data.index, y=yearly_data, mode='lines', name='Rata-rata Tahunan'))

    # Menyusun layout
    fig.update_layout(title='Perbandingan Rata-rata Beban Puncak (Mingguan, Bulanan, Tahunan)',
                      xaxis_title='Tanggal',
                      yaxis_title='Beban Puncak',
                      showlegend=True)

    # Menampilkan chart
    st.plotly_chart(fig, use_container_width=True)
    
# Fungsi untuk memuat data default
def load_default_data():
    try:
        return pd.read_csv('BP_2024.csv')
    except FileNotFoundError:
        st.error("Data default 'BP_2024.csv' tidak ditemukan.")
        return None

# Fungsi untuk menyimpan data ke file CSV
def save_data(data, filename="Save_Data.csv"):
    data.to_csv(filename, index=False)
    st.success(f"Data berhasil diupload.")
# Judul utama aplikasi
st.markdown(
    """
    <h1 style="text-align: center; color: #fffff; font-size:35px;">Aplikasi Prediksi Beban Puncak</h1>

    
    """, 
    unsafe_allow_html=True
)
col1, col2, col3 = st.columns([2,1,2])

with col1:
    st.write("")

with col2:
    st.image("images/logoPLN.png", width=100)

with col3:
    st.write("")


st.markdown("---")

def main():
    # Sidebar menu
    with st.sidebar:
        selected = create_option_menu()


    # Inisialisasi session state untuk data jika belum ada
    if 'data' not in st.session_state:
        st.session_state['data'] = load_default_data()

    # Pilihan untuk menggunakan data default atau yang sudah disimpan
    data_option = st.sidebar.selectbox(
        "Pilih data yang ingin digunakan:",
        ["Data Default", "Data Upload"]
    )

    # Memuat dataset sesuai pilihan pengguna
    if data_option == "Data Default":
        st.session_state['data'] = load_default_data()
    elif data_option == "Data Upload":
        try:
            st.session_state['data'] = pd.read_csv("Save_Data.csv")
        except FileNotFoundError:
            st.error("Belum ada data yang di upload.")


    # Landing Page
    if selected == "Beranda":
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


    # Analysis Page
    elif selected == "Analysis":
        if st.session_state['data'] is None:
            st.error("Tidak ada data yang tersedia untuk dianalisis. Silakan kembali ke halaman Landing Page dan upload data atau gunakan data default.")
        else:
            st.header("Analisis Data Beban Puncak 📈")
            st.write("Analisis beban puncak dapat membantu Anda memahami pola penggunaan energi secara mendalam. Dengan mengumpulkan dan menganalisis data seperti waktu penggunaan dan faktor-faktor lainnya, kami dapat mengidentifikasi tren yang memengaruhi beban puncak. Melalui visualisasi data yang mudah dipahami, Anda dapat melihat fluktuasi penggunaan energi dan memprediksi beban di masa depan. Layanan ini dirancang untuk mendukung keputusan yang lebih baik dalam manajemen energi, perencanaan kapasitas, dan strategi optimalisasi penggunaan energi.")
            sections = ["Daftar Isi", "Data Wrangling", "Exploratory Data Analysis", "Rata-Rata Beban"]
            create_toc(sections)
            # Mengonversi kolom 'Date' menjadi datetime dan mengatur sebagai index
            try:
                st.session_state['data']['Date'] = pd.to_datetime(st.session_state['data']['Date'], dayfirst=True, errors='coerce')
                st.session_state['data'].set_index('Date', inplace=True)
            except KeyError:
                st.error("Kolom 'Date' tidak ditemukan di dataset.")

            # Data Wrangling Section
            st.markdown("## Data Wrangling ⌛")
            st.subheader("Display Data")
            st.write("Berikut adalah data yang Anda gunakan. Untuk mengubah data, silakan pergi ke menu Landing Page.")
            st.dataframe(st.session_state['data'].head())

            st.subheader("Assessing Data")

            st.write("Proses menilai kualitas data meliputi pencarian nilai yang hilang dan data duplikat.")
            missing_values = st.session_state['data'].isnull().sum()
            
            if 'BP' in st.session_state['data'].columns and 'Year' in st.session_state['data'].columns:
                drop_colum = st.session_state['data'].drop(['BP', 'Year'], axis=1)
            elif 'BP' in st.session_state['data'].columns:
                drop_colum = st.session_state['data'].drop('BP', axis=1)
            else:
                drop_colum = st.session_state['data']  # Jika tidak ada kolom 'BP', biarkan DataFrame tetap utuh

            duplicate_data = drop_colum.duplicated().sum()
            st.write(f"Jumlah nilai yang hilang per kolom:\n{missing_values}")
            st.write(f"Jumlah data duplikat: {duplicate_data}")
            

            st.subheader("Cleaning Data")
            st.write("Proses membersihkan data dengan memperbaiki atau menghapus data yang tidak konsisten, hilang, atau duplikat untuk meningkatkan kualitas dan akurasi dataset.")
            if missing_values.any() or duplicate_data > 0:
                    st.session_state['data'] = st.session_state['data'].drop_duplicates()
                    st.session_state['data'] = st.session_state['data'].interpolate()   
                    st.write("Data berhasil dibersihkan.")
            else:
                st.write("Data sudah bersih.")

            # Fungsi untuk menumpukkan data berdasarkan tahun
            def plot_data_per_year(data):
                st.write("_Silahkan klik tanggal pada bagian keterangan untuk menyeleksi analisis data dari tahun-tahun tertentu sesuai dengan yang Anda inginkan._")
                data['Year'] = data.index.year
                years = data['Year'].unique()
                
                fig = go.Figure()
                
                for year in years:
                    yearly_data = data[data['Year'] == year]['BP'].resample('D').mean()
                    fig.add_trace(go.Scatter(x=yearly_data.index.dayofyear, 
                                            y=yearly_data, 
                                            mode='lines', 
                                            name=str(year)))
                
                fig.update_layout(title='Data Beban Puncak per Tahun',
                                xaxis_title='Hari ke-',
                                yaxis_title='Beban Puncak',
                                showlegend=True)
                return fig

            # Fungsi untuk memvisualisasikan semua data dalam satu grafik
            def plot_all_data(data):
                daily_data = data['BP'].resample('D').mean()
                fig = px.line(daily_data, title='Data Beban Puncak Semua Tahun',
                            labels={'index': 'Tanggal', 'value': 'Beban Puncak'})
                return fig

            # Menampilkan visualisasi berdasarkan pilihan
            st.markdown("## Exploratory Data Analysis 📊")
            st.write("Pada bagian ini, Anda dapat memilih untuk menampilkan grafik data beban puncak per tahun atau semua data sekaligus.")

           # Menambahkan opsi pilihan visualisasi sebagai dropdown
            eda_option = st.selectbox("Pilih jenis visualisasi:", ['Pertahun', 'Semua Data'])

            
            # Logika kondisi untuk menampilkan visualisasi berdasarkan pilihan
            if eda_option == 'Pertahun':
                st.plotly_chart(plot_data_per_year(st.session_state['data']), use_container_width=True)
                st.markdown(
                    """
                    <ul>
                        <li> Legends ditandakan dengan beberapa warna yang melambangkan tiap tahun, untuk keterangan tiap warna dapat dilihat di sebelah kanan grafik. </li>
                        <li> Selain memilih grafik tiap tahun, Anda juga dapat melihat hubungan antar 2 tahun atau lebih, sesuai dengan tahun yang Anda pilih. </li>
                    </ul>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.plotly_chart(plot_all_data(st.session_state['data']), use_container_width=True)
                st.markdown(
                    """
                    <ul>
                        <li> Grafik menunjukkan data gabungan dari setiap tahun. </li>
                        <li> Jika Anda ingin melihat data beban puncak untuk tiap tahunnya, silahkan kembali memilih jenis visualisasi, lalu pilih pertahun. </li>
                    </ul>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("## Rata-Rata Beban ➗")

            plot_stacked_chart(st.session_state['data'])
    
    
    # Prediksi Page
    elif selected == "Prediksi":
        st.header("Cek prediksi di sini, yuk! 📈")
        st.write("Prediksi beban puncak membantu mengidentifikasi pola penggunaan energi di masa depan. Dengan memanfaatkan data historis seperti waktu penggunaan dan faktor-faktor yang memengaruhi konsumsi energi, prediksi ini memberikan wawasan mengenai fluktuasi dan tren penggunaan energi. Melalui pendekatan ini, Anda dapat membuat keputusan yang lebih baik dalam manajemen energi, perencanaan kapasitas, dan strategi optimalisasi, sehingga meningkatkan efisiensi penggunaan energi dan mengurangi risiko kelebihan beban pada sistem.")
        st.subheader("Note:")
        st.markdown(
            """
            <ul>
                <li> Anda dapat menggeser garis di bawah untuk menentukan jangka waktu prediksi yang Anda inginkan. </li>
                <li> Prediksi dibuat dengan menggunakan algoritma Prophet. </li>
                <li> Terdapat 2 jenis prediksi, yaitu <em>historical</em> dan <em>future</em>. </li>
            </ul>
            """,
            unsafe_allow_html=True
        )

        # Tentukan jumlah periode untuk prediksi (misalnya, 30 hari ke depan)
        periods = st.slider('Pilih jumlah hari untuk prediksi:', min_value=1, max_value=365, value=30)
        # Tampilkan nilai prediksi
        st.subheader(f"⚡Tren untuk {periods} Hari Terakhir⚡")
        # Siapkan data untuk Prophet
        df_prophet = prepare_prophet_data(st.session_state['data'])
        
        # Prediksi masa depan
        model, forecast = predict_future(df_prophet, periods)
        
        # Visualisasi prediksi
        visualize_forecast(model, forecast, df_prophet, periods)
        
        def plot_forecast_with_capacity(forecast, total_capacity):
            fig = go.Figure()

            # Pisahkan data prediksi yang melebihi kapasitas dan yang tidak
            below_capacity = forecast['yhat'].where(forecast['yhat'] <= total_capacity, total_capacity)
            above_capacity = forecast['yhat'].where(forecast['yhat'] > total_capacity)

            # Plot prediksi beban puncak yang di bawah atau sama dengan kapasitas (warna biru)
            fig.add_trace(go.Scatter(
                x=forecast['ds'], 
                y=below_capacity,
                mode='lines', 
                name='Prediksi Beban Puncak (Di Bawah Kapasitas)',
                line=dict(color='blue')
            ))

            # Plot prediksi beban puncak yang melebihi kapasitas (warna merah)
            fig.add_trace(go.Scatter(
                x=forecast['ds'], 
                y=above_capacity,
                mode='lines', 
                name='Prediksi Beban Puncak (Melebihi Kapasitas)',
                line=dict(color='red')
            ))

            # Plot garis batas kapasitas listrik (garis putus-putus merah)
            fig.add_trace(go.Scatter(
                x=forecast['ds'],
                y=[total_capacity] * len(forecast),
                mode='lines',
                name='Kapasitas Maksimum Listrik',
                line=dict(color='red', dash='dash')
            ))

            # Menyusun layout
            fig.update_layout(title='Prediksi Beban Puncak vs Kapasitas Listrik',
                            xaxis_title='Tanggal',
                            yaxis_title='Beban Puncak (MW)',
                            showlegend=True)

            # Tampilkan plot
            st.plotly_chart(fig, use_container_width=True)

            # Filter prediksi yang melebihi kapasitas
            exceeding_capacity = forecast[forecast['yhat'] > total_capacity]

            # Tampilkan data yang melebihi kapasitas jika ada
            if not exceeding_capacity.empty:
                st.subheader("Prediksi yang Melebihi Kapasitas Listrik")
                st.write("Prediksi yang melebihi kapasitas listrik membantu mengidentifikasi potensi risiko kelebihan beban pada sistem energi. Dengan menganalisis data historis dan pola penggunaan, kita dapat memperkirakan momen-momen ketika konsumsi listrik diperkirakan akan melampaui batas kapasitas yang aman.")
                st.dataframe(exceeding_capacity[['ds', 'yhat']])
            else:
                st.write("Tidak ada prediksi yang melebihi kapasitas listrik.")

        
        total_capacity = st.session_state.get('total_capacity', 0)

        # Visualisasi prediksi dengan batas kapasitas listrik
        plot_forecast_with_capacity(forecast, total_capacity)
    
    # Mesin Page 
    elif selected == "Mesin":
        # Judul utama
        st.header("Pengelolaan Mesin dan Beban Puncak ⚙️")
        st.write("Pengelolaan mesin dan beban puncak bertujuan untuk memastikan setiap unit mesin beroperasi secara optimal, terutama saat menghadapi beban puncak. Dalam daftar ini, setiap mesin seperti MDU, GND, PNC, dan MTS EDG memiliki peran penting dalam menjaga stabilitas sistem energi. Pengaturan yang tepat dari masing-masing mesin membantu mengurangi risiko kelebihan beban dan memastikan ketersediaan listrik yang cukup. Dengan informasi mengenai total listrik yang dapat digunakan, Anda dapat memantau kapasitas energi yang tersedia dan mengoptimalkan alokasi daya secara efektif.")
        # Membuat dua kolom
        col1, col2, col3 = st.columns(3)

        # Menambahkan gambar ke kolom pertama
        with col1:
            st.image("images/mesin1.png", caption="", use_column_width=True)

        # Menambahkan gambar ke kolom kedua
        with col2:
            st.image("images/mesin2.png", caption="Sumber: PLTD Panca Bina", use_column_width=True)
        
        # Menambahkan gambar ke kolom kedua
        with col3:
            st.image("images/mesin3.png", caption="", use_column_width=True)
        
        
        
        st.subheader("Note:")
        st.markdown(
            """
            <ul>
                <li> Anda dapat mengaktifkan dan menonaktifkan mesin-mesin di bawah sesuai keinginan Anda. </li>
                <li> Setelah memilih mesin, akan terlihat total listrik yang dapat digunakan (MW). </li>
            </ul>
            """,
            unsafe_allow_html=True
        )
        
        # Membagi mesin dalam grid 5x4
        cols = st.columns(5)
        machines_list = list(machines.keys())
        for i, machine in enumerate(machines_list):
            with cols[i % 5]:
                st.session_state['machine_status'][machine] = st.checkbox(
                    label=machine, value=st.session_state['machine_status'][machine], key=f"checkbox_{machine}"
                )
                

        # Hitung ulang total kapasitas berdasarkan status mesin terbaru
        total_power = machine_state.calculate_total_power(st.session_state['machine_status'], machines)
        st.session_state['total_capacity'] = round(total_power * 1000)
        

        st.subheader(f"Total Listrik yang Dapat Digunakan: {st.session_state['total_capacity']} MW")

        
        # Input form untuk mematikan mesin
        st.subheader("Nonaktifkan Mesin")
        selected_machine = st.selectbox("Pilih Mesin", machines_list)
        start_date = st.date_input("Tanggal Mulai Nonaktif")
        end_date = st.date_input("Tanggal Selesai Nonaktif")
        description = st.text_area("Keterangan")

        if st.button("Simpan Nonaktif"):
            machine_state.save_history_to_csv(selected_machine, start_date, end_date, description)
            st.success(f"Nonaktif {selected_machine} disimpan dari {start_date} hingga {end_date}.")

        # Menampilkan history nonaktif
        st.subheader("History Nonaktif Mesin")
        history = machine_state.load_history_from_csv()
        machine_state.display_history_with_delete(history)


        # Tampilkan data beban puncak
        st.dataframe(st.session_state['data'].head())

        # Plot beban puncak vs kapasitas
        #machine_state.plot_load_vs_capacity(st.session_state['data'], machines, st.session_state['machine_status'], history)
        machine_state.plot_load_vs_capacity_old(st.session_state['data'], st.session_state['total_capacity'])

        # Simpan state mesin ke file CSV
        machine_state.save_state_to_csv(st.session_state['machine_status'], st.session_state['total_capacity'])

            
authenticator.login()

    
if st.session_state['authentication_status']:
    main()
    authenticator.logout('Logout', 'sidebar')
    with open('config.yaml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)
elif st.session_state['authentication_status'] is False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] is None:
    st.warning('Please enter your username and password')