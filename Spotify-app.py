import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime
import numpy as np

# 1. CẤU HÌNH GIAO DIỆN
st.set_page_config(page_title="Spotify Performance Hub", layout="wide", page_icon="🎧")

# ==========================================
# GIAO DIỆN NATIVE - OVERLAY KÍNH XANH
# ==========================================
st.markdown("""
<style>
    /* KỸ THUẬT PHỦ KÍNH: Phủ 1 lớp màu xanh siêu mỏng lên trên nền mặc định của Theme */
    [data-testid="stAppViewContainer"] { 
        background-color: var(--background-color) !important; 
        background-image: linear-gradient(rgba(29, 185, 84, 0.07), rgba(29, 185, 84, 0.07)) !important;
    }
    
    [data-testid="stSidebar"] { 
        background-color: var(--secondary-background-color) !important; 
        background-image: linear-gradient(rgba(29, 185, 84, 0.12), rgba(29, 185, 84, 0.12)) !important;
    }
    
    [data-testid="stHeader"] { background-color: transparent !important; }
    
    /* Chữ tự động lấy màu tương phản chuẩn của Streamlit */
    p, h1, h2, h3, h4, h5, h6, li, label, .stMarkdown, .stText, div[data-testid="stMarkdownContainer"] {
        color: var(--text-color) !important;
    }
    
    /* Thẻ Scorecard */
    .spotify-card {
        background-color: var(--secondary-background-color) !important; 
        background-image: linear-gradient(rgba(29, 185, 84, 0.03), rgba(29, 185, 84, 0.03)) !important;
        border: 1px solid rgba(29, 185, 84, 0.2) !important; 
        border-radius: 12px; padding: 15px; height: 100%; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .spotify-card:hover { transform: translateY(-3px); box-shadow: 0 6px 15px rgba(29,185,84,0.15); }
    
    .spotify-label { 
        font-size: 13px; font-weight: 600; 
        color: var(--text-color) !important; opacity: 0.7;
        text-transform: uppercase; margin-bottom: 5px; 
    }
    .spotify-value { font-size: 26px; font-weight: 900; margin-bottom: 10px; color: var(--text-color) !important; }
    
    /* Huy hiệu (Badges) thích ứng tốt trên cả 2 nền */
    .badge-green { background-color: rgba(29, 185, 84, 0.15) !important; color: #1DB954 !important; padding: 4px 8px; border-radius: 6px; font-size: 13px; font-weight: 800; border: 1px solid rgba(29, 185, 84, 0.3); }
    .badge-red { background-color: rgba(226, 33, 52, 0.15) !important; color: #E22134 !important; padding: 4px 8px; border-radius: 6px; font-size: 13px; font-weight: 800; border: 1px solid rgba(226, 33, 52, 0.3); }
    
    .text-success { color: #1DB954 !important; font-size: 18px; font-weight: bold; }
    .text-danger { color: #E22134 !important; font-size: 18px; font-weight: bold; }

    /* Nút Button */
    div.stButton > button[kind="primary"] { background-color: #1DB954 !important; color: white !important; border: none; border-radius: 20px; font-weight: bold; }
    div.stButton > button[kind="primary"]:hover { background-color: #1ED760 !important; color: white !important; }
    div.stButton > button * { color: white !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# KHỞI TẠO DATA
# ==========================================
FILE_DU_LIEU = "spotify_master_data.csv"
FILE_KPI = "spotify_channel_kpi.csv" 

def khoi_tao_he_thong_db():
    if not os.path.exists(FILE_DU_LIEU): pd.DataFrame(columns=["Tháng", "Tuần", "Kênh_Spotify", "Doanh_Thu_USD", "Luot_Play", "So_Gio_Nghe", "So_Tap_Upload", "Bat_Kiem_Tien", "Thoi_Gian_Nhap"]).to_csv(FILE_DU_LIEU, index=False)
    else:
        df_hien_tai = pd.read_csv(FILE_DU_LIEU)
        if "Bat_Kiem_Tien" not in df_hien_tai.columns: df_hien_tai["Bat_Kiem_Tien"] = False; df_hien_tai.to_csv(FILE_DU_LIEU, index=False)
            
    if not os.path.exists(FILE_KPI): pd.DataFrame(columns=["Tháng", "Kênh_Spotify", "KPI_Doanh_Thu", "KPI_Luot_Play", "KPI_So_Gio", "KPI_So_Tap", "So_Tuan", "Bat_Kiem_Tien"]).to_csv(FILE_KPI, index=False)
    else:
        df_kpi_hien_tai = pd.read_csv(FILE_KPI)
        if "Bat_Kiem_Tien" not in df_kpi_hien_tai.columns: df_kpi_hien_tai["Bat_Kiem_Tien"] = False; df_kpi_hien_tai.to_csv(FILE_KPI, index=False)

khoi_tao_he_thong_db()
df = pd.read_csv(FILE_DU_LIEU)
df_kpi = pd.read_csv(FILE_KPI)

danh_sach_kenh_master = list(set(df["Kênh_Spotify"].dropna().unique()) | set(df_kpi["Kênh_Spotify"].dropna().unique()))
danh_sach_kenh_master.sort()

def lay_trang_thai_kiem_tien(ten_kenh):
    kpi_match = df_kpi[df_kpi["Kênh_Spotify"] == ten_kenh]
    if not kpi_match.empty: return bool(kpi_match.iloc[-1]["Bat_Kiem_Tien"])
    df_match = df[df["Kênh_Spotify"] == ten_kenh]
    if not df_match.empty: return bool(df_match.iloc[-1]["Bat_Kiem_Tien"])
    return False

def make_card(label, value, pct=None):
    badge = f"<span class='{'badge-green' if pct >= 100 else 'badge-red'}'>{pct:.1f}% KPI</span>" if pct is not None else ""
    return f"""
    <div class="spotify-card">
        <div class="spotify-label">{label}</div>
        <div class="spotify-value">{value}</div>
        {f'<div>{badge}</div>' if badge else ''}
    </div>
    """

if "rk_kq" not in st.session_state: st.session_state.rk_kq = 0
if "rk_kpi" not in st.session_state: st.session_state.rk_kpi = 0

st.title("🎧 TRUNG TÂM QUẢN TRỊ HIỆU SUẤT SPOTIFY")
st.markdown("---")

if "toast_msg" in st.session_state:
    st.toast(st.session_state.toast_msg[0], icon=st.session_state.toast_msg[1])
    del st.session_state.toast_msg

cac_key_can_xoa = ["loc_thang", "loc_tuan", "loc_kenh", "loc_bkt", "loc_tuan_phan_tich", "loc_tuan_rank"]

tab_dashboard, tab_nhap_kpi, tab_nhap_kq, tab_xoa_data = st.tabs([
    "📊 Báo Cáo Dashboard", "🎯 Nhập Mục Tiêu Kênh", "📥 Nhập Kết Quả Kênh", "🛠️ Quản Lý Dữ Liệu"
])

# ==========================================
# TAB 2: NHẬP MỤC TIÊU 
# ==========================================
with tab_nhap_kpi:
    st.subheader("Thiết Lập Kênh & Mục Tiêu (KPI) Tháng")
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
        if not kenh_kpi: st.error("⚠️ Vui lòng nhập Tên Kênh!")
        else:
            dieu_kien_kpi = (df_kpi["Tháng"] == thang_kpi) & (df_kpi["Kênh_Spotify"] == kenh_kpi)
            df_kpi_filtered = df_kpi[~dieu_kien_kpi]
            kpi_moi = pd.DataFrame([{ "Tháng": thang_kpi, "Kênh_Spotify": kenh_kpi, "KPI_Doanh_Thu": float(dt_kpi), "KPI_Luot_Play": int(play_kpi), "KPI_So_Gio": float(gio_kpi), "KPI_So_Tap": int(tap_kpi), "So_Tuan": int(so_tuan_kpi), "Bat_Kiem_Tien": bkt_kpi }])
            pd.concat([df_kpi_filtered, kpi_moi], ignore_index=True).to_csv(FILE_KPI, index=False)
            st.session_state.toast_msg = (f"🎯 Đã lưu cấu hình & KPI cho kênh {kenh_kpi} vào {thang_kpi}!", "🎯")
            for k in cac_key_can_xoa:
                if k in st.session_state: del st.session_state[k]
            st.session_state.rk_kpi += 1; st.rerun()

# ==========================================
# TAB 3: NHẬP KẾT QUẢ
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
            st.caption(f"Trạng thái kênh: {'✅ Đã bật kiếm tiền' if trang_thai_bkt_kq else '⏳ Chưa bật kiếm tiền'}")
    with col2:
        dt_kq = st.number_input("Kết quả Doanh thu (USD):", min_value=0.0, step=1.0, key=f"dt_kq_{rk}")
        play_kq = st.number_input("Kết quả Lượt Play:", min_value=0, step=100, key=f"p_kq_{rk}")
    with col3:
        gio_kq = st.number_input("Kết quả Giờ nghe (h):", min_value=0.0, step=10.0, key=f"g_kq_{rk}")
        tap_kq = st.number_input("Kết quả Số tập Upload:", min_value=0, step=1, key=f"tap_kq_{rk}")
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Lưu Kết Quả", type="primary", use_container_width=True):
        if not kenh_kq: st.error("⚠️ Vui lòng chọn Tên Kênh!")
        else:
            if ((df["Tuần"] == tuan_kq) & (df["Kênh_Spotify"] == kenh_kq)).any():
                st.error(f"⛔ Dữ liệu '{kenh_kq}' ở '{tuan_kq}' đã có! Qua tab 'Quản Lý' xóa trước.")
            else:
                du_lieu_moi = pd.DataFrame([{ "Tháng": thang_kq, "Tuần": tuan_kq, "Kênh_Spotify": kenh_kq, "Doanh_Thu_USD": float(dt_kq), "Luot_Play": int(play_kq), "So_Gio_Nghe": float(gio_kq), "So_Tap_Upload": int(tap_kq), "Bat_Kiem_Tien": trang_thai_bkt_kq, "Thoi_Gian_Nhap": datetime.now().strftime("%Y-%m-%d %H:%M:%S") }])
                pd.concat([df, du_lieu_moi], ignore_index=True).to_csv(FILE_DU_LIEU, index=False)
                st.session_state.toast_msg = (f"✅ Đã lưu kết quả cho {kenh_kq} ({tuan_kq})!", "✅")
                for k in cac_key_can_xoa:
                    if k in st.session_state: del st.session_state[k]
                st.session_state.rk_kq += 1; st.rerun()

# ==========================================
# TAB 4: QUẢN LÝ DỮ LIỆU
# ==========================================
with tab_xoa_data:
    if not danh_sach_kenh_master: st.info("Hệ thống chưa có dữ liệu kênh nào.")
    else:
        st.subheader("🛠️ Chỉnh Sửa Thông Tin Kênh")
        kenh_can_sua = st.selectbox("1. Chọn Kênh cần chỉnh sửa:", danh_sach_kenh_master, key="edit_k")
        col_e1, col_e2 = st.columns(2)
        with col_e1: ten_kenh_moi = st.text_input("Tên kênh mới:", value=kenh_can_sua, key="edit_name").strip()
        with col_e2: 
            st.markdown("<br>", unsafe_allow_html=True)
            bkt_moi = st.checkbox("✅ Kênh đã bật kiếm tiền", value=lay_trang_thai_kiem_tien(kenh_can_sua), key="edit_bkt")
            
        if st.button("💾 Lưu Thay Đổi Thông Tin", type="primary"):
            if not ten_kenh_moi: st.error("⚠️ Tên kênh không được để trống!")
            elif ten_kenh_moi != kenh_can_sua and ten_kenh_moi in danh_sach_kenh_master: st.error("⚠️ Tên kênh đã tồn tại!")
            else:
                df.loc[df["Kênh_Spotify"] == kenh_can_sua, "Kênh_Spotify"] = ten_kenh_moi
                df.loc[df["Kênh_Spotify"] == ten_kenh_moi, "Bat_Kiem_Tien"] = bkt_moi
                df.to_csv(FILE_DU_LIEU, index=False)
                df_kpi.loc[df_kpi["Kênh_Spotify"] == kenh_can_sua, "Kênh_Spotify"] = ten_kenh_moi
                df_kpi.loc[df_kpi["Kênh_Spotify"] == ten_kenh_moi, "Bat_Kiem_Tien"] = bkt_moi
                df_kpi.to_csv(FILE_KPI, index=False)
                st.session_state.toast_msg = (f"✅ Đã cập nhật kênh {ten_kenh_moi}!", "✅")
                for k in cac_key_can_xoa:
                    if k in st.session_state: del st.session_state[k]
                st.rerun()
                
        st.markdown("---")
        st.subheader("🗑️ Dọn Dẹp Dữ Liệu Báo Cáo Sai")
        if df.empty: st.info("Kho dữ liệu báo cáo tuần đang trống.")
        else:
            col_x1, col_x2 = st.columns(2)
            with col_x1: kenh_can_xoa = st.selectbox("1. Chọn Kênh cần xóa:", df["Kênh_Spotify"].unique(), key="del_k")
            with col_x2: tuan_can_xoa = st.selectbox("2. Chọn Tuần bị sai:", df[df["Kênh_Spotify"] == kenh_can_xoa]["Tuần"].unique(), key="del_w")
            if st.button("🗑️ Xác Nhận Xóa Dữ Liệu Tuần Này", type="primary"):
                df[~((df["Kênh_Spotify"] == kenh_can_xoa) & (df["Tuần"] == tuan_can_xoa))].to_csv(FILE_DU_LIEU, index=False)
                st.session_state.toast_msg = ("✅ Đã xóa thành công!", "✅")
                for k in cac_key_can_xoa:
                    if k in st.session_state: del st.session_state[k]
                st.rerun()

# ==========================================
# TAB 1: DASHBOARD
# ==========================================
with tab_dashboard:
    if df.empty: st.info("Hệ thống chưa có dữ liệu kết quả nào được ghi nhận. Vui lòng cập nhật.")
    else:
        col_loc1, col_loc_tuan, col_loc2, col_loc3 = st.columns([1.2, 1.2, 2, 1.2])
        with col_loc1:
            thang_hien_co = list(df["Tháng"].unique())
            thang_chon = st.selectbox("📅 Lọc theo Tháng:", ["Tất cả các tháng"] + thang_hien_co, index=(len(thang_hien_co)), key="loc_thang")
            
        df_thang = df if thang_chon == "Tất cả các tháng" else df[df["Tháng"] == thang_chon]
        with col_loc_tuan:
            tuan_hien_co = list(df_thang["Tuần"].unique())
            tuan_hien_co.sort(key=lambda x: int(x.replace("Tuần ", "")) if "Tuần " in x else 0)
            tuan_chon = st.multiselect("📅 Lọc theo Tuần:", options=tuan_hien_co, default=tuan_hien_co, key="loc_tuan")

        danh_sach_kenh_hien_co = list(df_thang["Kênh_Spotify"].unique())
        with col_loc2: kenh_duoc_chon = st.multiselect("🎧 Lọc theo Kênh:", options=danh_sach_kenh_hien_co, default=danh_sach_kenh_hien_co, key="loc_kenh")
        with col_loc3: loc_bkt = st.selectbox("🚦 Kiếm Tiền:", ["Tất cả", "Đã bật", "Chưa bật"], key="loc_bkt")
            
        st.markdown("---")
        kenh_hien_thi_cuoi_cung = [k for k in kenh_duoc_chon if (loc_bkt == "Tất cả") or (loc_bkt == "Đã bật" and lay_trang_thai_kiem_tien(k)) or (loc_bkt == "Chưa bật" and not lay_trang_thai_kiem_tien(k))]

        if not kenh_hien_thi_cuoi_cung or not tuan_chon: st.warning(f"⚠️ Vui lòng chọn ít nhất 1 Kênh và 1 Tuần để hiển thị dữ liệu!")
        else:
            df_final = df_thang[df_thang["Kênh_Spotify"].isin(kenh_hien_thi_cuoi_cung)]
            df_final = df_final[df_final["Tuần"].isin(tuan_chon)]
            
            df_kpi_filter = df_kpi[df_kpi["Kênh_Spotify"].isin(kenh_hien_thi_cuoi_cung)]
            if thang_chon != "Tất cả các tháng": df_kpi_filter = df_kpi_filter[df_kpi_filter["Tháng"] == thang_chon]
                
            if len(tuan_chon) < len(tuan_hien_co):
                so_tuan_chon = len(tuan_chon)
                target_dt = (df_kpi_filter["KPI_Doanh_Thu"] / df_kpi_filter["So_Tuan"].fillna(4)).sum() * so_tuan_chon
                target_play = (df_kpi_filter["KPI_Luot_Play"] / df_kpi_filter["So_Tuan"].fillna(4)).sum() * so_tuan_chon
                target_gio = (df_kpi_filter["KPI_So_Gio"] / df_kpi_filter["So_Tuan"].fillna(4)).sum() * so_tuan_chon
                target_tap = (df_kpi_filter["KPI_So_Tap"] / df_kpi_filter["So_Tuan"].fillna(4)).sum() * so_tuan_chon
            else:
                target_dt = df_kpi_filter["KPI_Doanh_Thu"].sum()
                target_play = df_kpi_filter["KPI_Luot_Play"].sum()
                target_gio = df_kpi_filter["KPI_So_Gio"].sum()
                target_tap = df_kpi_filter["KPI_So_Tap"].sum()

            st.markdown("### 🏆 CHỈ SỐ KẾT QUẢ TỔNG QUAN")
            dt_pct = (df_final['Doanh_Thu_USD'].sum() / target_dt * 100) if target_dt > 0 else 0
            play_pct = (df_final['Luot_Play'].sum() / target_play * 100) if target_play > 0 else 0
            gio_pct = (df_final['So_Gio_Nghe'].sum() / target_gio * 100) if target_gio > 0 else 0
            tap_pct = (df_final['So_Tap_Upload'].sum() / target_tap * 100) if target_tap > 0 else 0
            
            sc1, sc2, sc3, sc4, sc5, sc6 = st.columns(6)
            sc1.markdown(make_card("🏢 Tổng Kênh", len(kenh_hien_thi_cuoi_cung)), unsafe_allow_html=True)
            sc2.markdown(make_card("💸 Đã Bật Kiếm Tiền", sum([1 for k in kenh_hien_thi_cuoi_cung if lay_trang_thai_kiem_tien(k)])), unsafe_allow_html=True)
            sc3.markdown(make_card("💰 Doanh Thu", f"${df_final['Doanh_Thu_USD'].sum():,.0f}", dt_pct), unsafe_allow_html=True)
            sc4.markdown(make_card("▶️ Lượt Play", f"{df_final['Luot_Play'].sum():,.0f}", play_pct), unsafe_allow_html=True)
            sc5.markdown(make_card("⏱️ Giờ Nghe", f"{df_final['So_Gio_Nghe'].sum():,.0f}h", gio_pct), unsafe_allow_html=True)
            sc6.markdown(make_card("🎙️ Tập Upload", f"{df_final['So_Tap_Upload'].sum():,.0f}", tap_pct), unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("---")
            
            st.markdown("### 🚀 Phân Tích Tiến Độ & Bảng Xếp Hạng Kênh")
            chiso_chon = st.radio("🛠️ Chọn chỉ số để xem phân tích:", ["Doanh Thu", "Lượt Play", "Giờ Nghe"], horizontal=True)
            map_chiso = { "Doanh Thu": {"kq": "Doanh_Thu_USD", "kpi": "KPI_Doanh_Thu", "format": "$"}, "Lượt Play": {"kq": "Luot_Play", "kpi": "KPI_Luot_Play", "format": ""}, "Giờ Nghe": {"kq": "So_Gio_Nghe", "kpi": "KPI_So_Gio", "format": "h"} }
            cot_kq, cot_kpi, kieu_format = map_chiso[chiso_chon]["kq"], map_chiso[chiso_chon]["kpi"], map_chiso[chiso_chon]["format"]

            df_kpi_filter["Muc_Tieu_Tuan_Hien_Tai"] = df_kpi_filter[cot_kpi].fillna(0) / df_kpi_filter["So_Tuan"].fillna(4)
            
            max_tuan_kpi = int(df_kpi_filter["So_Tuan"].max()) if not df_kpi_filter.empty and pd.notna(df_kpi_filter["So_Tuan"].max()) else 4
            tuan_tu_data = df_final["Tuần"].unique().tolist()
            danh_sach_tuan_full = list(set(tuan_tu_data + [f"Tuần {i}" for i in range(1, max_tuan_kpi + 1)])) 
            danh_sach_tuan_full.sort(key=lambda x: int(x.replace("Tuần ", "")) if "Tuần " in x else 0)
            
            tuan_hien_thi = st.multiselect("📅 Chọn Tuần vẽ biểu đồ Line:", options=danh_sach_tuan_full, default=danh_sach_tuan_full)
            tuan_hien_thi.sort(key=lambda x: int(x.replace("Tuần ", "")) if "Tuần " in x else 0)

            if not tuan_hien_thi: st.warning("⚠️ Vui lòng chọn ít nhất 1 tuần để vẽ biểu đồ Line.")
            else:
                df_trend = pd.merge(pd.DataFrame({"Tuần": tuan_hien_thi}), df_final.groupby("Tuần")[cot_kq].sum().reset_index(), on="Tuần", how="left")
                df_trend["Đường_Mục_Tiêu"] = round(df_kpi_filter["Muc_Tieu_Tuan_Hien_Tai"].sum(), 2)
                df_trend[cot_kq] = df_trend[cot_kq].round(2)
                
                def format_text(val):
                    if pd.isna(val): return ""
                    if chiso_chon == "Doanh Thu": return f"${val:,.2f}"
                    elif chiso_chon == "Giờ Nghe": return f"{val:,.1f}h"
                    return f"{val:,.0f}"

                fig_vs = go.Figure()
                fig_vs.add_trace(go.Scatter(x=df_trend["Tuần"], y=df_trend[cot_kq], mode='lines+markers+text', name=f'Kết Quả', text=df_trend[cot_kq].apply(format_text), textposition="top center", line=dict(color='#1DB954', width=3), marker=dict(size=8)))
                fig_vs.add_trace(go.Scatter(x=df_trend["Tuần"], y=df_trend["Đường_Mục_Tiêu"], mode='lines+markers', name=f'Mục Tiêu Tuần', line=dict(color='#E22134', width=3, dash='dash')))
                
                fig_vs.update_layout(
                    title=f"📈 Tiến độ {chiso_chon} các Tuần so với KPI", hovermode="x unified", 
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    yaxis=dict(rangemode='tozero', title=f"Giá trị ({kieu_format})"),
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_vs, use_container_width=True)

            st.markdown("---")
            st.markdown(f"### 🏅 Bảng Xếp Hạng Kênh Theo {chiso_chon}")
            tuan_co_data = list(df_final["Tuần"].unique()); tuan_co_data.sort(key=lambda x: int(x.replace("Tuần ", "")) if "Tuần " in x else 0)
            
            if not tuan_co_data: st.info("Chưa có dữ liệu tuần để xếp hạng.")
            else:
                tuan_chon_rank = st.selectbox("📌 Chọn thời gian để xếp hạng:", ["Tất cả các tuần"] + tuan_co_data, key="loc_tuan_rank")
                df_rank = df_final.groupby("Kênh_Spotify")[cot_kq].sum().reset_index() if tuan_chon_rank == "Tất cả các tuần" else df_final[df_final["Tuần"] == tuan_chon_rank].groupby("Kênh_Spotify")[cot_kq].sum().reset_index()
                df_rank = df_rank.sort_values(by=cot_kq, ascending=False).reset_index(drop=True); df_rank[cot_kq] = df_rank[cot_kq].round(2)
                
                top_5 = df_rank.head(5)
                bot_5 = pd.DataFrame(columns=["Kênh_Spotify", cot_kq]) if len(df_rank) <= 5 else df_rank[~df_rank["Kênh_Spotify"].isin(top_5["Kênh_Spotify"])].tail(5).sort_values(by=cot_kq, ascending=True)
                
                def fmt(val): return f"${val:,.2f}" if chiso_chon == "Doanh Thu" else (f"{val:,.1f}h" if chiso_chon == "Giờ Nghe" else f"{val:,.0f}")
                col_top, col_bot = st.columns(2)
                with col_top:
                    st.success(f"🌟 **TOP 5 CAO NHẤT**")
                    for idx, row in top_5.iterrows(): st.markdown(f"**#{idx+1}. {row['Kênh_Spotify']}** ➔ <span class='text-success'>{fmt(row[cot_kq])}</span>", unsafe_allow_html=True); st.markdown("")
                with col_bot:
                    st.error(f"⚠️ **TOP 5 THẤP NHẤT**")
                    for idx, row in bot_5.iterrows(): st.markdown(f"**🔻 {row['Kênh_Spotify']}** ➔ <span class='text-danger'>{fmt(row[cot_kq])}</span>", unsafe_allow_html=True); st.markdown("")

            st.markdown("---")
            st.markdown("### 🥧 Phân Tích Cơ Cấu & Tỷ Trọng")
            tuan_chon_pie = st.selectbox("📌 Phân tích Tỷ trọng theo thời gian:", ["Tất cả các tuần"] + tuan_co_data, key="loc_tuan_phan_tich")
            df_phan_tich = df_final if tuan_chon_pie == "Tất cả các tuần" else df_final[df_final["Tuần"] == tuan_chon_pie]
            
            if df_phan_tich.empty: st.info(f"Không có dữ liệu kết quả cho {tuan_chon_pie}.")
            else:
                col_pie, col_bar = st.columns(2)
                with col_pie:
                    df_pie = df_phan_tich.groupby("Kênh_Spotify")[cot_kq].sum().reset_index(); df_pie[cot_kq] = df_pie[cot_kq].round(2)
                    fig_pie = px.pie(df_pie, values=cot_kq, names="Kênh_Spotify", hole=0.4, title=f"Tỷ Trọng {chiso_chon}")
                    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_pie, use_container_width=True)
                with col_bar:
                    df_bar = df_phan_tich.groupby("Kênh_Spotify")[cot_kq].sum().reset_index(); df_bar[cot_kq] = df_bar[cot_kq].round(2)
                    fig_bar = px.bar(df_bar, x="Kênh_Spotify", y=cot_kq, title=f"So Sánh Lượng {chiso_chon}", text_auto='.2s')
                    fig_bar.update_traces(marker_color='#1DB954', textfont_size=12, textangle=0, textposition="outside")
                    fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_bar, use_container_width=True)
