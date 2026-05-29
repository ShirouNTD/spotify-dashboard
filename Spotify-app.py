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
FILE_KPI = "spotify_channel_kpi.csv" 

# Hàm khởi tạo & nâng cấp file CSV tự động
def khoi_tao_he_thong_db():
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
            
    if not os.path.exists(FILE_KPI):
        df_kpi_mau = pd.DataFrame(columns=["Tháng", "Kênh_Spotify", "KPI_Doanh_Thu", "KPI_Luot_Play", "KPI_So_Gio", "KPI_So_Tap", "So_Tuan", "Bat_Kiem_Tien"])
        df_kpi_mau.to_csv(FILE_KPI, index=False)
    else:
        df_kpi_hien_tai = pd.read_csv(FILE_KPI)
        if "Bat_Kiem_Tien" not in df_kpi_hien_tai.columns:
            df_kpi_hien_tai["Bat_Kiem_Tien"] = False
            df_kpi_hien_tai.to_csv(FILE_KPI, index=False)

khoi_tao_he_thong_db()
df = pd.read_csv(FILE_DU_LIEU)
df_kpi = pd.read_csv(FILE_KPI)

# TẠO DANH SÁCH KÊNH MASTER 
danh_sach_kenh_master = list(set(df["Kênh_Spotify"].dropna().unique()) | set(df_kpi["Kênh_Spotify"].dropna().unique()))
danh_sach_kenh_master.sort()

def lay_trang_thai_kiem_tien(ten_kenh):
    kpi_match = df_kpi[df_kpi["Kênh_Spotify"] == ten_kenh]
    if not kpi_match.empty:
        return bool(kpi_match.iloc[-1]["Bat_Kiem_Tien"])
    df_match = df[df["Kênh_Spotify"] == ten_kenh]
    if not df_match.empty:
        return bool(df_match.iloc[-1]["Bat_Kiem_Tien"])
    return False

if "rk_kq" not in st.session_state: st.session_state.rk_kq = 0
if "rk_kpi" not in st.session_state: st.session_state.rk_kpi = 0

st.title("🎧 TRUNG TÂM QUẢN TRỊ HIỆU SUẤT SPOTIFY")
st.markdown("---")

tab_dashboard, tab_nhap_kpi, tab_nhap_kq, tab_xoa_data = st.tabs([
    "📊 Báo Cáo Dashboard", "🎯 Nhập Mục Tiêu Kênh", "📥 Nhập Kết Quả Kênh", "🗑️ Quản Lý Dữ Liệu"
])

