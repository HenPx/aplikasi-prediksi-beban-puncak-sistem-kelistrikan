import streamlit as st
import pandas as pd
import os
from utils import machine_state
from components.option_menu import create_option_menu
from datetime import datetime


import streamlit_authenticator as stauth
import streamlit as st

import yaml
from yaml.loader import SafeLoader

from pages_control.machine_control import load_machine
from pages_control.prediction_control import load_prediction
from pages_control.analysis_control import load_analysis
from pages_control.home import homepage
from pages_control.faq import faq
from pages_control.form_control import load_form


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



    
# Fungsi untuk memuat data default
def load_default_data():
    try:
        st.session_state['data_file_name'] = 'BP_2024.csv'
        return pd.read_csv('BP_2024.csv')
    except FileNotFoundError:
        st.error("Data default 'BP_2024.csv' tidak ditemukan.")
        return None

machines = {
    "MDU #01": 1.1, "MDU #02": 1.1, "MDU #03": 1.1, "MDU #04": 1.1, "MDU #05": 1.1, 
    "MDU #06": 1.1, "MDU #07": 1.1, "GND #01": 0.5, "GND #02": 0.5, "GND #03": 0.6, 
    "GND #04": 0.6, "GND #05": 0.6, "GND #06": 0.6, "MTS EDG": 0.5, "PNC #01": 1.0, 
    "PNC #02": 1.0, "PNC #03": 1.0, "PNC #04": 1.0, "PNC #05": 0.7, "PNC #06": 0.3
}

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



def main(role):
    #  Apabila user tidak aktif dalam waktu tertentu, maka session state authentication_status akan di set False
    
    
    # Sidebar menu
    with st.sidebar:
        selected = create_option_menu(role)


    # Inisialisasi session state untuk data jika belum ada
    if 'data' not in st.session_state:
        st.session_state['data'] = load_default_data()
        
    # Inisialisasi session state untuk status mesin jika belum ada
    loaded_machine_status, loaded_total_capacity = machine_state.load_state_from_csv()

    # Jika data sudah tersimpan di file, gunakan data tersebut, jika tidak inisialisasi state baru
    if loaded_machine_status and loaded_total_capacity:
        st.session_state['machine_status'] = loaded_machine_status
        st.session_state['total_capacity'] = loaded_total_capacity
    else:
        if 'machine_status' not in st.session_state:
            st.session_state['machine_status'] = {name: True for name in machines}
            
    if 'turn_off_machine' not in st.session_state:
        st.session_state['turn_off_machine'] = None
    if 'turn_on_machine' not in st.session_state:
        st.session_state['turn_on_machine'] = None
    if 'data_with_machine' not in st.session_state:
        st.session_state['data_with_machine'] = "machine_state_default.csv"

    if 'machine_status' not in st.session_state:
            st.session_state['machine_status'] = None
            
    if st.session_state['data_file_name'] == "Save_Data.csv":
        st.session_state['data_with_machine'] = "machine_state_custom.csv"
    elif st.session_state['data_file_name'] == "BP_2024.csv":
        st.session_state['data_with_machine'] = "machine_state_default.csv"
    else:
        st.write("Data tidak ditemukan.")
    
    #  cek apakah file kosong
    if not os.path.exists(st.session_state['data_with_machine']) or os.path.getsize(st.session_state['data_with_machine']) == 0:
        with open(st.session_state['data_with_machine'], "w", newline="") as file:
                df = pd.read_csv(st.session_state['data_file_name'])
                new_colum = ["Power","Description", "List Machine NonAktif"]
                
                # menambahkan df dengan new_colum jika new columd nilai kosong maka defaultnya adalah 0 dan "Mesin Aktif"
                df[new_colum[0]] = 16600
                df[new_colum[1]] = "Mesin Aktif"
                df[new_colum[2]] = "Tidak Ada"
                
                df.to_csv(file, index=False)
                st.rerun()
        
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
            st.session_state['data_file_name'] = 'Save_Data.csv'
        except FileNotFoundError:
            st.error("Belum ada data yang di upload.")

    
    
    # Landing Page
    if selected == "Beranda":
        homepage()
    # Analysis Page
    elif selected == "Analysis":
        load_analysis()
    # Prediksi Page
    elif selected == "Prediksi":
        load_prediction()
    # Mesin Page 
    elif selected == "Mesin":
        load_machine()
    # Form Pengisian Page
    elif selected == "Form Pengisian":
        load_form()
    # FaQ Page
    elif selected == "FaQ":
        faq()
    

def main_admin():
    st.write("anda admin")
    
def main_user():
    st.write("anda user")
    


time_limit = 7  # dalam detik
current_time = datetime.now()

if 'last_active' not in st.session_state:
    st.session_state['last_active'] = current_time
if 'user_online' not in st.session_state:
    st.session_state['user_online'] = True
if 'user_allowed' not in st.session_state:
    st.session_state['user_allowed'] = False
# Hitung selisih waktu dalam detik
time_diff = (current_time - st.session_state['last_active']).total_seconds()

st.write(f"Last Active: {st.session_state['last_active'].strftime('%H:%M:%S')}")
st.write(f"Current Time: {current_time.strftime('%H:%M:%S')}")
st.write(f"Time Difference: {time_diff} seconds")
# Jika selisih waktu melebihi `time_limit`, maka logout
if time_diff > time_limit:
    # membuat state untuk bertanya apakah user ingin menambah waktu aktif
    # buat countdown untuk menunggu jawaban user 10 detik
    st.warning("Session akan berakhir dalam 60 detik. Apakah Anda ingin memperpanjang waktu aktif?")
    time_ask = 30
    time_diff = time_diff - time_limit
    st.write(f"Countdown: {time_diff} seconds")
    if st.button("Tambah waktu aktif", key="add_time"):
        st.session_state['user_online'] = True
        st.session_state['last_active'] = current_time
        

        
    if time_diff > time_ask:   
        st.session_state['authentication_status'] = False
        st.warning("Session expired. Please log in again.")
        st.session_state['last_active'] = current_time
        st.session_state['user_online'] = False
        st.session_state['user_allowed'] = False
        st.rerun()
else:
    st.session_state['last_active'] = current_time




if st.session_state['user_allowed']:
    st.write(f"status: {st.session_state['authentication_status']}")
    if st.session_state.get('authentication_status'):
        get_roles = str(st.session_state.get('roles')).replace("[", "").replace("]", "").replace("'", "")
        authenticator.logout('Logout', 'sidebar')
        st.write(get_roles)
        with open('config.yaml', 'w') as file:
            yaml.dump(config, file, default_flow_style=False)
            
        if get_roles:
            main(get_roles)
        else:
            st.error("Anda tidak dikenali. Silakan hubungi admin.")
    elif st.session_state.get('authentication_status') is False:
        authenticator.login()
        st.error('Username/password is incorrect')
    elif st.session_state.get('authentication_status') is None:
        st.warning('Please enter your username and password')
else:
    if st.button("Masuk", key="login"):
        st.session_state['user_allowed']= True
        st.session_state['authentication_status'] = False
        st.session_state['user_online'] = False
        