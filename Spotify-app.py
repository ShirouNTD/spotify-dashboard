import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime
import numpy as np

# 1. CẤU HÌNH GIAO DIỆN
st.set_page_config(page_title="Spotify Performance Hub", layout="wide", page_icon="🎧")

FILE_DU_LIEU = "spotify_master_data.csv"
FILE_KPI = "spotify_channel_kpi.csv" # Đổi thành KPI cấp độ Kênh

# Hàm khởi tạo & nâng cấp file CSV
def khoi_tao_he_thong_db():
    # DB Kết quả
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
            
    # DB Mục tiêu Kênh
    if not os.path.exists(FILE_KPI):
        df_kpi_mau = pd.DataFrame(columns=["Tháng", "Kênh_Spotify", "KPI_Doanh_Thu", "KPI_Luot_Play", "KPI_So_Gio", "KPI_So_Tap", "So_Tuan"])
        df_kpi_mau.to_csv(FILE_KPI, index=False)

khoi_tao_he_thong_db()
df = pd.read_csv(FILE_DU_LIEU)
df_kpi = pd.read_csv(FILE_KPI)

# THUẬT TOÁN CHÌA KHÓA TÁI SINH FORM
if "rk_kq" not in st.session_state: st.session_state.rk_kq = 0
if "rk_kpi" not in st.session_state: st.session_state.rk_kpi = 0

st.title("🎧 TRUNG TÂM QUẢN TRỊ HIỆU SUẤT SPOTIFY")
st.markdown("---")

# TẠO 4 TAB CHỨC NĂNG RIÊNG BIỆT
tab_dashboard, tab_nhap_kq, tab_nhap_kpi, tab_xoa_data = st.tabs([
    "📊 Báo Cáo Dashboard", "📥 Nhập Kết Quả Kênh", "🎯 Nhập Mục Tiêu Kênh", "🗑️ Quản Lý Dữ Liệu"
])

# ==========================================
# TAB 2: NHẬP KẾT QUẢ KÊNH (THỰC TẾ)
# ==========================================
with tab_nhap_kq:
    st.subheader("Cập Nhật Kết Quả Vận Hành Tuần")
    rk = st.session_state.rk_kq
    
    col1, col2, col3 = st.columns(3)
    with col1:
        thang_kq = st.selectbox("Tháng Báo Cáo:", [f"Tháng {i}" for i in range(1, 13)], key=f"t_kq_{rk}")
        tuan_kq = st.selectbox("Tuần Báo Cáo:", [f"Tuần {i}" for i in range(1, 53)], key=f"w_kq_{rk}")
        
        danh_sach_kenh_cu = list(df["Kênh_Spotify"].unique()) if not df.empty else []
        lua_chon_kenh = st.selectbox("Chọn Kênh / Thêm Kênh:", ["➕ Nhập kênh mới..."] + danh_sach_kenh_cu, key=f"c_kq_{rk}")
        
        if lua_chon_kenh == "➕ Nhập kênh mới...":
            kenh_kq = st.text_input("Gõ tên kênh mới:", key=f"new_c_kq_{rk}").strip()
            trang_thai_mac_dinh = False
        else:
            kenh_kq = lua_chon_kenh
            trang_thai_mac_dinh = bool(df[df["Kênh_Spotify"] == kenh_kq].iloc[-1]["Bat_Kiem_Tien"])
            
        bkt_kq = st.checkbox("✅ Kênh đã bật kiếm tiền", value=trang_thai_mac_dinh, key=f"bkt_{lua_chon_kenh}_{rk}")

    with col2:
        dt_kq = st.number_input("Thực tế Doanh thu (USD):", min_value=0.0, step=1.0, key=f"dt_kq_{rk}")
        play_kq = st.number_input("Thực tế Lượt Play:", min_value=0, step=100, key=f"p_kq_{rk}")
    with col3:
        gio_kq = st.number_input("Thực tế Giờ nghe (h):", min_value=0.0, step=10.0, key=f"g_kq_{rk}")
        tap_kq = st.number_input("Thực tế Số tập Upload:", min_value=0, step=1, key=f"tap_kq_{rk}")
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Lưu Kết Quả Thực Tế", type="primary", use_container_width=True):
        if not kenh_kq:
            st.error("⚠️ Vui lòng nhập Tên Kênh!")
        else:
            dieu_kien_trung = (df["Tuần"] == tuan_kq) & (df["Kênh_Spotify"] == kenh_kq)
            if dieu_kien_trung.any():
                st.error(f"⛔ Dữ liệu '{kenh_kq}' ở '{tuan_kq}' đã có! Qua tab 'Quản Lý Dữ Liệu' xóa trước khi nhập lại.")
            else:
                du_lieu_moi = pd.DataFrame([{
                    "Tháng": thang_kq, "Tuần": tuan_kq, "Kênh_Spotify": kenh_kq,
                    "Doanh_Thu_USD": float(dt_kq), "Luot_Play": int(play_kq),
                    "So_Gio_Nghe": float(gio_kq), "So_Tap_Upload": int(tap_kq),
                    "Bat_Kiem_Tien": bkt_kq, "Thoi_Gian_Nhap": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }])
                df_ghi = pd.concat([df, du_lieu_moi], ignore_index=True)
                df_ghi.to_csv(FILE_DU_LIEU, index=False)
                st.toast(f"✅ Đã lưu kết quả cho {kenh_kq} ({tuan_kq})!", icon="✅")
                
                # Ép xóa cache Dashboard
                for k in ["loc_thang", "loc_kenh", "loc_tuan_phan_tich"]:
                    if k in st.session_state: del st.session_state[k]
                st.session_state.rk_kq += 1
                st.rerun()