# ==========================================
# TAB 2: NHẬP MỤC TIÊU KÊNH 
# ==========================================
with tab_nhap_kpi:
    st.subheader("Thiết Lập Kênh & Mục Tiêu (KPI) Tháng")
    st.info("💡 Bạn có thể tạo Kênh mới tại đây. Hệ thống sẽ chia KPI Tháng ra các Tuần để vẽ biểu đồ.")
    
    rk_kpi = st.session_state.rk_kpi
    
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    with col_kpi1:
        thang_kpi = st.selectbox("Chọn Tháng thiết lập:", [f"Tháng {i}" for i in range(1, 13)], key=f"t_kpi_{rk_kpi}")
        lua_chon_kenh_kpi = st.selectbox("Chọn Kênh / Thêm Kênh mới:", ["➕ Nhập kênh mới..."] + danh_sach_kenh_master, key=f"c_kpi_{rk_kpi}")
        
        if lua_chon_kenh_kpi == "➕ Nhập kênh mới...":
            kenh_kpi = st.text_input("Gõ tên kênh mới:", key=f"new_c_kpi_{rk_kpi}").strip()
            trang_thai_mac_dinh = False
        else:
            kenh_kpi = lua_chon_kenh_kpi
            trang_thai_mac_dinh = lay_trang_thai_kiem_tien(kenh_kpi)
            
        bkt_kpi = st.checkbox("✅ Kênh đã bật kiếm tiền", value=trang_thai_mac_dinh, key=f"bkt_{lua_chon_kenh_kpi}_{rk_kpi}")
        so_tuan_kpi = st.number_input("Số tuần của tháng này:", min_value=1, max_value=5, value=4, key=f"w_kpi_{rk_kpi}")
        
    with col_kpi2:
        dt_kpi = st.number_input("Mục tiêu Doanh thu Tháng ($):", min_value=0.0, step=100.0, key=f"dt_kpi_{rk_kpi}")
        play_kpi = st.number_input("Mục tiêu Lượt Play Tháng:", min_value=0, step=10000, key=f"p_kpi_{rk_kpi}")
    with col_kpi3:
        gio_kpi = st.number_input("Mục tiêu Giờ nghe Tháng (h):", min_value=0.0, step=100.0, key=f"g_kpi_{rk_kpi}")
        tap_kpi = st.number_input("Mục tiêu Số tập Upload Tháng:", min_value=0, step=1, key=f"tap_kpi_{rk_kpi}")
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Lưu KPI & Cấu Hình Kênh", type="primary", use_container_width=True):
        if not kenh_kpi:
            st.error("⚠️ Vui lòng nhập Tên Kênh!")
        else:
            dieu_kien_kpi = (df_kpi["Tháng"] == thang_kpi) & (df_kpi["Kênh_Spotify"] == kenh_kpi)
            df_kpi_filtered = df_kpi[~dieu_kien_kpi]
            
            kpi_moi = pd.DataFrame([{
                "Tháng": thang_kpi, "Kênh_Spotify": kenh_kpi,
                "KPI_Doanh_Thu": float(dt_kpi), "KPI_Luot_Play": int(play_kpi),
                "KPI_So_Gio": float(gio_kpi), "KPI_So_Tap": int(tap_kpi), 
                "So_Tuan": int(so_tuan_kpi), "Bat_Kiem_Tien": bkt_kpi
            }])
            
            df_kpi_ghi = pd.concat([df_kpi_filtered, kpi_moi], ignore_index=True)
            df_kpi_ghi.to_csv(FILE_KPI, index=False)
            st.toast(f"🎯 Đã lưu cấu hình & KPI cho kênh {kenh_kpi} vào {thang_kpi}!", icon="🎯")
            
            for k in ["loc_thang", "loc_kenh", "loc_bkt", "loc_tuan_phan_tich"]:
                if k in st.session_state: del st.session_state[k]
            st.session_state.rk_kpi += 1
            st.rerun()

# ==========================================
# TAB 3: NHẬP KẾT QUẢ KÊNH 
# ==========================================
with tab_nhap_kq:
    st.subheader("Cập Nhật Kết Quả Vận Hành Tuần")
    rk = st.session_state.rk_kq
    
    col1, col2, col3 = st.columns(3)
    with col1:
        thang_kq = st.selectbox("Tháng Báo Cáo:", [f"Tháng {i}" for i in range(1, 13)], key=f"t_kq_{rk}")
        tuan_kq = st.selectbox("Tuần Báo Cáo:", [f"Tuần {i}" for i in range(1, 53)], key=f"w_kq_{rk}")
        
        if not danh_sach_kenh_master:
            st.warning("⚠️ Chưa có kênh nào! Hãy sang tab 'Nhập Mục Tiêu Kênh' để tạo kênh trước.")
            kenh_kq = ""
        else:
            kenh_kq = st.selectbox("Chọn Kênh Báo Cáo:", danh_sach_kenh_master, key=f"c_kq_{rk}")
            trang_thai_bkt_kq = lay_trang_thai_kiem_tien(kenh_kq)
            text_bkt = "✅ Đã bật kiếm tiền" if trang_thai_bkt_kq else "⏳ Chưa bật kiếm tiền"
            st.caption(f"Trạng thái kênh: {text_bkt}")

    with col2:
        dt_kq = st.number_input("Kết quả Doanh thu (USD):", min_value=0.0, step=1.0, key=f"dt_kq_{rk}")
        play_kq = st.number_input("Kết quả Lượt Play:", min_value=0, step=100, key=f"p_kq_{rk}")
    with col3:
        gio_kq = st.number_input("Kết quả Giờ nghe (h):", min_value=0.0, step=10.0, key=f"g_kq_{rk}")
        tap_kq = st.number_input("Kết quả Số tập Upload:", min_value=0, step=1, key=f"tap_kq_{rk}")
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Lưu Kết Quả", type="primary", use_container_width=True):
        if not kenh_kq:
            st.error("⚠️ Vui lòng chọn Tên Kênh!")
        else:
            dieu_kien_trung = (df["Tuần"] == tuan_kq) & (df["Kênh_Spotify"] == kenh_kq)
            if dieu_kien_trung.any():
                st.error(f"⛔ Dữ liệu '{kenh_kq}' ở '{tuan_kq}' đã có! Qua tab 'Quản Lý Dữ Liệu' xóa trước khi nhập lại.")
            else:
                du_lieu_moi = pd.DataFrame([{
                    "Tháng": thang_kq, "Tuần": tuan_kq, "Kênh_Spotify": kenh_kq,
                    "Doanh_Thu_USD": float(dt_kq), "Luot_Play": int(play_kq),
                    "So_Gio_Nghe": float(gio_kq), "So_Tap_Upload": int(tap_kq),
                    "Bat_Kiem_Tien": trang_thai_bkt_kq, "Thoi_Gian_Nhap": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }])
                df_ghi = pd.concat([df, du_lieu_moi], ignore_index=True)
                df_ghi.to_csv(FILE_DU_LIEU, index=False)
                st.toast(f"✅ Đã lưu kết quả cho {kenh_kq} ({tuan_kq})!", icon="✅")
                
                for k in ["loc_thang", "loc_kenh", "loc_bkt", "loc_tuan_phan_tich"]:
                    if k in st.session_state: del st.session_state[k]
                st.session_state.rk_kq += 1
                st.rerun()

