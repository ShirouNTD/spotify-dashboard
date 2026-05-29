import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# 1. CẤU HÌNH GIAO DIỆN
st.set_page_config(page_title="Spotify Performance Hub", layout="wide", page_icon="🎧")

FILE_DU_LIEU = "spotify_master_data.csv"

# Hàm khởi tạo & nâng cấp file CSV (Chống mất dữ liệu cũ)
def khoi_tao_db():
    if not os.path.exists(FILE_DU_LIEU):
        df_mau = pd.DataFrame(columns=[
            "Tháng", "Tuần", "Kênh_Spotify", "Doanh_Thu_USD", 
            "Luot_Play", "So_Gio_Nghe", "So_Tap_Upload", "Bat_Kiem_Tien", "Thoi_Gian_Nhap"
        ])
        df_mau.to_csv(FILE_DU_LIEU, index=False)
    else:
        # Cập nhật tương thích ngược: Thêm cột Bat_Kiem_Tien nếu file cũ chưa có
        df_hien_tai = pd.read_csv(FILE_DU_LIEU)
        if "Bat_Kiem_Tien" not in df_hien_tai.columns:
            df_hien_tai["Bat_Kiem_Tien"] = False
            df_hien_tai.to_csv(FILE_DU_LIEU, index=False)

khoi_tao_db()

# Đọc dữ liệu tổng để sử dụng chung
df = pd.read_csv(FILE_DU_LIEU)

# ==========================================
# KHU VỰC SIDEBAR: CÀI ĐẶT KPI
# ==========================================
st.sidebar.header("🎯 THIẾT LẬP KPI MỤC TIÊU")
st.sidebar.markdown("*(Thay đổi thông số tại đây để đánh giá hiệu suất)*")
kpi_doanh_thu = st.sidebar.number_input("KPI Doanh Thu ($):", value=5000.0, step=100.0)
kpi_play = st.sidebar.number_input("KPI Lượt Play:", value=500000, step=10000)
kpi_gio = st.sidebar.number_input("KPI Giờ Nghe:", value=20000.0, step=1000.0)
kpi_tap = st.sidebar.number_input("KPI Số Tập Upload:", value=15, step=1)

# ==========================================
# TIÊU ĐỀ CHÍNH
# ==========================================
st.title("🎧 TRUNG TÂM QUẢN TRỊ HIỆU SUẤT SPOTIFY")
st.markdown("---")

tab_dashboard, tab_nhap_lieu = st.tabs(["📊 Báo Cáo Dashboard", "📥 Cổng Nhập Liệu (Tự Động Gợi Ý)"])

# ==========================================
# KHU VỰC 1: CỔNG NHẬP LIỆU (UX MỚI)
# ==========================================
with tab_nhap_lieu:
    st.subheader("Nhập liệu Báo cáo Tuần")
    st.info("💡 Bạn có thể chọn tên kênh cũ để hệ thống tự động điền trạng thái Kiếm tiền, hoặc gõ tên kênh mới.")
    
    col1, col2, col3 = st.columns(3)
    
    # Cột 1: Thông tin kênh (Có Autocomplete & Tự nhớ BKT)
    with col1:
        thang = st.selectbox("Tháng Báo Cáo:", [f"Tháng {i}" for i in range(1, 13)])
        tuan = st.selectbox("Tuần Báo Cáo:", [f"Tuần {i}" for i in range(1, 53)])
        
        # Tạo list kênh đã từng nhập để làm Autocomplete
        danh_sach_kenh_cu = list(df["Kênh_Spotify"].unique()) if not df.empty else []
        lua_chon_kenh = st.selectbox("Gõ để tìm kênh hoặc Thêm kênh mới:", ["➕ Nhập kênh mới..."] + danh_sach_kenh_cu)
        
        # Xử lý logic hiển thị
        if lua_chon_kenh == "➕ Nhập kênh mới...":
            kenh = st.text_input("Gõ tên kênh mới vào đây:").strip()
            trang_thai_mac_dinh = False
        else:
            kenh = lua_chon_kenh
            # Lục tìm trí nhớ: Lấy trạng thái Bật kiếm tiền ở lần nhập gần nhất của kênh này
            trang_thai_mac_dinh = bool(df[df["Kênh_Spotify"] == kenh].iloc[-1]["Bat_Kiem_Tien"])
            
        trang_thai_kt = st.checkbox("✅ Kênh đã bật kiếm tiền", value=trang_thai_mac_dinh)

    # Cột 2 & 3: Các chỉ số thông thường
    with col2:
        doanh_thu = st.number_input("Doanh thu tuần (USD):", min_value=0.0, step=1.0)
        luot_play = st.number_input("Lượt Play tuần qua:", min_value=0, step=100)
    with col3:
        gio_nghe = st.number_input("Số giờ nghe tuần qua:", min_value=0.0, step=10.0)
        so_tap = st.number_input("Số tập Upload tuần qua:", min_value=0, step=1)
        
    st.markdown("<br>", unsafe_allow_html=True)
    btn_luu = st.button("Lưu Dữ Liệu Lên Hệ Thống", type="primary", use_container_width=True)
    
    if btn_luu:
        if not kenh:
            st.error("⚠️ Vui lòng nhập hoặc chọn Tên Kênh Spotify!")
        else:
            du_lieu_moi = pd.DataFrame([{
                "Tháng": thang, "Tuần": tuan, "Kênh_Spotify": kenh,
                "Doanh_Thu_USD": float(doanh_thu), "Luot_Play": int(luot_play),
                "So_Gio_Nghe": float(gio_nghe), "So_Tap_Upload": int(so_tap),
                "Bat_Kiem_Tien": trang_thai_kt, # Lưu lại trạng thái mới
                "Thoi_Gian_Nhap": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }])
            df_cap_nhat = pd.concat([df, du_lieu_moi], ignore_index=True)
            df_cap_nhat.to_csv(FILE_DU_LIEU, index=False)
            st.success(f"✅ Đã ghi nhận dữ liệu cho kênh '{kenh}'! Trạng thái Kiếm tiền đã được lưu.")
            # Nút refresh nhẹ để reload lại list Autocomplete
            st.rerun()