# ==========================================
# TAB 3: NHẬP MỤC TIÊU KÊNH (KPI MỚI)
# ==========================================
with tab_nhap_kpi:
    st.subheader("Thiết Lập Mục Tiêu (KPI) Cho Từng Kênh")
    st.info("💡 Hệ thống sẽ tự động chia Mục tiêu Tháng cho Số lượng Tuần để vẽ biểu đồ so sánh.")
    
    rk_kpi = st.session_state.rk_kpi
    
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    with col_kpi1:
        thang_kpi = st.selectbox("Chọn Tháng thiết lập:", [f"Tháng {i}" for i in range(1, 13)], key=f"t_kpi_{rk_kpi}")
        danh_sach_kenh_kpi = list(df["Kênh_Spotify"].unique())
        if not danh_sach_kenh_kpi:
            st.warning("Hãy nhập ít nhất 1 kênh ở phần Kết quả trước.")
            kenh_kpi = ""
        else:
            kenh_kpi = st.selectbox("Chọn Kênh áp dụng KPI:", danh_sach_kenh_kpi, key=f"c_kpi_{rk_kpi}")
            
        so_tuan_kpi = st.number_input("Số tuần của tháng này:", min_value=1, max_value=5, value=4, key=f"w_kpi_{rk_kpi}")
        
    with col_kpi2:
        dt_kpi = st.number_input("Mục tiêu Doanh thu Tháng ($):", min_value=0.0, step=100.0, key=f"dt_kpi_{rk_kpi}")
        play_kpi = st.number_input("Mục tiêu Lượt Play Tháng:", min_value=0, step=10000, key=f"p_kpi_{rk_kpi}")
    with col_kpi3:
        gio_kpi = st.number_input("Mục tiêu Giờ nghe Tháng (h):", min_value=0.0, step=100.0, key=f"g_kpi_{rk_kpi}")
        tap_kpi = st.number_input("Mục tiêu Số tập Upload Tháng:", min_value=0, step=1, key=f"tap_kpi_{rk_kpi}")
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Lưu Mục Tiêu (Ghi Đè Nêu Trùng)", type="primary", use_container_width=True):
        if kenh_kpi:
            # Xóa KPI cũ của kênh đó trong tháng đó nếu có
            dieu_kien_kpi = (df_kpi["Tháng"] == thang_kpi) & (df_kpi["Kênh_Spotify"] == kenh_kpi)
            df_kpi_filtered = df_kpi[~dieu_kien_kpi]
            
            kpi_moi = pd.DataFrame([{
                "Tháng": thang_kpi, "Kênh_Spotify": kenh_kpi,
                "KPI_Doanh_Thu": float(dt_kpi), "KPI_Luot_Play": int(play_kpi),
                "KPI_So_Gio": float(gio_kpi), "KPI_So_Tap": int(tap_kpi), "So_Tuan": int(so_tuan_kpi)
            }])
            
            df_kpi_ghi = pd.concat([df_kpi_filtered, kpi_moi], ignore_index=True)
            df_kpi_ghi.to_csv(FILE_KPI, index=False)
            st.toast(f"🎯 Đã lưu KPI cho kênh {kenh_kpi} vào {thang_kpi}!", icon="🎯")
            
            for k in ["loc_thang", "loc_kenh", "loc_tuan_phan_tich"]:
                if k in st.session_state: del st.session_state[k]
            st.session_state.rk_kpi += 1
            st.rerun()

