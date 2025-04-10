import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static, st_folium
import plotly.express as px

st.set_page_config(layout="wide")
# Load data sirkuit dengan koordinat dan negara
# Load data
df = pd.read_csv("Formula1_2024season_raceResults.csv")


circuits = {
    "Bahrain": [26.0325, 50.5106, "Bahrain"],
    "Jeddah": [21.6319, 39.1044, "Arab Saudi"],
    "Melbourne": [-37.8497, 144.968, "Australia"],
    "Suzuka": [34.8431, 136.541, "Jepang"],
    "Shanghai": [31.3389, 121.22, "China"],
    "Miami": [25.958, -80.2389, "Amerika Serikat"],
    "Monaco": [43.7347, 7.42056, "Monaco"],
    "Barcelona": [41.57, 2.26111, "Spanyol"],
    "Spielberg": [47.2197, 14.7647, "Austria"],
    "Silverstone": [52.0786, -1.01694, "Inggris"],
    "Hungaroring": [47.5789, 19.2486, "Hungaria"],
    "Spa": [50.4372, 5.97139, "Belgia"],
    "Zandvoort": [52.3888, 4.54092, "Belanda"],
    "Monza": [45.6156, 9.28111, "Italia"],
    "Singapore": [1.2914, 103.864, "Singapura"],
    "Austin": [30.1328, -97.6411, "Amerika Serikat"],
    "Mexico City": [19.4042, -99.0907, "Meksiko"],
    "Sao Paulo": [-23.7036, -46.6997, "Brasil"],
    "Las Vegas": [36.1147, -115.171, "Amerika Serikat"],
    "Lusail": [25.49, 51.4542, "Qatar"],
    "Abu Dhabi": [24.467, 54.6031, "Uni Emirat Arab"]
}

# Header
col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/3/33/F1.svg", width=150)  # Logo F1
with col2:
    st.title("🏎️ Formula 1 2024 Dashboard")

st.markdown("---")

# Konversi data ke DataFrame
circuit_df = pd.DataFrame.from_dict(circuits, orient='index', columns=["Latitude", "Longitude", "Country"])
circuit_df = circuit_df.reset_index().rename(columns={"index": "Circuit"})

# Pilihan dropdown buat nge-zoom peta
selected_circuit = st.selectbox("Pilih Sirkuit untuk Zoom:", circuit_df["Circuit"])
selected_row = circuit_df[circuit_df["Circuit"] == selected_circuit].iloc[0]
lat, lon = selected_row["Latitude"], selected_row["Longitude"]

# Layout 2 kolom dengan proporsi lebih luas buat peta
col1, col2 = st.columns([3, 2])  # Bikin peta lebih gede dibanding tabel

# Bagian kiri: Peta Sirkuit
with col1:
    st.subheader("🌍 Peta Sirkuit F1 2024")
    st.markdown("<br>", unsafe_allow_html=True)  # Kasih jarak sebelum peta

    # Render peta
    m = folium.Map(location=[lat, lon], zoom_start=10)
    for _, row in circuit_df.iterrows():
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=f"{row['Circuit']} - {row['Country']}",
            tooltip=f"{row['Circuit']} - {row['Country']}",
            icon=folium.Icon(color="red" if row["Circuit"] == selected_circuit else "blue")
        ).add_to(m)
    folium_static(m)

# Bagian kanan: Tabel Sirkuit
with col2:
    st.subheader("📋 Daftar Sirkuit dan Negara")
    st.markdown("<br>", unsafe_allow_html=True)  # Kasih jarak sebelum tabel
    st.dataframe(circuit_df[['Circuit', 'Country']], height=500)

st.markdown("---")  # Garis pembatas buat estetika

# Filter Tim & Pembalap
selected_teams = st.multiselect("Pilih Tim", df["Team"].unique(), default=df["Team"].unique())

# Terapkan filter ke dataframe
df_filtered = df[(df["Team"].isin(selected_teams))]

st.markdown("---")  # Garis pembatas buat estetika

# ===========================
# 1. Performance Comparison per Tim (Bar Chart)
# ===========================
st.subheader("📊 Rata-rata Posisi Finish per Tim")

# Konversi Position ke angka biar aman
df["Position"] = pd.to_numeric(df["Position"], errors="coerce")
df = df.dropna(subset=["Position"])  # Hapus baris yang gagal dikonversi

# Hitung rata-rata posisi finish per tim
avg_finish = df.groupby("Team", as_index=False)["Position"].mean()

# Buat visualisasi
fig1 = px.bar(avg_finish, x="Team", y="Position", color="Team", 
              title="Rata-rata Posisi Finish per Tim",
              labels={"Position": "Rata-rata Posisi Finish"})

st.plotly_chart(fig1, use_container_width=True)


# ===========================
# 2. Distribusi Posisi Finish per Tim (Box Plot)
# ===========================
st.subheader("📦 Distribusi Posisi Finish per Tim")

# Konversi posisi finish ke angka dan balik skalanya
df["Position"] = pd.to_numeric(df["Position"], errors="coerce")
df = df.dropna(subset=["Position"])  # Hapus NaN kalau ada
df["Reversed Position"] = 21 - df["Position"]  # Balikin, jadi makin gede makin bagus

