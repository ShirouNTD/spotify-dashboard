import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime

# ==========================================
# KHỞI TẠO SESSION STATE
# ==========================================
if "rk_kq" not in st.session_state:
    st.session_state.rk_kq = 0
if "rk_kq_thang" not in st.session_state:
    st.session_state.rk_kq_thang = 0
if "rk_kpi" not in st.session_state:
    st.session_state.rk_kpi = 0

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN & CUSTOM THEME TOGGLE
# ==========================================
st.set_page_config(page_title="Spotify Performance Hub", layout="wide", page_icon="🎧", initial_sidebar_state="expanded")

# TẠO CÔNG TẮC THEME ĐỘC QUYỀN TRÊN SIDEBAR
st.sidebar.markdown("### 🎨 Tùy chỉnh Giao diện")
theme_choice = st.sidebar.radio("Giao diện:", ["☀️ Light Mode", "🌙 Dark Mode"], horizontal=True, label_visibility="collapsed")

is_light = "Light" in theme_choice 

# Bơm màu theo công tắc của Boss
if is_light:
    bg_main = "#FFFFFF"
    bg_sec = "#F8F9FA"
    text_c = "#0C7A33"  # Xanh lá
    border_c = "#E0E0E0"
    alert_c = "#111827" # Chữ đen đậm cho ô báo lỗi/thông báo
else:
    bg_main = "#0E1117"
    bg_sec = "#262730"
    text_c = "#FAFAFA"  # Trắng
    border_c = "rgba(29, 185, 84, 0.2)"
    alert_c = "#FAFAFA" # Chữ trắng cho ô báo lỗi/thông báo

