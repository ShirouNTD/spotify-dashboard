import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
import numpy as np

# 1. CẤU HÌNH GIAO DIỆN
st.set_page_config(page_title="Spotify Performance Hub", layout="wide", page_icon="🎧")

FILE_DU_LIEU = "spotify_master_data.csv"

# Hàm khởi tạo & nâng cấp file CSV
def khoi_tao_db():
    if not os.path.exists(FILE_DU_LIEU):
        df_mau = pd.DataFrame(columns=[
            "Tháng", "Tuần", "Kênh_Spotify", "Doanh_Thu_USD", 
            "Luot_Play", "So_Gio_Nghe", "So_Tap_Upload", "Bat_Kiem_Tien", "Thoi_Gian_Nhap"
        ])
        df_mau.to_csv(FILE_DU_LIEU, index=False)
    else:
        df_hien_tai = pd.read_csv(FILE_DU_LIEU)
        if "Bat_Kiem_Tien" not in df_hien_tai.columns:
            df_hien_tai["Bat_Kiem_Tien"] = False
            df_hien_tai.to_csv(FILE_DU_LIEU, index=False)

khoi_tao_db()
df = pd.read_csv(FILE_DU_LIEU)

# ==========================================
# THUẬT TOÁN "CHÌA KHÓA TÁI SINH" ĐỂ RESET FORM
# ==========================================
if "form_reset_key" not in st.session_state: 
    st.session_state.form_reset_key = 0

# ==========================================
# KHU VỰC SIDEBAR: CÀI ĐẶT KPI
# ==========================================
st.sidebar.header("🎯 THIẾT LẬP KPI MỤC TIÊU")
kpi_doanh_thu = st.sidebar.number_input("KPI Doanh Thu ($):", value=5000.0, step=100.0)
kpi_play = st.sidebar.number_input("KPI Lượt Play:", value=500000, step=10000)
kpi_gio = st.sidebar.number_input("KPI Giờ Nghe:", value=20000.0, step=1000.0)
kpi_tap = st.sidebar.number_input("KPI Số Tập Upload:", value=15, step=1)

st.title("🎧 TRUNG TÂM QUẢN TRỊ HIỆU SUẤT SPOTIFY")
st.markdown("---")

tab_dashboard, tab_nhap_lieu = st.tabs(["📊 Báo Cáo Dashboard", "📥 Cổng Nhập Liệu (Tự Động Gợi Ý)"])

