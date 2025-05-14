import streamlit as st
from utils.prophet_model import prepare_prophet_data, predict_future
from utils.visualizer import visualize_data, visualize_forecast
from utils import machine_state
import plotly.graph_objs as go
import pandas as pd
machines = {
    "MDU #01": 1.1, "MDU #02": 1.1, "MDU #03": 1.1, "MDU #04": 1.1, "MDU #05": 1.1, 
    "MDU #06": 1.1, "MDU #07": 1.1, "GND #01": 0.5, "GND #02": 0.5, "GND #03": 0.6, 
    "GND #04": 0.6, "GND #05": 0.6, "GND #06": 0.6, "MTS EDG": 0.5, "PNC #01": 1.0, 
    "PNC #02": 1.0, "PNC #03": 1.0, "PNC #04": 1.0, "PNC #05": 0.7, "PNC #06": 0.3
}
def load_prediction():
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
    
    st.subheader("Check Prediksi vs Batas Kapasitas Listrik ⚡")
    st.write("Dengan memantau prediksi beban puncak dan batas kapasitas listrik, Anda dapat mengidentifikasi potensi risiko kelebihan beban pada sistem energi. Dengan menganalisis data historis dan pola penggunaan, kita dapat memperkirakan momen-momen ketika konsumsi listrik diperkirakan akan melampaui batas kapasitas yang aman. Ini membantu dalam perencanaan dan pengelolaan energi yang lebih baik.")
    
    st.write("Silakan pilih mesin yang ingin Anda aktifkan untuk menghitung total kapasitas listrik yang dapat digunakan.")
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
    
    def plot_forecast_with_capacity(forecast, data_total_capacity):
        fig = go.Figure()
        power_data = data_total_capacity['Power'].reindex(forecast.index, fill_value=st.session_state['total_capacity'])
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Beban Puncak'))
        fig.add_trace(go.Scatter(x=forecast['ds'], y=power_data, 
                                mode='lines', name='Kapasitas Maksimum Listrik', line=dict(color='green')))
        # # Garis Merah jika BP > Kapasitas Maksimum
        # Perbandingan
        exceed_mask = forecast['yhat'] > power_data

        if exceed_mask.any():
            fig.add_trace(go.Scatter(
                x=forecast['ds'][exceed_mask],
                y=forecast['yhat'][exceed_mask],
                mode='lines',
                name='BP Melebihi Kapasitas',
                line=dict(color='red')
            ))

        fig.update_layout(title='Beban Puncak vs Kapasitas Listrik', xaxis_title='Tanggal', yaxis_title='Beban Puncak (MW)', showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
        # Filter data yang melebihi kapasitas
        exceeding_capacity_data = forecast[forecast['yhat'] > power_data]

        # # Jika ada data yang melebihi kapasitas
        if not exceeding_capacity_data.empty:
            # Buat dataframe untuk mencatat tanggal dan nilai BP yang melebihi kapasitas
            exceeded_df = pd.DataFrame({
                'Tanggal': exceeding_capacity_data['ds'],
                'Beban Puncak': exceeding_capacity_data['yhat'],
                'Maksimal Kapasitas': power_data,
            })
            
            # Delete baris yang none
            exceeded_df = exceeded_df[~exceeded_df['Tanggal'].isna()]

            # Tampilkan dataframe
            st.subheader("Tanggal dan Beban Puncak yang Melebihi Kapasitas:")
            st.dataframe(exceeded_df)
        else:
            st.write("Tidak ada beban puncak yang melebihi kapasitas.")

        # # Tampilkan data yang melebihi kapasitas jika ada
        # if not exceeding_capacity.empty:
        #     st.subheader("Prediksi yang Melebihi Kapasitas Listrik")
        #     st.write("Prediksi yang melebihi kapasitas listrik membantu mengidentifikasi potensi risiko kelebihan beban pada sistem energi. Dengan menganalisis data historis dan pola penggunaan, kita dapat memperkirakan momen-momen ketika konsumsi listrik diperkirakan akan melampaui batas kapasitas yang aman.")
        #     st.dataframe(exceeding_capacity[['ds', 'yhat']])
        # else:
        #     st.write("Tidak ada prediksi yang melebihi kapasitas listrik.")

    
    data_total_capacity = pd.read_csv(st.session_state['data_with_machine'])

    # Visualisasi prediksi dengan batas kapasitas listrik
    plot_forecast_with_capacity(forecast, data_total_capacity)