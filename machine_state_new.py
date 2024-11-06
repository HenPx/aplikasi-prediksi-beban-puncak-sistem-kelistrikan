import csv
import os
from datetime import date
import pandas as pd
import plotly.graph_objs as go
import streamlit as st


# Nama file untuk menyimpan state mesin dan history di nonaktifkan
STATE_FILENAME = "machine_state.csv"
HISTORY_FILENAME = "machine_history.csv"
# Fungsi untuk menghapus history berdasarkan machine_name, start_date, dan end_date
def delete_history(machine_name, start_date, end_date):
    # Memuat riwayat dari file CSV
    history = load_history_from_csv()

    # Konversi start_date dan end_date dari string ke datetime
    start_date = pd.to_datetime(start_date, format='%d-%m-%Y', errors='coerce').date()
    end_date = pd.to_datetime(end_date, format='%d-%m-%Y', errors='coerce').date()

    # Filter riwayat yang valid (tanpa NaT) dan tidak sesuai dengan entri yang ingin dihapus
    updated_history = []
    for entry in history:
        entry_machine_name, entry_start_date, entry_end_date, description = entry
        
        # Konversi tanggal dari string ke datetime dan abaikan entri dengan NaT
        entry_start_date = pd.to_datetime(entry_start_date, format='%d-%m-%Y', errors='coerce')
        entry_end_date = pd.to_datetime(entry_end_date, format='%d-%m-%Y', errors='coerce')

        # Lewati entri yang memiliki NaT
        if pd.isna(entry_start_date) or pd.isna(entry_end_date):
            continue
        
        # Ubah tanggal ke tipe date untuk perbandingan
        entry_start_date = entry_start_date.date()
        entry_end_date = entry_end_date.date()

        # Simpan hanya jika mesin dan rentang tanggal tidak cocok
        if not (entry_machine_name == machine_name and entry_start_date == start_date and entry_end_date == end_date):
            updated_history.append(entry)

    # Tulis ulang file CSV dengan entri yang diperbarui
    with open(HISTORY_FILENAME, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Mesin', 'Tanggal Mulai Nonaktif', 'Tanggal Selesai Nonaktif', 'Deskripsi'])  # Tulis header
        writer.writerows(updated_history)

# Fungsi untuk menampilkan dropdown history per mesin
def display_history_with_delete(history):
    file_exists = os.path.isfile(HISTORY_FILENAME)

    with open(HISTORY_FILENAME, mode='a', newline='') as file:
        writer = csv.writer(file)

        # Jika data none, buat terlebih dahulu
        if not file_exists:
            writer.writerow(['Mesin', 'Tanggal Mulai Nonaktif', 'Tanggal Selesai Nonaktif', 'Deskripsi'])
    
    # Konversi history ke DataFrame 
    df = pd.DataFrame(history, columns=['Mesin', 'Tanggal Mulai Nonaktif', 'Tanggal Selesai Nonaktif', 'Deskripsi'])
    
    # Jika history kosong
    if df.empty:
        st.write("History belum ada.")
        return  # Berhenti jika tidak ada history
    
    # Buat dropdown untuk memilih mesin
    mesin_list = df['Mesin'].unique()
    selected_machine = st.selectbox("Pilih Mesin", mesin_list)

    # Buat dropdown untuk memilih tanggal berdasarkan mesin yang dipilih
    filtered_df = df[df['Mesin'] == selected_machine]
    date_options = filtered_df.apply(lambda row: f"{row['Tanggal Mulai Nonaktif']} - {row['Tanggal Selesai Nonaktif']}", axis=1)
    selected_date_range = st.selectbox("Pilih Tanggal", date_options)

    # Tampilkan deskripsi history yang relevan
    selected_entry = filtered_df[date_options == selected_date_range].iloc[0]
    st.write(f"Deskripsi: {selected_entry['Deskripsi']}")

    # Tambahkan tombol delete untuk entri yang dipilih
    if st.button("Delete"):
        start_date, end_date = selected_date_range.split(" - ")
        delete_history(selected_machine, start_date, end_date)
        st.success(f"History untuk {selected_machine} dihapus.")

# Fungsi untuk menyimpan history nonaktif ke file CSV
def save_history_to_csv(machine_name, start_date, end_date, description):
    # Format tanggal sesuai dengan 'dd-mm-yyyy'
    start_date_str = start_date.strftime('%d-%m-%Y')
    end_date_str = end_date.strftime('%d-%m-%Y')
    
    # Cek apakah file sudah ada atau belum
    file_exists = os.path.isfile(HISTORY_FILENAME)
    
    # Buka file CSV dan tulis data
    with open(HISTORY_FILENAME, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # Jika file belum ada, tambahkan header terlebih dahulu
        if not file_exists:
            writer.writerow(['Mesin', 'Tanggal Mulai Nonaktif', 'Tanggal Selesai Nonaktif', 'Deskripsi'])
        
        # Tulis data history
        writer.writerow([machine_name, start_date_str, end_date_str, description])

def load_history_from_csv():
    history = []
    if os.path.exists(HISTORY_FILENAME):
        with open(HISTORY_FILENAME, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                machine, start_date_str, end_date_str, desc = row
                # Gunakan format='%d-%m-%Y' untuk menangani berbagai format tanggal
                start_date = pd.to_datetime(start_date_str, format='%d-%m-%Y', errors='coerce').date()
                end_date = pd.to_datetime(end_date_str, format='%d-%m-%Y', errors='coerce').date()
                history.append((machine, start_date, end_date, desc))
    return history



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

# Fungsi untuk mendapatkan total kapasitas berdasarkan status mesin pada rentang tanggal tertentu
def get_total_capacity_on_date(machine_status, machines, nonactive_history, current_date):
    # Pastikan current_date adalah datetime.date, konversi jika perlu
    if isinstance(current_date, pd.Timestamp):
        current_date = current_date.date()
    
    # Mulai dengan kapasitas total saat ini (mesin yang aktif)
    active_capacity = sum([machines[machine] for machine, status in machine_status.items() if status])

    # Cek apakah ada mesin yang nonaktif pada tanggal tersebut dan kurangi kapasitas
    for machine, start_date, end_date, _ in nonactive_history:
        # Perbandingan hanya dilakukan jika start_date dan end_date bertipe datetime.date
        if isinstance(start_date, date) and isinstance(end_date, date):
            # Jika current_date berada dalam rentang penonaktifan, kurangi kapasitas mesin
            if start_date <= current_date <= end_date:
                active_capacity -= machines[machine]

    return active_capacity * 1000  # Kapasitas dalam MW

# Fungsi untuk memvisualisasikan data beban puncak dengan mempertimbangkan penonaktifan mesin
def plot_load_vs_capacity(data, machines, machine_status, nonactive_history):
    # Membaca data dari file CSV yang diberikan
    data = pd.read_csv('BP_2024.csv')

    # Konversi kolom Date menjadi tipe datetime
    data['Date'] = pd.to_datetime(data['Date'], format='%d-%m-%Y', errors='coerce')

    fig = go.Figure()

    capacities = []
    for current_date in data['Date']:
        if isinstance(current_date, pd.Timestamp):
            current_date = current_date.date()

        total_capacity = get_total_capacity_on_date(machine_status, machines, nonactive_history, current_date)
        capacities.append(total_capacity)

    fig.add_trace(go.Scatter(x=data['Date'], y=data['BP'], mode='lines', name='Beban Puncak'))

    fig.add_trace(go.Scatter(x=data['Date'], y=capacities, mode='lines', name='Kapasitas Maksimum Listrik', line=dict(color='green')))

    below_or_equal_capacity = data['BP'].where(data['BP'] <= capacities, capacities)
    fig.add_trace(go.Scatter(x=data['Date'], y=below_or_equal_capacity, mode='lines', name='Beban Puncak (Di Bawah Kapasitas)', line=dict(color='green')))

    above_capacity = data['BP'].where(data['BP'] > capacities, capacities)
    fig.add_trace(go.Scatter(x=data['Date'], y=above_capacity, mode='lines', name='Beban Melebihi Kapasitas', line=dict(color='red')))

    # Update layoutz
    fig.update_layout(title='Beban Puncak vs Kapasitas Listrik', xaxis_title='Tanggal', yaxis_title='Beban Puncak (MW)', showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

    # Filter data yang melebihi kapasitas
    exceeding_capacity_data = data[data['BP'] > capacities]

    # Jika ada data yang melebihi kapasitas
    if not exceeding_capacity_data.empty:
        # Buat dataframe untuk mencatat tanggal dan nilai BP yang melebihi kapasitas
        exceeded_df = pd.DataFrame({
            'Tanggal': exceeding_capacity_data.index,
            'Beban Puncak': exceeding_capacity_data['BP']
        })

        # Tampilkan dataframe
        st.subheader("Tanggal dan Beban Puncak yang Melebihi Kapasitas:")
        st.dataframe(exceeded_df)
    else:
        st.write("Tidak ada beban puncak yang melebihi kapasitas.")
        
# Fungsi untuk memvisualisasikan data beban puncak
def plot_load_vs_capacity_old(data, total_capacity):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['BP'], mode='lines', name='Beban Puncak'))
    fig.add_trace(go.Scatter(x=data.index, y=[total_capacity] * len(data), 
                             mode='lines', name='Kapasitas Maksimum Listrik', line=dict(color='green')))

    below_or_equal_capacity = data['BP'].where(data['BP'] <= total_capacity, total_capacity)
    fig.add_trace(go.Scatter(x=data.index, y=below_or_equal_capacity, mode='lines', 
                             name='Beban Puncak (Di Bawah Kapasitas)', line=dict(color='green')))
    
    above_capacity = data['BP'].where(data['BP'] > total_capacity, total_capacity)
    fig.add_trace(go.Scatter(x=data.index, y=above_capacity, mode='lines', 
                             name='Beban Melebihi Kapasitas', line=dict(color='red')))
    
    fig.update_layout(title='Beban Puncak vs Kapasitas Listrik', xaxis_title='Tanggal', yaxis_title='Beban Puncak (MW)', showlegend=True)
    st.plotly_chart(fig, use_container_width=True)
    # Filter data yang melebihi kapasitas
    exceeding_capacity_data = data[data['BP'] > total_capacity]

    # Jika ada data yang melebihi kapasitas
    if not exceeding_capacity_data.empty:
        # Buat dataframe untuk mencatat tanggal dan nilai BP yang melebihi kapasitas
        exceeded_df = pd.DataFrame({
            'Tanggal': exceeding_capacity_data['Date'],
            'Beban Puncak': exceeding_capacity_data['BP']
        })

        # Tampilkan dataframe
        st.subheader("Tanggal dan Beban Puncak yang Melebihi Kapasitas:")
        st.dataframe(exceeded_df)
    else:
        st.write("Tidak ada beban puncak yang melebihi kapasitas.")