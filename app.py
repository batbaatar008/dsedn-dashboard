import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import os

# 1. Өгөгдөл холболт
sheet_id = "1YPHKmtE1F-xttYzvk5g0EZsK6GF7Z4fr5GgjTqZeZDE"
sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"

st.set_page_config(page_title="DSEDN Dashboard", layout="wide")

def load_data():
    return pd.read_csv(sheet_url, header=None)

try:
    raw_df = load_data()

    def clean_val(r, c):
        try:
            val = raw_df.iloc[r, c]
            if pd.isna(val) or str(val).strip().lower() == 'nan': return 0.0
            return float(str(val).replace(',', '').replace(' ', '').replace('₮', ''))
        except: return 0.0

    # --- 1. SIDEBAR: ШИНЭ ЛОГО БОЛОН ГАРЫН ҮСЭГ ---
    logo_path = "ДСТЦС ХК.png" # Энэ файл app.py-тай хамт байх ёстой
    if os.path.exists(logo_path):
        img = Image.open(logo_path)
        st.sidebar.image(img, use_container_width=True)
    
    st.sidebar.markdown("""
        <div style='text-align: center;'>
            <h4 style='font-size: 15px; color: #2C3E50; font-weight: bold; line-height: 1.4;'>
                БОРЛУУЛАЛТЫН БОДЛОГО<br>ТӨЛӨВЛӨЛТИЙН ХЭЛТЭС
            </h4>
        </div>
        """, unsafe_allow_html=True)
    
    st.sidebar.write("---")
    
    # Датаг бэлдэх
    branches = ["Дархан - ХҮТ", "Зүүнхараа", "Сүхбаатар", "Хөтөл", "Жаргалант"]
    bichilt_vals = [clean_val(17, 3), clean_val(28, 3), clean_val(39, 3), clean_val(51, 3), clean_val(62, 3)]
    orlogo_vals = [clean_val(17, 4), clean_val(28, 4), clean_val(39, 4), clean_val(51, 4), clean_val(62, 4)]
    percent_vals = [clean_val(17, 12), clean_val(28, 12), clean_val(39, 12), clean_val(51, 12), clean_val(62, 12)]

    df_full = pd.DataFrame({
        "Салбар": branches,
        "Бичилт": bichilt_vals,
        "Орлого": orlogo_vals,
        "Гүйцэтгэл": percent_vals
    })

    # Шүүлтүүр
    selected_branches = st.sidebar.multiselect("Салбар сонгох", options=df_full["Салбар"].unique(), default=df_full["Салбар"].unique())
    st.sidebar.markdown("<br><br><p style='text-align: right; color: #95A5A6; font-style: italic; font-size: 12px;'>by Batbaatar</p>", unsafe_allow_html=True)

    df = df_full[df_full["Салбар"].isin(selected_branches)].copy()

    # --- 2. ТОЛГОЙ ХЭСЭГ ---
    st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>Салбар, ХҮТ-ийн бичилт орлого</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: gray;'>Хугацаа: {raw_df.iloc[2, 0]}</p>", unsafe_allow_html=True)

    # Динамик нийт дүн (Шүүлтүүртэй уялдана)
    total_b = df["Бичилт"].sum()
    total_o = df["Орлого"].sum()
    total_p = (total_o / total_b * 100) if total_b > 0 else 0

    st.write("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("📌 Нийт Бичилт", f"{total_b:,.2f} ₮")
    col2.metric("💰 Нийт Орлого", f"{total_o:,.2f} ₮")
    col3.metric("📊 Нийт Гүйцэтгэл", f"{total_p:.2f}%")
    st.write("---")

    # --- 3. ХҮСНЭГТ (Мянгатын таслал болон Хувийн тэмдэгтэй) ---
    st.subheader("📊 Салбаруудын дэлгэрэнгүй мэдээ")
    st.dataframe(
        df,
        column_config={
            "Салбар": "Салбарын нэр",
            "Бичилт": st.column_config.NumberColumn("Бичилт (₮)", format="%0,.2f"),
            "Орлого": st.column_config.NumberColumn("Орлого (₮)", format="%0,.2f"),
            "Гүйцэтгэл": st.column_config.NumberColumn("Гүйцэтгэл", format="%.2f%%"),
        },
        hide_index=True,
        use_container_width=True
    )

    # --- 4. ГРАФИК (3 өнгөөр) ---
    st.write("---")
    st.subheader("📈 Харьцуулсан график")
    df["Зөрүү"] = df["Бичилт"] - df["Орлого"]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Салбар"], y=df["Бичилт"], name='Бичилт', marker_color='#2980B9'))
    fig.add_trace(go.Bar(x=df["Салбар"], y=df["Орлого"], name='Орлого', marker_color='#27AE60'))
    fig.add_trace(go.Bar(x=df["Салбар"], y=df["Зөрүү"], name='Зөрүү (Авлага)', marker_color='#E74C3C'))
    
    fig.update_layout(
        barmode='group',
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Алдаа гарлаа: {e}")