# ==========================================
# KHU VỰC 1: CỔNG NHẬP LIỆU (ĐÃ FIX LỖI INSTANTIATION)
# ==========================================
with tab_nhap_lieu:
    st.subheader("Nhập liệu Báo cáo Tuần")
    st.info("💡 Hệ thống tự động Ghi đè dữ liệu trùng. Nhập thành công Form sẽ tự làm mới.")
    
    # Lấy chìa khóa reset hiện tại
    rk = st.session_state.form_reset_key
    
    col1, col2, col3 = st.columns(3)
    with col1:
        thang = st.selectbox("Tháng Báo Cáo:", [f"Tháng {i}" for i in range(1, 13)], key=f"thang_{rk}")
        tuan = st.selectbox("Tuần Báo Cáo:", [f"Tuần {i}" for i in range(1, 53)], key=f"tuan_{rk}")
        
        danh_sach_kenh_cu = list(df["Kênh_Spotify"].unique()) if not df.empty else []
        lua_chon_kenh = st.selectbox(
            "Gõ để tìm kênh hoặc Thêm kênh mới:", 
            options=["➕ Nhập kênh mới..."] + danh_sach_kenh_cu,
            key=f"chon_kenh_{rk}"
        )
        
        if lua_chon_kenh == "➕ Nhập kênh mới...":
            kenh = st.text_input("Gõ tên kênh mới vào đây:", key=f"kenh_moi_{rk}").strip()
            trang_thai_mac_dinh = False
        else:
            kenh = lua_chon_kenh
            trang_thai_mac_dinh = bool(df[df["Kênh_Spotify"] == kenh].iloc[-1]["Bat_Kiem_Tien"])
            
        trang_thai_kt = st.checkbox("✅ Kênh đã bật kiếm tiền", value=trang_thai_mac_dinh, key=f"bkt_{rk}")

    with col2:
        doanh_thu = st.number_input("Doanh thu tuần (USD):", min_value=0.0, step=1.0, key=f"dt_{rk}")
        luot_play = st.number_input("Lượt Play tuần qua:", min_value=0, step=100, key=f"play_{rk}")
    with col3:
        gio_nghe = st.number_input("Số giờ nghe tuần qua:", min_value=0.0, step=10.0, key=f"gio_{rk}")
        so_tap = st.number_input("Số tập Upload tuần qua:", min_value=0, step=1, key=f"tap_{rk}")
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Lưu Dữ Liệu Lên Hệ Thống", type="primary", use_container_width=True):
        if not kenh:
            st.error("⚠️ Vui lòng nhập hoặc chọn Tên Kênh Spotify!")
        else:
            # 1. Cơ chế Upsert (Ghi đè hoặc Thêm mới)
            dieu_kien_trung = (df["Tuần"] == tuan) & (df["Kênh_Spotify"] == kenh)
            if dieu_kien_trung.any():
                df.loc[dieu_kien_trung, ["Tháng", "Doanh_Thu_USD", "Luot_Play", "So_Gio_Nghe", "So_Tap_Upload", "Bat_Kiem_Tien", "Thoi_Gian_Nhap"]] = [
                    thang, float(doanh_thu), int(luot_play), float(gio_nghe), int(so_tap), trang_thai_kt, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ]
                st.toast(f"🔄 Đã ghi đè & cập nhật số liệu mới cho {kenh} ({tuan})!", icon="🔄")
            else:
                du_lieu_moi = pd.DataFrame([{
                    "Tháng": thang, "Tuần": tuan, "Kênh_Spotify": kenh,
                    "Doanh_Thu_USD": float(doanh_thu), "Luot_Play": int(luot_play),
                    "So_Gio_Nghe": float(gio_nghe), "So_Tap_Upload": int(so_tap),
                    "Bat_Kiem_Tien": trang_thai_kt,
                    "Thoi_Gian_Nhap": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }])
                df = pd.concat([df, du_lieu_moi], ignore_index=True)
                st.toast(f"✅ Đã lưu thành công số liệu mới cho {kenh} ({tuan})!", icon="✅")
            
            df.to_csv(FILE_DU_LIEU, index=False)
            
            # 2. Xóa trí nhớ bộ lọc Dashboard để biểu đồ tự vẽ lại
            if "loc_thang" in st.session_state: del st.session_state["loc_thang"]
            if "loc_kenh" in st.session_state: del st.session_state["loc_kenh"]
            
            # 3. KÍCH HOẠT TÁI SINH FORM (Tự động đưa số về 0 mà không bị lỗi đỏ)
            st.session_state.form_reset_key += 1
            st.rerun()

