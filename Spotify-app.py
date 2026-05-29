import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
import numpy as np

# 1. CẤU HÌNH GIAO DIỆN
st.set_page_config(page_title="Spotify Performance Hub", layout="wide", page_icon="🎧")

FILE_DU_LIEU = "spotify_master_data.csv"
FILE_KPI = "spotify_kpi_data.csv"

# Hàm khởi tạo cơ sở dữ liệu chính và cơ sở dữ liệu KPI
def khoi_tao_he_thong_db():
    # Khởi tạo DB Master Data
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
            
    # Khởi tạo DB KPI theo Tháng
    if not os.path.exists(FILE_KPI):
        df_kpi_mau = pd.DataFrame(columns=["Tháng", "KPI_Doanh_Thu", "KPI_Luot_Play", "KPI_So_Gio", "KPI_So_Tap"])
        df_kpi_mau.to_csv(FILE_KPI, index=False)

khoi_tao_he_thong_db()
df = pd.read_csv(FILE_DU_LIEU)
df_kpi_all = pd.read_csv(FILE_KPI)

# THUẬT TOÁN RESET FORM VỀ 0
if "form_reset_key" not in st.session_state: 
    st.session_state.form_reset_key = 0

# ==========================================
# KHU VỰC SIDEBAR: QUẢN LÝ KPI VĨNH CỬU THEO THÁNG
# ==========================================
st.sidebar.header("🎯 CẤU HÌNH KPI THEO THÁNG")
thang_kpi = st.sidebar.selectbox("Cài đặt mục tiêu cho:", [f"Tháng {i}" for i in range(1, 13)])

# Đọc xem tháng được chọn đã có dữ liệu KPI trong file chưa
row_kpi = df_kpi_all[df_kpi_all["Tháng"] == thang_kpi]
if not row_kpi.empty:
    default_dt = float(row_kpi.iloc[0]["KPI_Doanh_Thu"])
    default_play = int(row_kpi.iloc[0]["KPI_Luot_Play"])
    default_gio = float(row_kpi.iloc[0]["KPI_So_Gio"])
    default_tap = int(row_kpi.iloc[0]["KPI_So_Tap"])
else:
    # Nếu tháng mới tinh chưa cài bao giờ, lấy số mặc định ban đầu
    default_dt, default_play, default_gio, default_tap = 5000.0, 500000, 20000.0, 15

# Dùng key động theo tháng để tự động cập nhật số liệu trên form khi đổi tháng
val_kpi_dt = st.sidebar.number_input("KPI Doanh Thu ($):", value=default_dt, step=100.0, key=f"kpi_dt_{thang_kpi}")
val_kpi_play = st.sidebar.number_input("KPI Lượt Play:", value=default_play, step=10000, key=f"kpi_play_{thang_kpi}")
val_kpi_gio = st.sidebar.number_input("KPI Giờ Nghe (h):", value=default_gio, step=1000.0, key=f"kpi_gio_{thang_kpi}")
val_kpi_tap = st.sidebar.number_input("KPI Số Tập Upload:", value=default_tap, step=1, key=f"kpi_tap_{thang_kpi}")

if st.sidebar.button("💾 Lưu Cấu Hình KPI", type="secondary", use_container_width=True):
    # Sử dụng cơ chế Drop & Append để lưu đè KPI tháng cũ
    df_kpi_filtered = df_kpi_all[df_kpi_all["Tháng"] != thang_kpi]
    new_kpi_row = pd.DataFrame([{
        "Tháng": thang_kpi,
        "KPI_Doanh_Thu": val_kpi_dt,
        "KPI_Luot_Play": val_kpi_play,
        "KPI_So_Gio": val_kpi_gio,
        "KPI_So_Tap": val_kpi_tap
    }])
    df_kpi_save = pd.concat([df_kpi_filtered, new_kpi_row], ignore_index=True)
    df_kpi_save.to_csv(FILE_KPI, index=False)
    st.toast(f"💾 Đã lưu cấu hình KPI vĩnh viễn cho {thang_kpi}!", icon="💾")
    st.rerun()

st.sidebar.markdown("---")

# ==========================================
# TIÊU ĐỀ CHÍNH
# ==========================================
st.title("🎧 TRUNG TÂM QUẢN TRỊ HIỆU SUẤT SPOTIFY")
st.markdown("---")