# ==========================================
# TAB 4: XÓA DỮ LIỆU
# ==========================================
with tab_xoa_data:
    st.subheader("Dọn Dẹp Dữ Liệu Sai")
    if df.empty:
        st.info("Kho dữ liệu trống.")
    else:
        col_x1, col_x2 = st.columns(2)
        with col_x1:
            kenh_can_xoa = st.selectbox("1. Chọn Kênh cần xóa:", df["Kênh_Spotify"].unique(), key="del_k")
        with col_x2:
            cac_tuan_da_co = df[df["Kênh_Spotify"] == kenh_can_xoa]["Tuần"].unique()
            tuan_can_xoa = st.selectbox("2. Chọn Tuần bị sai:", cac_tuan_da_co, key="del_w")
            
        if st.button("🗑️ Xác Nhận Xóa", type="primary"):
            df_con_lai = df[~((df["Kênh_Spotify"] == kenh_can_xoa) & (df["Tuần"] == tuan_can_xoa))]
            df_con_lai.to_csv(FILE_DU_LIEU, index=False)
            for k in ["loc_thang", "loc_kenh", "loc_tuan_phan_tich"]:
                if k in st.session_state: del st.session_state[k]
            st.toast("✅ Đã xóa thành công!")
            st.rerun()

# ==========================================
# TAB 1: DASHBOARD TỔNG HỢP & SO SÁNH KPI
# ==========================================
with tab_dashboard:
    if df.empty:
        st.info("Hệ thống chưa có dữ liệu. Vui lòng sang tab 'Nhập Kết Quả Kênh'.")
    else:
        col_loc1, col_loc2 = st.columns(2)
        with col_loc1:
            thang_hien_co = list(df["Tháng"].unique())
            thang_chon = st.selectbox("📅 Lọc Dashboard theo Tháng:", ["Tất cả các tháng"] + thang_hien_co, key="loc_thang")
            
        df_thang = df if thang_chon == "Tất cả các tháng" else df[df["Tháng"] == thang_chon]
        danh_sach_kenh_hien_co = list(df_thang["Kênh_Spotify"].unique())
        
        with col_loc2:
            kenh_duoc_chon = st.multiselect("🎧 Lọc theo Kênh:", options=danh_sach_kenh_hien_co, default=danh_sach_kenh_hien_co, key="loc_kenh")
            
        st.markdown("---")
        
        if not kenh_duoc_chon:
            st.warning("⚠️ Vui lòng tick chọn ít nhất 1 kênh!")
        else:
            df_final = df_thang[df_thang["Kênh_Spotify"].isin(kenh_duoc_chon)]
            
            # --- TÍNH TỔNG KPI ĐỘNG ---
            df_kpi_read = pd.read_csv(FILE_KPI)
            target_dt = target_play = target_gio = target_tap = 0
            
            # Lọc KPI dựa trên các Kênh đang được chọn trên Dashboard
            df_kpi_filter = df_kpi_read[df_kpi_read["Kênh_Spotify"].isin(kenh_duoc_chon)]
            
            if thang_chon != "Tất cả các tháng":
                df_kpi_filter = df_kpi_filter[df_kpi_filter["Tháng"] == thang_chon]
                
            target_dt = df_kpi_filter["KPI_Doanh_Thu"].sum()
            target_play = df_kpi_filter["KPI_Luot_Play"].sum()
            target_gio = df_kpi_filter["KPI_So_Gio"].sum()
            target_tap = df_kpi_filter["KPI_So_Tap"].sum()

            # --- SCORECARDS ---
            st.markdown("### 🏆 CHỈ SỐ THỰC TẾ vs MỤC TIÊU")
            sc1, sc2, sc3, sc4 = st.columns(4)
            sc1.metric("💰 Doanh Thu", f"${df_final['Doanh_Thu_USD'].sum():,.2f}", delta=f"${df_final['Doanh_Thu_USD'].sum() - target_dt:,.2f} so với KPI")
            sc2.metric("▶️ Lượt Play", f"{df_final['Luot_Play'].sum():,}", delta=f"{df_final['Luot_Play'].sum() - target_play:,} so với KPI")
            sc3.metric("⏱️ Giờ Nghe", f"{df_final['So_Gio_Nghe'].sum():,.1f}h", delta=f"{df_final['So_Gio_Nghe'].sum() - target_gio:,.1f}h so với KPI")
            sc4.metric("🎙️ Tập Upload", f"{df_final['So_Tap_Upload'].sum():,}", delta=f"{df_final['So_Tap_Upload'].sum() - target_tap:,} so với KPI")
            
            st.markdown("---")
            
            # --- BIỂU ĐỒ KÉP: THỰC TẾ VS MỤC TIÊU ---
            st.markdown("### 🚀 Tiến Độ Chạy Đua KPI (Thực Tế vs Mục Tiêu Tuần)")
            
            # Tiền xử lý dữ liệu để vẽ biểu đồ kép
            df_chart_actual = df_final.groupby(["Tháng", "Tuần", "Kênh_Spotify"])["Doanh_Thu_USD"].sum().reset_index()
            # Ghép nối với DB KPI để lấy Số Tuần
            df_chart_merged = pd.merge(df_chart_actual, df_kpi_read, on=["Tháng", "Kênh_Spotify"], how="left")
            # Nếu chưa có KPI thì mặc định mục tiêu tuần = 0
            df_chart_merged["So_Tuan"] = df_chart_merged["So_Tuan"].fillna(4) 
            df_chart_merged["Mục_Tiêu_Tuần_USD"] = (df_chart_merged["KPI_Doanh_Thu"].fillna(0) / df_chart_merged["So_Tuan"])
            
            # Gom nhóm lại theo Tuần (để lỡ Boss chọn xem nhiều kênh 1 lúc)
            df_chart_final = df_chart_merged.groupby("Tuần")[["Doanh_Thu_USD", "Mục_Tiêu_Tuần_USD"]].sum().reset_index()
            df_chart_final["Tuan_Num"] = df_chart_final["Tuần"].apply(lambda x: int(x.replace("Tuần ", "")) if "Tuần " in x else 0)
            df_chart_final = df_chart_final.sort_values("Tuan_Num")
            
            # Vẽ biểu đồ kép bằng Graph Objects
            fig_vs = go.Figure()
            fig_vs.add_trace(go.Scatter(x=df_chart_final["Tuần"], y=df_chart_final["Doanh_Thu_USD"], mode='lines+markers', name='Thực Tế Đạt Được', line=dict(color='#1DB954', width=3)))
            fig_vs.add_trace(go.Scatter(x=df_chart_final["Tuần"], y=df_chart_final["Mục_Tiêu_Tuần_USD"], mode='lines+markers', name='Mục Tiêu Đề Ra', line=dict(color='#FF5722', width=3, dash='dash')))
            fig_vs.update_layout(title="So Sánh Doanh Thu Thực Tế và KPI Hàng Tuần", hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            
            st.plotly_chart(fig_vs, use_container_width=True)

            st.markdown("---")

            # --- BIỂU ĐỒ PHÂN TÍCH ---
            st.markdown("### 🥧 Phân Tích Cơ Cấu & Hiệu Suất Cục Bộ")
            tuan_hien_co = list(df_final["Tuần"].unique())
            tuan_hien_co.sort(key=lambda x: int(x.replace("Tuần ", "")) if "Tuần " in x else 0)
            
            tuan_chon = st.selectbox("📌 Tách lớp dữ liệu Phân tích theo:", ["Tất cả các tuần"] + tuan_hien_co, key="loc_tuan_phan_tich")
            df_phan_tich = df_final if tuan_chon == "Tất cả các tuần" else df_final[df_final["Tuần"] == tuan_chon]
            
            if df_phan_tich.empty:
                st.info(f"Không có dữ liệu cho {tuan_chon}.")
            else:
                col_pie, col_rpm = st.columns(2)
                with col_pie:
                    df_pie = df_phan_tich.groupby("Kênh_Spotify")["Doanh_Thu_USD"].sum().reset_index()
                    fig_pie = px.pie(df_pie, values="Doanh_Thu_USD", names="Kênh_Spotify", hole=0.4, title=f"Tỷ Trọng Doanh Thu ({tuan_chon})")
                    st.plotly_chart(fig_pie, use_container_width=True)
                    
                with col_rpm:
                    df_rpm = df_phan_tich.groupby("Kênh_Spotify")[["Doanh_Thu_USD", "Luot_Play"]].sum().reset_index()
                    df_rpm["RPM_USD"] = np.where(df_rpm["Luot_Play"] > 0, (df_rpm["Doanh_Thu_USD"] / df_rpm["Luot_Play"]) * 1000, 0)
                    fig_rpm = px.bar(df_rpm, x="Kênh_Spotify", y="RPM_USD", title=f"Chỉ số RPM ({tuan_chon})", text_auto='.2f')
                    fig_rpm.update_traces(marker_color='#1DB954')
                    st.plotly_chart(fig_rpm, use_container_width=True)