# ==========================================
# KHU VỰC 2: DASHBOARD TỔNG HỢP
# ==========================================
with tab_dashboard:
    if df.empty:
        st.info("Hệ thống chưa có dữ liệu. Vui lòng sang tab 'Cổng Nhập Liệu' để bổ sung thông tin.")
    else:
        col_loc1, col_loc2 = st.columns(2)
        with col_loc1:
            thang_hien_co = list(df["Tháng"].unique())
            thang_chon = st.selectbox("📅 Lọc Dashboard theo Tháng:", ["Tất cả các tháng"] + thang_hien_co, key="loc_thang")
            
        df_thang = df if thang_chon == "Tất cả các tháng" else df[df["Tháng"] == thang_chon]
        danh_sach_kenh_hien_co = list(df_thang["Kênh_Spotify"].unique())
        
        with col_loc2:
            kenh_duoc_chon = st.multiselect("🎧 Tích chọn các kênh muốn theo dõi:", options=danh_sach_kenh_hien_co, default=danh_sach_kenh_hien_co, key="loc_kenh")
            
        st.markdown("---")
        
        if not kenh_duoc_chon:
            st.warning("⚠️ Vui lòng tick chọn ít nhất 1 kênh ở bộ lọc phía trên!")
        else:
            df_final = df_thang[df_thang["Kênh_Spotify"].isin(kenh_duoc_chon)]
            
            # 1. TÌNH TRẠNG KÊNH
            df_kenh_duy_nhat = df_final.sort_values("Thoi_Gian_Nhap").groupby("Kênh_Spotify").tail(1)
            tong_so_kenh = len(df_kenh_duy_nhat)
            kenh_da_bkt = int(df_kenh_duy_nhat["Bat_Kiem_Tien"].sum())
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Tổng Số Kênh Đang Có", f"{tong_so_kenh} Kênh")
            c2.metric("Kênh Đã Bật Kiếm Tiền 💸", f"{kenh_da_bkt} Kênh")
            c3.metric("Kênh Chưa Bật KT ⏳", f"{tong_so_kenh - kenh_da_bkt} Kênh")
            
            # 2. SCORECARDS
            st.markdown("### 🏆 CHỈ SỐ THỰC TẾ vs KPI MỤC TIÊU")
            sc1, sc2, sc3, sc4 = st.columns(4)
            sc1.metric("💰 Doanh Thu", f"${df_final['Doanh_Thu_USD'].sum():,.2f}", delta=f"${df_final['Doanh_Thu_USD'].sum() - kpi_doanh_thu:,.2f}")
            sc2.metric("▶️ Lượt Play", f"{df_final['Luot_Play'].sum():,}", delta=f"{df_final['Luot_Play'].sum() - kpi_play:,}")
            sc3.metric("⏱️ Giờ Nghe", f"{df_final['So_Gio_Nghe'].sum():,.1f}h", delta=f"{df_final['So_Gio_Nghe'].sum() - kpi_gio:,.1f}h")
            sc4.metric("🎙️ Tập Upload", f"{df_final['So_Tap_Upload'].sum():,}", delta=f"{df_final['So_Tap_Upload'].sum() - kpi_tap:,}")
            
            st.markdown("---")
            
            # 3. BIỂU ĐỒ XU HƯỚNG TĂNG TRƯỞNG
            st.markdown("### 📈 Biểu Đồ Xu Hướng Theo Thời Gian")
            tab_dt, tab_play, tab_gio = st.tabs(["💰 Xu Hướng Doanh Thu", "▶️ Xu Hướng Lượt Play", "⏱️ Xu Hướng Giờ Nghe"])
            
            df_trend = df_final.groupby(["Tuần", "Kênh_Spotify"])[["Doanh_Thu_USD", "Luot_Play", "So_Gio_Nghe"]].sum().reset_index()
            
            with tab_dt:
                fig_dt = px.line(df_trend, x="Tuần", y="Doanh_Thu_USD", color="Kênh_Spotify", markers=True)
                st.plotly_chart(fig_dt, use_container_width=True)
            with tab_play:
                fig_play = px.line(df_trend, x="Tuần", y="Luot_Play", color="Kênh_Spotify", markers=True)
                st.plotly_chart(fig_play, use_container_width=True)
            with tab_gio:
                fig_gio = px.line(df_trend, x="Tuần", y="So_Gio_Nghe", color="Kênh_Spotify", markers=True)
                st.plotly_chart(fig_gio, use_container_width=True)

            st.markdown("---")

            # 4. PHÂN TÍCH CHUYÊN SÂU
            st.markdown("### 🥧 Phân Tích Cơ Cấu & Hiệu Suất")
            col_pie, col_rpm = st.columns(2)
            
            with col_pie:
                df_pie = df_final.groupby("Kênh_Spotify")["Doanh_Thu_USD"].sum().reset_index()
                fig_pie = px.pie(df_pie, values="Doanh_Thu_USD", names="Kênh_Spotify", hole=0.4, title="Tỷ Trọng Doanh Thu Theo Kênh")
                st.plotly_chart(fig_pie, use_container_width=True)
                
            with col_rpm:
                df_rpm = df_final.groupby("Kênh_Spotify")[["Doanh_Thu_USD", "Luot_Play"]].sum().reset_index()
                df_rpm["RPM_USD"] = np.where(df_rpm["Luot_Play"] > 0, (df_rpm["Doanh_Thu_USD"] / df_rpm["Luot_Play"]) * 1000, 0)
                fig_rpm = px.bar(df_rpm, x="Kênh_Spotify", y="RPM_USD", title="Chỉ số RPM (Doanh thu trên 1.000 Lượt Play)", text_auto='.2f')
                fig_rpm.update_traces(marker_color='#1DB954')
                st.plotly_chart(fig_rpm, use_container_width=True)
