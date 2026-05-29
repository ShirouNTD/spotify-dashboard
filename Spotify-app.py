import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# 1. CẤU HÌNH GIAO DIỆN
st.set_page_config(page_title="Spotify Performance Hub", layout="wide", page_icon="🎧")

FILE_DU_LIEU = "spotify_master_data.csv"

# Hàm khởi tạo file CSV với cấu trúc chuẩn nếu chưa có
def khoi_tao_db():
    if not os.path.exists(FILE_DU_LIEU):
        df_mau = pd.DataFrame(columns=[
            "Tháng", "Tuần", "Kênh_Spotify", "Doanh_Thu_USD", 
            "Luot_Play", "So_Gio_Nghe", "So_Tap_Upload", "Thoi_Gian_Nhap"
        ])
        df_mau.to_csv(FILE_DU_LIEU, index=False)

khoi_tao_db()

st.title("🎧 TRUNG TÂM QUẢN TRỊ HIỆU SUẤT SPOTIFY")
st.markdown("---")

tab_dashboard, tab_nhap_lieu = st.tabs(["📊 Báo Cáo Dashboard", "📥 Cổng Nhập Liệu (Nhân Sự)"])

# ==========================================
# KHU VỰC 1: CỔNG NHẬP LIỆU
# ==========================================
with tab_nhap_lieu:
    st.subheader("Nhập liệu Báo cáo Tuần")
    
    with st.form("form_spotify", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            thang = st.selectbox("Tháng Báo Cáo:", [f"Tháng {i}" for i in range(1, 13)])
            tuan = st.selectbox("Tuần Báo Cáo:", [f"Tuần {i}" for i in range(1, 53)])
            kenh = st.text_input("Tên Kênh Spotify:").strip()
            
        with col2:
            doanh_thu = st.number_input("Doanh thu tuần (USD):", min_value=0.0, step=1.0)
            luot_play = st.number_input("Lượt Play tuần qua:", min_value=0, step=100)
            
        with col3:
            gio_nghe = st.number_input("Số giờ nghe tuần qua:", min_value=0.0, step=10.0)
            so_tap = st.number_input("Số tập Upload tuần qua:", min_value=0, step=1)
            
        btn_luu = st.form_submit_button("Lưu Dữ Liệu Lên Hệ Thống", use_container_width=True)
        
        if btn_luu:
            if not kenh:
                st.error("⚠️ Vui lòng nhập Tên Kênh Spotify!")
            else:
                df = pd.read_csv(FILE_DU_LIEU)
                du_lieu_moi = pd.DataFrame([{
                    "Tháng": thang,
                    "Tuần": tuan,
                    "Kênh_Spotify": kenh,
                    "Doanh_Thu_USD": float(doanh_thu),
                    "Luot_Play": int(luot_play),
                    "So_Gio_Nghe": float(gio_nghe),
                    "So_Tap_Upload": int(so_tap),
                    "Thoi_Gian_Nhap": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }])
                df = pd.concat([df, du_lieu_moi], ignore_index=True)
                df.to_csv(FILE_DU_LIEU, index=False)
                st.success(f"✅ Đã cập nhật thành công dữ liệu cho kênh '{kenh}' - {tuan} / {thang}!")

# ==========================================
# KHU VỰC 2: DASHBOARD TỔNG HỢP CHO BOSS
# ==========================================
with tab_dashboard:
    df = pd.read_csv(FILE_DU_LIEU)
    
    if df.empty:
        st.info("Hệ thống chưa có dữ liệu. Vui lòng sang tab 'Cổng Nhập Liệu' để bổ sung thông tin.")
    else:
        # Bộ lọc theo Tháng để xem MTD
        thang_hien_co = list(df["Tháng"].unique())
        thang_chon = st.selectbox("📅 Lọc Dashboard theo:", ["Tất cả các tháng"] + thang_hien_co)
        
        if thang_chon != "Tất cả các tháng":
            df_thang = df[df["Tháng"] == thang_chon]
        else:
            df_thang = df
            
        # 1. SCORECARDS: TỔNG DOANH THU & CHỈ SỐ MTD
        st.markdown("### 🏆 Chỉ Số Tổng Của Tháng (MTD)")
        tong_dt = df_thang["Doanh_Thu_USD"].sum()
        tong_play = df_thang["Luot_Play"].sum()
        tong_gio = df_thang["So_Gio_Nghe"].sum()
        tong_tap = df_thang["So_Tap_Upload"].sum()
        
        sc1, sc2, sc3, sc4 = st.columns(4)
        sc1.metric("💰 Tổng Doanh Thu", f"${tong_dt:,.2f}")
        sc2.metric("▶️ Tổng Lượt Play", f"{tong_play:,}")
        sc3.metric("⏱️ Tổng Giờ Nghe", f"{tong_gio:,.1f}h")
        sc4.metric("🎙️ Tổng Tập Đã Úp", f"{tong_tap:,}")
        
        st.markdown("---")
        
        # 2. XẾP HẠNG KÊNH TỐT NHẤT / YẾU NHẤT TRONG TUẦN/THÁNG
        st.markdown("### 🎯 Bảng Phong Thần Kênh Spotify")
        df_ranking = df_thang.groupby("Kênh_Spotify")["Doanh_Thu_USD"].sum().reset_index()
        df_ranking = df_ranking.sort_values(by="Doanh_Thu_USD", ascending=False)
        
        if len(df_ranking) > 0:
            top_1 = df_ranking.iloc[0]
            bot_1 = df_ranking.iloc[-1]
            
            cx, cy = st.columns(2)
            with cx:
                st.success(f"**🔥 KÊNH PERFORMANCE TỐT NHẤT:**\n\n**{top_1['Kênh_Spotify']}** (${top_1['Doanh_Thu_USD']:,.2f})")
            with cy:
                st.error(f"**❄️ KÊNH PERFORMANCE THẤP NHẤT:**\n\n**{bot_1['Kênh_Spotify']}** (${bot_1['Doanh_Thu_USD']:,.2f})")
        
        st.markdown("---")
        
        # 3. BIỂU ĐỒ TĂNG TRƯỞNG LINE CHART
        st.markdown("### 📈 Biểu Đồ Xu Hướng Tăng Trưởng (Doanh Thu & Lượt Play)")
        
        # Gom nhóm theo Tuần và Kênh để vẽ line chart nhiều đường
        df_trend = df.groupby(["Tuần", "Kênh_Spotify"])[["Doanh_Thu_USD", "Luot_Play"]].sum().reset_index()
        
        ch1, ch2 = st.columns(2)
        with ch1:
            fig_dt = px.line(df_trend, x="Tuần", y="Doanh_Thu_USD", color="Kênh_Spotify", markers=True, title="Tăng trưởng Doanh Thu qua các Tuần")
            st.plotly_chart(fig_dt, use_container_width=True)
            
        with ch2:
            fig_play = px.line(df_trend, x="Tuần", y="Luot_Play", color="Kênh_Spotify", markers=True, title="Tăng trưởng Lượt Play qua các Tuần")
            st.plotly_chart(fig_play, use_container_width=True)