tab_dashboard, tab_nhap_lieu, tab_xoa_data = st.tabs(["📊 Báo Cáo Dashboard", "📥 Cổng Nhập Liệu", "🗑️ Xóa Dữ Liệu"])

# ==========================================
# TAB 1: CỔNG NHẬP LIỆU
# ==========================================
with tab_nhap_lieu:
    st.subheader("Nhập liệu Báo cáo Tuần")
    st.info("💡 Nếu nhập sai số liệu cũ, vui lòng sang tab 'Xóa Dữ Liệu' để dọn dẹp bản ghi cũ trước khi nhập số mới.")
    
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
            dieu_kien_trung = (df["Tuần"] == tuan) & (df["Kênh_Spotify"] == kenh)
            if dieu_kien_trung.any():
                st.error(f"⛔ Dữ liệu của '{kenh}' trong '{tuan}' đã tồn tại! Vui lòng sang tab '🗑️ Xóa Dữ Liệu' để gỡ bỏ bản ghi bị sai trước khi nhập lại.")
            else:
                du_lieu_moi = pd.DataFrame([{
                    "Tháng": thang, "Tuần": tuan, "Kênh_Spotify": kenh,
                    "Doanh_Thu_USD": float(doanh_thu), "Luot_Play": int(luot_play),
                    "So_Gio_Nghe": float(gio_nghe), "So_Tap_Upload": int(so_tap),
                    "Bat_Kiem_Tien": trang_thai_kt,
                    "Thoi_Gian_Nhap": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }])
                
                df_ghi_so = pd.concat([df, du_lieu_moi], ignore_index=True)
                df_ghi_so.to_csv(FILE_DU_LIEU, index=False)
                st.toast(f"✅ Đã lưu thành công số liệu mới cho {kenh} ({tuan})!", icon="✅")
                
                if "loc_thang" in st.session_state: del st.session_state["loc_thang"]
                if "loc_kenh" in st.session_state: del st.session_state["loc_kenh"]
                if "loc_tuan_phan_tich" in st.session_state: del st.session_state["loc_tuan_phan_tich"]
                
                st.session_state.form_reset_key += 1
                st.rerun()

# ==========================================
# TAB 2: XÓA DỮ LIỆU
# ==========================================
with tab_xoa_data:
    st.subheader("Trình Quản Lý & Xóa Dữ Liệu Cũ")
    df_xoa = pd.read_csv(FILE_DU_LIEU)
    
    if df_xoa.empty:
        st.info("Kho dữ liệu hiện đang trống.")
    else:
        col_x1, col_x2 = st.columns(2)
        with col_x1:
            kenh_can_xoa = st.selectbox("1. Chọn Kênh cần sửa dữ liệu:", df_xoa["Kênh_Spotify"].unique(), key="del_kenh")
        with col_x2:
            cac_tuan_da_co = df_xoa[df_xoa["Kênh_Spotify"] == kenh_can_xoa]["Tuần"].unique()
            tuan_can_xoa = st.selectbox("2. Chọn Tuần bị sai cần xóa:", cac_tuan_da_co, key="del_tuan")
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Xác Nhận Xóa Bản Ghi Này", type="primary", use_container_width=True):
            df_con_lai = df_xoa[~((df_xoa["Kênh_Spotify"] == kenh_can_xoa) & (df_xoa["Tuần"] == tuan_can_xoa))]
            df_con_lai.to_csv(FILE_DU_LIEU, index=False)
            
            if "loc_thang" in st.session_state: del st.session_state["loc_thang"]
            if "loc_kenh" in st.session_state: del st.session_state["loc_kenh"]
            if "loc_tuan_phan_tich" in st.session_state: del st.session_state["loc_tuan_phan_tich"]
            
            st.toast(f"✅ Đã xóa vĩnh viễn dữ liệu của {kenh_can_xoa} ({tuan_can_xoa})!", icon="✅")
            st.rerun()

