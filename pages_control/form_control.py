import streamlit as st
import csv
import pandas as pd
from datetime import datetime


def load_form():
    # Initialize session state
    if 'add_new_data' not in st.session_state:
        st.session_state['add_new_data'] = None
    if 'edit_new_data' not in st.session_state:
        st.session_state['edit_new_data'] = None
    if 'delete_new_data' not in st.session_state:
        st.session_state['delete_new_data'] = None
        st.write("Form Pengisian")
    
    
    st.dataframe(st.session_state['data'])
    df = pd.read_csv(st.session_state['data_file_name'])
    
    tabs = st.tabs(["Tambah Data", "Edit Data", "Hapus Data"])

    with tabs[0]:
        if st.button("Tambah Data", key="add_data"):
            st.session_state["add_new_data"] = True
        
        if st.session_state["add_new_data"]:
            choose_date = st.date_input("Pilih tanggal masukan data: ", format="DD/MM/YYYY")
            input_date = datetime.strftime(choose_date, "%d-%m-%Y")
            choose_value = st.number_input("Masukkan nilai beban puncak: ", min_value=0, step=1)

            if st.button("Submit", key="submit_add_data"):
                if (input_date) in df['Date'].values:
                    st.error("Tanggal sudah ada dalam data.")
                else:
                    with open(st.session_state['data_file_name'], 'a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([input_date, choose_value])
                        st.session_state["add_new_data"] = False
                        st.success("Data berhasil ditambahkan.")
                        st.rerun()

    with tabs[1]:
        if st.button("Edit Data", key="edit_data"):
            st.session_state["edit_new_data"] = True
        
        if st.session_state["edit_new_data"]:
            choose_date = st.date_input("Pilih tanggal yang ingin diedit: ", format="DD/MM/YYYY")
            input_date = datetime.strftime(choose_date, "%d-%m-%Y")
            input_value = st.number_input("Masukkan nilai beban puncak baru: ", min_value=0, step=1)
            if st.button("Submit", key="submit_edit_data"):
                if (input_date) not in df['Date'].values:
                    st.error("Tanggal tidak ditemukan dalam data.")
                else:
                    st.success("Tanggal ditemukan dalam data.")
                    df.loc[df['Date'] == input_date, 'BP'] = input_value
                    df.to_csv(st.session_state['data_file_name'], index=False)
                    st.session_state["edit_new_data"] = False
                    st.success("Data berhasil diedit.")
                    st.rerun()
            
    with tabs[2]:  
        if st.button("Hapus Data", key="delete_data"):
            st.session_state["delete_new_data"] = True
        
        if st.session_state["delete_new_data"]:
            choose_date = st.date_input("Pilih tanggal yang ingin dihapus: ", format="DD/MM/YYYY")
            input_date = datetime.strftime(choose_date, "%d-%m-%Y")
            if st.button("Submit", key="submit_delete_data"):
                if (input_date) not in df['Date'].values:
                    st.error("Tanggal tidak ditemukan dalam data.")
                else:
                    df = df[df['Date'] != input_date]
                    df.to_csv(st.session_state['data_file_name'], index=False)
                    st.session_state["delete_new_data"] = False
                    st.success("Data berhasil dihapus.")
                    st.rerun()
    
    