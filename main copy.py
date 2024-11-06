import streamlit as st
import pandas as pd
import plotly.graph_objs as go

# from utils.data_loader import load_data
# from utils.prophet_model import prepare_prophet_data, predict_future
# from utils.visualizer import visualize_data, visualize_forecast
from sidebar import create_option_menu
import plotly.express as px

def create_toc(sections):
    """
    Membuat daftar isi dinamis berdasarkan heading yang diberikan.
    """
    st.markdown("## Daftar Isi 📃")
    for section in sections:
        st.markdown(f"- [{section}](#{section.lower().replace(' ', '-')})")

def plot_stacked_chart(data):
    # Resampling data
    weekly_data = data['BP'].resample('W').mean()
    monthly_data = data['BP'].resample('M').mean()
    yearly_data = data['BP'].resample('Y').mean()

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
    st.write("Silahkan klik tanggal pada bagian keterangan untuk menyeleksi analisis data dari tahun-tahun tertentu sesuai dengan yang Anda inginkan.")

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
    <h1 style="text-align: center; color: #fffff;">Aplikasi Forecasting Beban Puncak</h1>
    """, 
    unsafe_allow_html=True
)
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
    if selected == "Landing Page":
        st.subheader("Hai! 👋")
        st.write("Aplikasi ini dirancang untuk membantu Anda menganalisis data beban puncak dan memprediksi tren yang akan datang. Dengan wawasan yang tepat, Anda dapat mengambil keputusan yang lebih baik dalam pengelolaan sumber daya listrik.")
        st.write("Kami berharap aplikasi ini akan memberikan informasi yang berguna dan mendukung Anda dalam merencanakan kebutuhan energi yang lebih efisien. Selamat menggunakan aplikasi ini!")
        st.subheader("Data yang digunakan per hari ini:  📊")

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


    # Analysis Page ##################################################################################################
    elif selected == "Analysis":
        if st.session_state['data'] is None:
            st.error("Tidak ada data yang tersedia untuk dianalisis. Silakan kembali ke halaman Landing Page dan upload data atau gunakan data default.")
        else:
            st.subheader("Analisis Data Beban Puncak 📈")
            st.write("Proses analisis dimulai dengan mengumpulkan data beban puncak yang relevan, yang mencakup waktu, jumlah penggunaan, dan faktor-faktor lain yang mungkin mempengaruhi beban. Data tersebut kemudian akan dianalisis untuk mengidentifikasi pola dan tren yang muncul, seperti fluktuasi beban berdasarkan waktu, hari, atau bahkan musim.")
            st.write("Melalui visualisasi data, seperti grafik atau diagram, pengguna dapat dengan mudah memahami dan menilai informasi yang kompleks. Analisis ini tidak hanya bertujuan untuk mengevaluasi kondisi saat ini, tetapi juga untuk memprediksi beban puncak di masa depan berdasarkan pola yang ditemukan. Dengan pemahaman yang lebih baik tentang faktor-faktor yang mempengaruhi beban puncak, pengguna dapat membuat keputusan yang lebih baik dalam manajemen energi, perencanaan kapasitas, dan pengembangan strategi untuk mengoptimalkan penggunaan energi.")
            # Membuat daftar isi
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
            print(st.session_state['data'])

            st.write("Proses menilai kualitas data dengan mencari nilai yang hilang dan data duplikat. Menemukan nilai-nilai hilang ini membantu kita memastikan bahwa dataset lengkap dan tidak ada informasi penting yang terlewatkan. Selain itu, data duplikat diidentifikasi agar tidak terjadi penghitungan ganda atau pengaruh yang berlebihan dalam analisis, yang bisa mengakibatkan kesimpulan yang salah. Dengan menilai data secara menyeluruh, kita dapat menjamin bahwa data yang digunakan valid dan siap untuk analisis lebih lanjut.")
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
            st.write("Proses membersihkan data dengan memperbaiki atau menghapus data yang tidak konsisten, hilang, atau duplikat untuk meningkatkan kualitas dan akurasi dataset. Proses ini dimulai dengan menangani nilai-nilai hilang, misalnya dengan mengisi data yang hilang menggunakan metode tertentu atau menghapus baris yang tidak lengkap jika dianggap tidak signifikan.")
            if missing_values.any() or duplicate_data > 0:
                    st.session_state['data'] = st.session_state['data'].drop_duplicates()
                    st.session_state['data'] = st.session_state['data'].interpolate()   
                    st.write("Data berhasil dibersihkan.")
            else:
                st.write("Data sudah bersih.")

            # Fungsi untuk menumpukkan data berdasarkan tahun
            def plot_data_per_year(data):
                st.write("Silahkan klik tanggal pada bagian keterangan untuk menyeleksi analisis data dari tahun-tahun tertentu sesuai dengan yang Anda inginkan.")
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
            else:
                st.plotly_chart(plot_all_data(st.session_state['data']), use_container_width=True)

            st.markdown("## Rata-Rata Beban ➗")

            plot_stacked_chart(st.session_state['data'])


if _name_ == "_main_":
    main()