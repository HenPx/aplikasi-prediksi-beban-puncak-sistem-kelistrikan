import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px


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

def load_analysis():
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