# Hitung jumlah podium tiap tim
df["Podium"] = df["Position"].apply(lambda x: 1 if x <= 3 else 0)  # 1 kalau P1-P3, 0 kalau di luar
podium_counts = df.groupby("Team")["Podium"].sum().reset_index()

# Urutin tim berdasarkan jumlah podium tertinggi
sorted_teams = podium_counts.sort_values(by="Podium", ascending=False)["Team"]

# Bikin box plot dengan tim yang udah diurutkan
fig2 = px.box(df, x="Team", y="Reversed Position", color="Team",
              title="Distribusi Posisi Finish per Tim",
              labels={"Reversed Position": "Posisi Finish (Semakin Besar, Semakin Bagus)"},
              category_orders={"Team": sorted_teams})  # Urutin berdasarkan podium terbanyak

st.plotly_chart(fig2, use_container_width=True)


# ===========================
# 3. Tren Poin Kejuaraan (Line Chart)
# ===========================
st.subheader("📈 Tren Akumulasi Poin per Tim")

# Konversi kolom "Points" ke angka (biar aman)
df["Points"] = pd.to_numeric(df["Points"], errors="coerce")
df = df.dropna(subset=["Points"])  # Hapus NaN kalau ada

# Hitung akumulasi poin per tim sepanjang musim
df["Cumulative Points"] = df.groupby("Team")["Points"].cumsum()

# Filter data (misalnya berdasarkan tim/pembalap yang dipilih user)
df_filtered = df.copy()  # <- Sesuaikan dengan filter yang lu pake sebelumnya

# Pastikan df_filtered juga punya "Cumulative Points"
df_filtered["Cumulative Points"] = df_filtered.groupby("Team")["Points"].cumsum()

# Grafik animasi perkembangan poin per sirkuit
fig3 = px.line(df_filtered, x="Track", y="Cumulative Points", color="Team",
               title="Perkembangan Poin Sepanjang Musim",
               labels={"Track": "Sirkuit", "Cumulative Points": "Total Poin"})
st.plotly_chart(fig3, use_container_width=True, key="fig3")

# ===========================
# 4. Distribusi Fastest Lap per Tim (Histogram)
# ===========================
st.subheader("⏱️ Distribusi Fastest Lap per Tim")
fig4 = px.box(df, x="Team", y="Fastest Lap Time", color="Team",
              title="Distribusi Fastest Lap per Tim",
              labels={"Fastest Lap Time": "Waktu Lap Tercepat (s)"})
fig4.update_yaxes(autorange="reversed")



st.plotly_chart(fig4, use_container_width=True)

# ===========================
# 5. Perbandingan Kemenangan per Tim (Pie Chart)
# ===========================
st.subheader("🏆 Proporsi Kemenangan per Tim")
win_count = df[df["Position"] == 1]["Team"].value_counts().reset_index()
win_count.columns = ["Team", "Wins"]
fig5 = px.pie(win_count, values="Wins", names="Team", title="Distribusi Kemenangan per Tim")
st.plotly_chart(fig5, use_container_width=True)

fig_bar = px.bar(df_filtered, x="Cumulative Points", y="Team", color="Team",
                 orientation="h", title="Peringkat Tim Berdasarkan Poin",
                 animation_frame="Track")

st.plotly_chart(fig_bar, use_container_width=True, key="bar_chart")

import streamlit as st

# Pilih pembalap
selected_driver = st.selectbox("Pilih Pembalap", df_filtered["Driver"].unique())

# Filter data pembalap yang dipilih
df_driver = df_filtered[df_filtered["Driver"] == selected_driver]

# Buat layout 2 kolom
col1, col2 = st.columns([1, 2])  # Kolom kiri lebih lebar buat tabel

with col2:
    st.write(df_driver[["Track", "Position", "Points", "Fastest Lap Time"]])

with col1:
    # Masukkan gambar pembalap
    driver_images = {
        "Max Verstappen": "https://image-service.zaonce.net/eyJidWNrZXQiOiJmcm9udGllci1jbXMiLCJrZXkiOiJmMW1hbmFnZXIvMjAyNC9kcml2ZXJzL2hlYWRzaG90cy9mMS92ZXIucG5nIiwiZWRpdHMiOnsicmVzaXplIjp7IndpZHRoIjo1MDB9fX0=",
        "Fernando Alonso": "https://image-service.zaonce.net/eyJidWNrZXQiOiJmcm9udGllci1jbXMiLCJrZXkiOiJmMW1hbmFnZXIvMjAyNC9kcml2ZXJzL2hlYWRzaG90cy9mMS9hbG8ucG5nIiwiZWRpdHMiOnsicmVzaXplIjp7IndpZHRoIjo1MDB9fX0=",
        "Lewis Hamilton": "https://www.formula1.com/content/dam/fom-website/drivers/2024/lewis-hamilton/lewis-hamilton.png",
        "Charles Leclerc": "https://www.formula1.com/content/dam/fom-website/drivers/2024/charles-leclerc/charles-leclerc.png",
        # Tambahin pembalap lain sesuai kebutuhan
    }

    if selected_driver in driver_images:
        st.image(driver_images[selected_driver], caption=selected_driver, )
    else:
        st.write("Foto tidak tersedia")




