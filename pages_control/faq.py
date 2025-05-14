import streamlit as st

def faq():
    st.title("FAQ - Frequently Asked Questions")

    st.subheader("1. Apa itu website SiPRELIS?")
    st.write("""
        <strong>SiPRELIS</strong> adalah website yang dikembangkan untuk menyediakan <strong>sistem prediksi penggunaan listrik</strong> berbasis data. Website ini bertujuan untuk membantu pengguna dalam memprediksi penggunaan listrik mereka dalam <strong>kilowatt (kW)</strong>, sehingga dapat merencanakan konsumsi energi secara lebih efisien. 
        Dengan menggunakan data historis, <strong>SiPRELIS</strong> memberikan estimasi penggunaan listrik di masa depan, membantu mengoptimalkan biaya dan penggunaan energi.
    """, unsafe_allow_html=True)

    st.subheader("2. Apakah SiPRELIS aman?")
    st.write("""
        <strong>SiPRELIS</strong> sangat aman digunakan. Namun, kami sangat menyarankan agar Anda selalu <strong>LOGOUT</strong> setelah menggunakan website ini.
        Dengan logout, Anda dapat memastikan bahwa akun Anda tetap aman dan tidak ada informasi pribadi yang terakses oleh orang lain.
    """, unsafe_allow_html=True)

    st.subheader("3. Bagaimana urutan cara menggunakan SiPRELIS?")
    st.write("""
        Berikut adalah langkah-langkah untuk menggunakan <strong>SiPRELIS</strong> secara efektif:
        1. Mulailah dari menu <strong>Beranda</strong>, yang memberikan pengantar dan dapat mengunggah file pribadi anda.
        2. Lanjutkan ke menu <strong>Analisis</strong>, di mana Anda dapat menganalisis pola penggunaan energi listrik Anda.
        3. Terakhir, lihat hasil prediksi di menu <strong>Prediksi</strong>, yang akan memberikan perkiraan penggunaan listrik untuk periode mendatang. Ini sangat membantu dalam merencanakan penghematan energi atau biaya listrik.
    """, unsafe_allow_html=True)

    st.subheader("4. Apakah algoritma yang dipakai SiPRELIS dalam memprediksi nilai?")
    st.write("""
        <strong>SiPRELIS</strong> menggunakan <strong>algoritma Prophet</strong>, yang merupakan salah satu algoritma prediksi terbaik untuk data time series. Prophet sangat efisien dalam mengelola data yang memiliki musim atau pola yang berubah-ubah sepanjang waktu. 
        Algoritma ini dikembangkan oleh <strong>Facebook</strong> untuk menangani data dengan banyak variasi dan outlier. Prophet tidak hanya memprediksi tren masa depan tetapi juga mampu menangkap pola musiman, seperti fluktuasi musiman dalam penggunaan listrik, dengan sangat akurat.
        Oleh karena itu, <strong>SiPRELIS</strong> dapat memberikan hasil prediksi yang lebih baik, meskipun data yang digunakan tidak selalu sempurna atau terstruktur dengan sangat baik.
    """, unsafe_allow_html=True)

    st.subheader("5. Bagaimana jika saya mengalami kendala saat menggunakan website SiPRELIS?")
    st.write("""
        Jika Anda mengalami kendala teknis atau memiliki pertanyaan terkait penggunaan <strong>SiPRELIS</strong>, kami siap membantu! Anda dapat mengirimkan pertanyaan atau laporan masalah melalui email ke <strong>henptra@gmail.com</strong>. 
        Tim dukungan kami akan segera merespons dan memberikan solusi yang diperlukan untuk memastikan Anda dapat menggunakan website ini dengan lancar. 
        Jangan ragu untuk menghubungi kami jika Anda membutuhkan bantuan atau memiliki saran untuk meningkatkan <strong>SiPRELIS</strong>.
    """, unsafe_allow_html=True)