# ==========================================
# TAB 3: DASHBOARD TỔNG HỢP (TỰ ĐỘNG TÍNH TOÁN KPI THEO THÁNG)
# ==========================================
with tab_dashboard:
    if df.empty:
        st.info("Hệ thống chưa có dữ liệu. Vui lòng sang tab 'Cổng Nhập Liệu' để bổ sung thông tin.")
    else:
        # BỘ LỌC TỔNG
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
            
            # --- THUẬT TOÁN TÍNH TOÁN KPI ĐỘNG THEO THÁNG ---
            df_kpi_read = pd.read_csv(FILE_KPI)
            
            if thang_chon != "Tất cả các tháng":
                # Lấy đích danh KPI của tháng được chọn
                target_kpi = df_kpi_read[df_kpi_read["Tháng"] == thang_chon]
                if not target_kpi.empty:
                    target_dt = float(target_kpi.iloc[0]["KPI_Doanh_Thu"])
                    target_play = int(target_kpi.iloc[0]["KPI_Luot_Play"])
                    target_gio = float(target_kpi.iloc[0]["KPI_So_Gio"])
                    target_tap = int(target_kpi.iloc[0]["KPI_So_Tap"])
                else:
                    # Nếu tháng này chưa được cài KPI, lấy tạm số đang hiển thị trên Sidebar hiện tại
                    target_dt, target_play, target_gio, target_tap = val_kpi_dt, val_kpi_play, val_kpi_gio, val_kpi_tap
            else:
                # Nếu xem "Tất cả các tháng", cộng dồn KPI của tất cả các tháng xuất hiện trong data thực tế
                thang_trong_data = df_final["Tháng"].unique()
                target_dt, target_play, target_gio, target_tap = 0.0, 0, 0.0, 0
                for m in thang_trong_data:
                    target_kpi = df_kpi_read[df_kpi_read["Tháng"] == m]
                    if not target_kpi.empty:
                        target_dt += float(target_kpi.iloc[0]["KPI_Doanh_Thu"])
                        target_play += int(target_kpi.iloc[0]["KPI_Luot_Play"])
                        target_gio += float(target_kpi.iloc[0]["KPI_So_Gio"])
                        target_tap += int(target_kpi.iloc[0]["KPI_So_Tap"])
                    else:
                        target_dt, target_play, target_gio, target_tap = target_dt + val_kpi_dt, target_play + val_kpi_play, target_gio + val_kpi_gio, target_tap + val_kpi_tap

            # 2. SCORECARDS
            st.markdown("### 🏆 CHỈ SỐ THỰC TẾ vs KPI MỤC TIÊU")
            sc1, sc2, sc3, sc4 = st.columns(4)
            sc1.metric("💰 Doanh Thu", f"${df_final['Doanh_Thu_USD'].sum():,.2f}", delta=f"${df_final['Doanh_Thu_USD'].sum() - target_dt:,.2f}")
            sc2.metric("▶️ Lượt Play", f"{df_final['Luot_Play'].sum():,}", delta=f"{df_final['Luot_Play'].sum() - target_play:,}")
            sc3.metric("⏱️ Giờ Nghe", f"{df_final['So_Gio_Nghe'].sum():,.1f}h", delta=f"{df_final['So_Gio_Nghe'].sum() - target_gio:,.1f}h")
            sc4.metric("🎙️ Tập Upload", f"{df_final['So_Tap_Upload'].sum():,}", delta=f"{df_final['So_Tap_Upload'].sum() - target_tap:,}")
            
            st.markdown("---")
            
            # 3. BIỂU ĐỒ XU HƯỚNG TĂNG TRƯỞNG
            st.markdown("### 📈 Biêu Đồ Xu Hướng Theo Thời Gian")
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

            # 4. PHÂN TÍCH CHUYÊN SÂU THEO TUẦN CỤC BỘ
            st.markdown("### 🥧 Phân Tích Cơ Cấu & Hiệu Suất Cục Bộ")
            tuan_hien_co = list(df_final["Tuần"].unique())
            tuan_hien_co.sort(key=lambda x: int(x.replace("Tuần ", "")) if "Tuần " in x else 0)
            
            tuan_chon = st.selectbox("📌 Tách lớp dữ liệu Phân tích theo:", ["Tất cả các tuần"] + tuan_hien_co, key="loc_tuan_phan_tich")
            df_phan_tich = df_final if tuan_chon == "Tất cả các tuần" else df_final[df_final["Tuần"] == tuan_chon]
            
            if df_phan_tich.empty:
                st.info(f"Không có dữ liệu phân tích cho {tuan_chon}.")
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