# ==========================================
# KHU VỰC 2: DASHBOARD TỔNG HỢP (KÈM BÁO CÁO KÊNH BKT)
# ==========================================
with tab_dashboard:
    if df.empty:
        st.info("Hệ thống chưa có dữ liệu. Vui lòng sang tab 'Cổng Nhập Liệu' để bổ sung thông tin.")
    else:
        st.markdown("### 🔍 BỘ LỌC DỮ LIỆU ĐỘNG")
        col_loc1, col_loc2 = st.columns(2)
        with col_loc1:
            thang_hien_co = list(df["Tháng"].unique())
            thang_chon = st.selectbox("📅 Lọc Dashboard theo Tháng:", ["Tất cả các tháng"] + thang_hien_co)
            
        df_thang = df if thang_chon == "Tất cả các tháng" else df[df["Tháng"] == thang_chon]
        danh_sach_kenh_hien_co = list(df_thang["Kênh_Spotify"].unique())
        
        with col_loc2:
            kenh_duoc_chon = st.multiselect("🎧 Tích chọn các kênh muốn theo dõi:", options=danh_sach_kenh_hien_co, default=danh_sach_kenh_hien_co)
            
        st.markdown("---")
        
        if not kenh_duoc_chon:
            st.warning("⚠️ Vui lòng tick chọn ít nhất 1 kênh ở bộ lọc phía trên!")
        else:
            df_final = df_thang[df_thang["Kênh_Spotify"].isin(kenh_duoc_chon)]
            
            # --- TỔNG KẾT SỐ LƯỢNG KÊNH & TRẠNG THÁI BKT ---
            st.markdown("### 📺 TÌNH TRẠNG KÊNH SPOTIFY")
            # Thuật toán lọc ra dòng cập nhật mới nhất của từng kênh
            df_kenh_duy_nhat = df_final.sort_values("Thoi_Gian_Nhap").groupby("Kênh_Spotify").tail(1)
            tong_so_kenh = len(df_kenh_duy_nhat)
            kenh_da_bkt = int(df_kenh_duy_nhat["Bat_Kiem_Tien"].sum())
            kenh_chua_bkt = tong_so_kenh - kenh_da_bkt
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Tổng Số Kênh Đang Có", f"{tong_so_kenh} Kênh")
            c2.metric("Kênh Đã Bật Kiếm Tiền 💸", f"{kenh_da_bkt} Kênh")
            c3.metric("Kênh Chưa Bật KT ⏳", f"{kenh_chua_bkt} Kênh")
            
            st.markdown("---")
            
            # --- SCORECARDS HIỆU SUẤT VS KPI ---
            st.markdown("### 🏆 CHỈ SỐ THỰC TẾ vs KPI MỤC TIÊU")
            tong_dt = df_final["Doanh_Thu_USD"].sum()
            tong_play = df_final["Luot_Play"].sum()
            tong_gio = df_final["So_Gio_Nghe"].sum()
            tong_tap = df_final["So_Tap_Upload"].sum()
            
            sc1, sc2, sc3, sc4 = st.columns(4)
            sc1.metric("💰 Doanh Thu", f"${tong_dt:,.2f}", delta=f"${tong_dt - kpi_doanh_thu:,.2f} so với KPI")
            sc2.metric("▶️ Lượt Play", f"{tong_play:,}", delta=f"{tong_play - kpi_play:,} so với KPI")
            sc3.metric("⏱️ Giờ Nghe", f"{tong_gio:,.1f}h", delta=f"{tong_gio - kpi_gio:,.1f}h so với KPI")
            sc4.metric("🎙️ Tập Upload", f"{tong_tap:,}", delta=f"{tong_tap - kpi_tap:,} so với KPI")
            
            st.markdown("---")
            
            # --- BẢNG PHONG THẦN & BIỂU ĐỒ ---
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                st.markdown("### 🎯 Bảng Phong Thần Doanh Thu")
                df_ranking = df_final.groupby("Kênh_Spotify")["Doanh_Thu_USD"].sum().reset_index().sort_values(by="Doanh_Thu_USD", ascending=False)
                if len(df_ranking) > 0:
                    st.success(f"**🔥 KÊNH DẪN ĐẦU:** {df_ranking.iloc[0]['Kênh_Spotify']} (${df_ranking.iloc[0]['Doanh_Thu_USD']:,.2f})")
                    st.error(f"**❄️ KÊNH ĐANG YẾU:** {df_ranking.iloc[-1]['Kênh_Spotify']} (${df_ranking.iloc[-1]['Doanh_Thu_USD']:,.2f})")
                    
            with col_b2:
                st.markdown("### 📈 Biểu Đồ Tăng Trưởng Doanh Thu")
                df_trend = df_final.groupby(["Tuần", "Kênh_Spotify"])["Doanh_Thu_USD"].sum().reset_index()
                fig_dt = px.line(df_trend, x="Tuần", y="Doanh_Thu_USD", color="Kênh_Spotify", markers=True)
                st.plotly_chart(fig_dt, use_container_width=True)