# Bơm CSS ép tuyệt đối 
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"], [class*="st-"] {{ font-family: 'Lexend', sans-serif !important; }}

    /* ÉP MÀU NỀN CỰC MẠNH */
    .stApp, [data-testid="stAppViewContainer"] {{ background-color: {bg_main} !important; background-image: none !important; }}
    [data-testid="stSidebar"] {{ background-color: {bg_sec} !important; background-image: none !important; }}
    
   /* ẨN TOÀN BỘ MENU, NÚT DEPLOY VÀ HEADER MẶC ĐỊNH CỦA STREAMLIT */

    #MainMenu {visibility: hidden;}

    [data-testid="stHeader"] {display: none !important;}

    [data-testid="stToolbar"] {visibility: hidden !important;}

    footer {visibility: hidden;}

    /* ÉP MÀU CHỮ TOÀN CỤC */
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, label, li, span, div[data-testid="stMarkdownContainer"] {{
        color: {text_c} !important;
    }}

    /* 🛡️ TRỊ DỨT ĐIỂM CHỮ XANH LÁ TRONG CÁC Ô ĐỎ (ERROR) & XANH (INFO) */
    div[data-testid="stAlert"] *, div[data-testid="stAlert"] p, div[data-testid="stAlert"] span {{
        color: {alert_c} !important; 
    }}

    /* FORMAT THẺ CARD CHỈ SỐ */
    .spotify-card {{
        background-color: {bg_sec} !important;
        border: 1px solid {border_c} !important;
        border-radius: 12px; padding: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }}

    /* BẢO VỆ CÁC MÀU XANH ĐỎ TRONG BẢNG XẾP HẠNG KHÔNG BỊ ĐÈ */
    .text-success, .text-success * {{ color: #1DB954 !important; }}
    .text-danger, .text-danger * {{ color: #E22134 !important; }}
    .badge-green {{ background-color: rgba(29, 185, 84, 0.15) !important; color: #1DB954 !important; }}
    .badge-red {{ background-color: rgba(226, 33, 52, 0.15) !important; color: #E22134 !important; }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# KHỞI TẠO DATA
# ==========================================
FILE_DU_LIEU = "spotify_master_data.csv" 
FILE_KQ_THANG = "spotify_monthly_data.csv" 
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
        
    if not os.path.exists(FILE_KQ_THANG): pd.DataFrame(columns=["Năm", "Tháng", "Kênh_Spotify", "Doanh_Thu_USD", "Luot_Play", "So_Gio_Nghe", "So_Tap_Upload", "Bat_Kiem_Tien", "Thoi_Gian_Nhap"]).to_csv(FILE_KQ_THANG, index=False)

khoi_tao_he_thong_db()
df = pd.read_csv(FILE_DU_LIEU)
df_thang_chot = pd.read_csv(FILE_KQ_THANG)
df_kpi = pd.read_csv(FILE_KPI)

danh_sach_kenh_master = list(set(df["Kênh_Spotify"].dropna().unique()) | set(df_kpi["Kênh_Spotify"].dropna().unique()) | set(df_thang_chot["Kênh_Spotify"].dropna().unique()))
danh_sach_kenh_master.sort()

def lay_trang_thai_kiem_tien(ten_kenh):
    kpi_match = df_kpi[df_kpi["Kênh_Spotify"] == ten_kenh]
    if not kpi_match.empty: return bool(kpi_match.iloc[-1]["Bat_Kiem_Tien"])
    df_match = df[df["Kênh_Spotify"] == ten_kenh]
    if not df_match.empty: return bool(df_match.iloc[-1]["Bat_Kiem_Tien"])
    return False

def make_card(label, value, pct=None):
    if pct is not None:
        badge_html = f"<span class='{'badge-green' if pct >= 100 else 'badge-red'}'>{pct:.1f}% KPI</span>"
    else:
        badge_html = ""
    return f"""
    <div class="spotify-card">
        <div class="spotify-label">{label}</div>
        <div class="spotify-value">{value}</div>
        <div>{badge_html}</div>
    </div>
    """

def tao_sheet_tong_hop(thang_chon, chiso_chon):
    df_kq = pd.read_csv(FILE_DU_LIEU)
    df_kpi = pd.read_csv(FILE_KPI)
    df_kq_thang = pd.read_csv(FILE_KQ_THANG)
    
    # Từ điển ánh xạ Chỉ số sang tên Cột trong Database
    map_col = {
        "Doanh Thu": {"kq": "Doanh_Thu_USD", "kpi": "KPI_Doanh_Thu"},
        "Lượt Play": {"kq": "Luot_Play", "kpi": "KPI_Luot_Play"},
        "Giờ Nghe": {"kq": "So_Gio_Nghe", "kpi": "KPI_So_Gio"},
        "Số Tập Upload": {"kq": "So_Tap_Upload", "kpi": "KPI_So_Tap"}
    }
    
    col_kq = map_col[chiso_chon]["kq"]
    col_kpi = map_col[chiso_chon]["kpi"]
    
    kpi_thang = df_kpi[df_kpi["Tháng"] == thang_chon]
    master = pd.DataFrame(danh_sach_kenh_master, columns=["Kênh_Spotify"])
    master = master.merge(kpi_thang[["Kênh_Spotify", col_kpi, "So_Tuan"]], on="Kênh_Spotify", how="left")
    master[col_kpi] = master[col_kpi].fillna(0)
    
    # Kết quả Tổng hợp (Của các tuần)
    thang_kq_sum = df_kq[df_kq["Tháng"] == thang_chon].groupby("Kênh_Spotify")[col_kq].sum().reset_index()
    thang_kq_sum.rename(columns={col_kq: "Kết quả tổng"}, inplace=True)
    master = master.merge(thang_kq_sum, on="Kênh_Spotify", how="left")
    master["Kết quả tổng"] = master["Kết quả tổng"].fillna(0)
    master["% Hoàn thành"] = (master["Kết quả tổng"] / master[col_kpi] * 100).replace([float('inf'), -float('inf')], 0).fillna(0)
    
    # Kết quả chốt Final
    chot_thang = df_kq_thang[df_kq_thang["Tháng"] == thang_chon][["Kênh_Spotify", col_kq]]
    chot_thang.rename(columns={col_kq: "Kết quả tháng"}, inplace=True)
    chot_thang = chot_thang.groupby("Kênh_Spotify")["Kết quả tháng"].sum().reset_index() 
    master = master.merge(chot_thang, on="Kênh_Spotify", how="left")
    master["Kết quả tháng"] = master["Kết quả tháng"].fillna(0)
    master["% Hoàn thành tháng"] = (master["Kết quả tháng"] / master[col_kpi] * 100).replace([float('inf'), -float('inf')], 0).fillna(0)
    
    # Trải chi tiết từng Tuần
    tuan_trong_thang = sorted([t for t in df_kq[df_kq["Tháng"] == thang_chon]["Tuần"].unique()])
    for tuan in tuan_trong_thang:
        master[f"{tuan}_Target"] = (master[col_kpi] / master["So_Tuan"]).fillna(0)
        kq_tuan = df_kq[(df_kq["Tháng"] == thang_chon) & (df_kq["Tuần"] == tuan)][["Kênh_Spotify", col_kq]]
        master = master.merge(kq_tuan.rename(columns={col_kq: f"{tuan}_Actual"}), on="Kênh_Spotify", how="left")
        master[f"{tuan}_Actual"] = master[f"{tuan}_Actual"].fillna(0)
        master[f"{tuan}_%"] = (master[f"{tuan}_Actual"] / master[f"{tuan}_Target"] * 100).replace([float('inf'), -float('inf')], 0).fillna(0)
        
    return master, col_kpi

st.title("🎧 TRUNG TÂM QUẢN TRỊ HIỆU SUẤT SPOTIFY")
st.markdown("---")

tab_dashboard, tab_master, tab_nhap_kpi, tab_nhap_kq, tab_xoa_data = st.tabs([
    "📊 Dashboard", "📑 Sheet Tổng Hợp", "🎯 Nhập Mục Tiêu", "📥 Nhập Kết Quả", "🛠️ Quản Lý"
])

# ==========================================
# TAB 1: SHEET TỔNG HỢP
# ==========================================
with tab_master:
    st.header("📑 Sheet Tổng Hợp Hiệu Suất")
    
    col1, col2 = st.columns(2)
    with col1:
        chon_thang = st.selectbox("📅 Chọn tháng:", [f"Tháng {i}" for i in range(1, 13)])
    with col2:
        chiso_sheet = st.selectbox("🛠️ Chọn chỉ số hiển thị:", ["Doanh Thu", "Lượt Play", "Giờ Nghe", "Số Tập Upload"])
    
    # Cấp dữ liệu động
    df_raw, col_kpi_name = tao_sheet_tong_hop(chon_thang, chiso_sheet)
    df_display = df_raw.copy()
    
    # Đổi tên cột chuẩn xác
    rename_map = { "Kênh_Spotify": "Kênh", col_kpi_name: f"KPI {chiso_sheet}" }
    for col in df_display.columns:
        if "Tuần" in col:
            if "_Target" in col: rename_map[col] = col.replace("Tuần ", "KPI Tuần ").replace("_Target", "")
            elif "_Actual" in col: rename_map[col] = col.replace("Tuần ", "Kết quả Tuần ").replace("_Actual", "")
            elif "_%" in col: rename_map[col] = col.replace("Tuần ", "% Tuần ").replace("_%", "")
    
    df_display = df_display.rename(columns=rename_map)
    
    # Sắp xếp hiển thị
    cols = ["Kênh", f"KPI {chiso_sheet}", "Kết quả tổng", "% Hoàn thành", "Kết quả tháng", "% Hoàn thành tháng"]
    tuan_cols = [c for c in df_display.columns if "Tuần" in c]
    df_display = df_display[cols + tuan_cols]
    df_display.insert(0, "STT", range(1, len(df_display) + 1))

    df_clean = df_display.copy()
    cols_to_drop = ["So_Tuan", "index"]
    for col in cols_to_drop:
        if col in df_clean.columns: df_clean = df_clean.drop(columns=[col])

    # Dynamic Formatting (Định dạng Đô la, Giờ nghe, hay Số thập phân tự động nhảy)
    format_dict = {
        "Doanh Thu": "${:,.0f}",
        "Lượt Play": "{:,.0f}",
        "Giờ Nghe": "{:,.0f}h",
        "Số Tập Upload": "{:,.0f}"
    }
    val_fmt = format_dict[chiso_sheet]

    st.dataframe(
        df_clean.style
        .format({
            f"KPI {chiso_sheet}": val_fmt, 
            "Kết quả tổng": val_fmt, 
            "% Hoàn thành": "{:.0f}%",
            "Kết quả tháng": val_fmt, 
            "% Hoàn thành tháng": "{:.0f}%",
            **{col: val_fmt for col in df_clean.columns if "KPI Tuần" in col},
            **{col: val_fmt for col in df_clean.columns if "Kết quả Tuần" in col},
            **{col: "{:.0f}%" for col in df_clean.columns if "% Tuần" in col}
        }).hide(axis="index"), 
        use_container_width=True
    )

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
        
    kpi_cu = df_kpi[(df_kpi["Tháng"] == thang_kpi) & (df_kpi["Kênh_Spotify"] == kenh_kpi)]
    if not kpi_cu.empty and kenh_kpi:
        v_w = int(kpi_cu.iloc[0]["So_Tuan"]) if pd.notna(kpi_cu.iloc[0]["So_Tuan"]) else 4
        v_dt = float(kpi_cu.iloc[0]["KPI_Doanh_Thu"])
        v_p = int(kpi_cu.iloc[0]["KPI_Luot_Play"])
        v_g = float(kpi_cu.iloc[0]["KPI_So_Gio"])
        v_t = int(kpi_cu.iloc[0]["KPI_So_Tap"])
        st.info(f"💡 Đang hiển thị Mục tiêu cũ của **{kenh_kpi}**. Bạn có thể sửa số và bấm Lưu để GHI ĐÈ.")
    else:
        v_w, v_dt, v_p, v_g, v_t = 4, 0.0, 0, 0.0, 0
        
    with col_kpi1: so_tuan_kpi = st.number_input("Số tuần của tháng này:", min_value=1, max_value=5, value=v_w, key=f"w_{thang_kpi}_{kenh_kpi}_{rk_kpi}")
    with col_kpi2:
        dt_kpi = st.number_input("Mục tiêu Doanh thu Tháng ($):", min_value=0.0, step=100.0, value=v_dt, key=f"dt_{thang_kpi}_{kenh_kpi}_{rk_kpi}")
        play_kpi = st.number_input("Mục tiêu Lượt Play Tháng:", min_value=0, step=10000, value=v_p, key=f"p_{thang_kpi}_{kenh_kpi}_{rk_kpi}")
    with col_kpi3:
        gio_kpi = st.number_input("Mục tiêu Giờ nghe Tháng (h):", min_value=0.0, step=100.0, value=v_g, key=f"g_{thang_kpi}_{kenh_kpi}_{rk_kpi}")
        tap_kpi = st.number_input("Mục tiêu Số tập Upload Tháng:", min_value=0, step=1, value=v_t, key=f"tap_{thang_kpi}_{kenh_kpi}_{rk_kpi}")
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Lưu KPI & Cấu Hình Kênh", type="primary", use_container_width=True):
        if not kenh_kpi: st.error("⚠️ Vui lòng nhập Tên Kênh!")
        else:
            df_kpi_filtered = df_kpi[~((df_kpi["Tháng"] == thang_kpi) & (df_kpi["Kênh_Spotify"] == kenh_kpi))]
            kpi_moi = pd.DataFrame([{ "Tháng": thang_kpi, "Kênh_Spotify": kenh_kpi, "KPI_Doanh_Thu": float(dt_kpi), "KPI_Luot_Play": int(play_kpi), "KPI_So_Gio": float(gio_kpi), "KPI_So_Tap": int(tap_kpi), "So_Tuan": int(so_tuan_kpi), "Bat_Kiem_Tien": bkt_kpi }])
            pd.concat([df_kpi_filtered, kpi_moi], ignore_index=True).to_csv(FILE_KPI, index=False)
            st.session_state.toast_msg = (f"🎯 Đã lưu KPI cho kênh {kenh_kpi} vào {thang_kpi}!", "🎯")
            st.session_state.rk_kpi += 1; st.rerun()

# ==========================================
# TAB 3: NHẬP KẾT QUẢ 
# ==========================================
with tab_nhap_kq:
    loai_nhap_kq = st.radio("🛠️ Chọn chế độ nhập liệu:", ["📥 Nhập Kết Quả Tuần", "📅 Kết Quả Tháng (Final)"], horizontal=True, label_visibility="collapsed")
    st.markdown("---")
    
    if loai_nhap_kq == "📥 Nhập Kết Quả Tuần":
        st.subheader("Cập Nhật Kết Quả Vận Hành Tuần")
        rk = st.session_state.rk_kq
        col1, col2, col3 = st.columns(3)
        with col1:
            thang_kq = st.selectbox("Tháng Báo Cáo:", [f"Tháng {i}" for i in range(1, 13)], key=f"t_kq_{rk}")
            tuan_kq = st.selectbox("Tuần Báo Cáo:", [f"Tuần {i}" for i in range(1, 53)], key=f"w_kq_{rk}")
            if not danh_sach_kenh_master:
                st.warning("⚠️ Chưa có kênh nào! Hãy sang tab 'Nhập Mục Tiêu' để tạo kênh trước.")
                kenh_kq = ""
            else:
                kenh_kq = st.selectbox("Chọn Kênh Báo Cáo:", danh_sach_kenh_master, key=f"c_kq_{rk}")
                trang_thai_bkt_kq = lay_trang_thai_kiem_tien(kenh_kq)

        kq_cu = df[(df["Tháng"] == thang_kq) & (df["Tuần"] == tuan_kq) & (df["Kênh_Spotify"] == kenh_kq)]
        if not kq_cu.empty and kenh_kq:
            v_dt_kq, v_p_kq, v_g_kq, v_t_kq = float(kq_cu.iloc[0]["Doanh_Thu_USD"]), int(kq_cu.iloc[0]["Luot_Play"]), float(kq_cu.iloc[0]["So_Gio_Nghe"]), int(kq_cu.iloc[0]["So_Tap_Upload"])
            st.info(f"💡 Đã có dữ liệu của **{kenh_kq}** ({tuan_kq}). Sửa và lưu để GHI ĐÈ.")
        else:
            v_dt_kq, v_p_kq, v_g_kq, v_t_kq = 0.0, 0, 0.0, 0

        with col2:
            dt_kq = st.number_input("Doanh thu Tuần (USD):", min_value=0.0, step=1.0, value=v_dt_kq, key=f"dt_kq_{rk}")
            play_kq = st.number_input("Lượt Play Tuần:", min_value=0, step=100, value=v_p_kq, key=f"p_kq_{rk}")
        with col3:
            gio_kq = st.number_input("Giờ nghe Tuần (h):", min_value=0.0, step=10.0, value=v_g_kq, key=f"g_kq_{rk}")
            tap_kq = st.number_input("Số tập Upload Tuần:", min_value=0, step=1, value=v_t_kq, key=f"tap_kq_{rk}")
            
        if st.button("Lưu Kết Quả Tuần", type="primary", use_container_width=True):
            if not kenh_kq: st.error("⚠️ Vui lòng chọn Tên Kênh!")
            else:
                df_kq_filtered = df[~((df["Tuần"] == tuan_kq) & (df["Kênh_Spotify"] == kenh_kq) & (df["Tháng"] == thang_kq))]
                du_lieu_moi = pd.DataFrame([{ "Tháng": thang_kq, "Tuần": tuan_kq, "Kênh_Spotify": kenh_kq, "Doanh_Thu_USD": float(dt_kq), "Luot_Play": int(play_kq), "So_Gio_Nghe": float(gio_kq), "So_Tap_Upload": int(tap_kq), "Bat_Kiem_Tien": trang_thai_bkt_kq, "Thoi_Gian_Nhap": datetime.now().strftime("%Y-%m-%d %H:%M:%S") }])
                pd.concat([df_kq_filtered, du_lieu_moi], ignore_index=True).to_csv(FILE_DU_LIEU, index=False)
                st.session_state.toast_msg = (f"✅ Đã lưu kết quả TUẦN cho {kenh_kq}!", "✅")
                st.session_state.rk_kq += 1; st.rerun()

    else:
        # NHẬP KẾT QUẢ THÁNG (FINAL)
        st.subheader("Cập Nhật Số Liệu Tháng (Thực Tế Final)")
        rkm = st.session_state.rk_kq_thang
        colm1, colm2, colm3 = st.columns(3)
        with colm1:
            nam_kq_m = st.selectbox("Năm Báo Cáo:", [2026, 2027], key=f"nam_m_{rkm}")
            thang_kq_m = st.selectbox("Tháng Báo Cáo:", [f"Tháng {i}" for i in range(1, 13)], key=f"t_kq_m_{rkm}")
            if not danh_sach_kenh_master:
                st.warning("⚠️ Chưa có kênh nào!")
                kenh_kq_m = ""
            else:
                kenh_kq_m = st.selectbox("Chọn Kênh Báo Cáo:", danh_sach_kenh_master, key=f"c_kq_m_{rkm}")
                trang_thai_bkt_m = lay_trang_thai_kiem_tien(kenh_kq_m)

        kq_m_cu = df_thang_chot[(df_thang_chot["Năm"] == nam_kq_m) & (df_thang_chot["Tháng"] == thang_kq_m) & (df_thang_chot["Kênh_Spotify"] == kenh_kq_m)]
        if not kq_m_cu.empty and kenh_kq_m:
            v_dt_m, v_p_m, v_g_m, v_t_m = float(kq_m_cu.iloc[0]["Doanh_Thu_USD"]), int(kq_m_cu.iloc[0]["Luot_Play"]), float(kq_m_cu.iloc[0]["So_Gio_Nghe"]), int(kq_m_cu.iloc[0]["So_Tap_Upload"])
            st.info(f"💡 Đã có dữ liệu chốt THÁNG của **{kenh_kq_m}**. Sửa và lưu để GHI ĐÈ.")
        else:
            v_dt_m, v_p_m, v_g_m, v_t_m = 0.0, 0, 0.0, 0

        with colm2:
            dt_kq_m = st.number_input("Chốt Doanh thu Tháng (USD):", min_value=0.0, step=10.0, value=v_dt_m, key=f"dt_m_{rkm}")
            play_kq_m = st.number_input("Chốt Lượt Play Tháng:", min_value=0, step=1000, value=v_p_m, key=f"p_m_{rkm}")
        with colm3:
            gio_kq_m = st.number_input("Chốt Giờ nghe Tháng (h):", min_value=0.0, step=10.0, value=v_g_m, key=f"g_m_{rkm}")
            tap_kq_m = st.number_input("Chốt Số tập Upload Tháng:", min_value=0, step=1, value=v_t_m, key=f"tap_m_{rkm}")
            
        if st.button("Lưu Chốt Số Tháng", type="primary", use_container_width=True):
            if not kenh_kq_m: st.error("⚠️ Vui lòng chọn Tên Kênh!")
            else:
                df_kq_m_filter = df_thang_chot[~((df_thang_chot["Năm"] == nam_kq_m) & (df_thang_chot["Tháng"] == thang_kq_m) & (df_thang_chot["Kênh_Spotify"] == kenh_kq_m))]
                du_lieu_moi_m = pd.DataFrame([{ "Năm": nam_kq_m, "Tháng": thang_kq_m, "Kênh_Spotify": kenh_kq_m, "Doanh_Thu_USD": float(dt_kq_m), "Luot_Play": int(play_kq_m), "So_Gio_Nghe": float(gio_kq_m), "So_Tap_Upload": int(tap_kq_m), "Bat_Kiem_Tien": trang_thai_bkt_m, "Thoi_Gian_Nhap": datetime.now().strftime("%Y-%m-%d %H:%M:%S") }])
                pd.concat([df_kq_m_filter, du_lieu_moi_m], ignore_index=True).to_csv(FILE_KQ_THANG, index=False)
                st.session_state.toast_msg = (f"✅ Đã lưu CHỐT THÁNG cho {kenh_kq_m}!", "✅")
                st.session_state.rk_kq_thang += 1; st.rerun()

# ==========================================
# TAB 5: QUẢN LÝ DỮ LIỆU
# ==========================================
with tab_xoa_data:
    if not danh_sach_kenh_master: st.info("Hệ thống chưa có dữ liệu kênh nào.")
    else:
        st.subheader("🛠️ Chỉnh Sửa Thông Tin Kênh Toàn Cục")
        kenh_can_sua = st.selectbox("1. Chọn Kênh cần đổi tên / bật kiếm tiền:", danh_sach_kenh_master, key="edit_k")
        col_e1, col_e2 = st.columns(2)
        with col_e1: ten_kenh_moi = st.text_input("Tên kênh mới:", value=kenh_can_sua, key="edit_name").strip()
        with col_e2: 
            st.markdown("<br>", unsafe_allow_html=True)
            bkt_moi = st.checkbox("✅ Kênh đã bật kiếm tiền", value=lay_trang_thai_kiem_tien(kenh_can_sua), key="edit_bkt")
            
        if st.button("💾 Lưu Thay Đổi Thông Tin", type="primary"):
            if not ten_kenh_moi: st.error("⚠️ Tên kênh không được để trống!")
            elif ten_kenh_moi != kenh_can_sua and ten_kenh_moi in danh_sach_kenh_master: st.error("⚠️ Tên kênh đã tồn tại!")
            else:
                for d_file, d_df in [(FILE_DU_LIEU, df), (FILE_KPI, df_kpi), (FILE_KQ_THANG, df_thang_chot)]:
                    d_df.loc[d_df["Kênh_Spotify"] == kenh_can_sua, "Kênh_Spotify"] = ten_kenh_moi
                    d_df.loc[d_df["Kênh_Spotify"] == ten_kenh_moi, "Bat_Kiem_Tien"] = bkt_moi
                    d_df.to_csv(d_file, index=False)
                st.session_state.toast_msg = (f"✅ Đã cập nhật kênh {ten_kenh_moi}!", "✅")
                st.rerun()

# ==========================================
# TAB 1: DASHBOARD CHÍNH 
# ==========================================
with tab_dashboard:
    loai_dashboard = st.radio("📊 Chọn cấp độ báo cáo:", ["📅 Báo cáo Tuần (Tiến độ)", "📆 Báo cáo Tháng (Final)"], horizontal=True, label_visibility="collapsed")
    st.markdown("---")
    
    if loai_dashboard == "📅 Báo cáo Tuần (Tiến độ)":
        if df.empty: st.info("Hệ thống chưa có dữ liệu kết quả TUẦN nào.")
        else:
            col_loc1, col_loc_tuan, col_loc2, col_loc3 = st.columns([1.2, 1.2, 2, 1.2])
            with col_loc1:
                thang_hien_co = list(df["Tháng"].unique())
                thang_chon_db = st.selectbox("📅 Lọc theo Tháng:", ["Tất cả các tháng"] + thang_hien_co, index=(len(thang_hien_co)), key="loc_thang_w")
            
            df_thang = df if thang_chon_db == "Tất cả các tháng" else df[df["Tháng"] == thang_chon_db]
            with col_loc_tuan:
                tuan_hien_co = list(df_thang["Tuần"].unique()); tuan_hien_co.sort(key=lambda x: int(x.replace("Tuần ", "")) if "Tuần " in x else 0)
                tuan_chon = st.multiselect("📅 Lọc theo Tuần:", options=tuan_hien_co, default=tuan_hien_co, key="loc_tuan_w")

            danh_sach_kenh_hien_co = list(df_thang["Kênh_Spotify"].unique())
            with col_loc2: kenh_duoc_chon = st.multiselect("🎧 Lọc theo Kênh:", options=danh_sach_kenh_hien_co, default=danh_sach_kenh_hien_co, key="loc_kenh_w")
            with col_loc3: loc_bkt = st.selectbox("🚦 Kiếm Tiền:", ["Tất cả", "Đã bật", "Chưa bật"], key="loc_bkt_w")
            
            kenh_hien_thi_cuoi_cung = [k for k in kenh_duoc_chon if (loc_bkt == "Tất cả") or (loc_bkt == "Đã bật" and lay_trang_thai_kiem_tien(k)) or (loc_bkt == "Chưa bật" and not lay_trang_thai_kiem_tien(k))]

            if not kenh_hien_thi_cuoi_cung or not tuan_chon: st.warning(f"⚠️ Vui lòng chọn ít nhất 1 Kênh và 1 Tuần!")
            else:
                df_final = df_thang[df_thang["Kênh_Spotify"].isin(kenh_hien_thi_cuoi_cung) & df_thang["Tuần"].isin(tuan_chon)]
                df_kpi_filter = df_kpi[df_kpi["Kênh_Spotify"].isin(kenh_hien_thi_cuoi_cung)]
                if thang_chon_db != "Tất cả các tháng": df_kpi_filter = df_kpi_filter[df_kpi_filter["Tháng"] == thang_chon_db]
                    
                so_tuan_chon = len(tuan_chon)
                target_dt = (df_kpi_filter["KPI_Doanh_Thu"] / df_kpi_filter["So_Tuan"].fillna(4)).sum() * so_tuan_chon if len(tuan_chon) < len(tuan_hien_co) else df_kpi_filter["KPI_Doanh_Thu"].sum()
                target_play = (df_kpi_filter["KPI_Luot_Play"] / df_kpi_filter["So_Tuan"].fillna(4)).sum() * so_tuan_chon if len(tuan_chon) < len(tuan_hien_co) else df_kpi_filter["KPI_Luot_Play"].sum()

                st.markdown("### 🏆 1. Chỉ Số Tuần Tổng Quan")
                dt_pct = (df_final['Doanh_Thu_USD'].sum() / target_dt * 100) if target_dt > 0 else 0
                play_pct = (df_final['Luot_Play'].sum() / target_play * 100) if target_play > 0 else 0
                
                sc1, sc2, sc3, sc4 = st.columns(4)
                sc1.markdown(make_card("🏢 Tổng Kênh", len(kenh_hien_thi_cuoi_cung)), unsafe_allow_html=True)
                sc2.markdown(make_card("💸 Đã Bật KT", sum([1 for k in kenh_hien_thi_cuoi_cung if lay_trang_thai_kiem_tien(k)])), unsafe_allow_html=True)
                sc3.markdown(make_card("💰 Doanh Thu", f"${df_final['Doanh_Thu_USD'].sum():,.0f}", dt_pct), unsafe_allow_html=True)
                sc4.markdown(make_card("▶️ Lượt Play", f"{df_final['Luot_Play'].sum():,.0f}", play_pct), unsafe_allow_html=True)
                
                st.markdown("### 🚀 2. Phân Tích Tiến Độ Các Tuần")
                chiso_chon = st.radio("🛠️ Chọn chỉ số:", ["Doanh Thu", "Lượt Play", "Giờ Nghe"], horizontal=True, key="cs_w")
                map_chiso = { "Doanh Thu": {"kq": "Doanh_Thu_USD", "kpi": "KPI_Doanh_Thu", "format": "$"}, "Lượt Play": {"kq": "Luot_Play", "kpi": "KPI_Luot_Play", "format": ""}, "Giờ Nghe": {"kq": "So_Gio_Nghe", "kpi": "KPI_So_Gio", "format": "h"} }
                cot_kq, cot_kpi, kieu_format = map_chiso[chiso_chon]["kq"], map_chiso[chiso_chon]["kpi"], map_chiso[chiso_chon]["format"]

                df_kpi_filter["Muc_Tieu_Tuan_Hien_Tai"] = df_kpi_filter[cot_kpi].fillna(0) / df_kpi_filter["So_Tuan"].fillna(4)
                
                df_trend = df_final.groupby("Tuần")[cot_kq].sum().reset_index()
                df_trend["Đường_Mục_Tiêu"] = round(df_kpi_filter["Muc_Tieu_Tuan_Hien_Tai"].sum(), 2)
                
                fig_vs = go.Figure()
                fig_vs.add_trace(go.Scatter(x=df_trend["Tuần"], y=df_trend[cot_kq], mode='lines+markers+text', name='Kết Quả', textposition="top center", line=dict(color='#1DB954', width=3)))
                fig_vs.add_trace(go.Scatter(x=df_trend["Tuần"], y=df_trend["Đường_Mục_Tiêu"], mode='lines+markers', name='Mục Tiêu', line=dict(color='#E22134', width=3, dash='dash')))
                fig_vs.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=text_c))
                st.plotly_chart(fig_vs, use_container_width=True)

                # --- 🏅 3. BẢNG XẾP HẠNG TOP KÊNH (TUẦN - FORMAT V30) ---
                st.markdown("---")
                st.markdown(f"### 🏅 3. Bảng Xếp Hạng Kênh Theo {chiso_chon}")
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

                # --- 🍩 4. BIỂU ĐỒ DONUT (BÁO CÁO TUẦN) ---
                st.markdown("### 🍩 4. Phân Tích Cơ Cấu & Tỷ Trọng (Tuần)")
                col_sl1_w, col_sl2_w = st.columns(2)
                with col_sl1_w:
                    tieu_chi_map_w = {"Doanh thu": "Doanh_Thu_USD", "Lượt Play": "Luot_Play", "Giờ nghe": "So_Gio_Nghe"}
                    tieu_chi_chon_w = st.selectbox("Tiêu chí so sánh:", list(tieu_chi_map_w.keys()), key="tc_donut_w")
                    cot_tieu_chi_w = tieu_chi_map_w[tieu_chi_chon_w]
                with col_sl2_w:
                    kenh_all_w = df_final["Kênh_Spotify"].unique()
                    kenh_chon_w = st.multiselect("Chọn kênh:", options=kenh_all_w, default=kenh_all_w, key="kc_donut_w")

                df_pie_w = df_final[df_final["Kênh_Spotify"].isin(kenh_chon_w)]
                
                if df_pie_w.empty: st.info("Vui lòng chọn kênh để hiển thị biểu đồ.")
                else:
                    df_plot_w = df_pie_w.groupby("Kênh_Spotify")[cot_tieu_chi_w].sum().sort_values(ascending=False).reset_index()
                    palette = ['#2E7D32', '#4CAF50', '#81C784', '#A5D6A7', '#DCE775', '#E8F5E9']
                    colors = (palette * (len(df_plot_w) // len(palette) + 1))[:len(df_plot_w)]

                    fig_pie_w = px.pie(df_plot_w, values=cot_tieu_chi_w, names="Kênh_Spotify", hole=0.4, title=f"Tỷ Trọng theo {tieu_chi_chon_w}", color_discrete_sequence=colors)
                    fig_pie_w.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=True, legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5), font=dict(color=text_c))
                    fig_pie_w.update_traces(textinfo='percent', textfont_color="white", textfont_size=12, textposition='inside')
                    st.plotly_chart(fig_pie_w, use_container_width=True)

    else:
        # DASHBOARD THÁNG (FINAL)
        if df_thang_chot.empty: st.info("Hệ thống chưa có dữ liệu chốt THÁNG nào.")
        else:
            col_loc1_m, col_loc_thang_m, col_loc2_m, col_loc3_m = st.columns([1.2, 1.2, 2, 1.2])
            with col_loc1_m: nam_chon_m = st.selectbox("📅 Lọc theo Năm:", [2026, 2027], key="loc_nam_m")
            
            df_nam_m = df_thang_chot[df_thang_chot["Năm"] == nam_chon_m]
            
            with col_loc_thang_m:
                thang_hien_co_m = list(df_nam_m["Tháng"].unique()); thang_hien_co_m.sort(key=lambda x: int(x.replace("Tháng ", "")) if "Tháng " in x else 0)
                thang_chon_m = st.multiselect("📅 Lọc theo Tháng:", options=thang_hien_co_m, default=thang_hien_co_m, key="loc_thang_m")

            danh_sach_kenh_hien_co_m = list(df_nam_m["Kênh_Spotify"].unique())
            with col_loc2_m: kenh_duoc_chon_m = st.multiselect("🎧 Lọc theo Kênh:", options=danh_sach_kenh_hien_co_m, default=danh_sach_kenh_hien_co_m, key="loc_kenh_m")
            with col_loc3_m: loc_bkt_m = st.selectbox("🚦 Kiếm Tiền:", ["Tất cả", "Đã bật", "Chưa bật"], key="loc_bkt_m")
            
            kenh_hien_thi_m = [k for k in kenh_duoc_chon_m if (loc_bkt_m == "Tất cả") or (loc_bkt_m == "Đã bật" and lay_trang_thai_kiem_tien(k)) or (loc_bkt_m == "Chưa bật" and not lay_trang_thai_kiem_tien(k))]

            if not kenh_hien_thi_m or not thang_chon_m: st.warning(f"⚠️ Vui lòng chọn ít nhất 1 Kênh và 1 Tháng!")
            else:
                df_final_m = df_nam_m[df_nam_m["Kênh_Spotify"].isin(kenh_hien_thi_m) & df_nam_m["Tháng"].isin(thang_chon_m)]
                df_kpi_filter_m = df_kpi[df_kpi["Kênh_Spotify"].isin(kenh_hien_thi_m) & df_kpi["Tháng"].isin(thang_chon_m)]
                    
                target_dt_m = df_kpi_filter_m["KPI_Doanh_Thu"].sum()
                target_play_m = df_kpi_filter_m["KPI_Luot_Play"].sum()

                st.markdown("### 🏆 1. Chỉ Số Tháng Tổng Quan")
                dt_pct_m = (df_final_m['Doanh_Thu_USD'].sum() / target_dt_m * 100) if target_dt_m > 0 else 0
                play_pct_m = (df_final_m['Luot_Play'].sum() / target_play_m * 100) if target_play_m > 0 else 0
                
                scm1, scm2, scm3, scm4 = st.columns(4)
                scm1.markdown(make_card("🏢 Tổng Kênh", len(kenh_hien_thi_m)), unsafe_allow_html=True)
                scm2.markdown(make_card("💸 Đã Bật KT", sum([1 for k in kenh_hien_thi_m if lay_trang_thai_kiem_tien(k)])), unsafe_allow_html=True)
                scm3.markdown(make_card("💰 Doanh Thu Tháng", f"${df_final_m['Doanh_Thu_USD'].sum():,.0f}", dt_pct_m), unsafe_allow_html=True)
                scm4.markdown(make_card("▶️ Lượt Play Tháng", f"{df_final_m['Luot_Play'].sum():,.0f}", play_pct_m), unsafe_allow_html=True)
                
                st.markdown("### 🚀 2. Phân Tích Tiến Độ Các Tháng")
                chiso_chon_m = st.radio("🛠️ Chọn chỉ số:", ["Doanh Thu", "Lượt Play", "Giờ Nghe"], horizontal=True, key="cs_m")
                map_chiso_m = { "Doanh Thu": {"kq": "Doanh_Thu_USD", "kpi": "KPI_Doanh_Thu"}, "Lượt Play": {"kq": "Luot_Play", "kpi": "KPI_Luot_Play"}, "Giờ Nghe": {"kq": "So_Gio_Nghe", "kpi": "KPI_So_Gio"} }
                cot_kq_m, cot_kpi_m = map_chiso_m[chiso_chon_m]["kq"], map_chiso_m[chiso_chon_m]["kpi"]
                
                df_trend_m = df_final_m.groupby("Tháng")[cot_kq_m].sum().reset_index()
                df_trend_m["Sort"] = df_trend_m["Tháng"].apply(lambda x: int(x.replace("Tháng ", "")))
                df_trend_m = df_trend_m.sort_values(by="Sort").drop(columns=["Sort"])
                
                df_kpi_trend = df_kpi_filter_m.groupby("Tháng")[cot_kpi_m].sum().reset_index()
                df_trend_m = df_trend_m.merge(df_kpi_trend, on="Tháng", how="left")
                
                fig_vs_m = go.Figure()
                fig_vs_m.add_trace(go.Scatter(x=df_trend_m["Tháng"], y=df_trend_m[cot_kq_m], mode='lines+markers+text', name='Kết Quả Tháng', line=dict(color='#1DB954', width=3)))
                fig_vs_m.add_trace(go.Scatter(x=df_trend_m["Tháng"], y=df_trend_m[cot_kpi_m], mode='lines+markers', name='Mục Tiêu Tháng', line=dict(color='#E22134', width=3, dash='dash')))
                fig_vs_m.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                fig_vs_m.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=text_c))
                st.plotly_chart(fig_vs_m, use_container_width=True)

                # --- 🏅 3. BẢNG XẾP HẠNG TOP KÊNH (THÁNG FINAL - FORMAT V30) ---
                st.markdown("---")
                st.markdown(f"### 🏅 3. Bảng Xếp Hạng Kênh Theo {chiso_chon_m} (Tháng Final)")
                thang_co_data = list(df_final_m["Tháng"].unique()); thang_co_data.sort(key=lambda x: int(x.replace("Tháng ", "")) if "Tháng " in x else 0)

                if not thang_co_data: st.info("Chưa có dữ liệu tháng để xếp hạng.")
                else:
                    thang_chon_rank_m = st.selectbox("📌 Chọn thời gian để xếp hạng:", ["Tất cả các tháng"] + thang_co_data, key="loc_thang_rank_m")
                    df_rank_m = df_final_m.groupby("Kênh_Spotify")[cot_kq_m].sum().reset_index() if thang_chon_rank_m == "Tất cả các tháng" else df_final_m[df_final_m["Tháng"] == thang_chon_rank_m].groupby("Kênh_Spotify")[cot_kq_m].sum().reset_index()
                    df_rank_m = df_rank_m.sort_values(by=cot_kq_m, ascending=False).reset_index(drop=True); df_rank_m[cot_kq_m] = df_rank_m[cot_kq_m].round(2)

                    top_5_m = df_rank_m.head(5)
                    bot_5_m = pd.DataFrame(columns=["Kênh_Spotify", cot_kq_m]) if len(df_rank_m) <= 5 else df_rank_m[~df_rank_m["Kênh_Spotify"].isin(top_5_m["Kênh_Spotify"])].tail(5).sort_values(by=cot_kq_m, ascending=True)

                    def fmt_m(val): return f"${val:,.2f}" if chiso_chon_m == "Doanh Thu" else (f"{val:,.1f}h" if chiso_chon_m == "Giờ Nghe" else f"{val:,.0f}")
                    col_top_m, col_bot_m = st.columns(2)
                    with col_top_m:
                        st.success(f"🌟 **TOP 5 CAO NHẤT**")
                        for idx, row in top_5_m.iterrows(): st.markdown(f"**#{idx+1}. {row['Kênh_Spotify']}** ➔ <span class='text-success'>{fmt_m(row[cot_kq_m])}</span>", unsafe_allow_html=True); st.markdown("")
                    with col_bot_m:
                        st.error(f"⚠️ **TOP 5 THẤP NHẤT**")
                        for idx, row in bot_5_m.iterrows(): st.markdown(f"**🔻 {row['Kênh_Spotify']}** ➔ <span class='text-danger'>{fmt_m(row[cot_kq_m])}</span>", unsafe_allow_html=True); st.markdown("")

                # --- 🍩 4. BIỂU ĐỒ DONUT (BÁO CÁO THÁNG) ---
                st.markdown("### 🍩 4. Phân Tích Cơ Cấu & Tỷ Trọng (Tháng Final)")
                col_sl1_m, col_sl2_m = st.columns(2)
                with col_sl1_m:
                    tieu_chi_map_m = {"Doanh thu": "Doanh_Thu_USD", "Lượt Play": "Luot_Play", "Giờ nghe": "So_Gio_Nghe"}
                    tieu_chi_chon_m = st.selectbox("Tiêu chí so sánh:", list(tieu_chi_map_m.keys()), key="tc_donut_m")
                    cot_tieu_chi_m = tieu_chi_map_m[tieu_chi_chon_m]
                with col_sl2_m:
                    kenh_all_m = df_final_m["Kênh_Spotify"].unique()
                    kenh_chon_m = st.multiselect("Chọn kênh:", options=kenh_all_m, default=kenh_all_m, key="kc_donut_m")

                df_pie_m = df_final_m[df_final_m["Kênh_Spotify"].isin(kenh_chon_m)]
                
                if df_pie_m.empty: st.info("Vui lòng chọn kênh để hiển thị biểu đồ.")
                else:
                    df_plot_m = df_pie_m.groupby("Kênh_Spotify")[cot_tieu_chi_m].sum().sort_values(ascending=False).reset_index()
                    palette = ['#2E7D32', '#4CAF50', '#81C784', '#A5D6A7', '#DCE775', '#E8F5E9']
                    colors = (palette * (len(df_plot_m) // len(palette) + 1))[:len(df_plot_m)]

                    fig_pie_m = px.pie(df_plot_m, values=cot_tieu_chi_m, names="Kênh_Spotify", hole=0.4, title=f"Tỷ Trọng theo {tieu_chi_chon_m}", color_discrete_sequence=colors)
                    fig_pie_m.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=True, legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5), font=dict(color=text_c))
                    fig_pie_m.update_traces(textinfo='percent', textfont_color="white", textfont_size=12, textposition='inside')
                    st.plotly_chart(fig_pie_m, use_container_width=True)
