import streamlit as st
from utils import machine_state
import pandas as pd
import os

# Data awal mesin dan tenaga yang dihasilkan
machines = {
    "MDU #01": 1.1, "MDU #02": 1.1, "MDU #03": 1.1, "MDU #04": 1.1, "MDU #05": 1.1, 
    "MDU #06": 1.1, "MDU #07": 1.1, "GND #01": 0.5, "GND #02": 0.5, "GND #03": 0.6, 
    "GND #04": 0.6, "GND #05": 0.6, "GND #06": 0.6, "MTS EDG": 0.5, "PNC #01": 1.0, 
    "PNC #02": 1.0, "PNC #03": 1.0, "PNC #04": 1.0, "PNC #05": 0.7, "PNC #06": 0.3
}


def load_machine():
    # Memuat state mesin dari file CSV jika ada
    
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

    
    tabs = st.tabs(["Form Pengisian", "Form Edit"])    
    with tabs[0]:
        if st.button("Form mematikan daya mesin", key="off_machine"):
            st.session_state["turn_off_machine"] = True
            
        if st.session_state["turn_off_machine"]:
            choose_start_date = st.date_input("Pilih tanggal mulai nonaktif: ", format="DD/MM/YYYY")
            input_start_date = pd.to_datetime(choose_start_date, format="%d-%m-%Y")
            choose_end_date = st.date_input("Pilih tanggal selesai nonaktif: ", format="DD/MM/YYYY")
            input_end_date = pd.to_datetime(choose_end_date, format="%d-%m-%Y")
            input_description = st.text_input("Masukkan keterangan: ", value="Mesin Nonaktif")
            input_new_power = st.session_state['total_capacity']
            st.write(f"Total daya yang digunakan: {input_new_power} MW")
            
            # loop untuk mendapatkan nama mesin yang dinonaktifkan
            machine_off = []
            for machine in st.session_state['machine_status']:
                if st.session_state['machine_status'][machine] == False:
                    machine_off.append(machine)
            st.write("Mesin yang dinonaktifkan:")
            
            cols = st.columns(5)
            
            for i, the_machine in enumerate(machine_off):
                with cols[i % 5]:
                    st.markdown(f"- {the_machine}")
            
            if st.button("Submit", key="submit_off_machine"):
                if input_start_date > input_end_date:
                    st.error("Tanggal mulai tidak boleh lebih besar dari tanggal selesai.")
                else:
                    df = pd.read_csv(st.session_state['data_with_machine'])
                    for single_date in pd.date_range(start=input_start_date, end=input_end_date):
                        df.loc[df['Date'] == single_date.strftime("%d-%m-%Y"), 'Power'] = input_new_power
                        df.loc[df['Date'] == single_date.strftime("%d-%m-%Y"), 'Description'] = input_description
                        df.loc[df['Date'] == single_date.strftime("%d-%m-%Y"), 'List Machine NonAktif'] = ', '.join(machine_off)
                    df.to_csv(st.session_state['data_with_machine'], index=False)
                    st.session_state["turn_off_machine"] = False
                    st.rerun()
    with tabs[1]:
        if st.button("Form edit daya mesin", key="on_machine"):
            st.session_state["turn_on_machine"] = True
            
        if st.session_state["turn_on_machine"]:
            choose_start_date = st.date_input("Pilih tanggal mulai: ", format="DD/MM/YYYY")
            input_start_date = pd.to_datetime(choose_start_date, format="%d-%m-%Y")
            choose_end_date = st.date_input("Pilih tanggal selesai : ", format="DD/MM/YYYY")
            input_end_date = pd.to_datetime(choose_end_date, format="%d-%m-%Y")
            input_description = st.text_input("Masukkan keterangan: ", value="Mesin Aktif")
            input_new_power = st.session_state['total_capacity']
            st.write(f"Total daya yang digunakan: {input_new_power} MW")
            
            # loop untuk mendapatkan nama mesin yang dinonaktifkan
            machine_on = []
            for machine in st.session_state['machine_status']:
                if st.session_state['machine_status'][machine] == True:
                    machine_on.append(machine)
            st.write("Mesin yang dihidupkan:")
            
            cols = st.columns(5)
            
            for i, the_machine in enumerate(machine_on):
                with cols[i % 5]:
                    st.markdown(f"- {the_machine}")
            
            if st.button("Submit", key="submit_on_machine"):
                if input_start_date > input_end_date:
                    st.error("Tanggal mulai tidak boleh lebih besar dari tanggal selesai.")
                else:
                    df = pd.read_csv(st.session_state['data_with_machine'])
                    for single_date in pd.date_range(start=input_start_date, end=input_end_date):
                        df.loc[df['Date'] == single_date.strftime("%d-%m-%Y"), 'Power'] = input_new_power
                        df.loc[df['Date'] == single_date.strftime("%d-%m-%Y"), 'Description'] = input_description
                        df.loc[df['Date'] == single_date.strftime("%d-%m-%Y"), 'List Machine NonAktif'] = "Tidak Ada"
                    df.to_csv(st.session_state['data_with_machine'], index=False)
                    st.session_state["turn_on_machine"] = False
                    st.rerun()
    
    # Tampilkan data beban puncak
    st.dataframe(pd.read_csv(st.session_state['data_with_machine']), use_container_width=True)

    
    # masukan power dari setiap tanggal kedalam plot
    data_total_power = pd.read_csv(st.session_state['data_with_machine'])
    total_power = data_total_power['Power']
    machine_state.plot_load_vs_capacity_old(st.session_state['data'], data_total_power)

    # Simpan state mesin ke file CSV
    machine_state.save_state_to_csv(st.session_state['machine_status'], st.session_state['total_capacity'])

    if st.button("Reset Kapasitas Mesin", key="reset_machine"):
        with open(st.session_state['data_with_machine'], "w", newline="") as file:
            df = pd.read_csv(st.session_state['data_file_name'])
            new_colum = ["Power","Description", "List Machine NonAktif"]
            
            # menambahkan df dengan new_colum jika new columd nilai kosong maka defaultnya adalah 0 dan "Mesin Aktif"
            df[new_colum[0]] = 16600
            df[new_colum[1]] = "Mesin Aktif"
            df[new_colum[2]] = "Tidak Ada"
            
            df.to_csv(file, index=False)
            st.rerun()