# ==========================================
# TAB 4: XÓA DỮ LIỆU
# ==========================================
with tab_xoa_data:
    st.subheader("Dọn Dẹp Dữ liệu sai")
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
            for k in ["loc_thang", "loc_kenh", "loc_bkt", "loc_tuan_phan_tich"]:
                if k in st.session_state: del st.session_state[k]
            st.toast("✅ Đã xóa thành công!")
            st.rerun()

# ==========================================
# TAB 1: DASHBOARD TỔNG HỢP & SO SÁNH KPI
# ==========================================
with tab_dashboard:
    if df.empty:
        st.info("Hệ thống chưa có dữ liệu kết quả nào được ghi nhận. Vui lòng cập nhật.")
    else:
        # BỘ LỌC TỔNG (THÊM BỘ LỌC BẬT KIẾM TIỀN)
        col_loc1, col_loc2, col_loc3 = st.columns([1, 2, 1])
        with col_loc1:
            thang_hien_co = list(df["Tháng"].unique())
            thang_mac_dinh = thang_hien_co[-1] if thang_hien_co else "Tất cả các tháng"
            thang_chon = st.selectbox("📅 Lọc Dashboard theo Tháng:", ["Tất cả các tháng"] + thang_hien_co, index=(len(thang_hien_co)), key="loc_thang")
            
        df_thang = df if thang_chon == "Tất cả các tháng" else df[df["Tháng"] == thang_chon]
        danh_sach_kenh_hien_co = list(df_thang["Kênh_Spotify"].unique())
        
        with col_loc2:
            kenh_duoc_chon = st.multiselect("🎧 Lọc theo Kênh:", options=danh_sach_kenh_hien_co, default=danh_sach_kenh_hien_co, key="loc_kenh")
            
        with col_loc3:
            loc_bkt = st.selectbox("🚦 Trạng thái Kiếm Tiền:", ["Tất cả", "Đã bật kiếm tiền", "Chưa bật kiếm tiền"], key="loc_bkt")
            
        st.markdown("---")
        
        # XỬ LÝ LOGIC LỌC KENH THEO TRẠNG THÁI KIẾM TIỀN
        kenh_hien_thi_cuoi_cung = []
        for k in kenh_duoc_chon:
            is_bkt = lay_trang_thai_kiem_tien(k)
            if loc_bkt == "Tất cả":
                kenh_hien_thi_cuoi_cung.append(k)
            elif loc_bkt == "Đã bật kiếm tiền" and is_bkt:
                kenh_hien_thi_cuoi_cung.append(k)
            elif loc_bkt == "Chưa bật kiếm tiền" and not is_bkt:
                kenh_hien_thi_cuoi_cung.append(k)

        if not kenh_hien_thi_cuoi_cung:
            st.warning(f"⚠️ Không có kênh nào thỏa mãn điều kiện '{loc_bkt}' trong danh sách đã chọn!")
        else:
            # Gán lại tập dữ liệu chuẩn để vẽ toàn bộ Dashboard
            df_final = df_thang[df_thang["Kênh_Spotify"].isin(kenh_hien_thi_cuoi_cung)]
            
            # ĐỌC VÀ LỌC KPI
            df_kpi_read = pd.read_csv(FILE_KPI)
            df_kpi_filter = df_kpi_read[df_kpi_read["Kênh_Spotify"].isin(kenh_hien_thi_cuoi_cung)]
            if thang_chon != "Tất cả các tháng":
                df_kpi_filter = df_kpi_filter[df_kpi_filter["Tháng"] == thang_chon]
                
            target_dt = df_kpi_filter["KPI_Doanh_Thu"].sum()
            target_play = df_kpi_filter["KPI_Luot_Play"].sum()
            target_gio = df_kpi_filter["KPI_So_Gio"].sum()
            target_tap = df_kpi_filter["KPI_So_Tap"].sum()

            # --- SCORECARDS (ĐÃ THÊM TỔNG KÊNH & KÊNH BẬT KIẾM TIỀN) ---
            st.markdown("### 🏆 CHỈ SỐ KẾT QUẢ vs MỤC TIÊU")
            
            # Đếm số liệu kênh
            tong_so_kenh = len(kenh_hien_thi_cuoi_cung)
            so_kenh_bkt = sum([1 for k in kenh_hien_thi_cuoi_cung if lay_trang_thai_kiem_tien(k)])
            
            sc1, sc2, sc3, sc4, sc5, sc6 = st.columns(6)
            sc1.metric("🏢 Tổng Kênh Đang Lọc", tong_so_kenh)
            sc2.metric("💸 Kênh Bật Kiếm Tiền", so_kenh_bkt)
            sc3.metric("💰 Doanh Thu", f"${df_final['Doanh_Thu_USD'].sum():,.0f}", delta=f"${df_final['Doanh_Thu_USD'].sum() - target_dt:,.0f} vs KPI")
            sc4.metric("▶️ Lượt Play", f"{df_final['Luot_Play'].sum():,.0f}", delta=f"{df_final['Luot_Play'].sum() - target_play:,.0f} vs KPI")
            sc5.metric("⏱️ Giờ Nghe", f"{df_final['So_Gio_Nghe'].sum():,.0f}h", delta=f"{df_final['So_Gio_Nghe'].sum() - target_gio:,.0f} vs KPI")
            sc6.metric("🎙️ Tập Upload", f"{df_final['So_Tap_Upload'].sum():,.0f}", delta=f"{df_final['So_Tap_Upload'].sum() - target_tap:,.0f} vs KPI")
            
            st.markdown("---")
            
            # --- CHỌN CHỈ SỐ CHO TOÀN BỘ BIỂU ĐỒ & RANKING ---
            st.markdown("### 🚀 Phân Tích Tiến Độ & Hiệu Suất Theo Chỉ Số")
            chiso_chon = st.radio("🛠️ Chọn chỉ số để xem phân tích:", 
                                  ["Doanh Thu", "Lượt Play", "Giờ Nghe"], horizontal=True)
            
            map_chiso = {
                "Doanh Thu": {"kq": "Doanh_Thu_USD", "kpi": "KPI_Doanh_Thu", "format": "$"},
                "Lượt Play": {"kq": "Luot_Play", "kpi": "KPI_Luot_Play", "format": ""},
                "Giờ Nghe": {"kq": "So_Gio_Nghe", "kpi": "KPI_So_Gio", "format": "h"}
            }
            cot_kq = map_chiso[chiso_chon]["kq"]
            cot_kpi = map_chiso[chiso_chon]["kpi"]
            kieu_format = map_chiso[chiso_chon]["format"]

            # --- 1. BIỂU ĐỒ LINE KÉP (TIẾN ĐỘ) ---
            df_kpi_filter["Muc_Tieu_Tuan_Hien_Tai"] = df_kpi_filter[cot_kpi].fillna(0) / df_kpi_filter["So_Tuan"].fillna(4)
            tong_muc_tieu_1_tuan = df_kpi_filter["Muc_Tieu_Tuan_Hien_Tai"].sum()
            
            max_tuan_kpi = int(df_kpi_filter["So_Tuan"].max()) if not df_kpi_filter.empty and pd.notna(df_kpi_filter["So_Tuan"].max()) else 4
            tuan_tu_data = df_final["Tuần"].unique().tolist()
            tuan_tu_kpi = [f"Tuần {i}" for i in range(1, max_tuan_kpi + 1)]
            danh_sach_tuan_full = list(set(tuan_tu_data + tuan_tu_kpi)) 
            danh_sach_tuan_full.sort(key=lambda x: int(x.replace("Tuần ", "")) if "Tuần " in x else 0)
            
            tuan_hien_thi = st.multiselect("📅 Chọn các Tuần hiển thị trên Biểu đồ Line:", 
                                           options=danh_sach_tuan_full, 
                                           default=danh_sach_tuan_full)
            tuan_hien_thi.sort(key=lambda x: int(x.replace("Tuần ", "")) if "Tuần " in x else 0)

            if not tuan_hien_thi:
                st.warning("⚠️ Vui lòng chọn ít nhất 1 tuần để vẽ biểu đồ Line.")
            else:
                df_trend = pd.DataFrame({"Tuần": tuan_hien_thi})
                df_trend["Đường_Mục_Tiêu"] = tong_muc_tieu_1_tuan
    
                df_kq_group_line = df_final.groupby("Tuần")[cot_kq].sum().reset_index()
                df_trend = pd.merge(df_trend, df_kq_group_line, on="Tuần", how="left")
                
                fig_vs = go.Figure()
                fig_vs.add_trace(go.Scatter(x=df_trend["Tuần"], y=df_trend[cot_kq], mode='lines+markers+text', 
                                            name=f'Kết Quả {chiso_chon}', text=df_trend[cot_kq], textposition="top center",
                                            line=dict(color='#1DB954', width=3), marker=dict(size=8)))
                
                fig_vs.add_trace(go.Scatter(x=df_trend["Tuần"], y=df_trend["Đường_Mục_Tiêu"], mode='lines+markers', 
                                            name=f'Mục Tiêu {chiso_chon} (Tổng)', 
                                            line=dict(color='#FF5722', width=3, dash='dash')))
                
                fig_vs.update_layout(
                    title=f"📈 Tiến độ {chiso_chon} các Tuần so với KPI", 
                    hovermode="x unified", 
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    yaxis=dict(rangemode='tozero', title=f"Giá trị ({kieu_format})")
                )
                st.plotly_chart(fig_vs, use_container_width=True)

            st.markdown("---")

            # --- 2. BẢNG XẾP HẠNG TOP 5: TĂNG TRƯỞNG WOW (WEEK-OVER-WEEK) ---
            st.markdown(f"### 🏅 Top 5 Kênh Biến Động Hiệu Suất ({chiso_chon})")
            
            tuan_co_data = list(df_final["Tuần"].unique())
            tuan_co_data.sort(key=lambda x: int(x.replace("Tuần ", "")) if "Tuần " in x else 0)
            
            if not tuan_co_data:
                st.info("Chưa có dữ liệu tuần để so sánh biến động.")
            else:
                tuan_chon_rank = st.selectbox("📌 Chọn Tuần xem biến động (Hệ thống sẽ tự so sánh với Tuần liền trước):", tuan_co_data, key="loc_tuan_rank")
                
                tuan_num = int(tuan_chon_rank.replace("Tuần ", "")) if "Tuần " in tuan_chon_rank else 0
                tuan_truoc_str = f"Tuần {tuan_num - 1}"
                
                if tuan_num == 1:
                    st.info("💡 Đây là Tuần 1 nên chưa có dữ liệu Tuần trước đó để so sánh. Các kênh mặc định được xem là tăng trưởng mới.")
                elif tuan_truoc_
