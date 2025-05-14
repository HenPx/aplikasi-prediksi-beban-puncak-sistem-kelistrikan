import csv
import os
import pandas as pd
import plotly.graph_objs as go
import streamlit as st

# Nama file untuk menyimpan state mesin dan total kapasitas
STATE_FILENAME = "machine_state.csv"


# Fungsi untuk menyimpan state mesin dan total kapasitas ke file CSV
def save_state_to_csv(machine_status, total_capacity):
    with open(STATE_FILENAME, mode='w', newline='') as file:
        writer = csv.writer(file)
        for machine, status in machine_status.items():
            writer.writerow([machine, status])
        writer.writerow(["total_capacity", total_capacity])

# Fungsi untuk memuat state mesin dan total kapasitas dari file CSV
def load_state_from_csv():
    if os.path.exists(STATE_FILENAME):
        machine_status = {}
        total_capacity = 0
        with open(STATE_FILENAME, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == "total_capacity":
                    total_capacity = float(row[1])
                else:
                    machine_status[row[0]] = row[1] == 'True'
        return machine_status, total_capacity
    else:
        return None, None

# Fungsi untuk menghitung total tenaga yang dihasilkan
def calculate_total_power(machine_status, machines):
    total_power = 0
    for machine, status in machine_status.items():
        if status:
            total_power += machines[machine]
    return total_power



# Fungsi untuk memvisualisasikan data beban puncak
def plot_load_vs_capacity_old(data, data_total_capacity):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['BP'], mode='lines', name='Beban Puncak'))
    fig.add_trace(go.Scatter(x=data['Date'], y=data_total_capacity['Power'], 
                            mode='lines', name='Kapasitas Maksimum Listrik', line=dict(color='green')))
    # Garis Merah jika BP > Kapasitas Maksimum
    exceed_mask = data['BP'] > data_total_capacity['Power']

    if exceed_mask.any():
        fig.add_trace(go.Scatter(
            x=data['Date'][exceed_mask],
            y=data['BP'][exceed_mask],
            mode='lines',
            name='BP Melebihi Kapasitas',
            line=dict(color='red')
        ))

    fig.update_layout(title='Beban Puncak vs Kapasitas Listrik', xaxis_title='Tanggal', yaxis_title='Beban Puncak (MW)', showlegend=True)
    st.plotly_chart(fig, use_container_width=True)
    # # Filter data yang melebihi kapasitas
    exceeding_capacity_data = data[data['BP'] > data_total_capacity['Power']]

    # # Jika ada data yang melebihi kapasitas
    if not exceeding_capacity_data.empty:
        # Buat dataframe untuk mencatat tanggal dan nilai BP yang melebihi kapasitas
        exceeded_df = pd.DataFrame({
            'Tanggal': exceeding_capacity_data['Date'],
            'Beban Puncak': exceeding_capacity_data['BP'],
            'Maksimal Kapasitas': data_total_capacity['Power'],
            'Keterangan': data_total_capacity['Description'],
            'List Mesin NonAktif': data_total_capacity['List Machine NonAktif']
        })
        
        # Delete baris yang none
        exceeded_df = exceeded_df[~exceeded_df['Tanggal'].isna()]

        # Tampilkan dataframe
        st.subheader("Tanggal dan Beban Puncak yang Melebihi Kapasitas:")
        st.dataframe(exceeded_df)
    else:
        st.write("Tidak ada beban puncak yang melebihi kapasitas.")
        
