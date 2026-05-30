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
# 1. CẤU HÌNH GIAO DIỆN & CUSTOM THEME
# ==========================================
st.set_page_config(page_title="Spotify Performance Hub", layout="wide", page_icon="🎧", initial_sidebar_state="expanded")
 
# TẠO GIAO DIỆN TOP-RIGHT CHỨA TIÊU ĐỀ VÀ NÚT ĐỔI THEME
col_title, col_toggle = st.columns([8, 2])
with col_title:
    st.title("🎧 TRUNG TÂM QUẢN TRỊ HIỆU SUẤT SPOTIFY")
with col_toggle:
    st.write("") 
    theme_choice = st.radio("Giao diện:", ["☀️ Light Mode", "🌙 Dark Mode"], horizontal=True, label_visibility="collapsed")
 
is_light = "Light" in theme_choice

# Bơm màu theo công tắc của Boss
if is_light:
    bg_main = "#FFFFFF"
    bg_sec = "#F8F9FA"
    text_c = "#0C7A33"  # Xanh lá đậm
    border_c = "#E0E0E0"
    primary_bg = "#FFD1BA" 
    primary_text = "#111827" # Chữ đen xám cho dễ đọc
else:
    bg_main = "#0E1117"
    bg_sec = "#262730"
    text_c = "#FAFAFA"  # Trắng
    border_c = "rgba(29, 185, 84, 0.2)"
    primary_bg = "#E22134" 
    primary_text = "#FAFAFA"
 
# Bơm CSS ép tuyệt đối
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;600;800&display=swap');
    html, body, [class*="css"], [class*="st-"] {{ font-family: 'Lexend', sans-serif !important; }}
    
    /* GIAO DIỆN CHUNG */
    .stApp, [data-testid="stAppViewContainer"] {{ background-color: {'#FFFFFF' if is_light else '#0E1117'} !important; }}
    [data-testid="stSidebar"] {{ background-color: {'#F8F9FA' if is_light else '#262730'} !important; }}
    [data-testid="stToolbar"] {{ visibility: hidden !important; }}
    #MainMenu {{ display: none !important; }}
    
    /* CHỮ TOÀN CỤC */
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, label, li, span, div[data-testid="stMarkdownContainer"] {{
        color: {text_c} !important;
    }}

    /* NÚT & TAG */
    span[data-baseweb="tag"] {{ background-color: {primary_bg} !important; color: {primary_text} !important; }}
    span[data-baseweb="tag"] span {{ color: {primary_text} !important; }}
    div.stButton > button[kind="primary"] {{ background-color: {primary_bg} !important; color: {primary_text} !important; border: none !important; }}
    div.stButton > button[kind="primary"] * {{ color: {primary_text} !important; }}

    /* THẺ CARD */
    .spotify-card {{ background-color: {bg_sec} !important; border: 1px solid {border_c} !important; border-radius: 12px; padding: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }}
    
    /* MÀU XANH/ĐỎ CHỈ SỐ */
    .text-success, .text-success * {{ color: #1DB954 !important; }}
    .text-danger, .text-danger * {{ color: #E22134 !important; }}
    .badge-green {{ background-color: rgba(29, 185, 84, 0.15) !important; color: #1DB954 !important; }}
    .badge-red {{ background-color: rgba(226, 33, 52, 0.15) !important; color: #E22134 !important; }}

    /* ÉP MÀU CHỮ CỰC MẠNH CHO OPTION DROPDOWN */
    li[role="option"] div[data-testid="stMarkdownContainer"] p,
    li[role="option"] span {{
        color: {'#111827' if is_light else '#FAFAFA'} !important;
        -webkit-text-fill-color: {'#111827' if is_light else '#FAFAFA'} !important;
    }}
    li[role="option"] {{ background-color: {'#FFFFFF' if is_light else '#262730'} !important; }}
    li[role="option"]:hover {{ background-color: {'#E0E0E0' if is_light else '#404040'} !important; }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# KHỞI TẠO DATA
# ==========================================
FILE_DU_LIEU = "spotify_master_data.csv" 
FILE_KQ_THANG = "spotify_monthly_data.csv" 
FILE_KPI = "spotify_channel_kpi.csv" 

def khoi_tao_he_thong_db():
    # File Dữ Liệu Tuần
    if not os.path.exists(FILE_DU_LIEU): 
        pd.DataFrame(columns=["Tháng", "Tuần", "Kênh_Spotify", "Doanh_Thu_USD", "Luot_Play", "So_Gio_Nghe", "So_Tap_Upload", "Bat_Kiem_Tien", "Thoi_Gian_Nhap", "Link_Dan_Chung"]).to_csv(FILE_DU_LIEU, index=False)
    else:
        df_hien_tai = pd.read_csv(FILE_DU_LIEU)
        changed = False
        if "Bat_Kiem_Tien" not in df_hien_tai.columns: df_hien_tai["Bat_Kiem_Tien"] = False; changed = True
        if "Link_Dan_Chung" not in df_hien_tai.columns: df_hien_tai["Link_Dan_Chung"] = ""; changed = True
        if changed: df_hien_tai.to_csv(FILE_DU_LIEU, index=False)
            
    # File KPI
    if not os.path.exists(FILE_KPI): 
        pd.DataFrame(columns=["Tháng", "Kênh_Spotify", "KPI_Doanh_Thu", "KPI_Luot_Play", "KPI_So_Gio", "KPI_So_Tap", "So_Tuan", "Bat_Kiem_Tien"]).to_csv(FILE_KPI, index=False)
    else:
        df_kpi_hien_tai = pd.read_csv(FILE_KPI)
        if "Bat_Kiem_Tien" not in df_kpi_hien_tai.columns: df_kpi_hien_tai["Bat_Kiem_Tien"] = False; df_kpi_hien_tai.to_csv(FILE_KPI, index=False)
        
    # File Kết Quả Tháng
    if not os.path.exists(FILE_KQ_THANG): 
        pd.DataFrame(columns=["Năm", "Tháng", "Kênh_Spotify", "Doanh_Thu_USD", "Luot_Play", "So_Gio_Nghe", "So_Tap_Upload", "Bat_Kiem_Tien", "Thoi_Gian_Nhap", "Link_Dan_Chung"]).to_csv(FILE_KQ_THANG, index=False)
    else:
        df_thang_hien_tai = pd.read_csv(FILE_KQ_THANG)
        changed = False
        if "Bat_Kiem_Tien" not in df_thang_hien_tai.columns: df_thang_hien_tai["Bat_Kiem_Tien"] = False; changed = True
        if "Link_Dan_Chung" not in df_thang_hien_tai.columns: df_thang_hien_tai["Link_Dan_Chung"] = ""; changed = True
        if changed: df_thang_hien_tai.to_csv(FILE_KQ_THANG, index=False)

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
    if "Link_Dan_Chung" not in df_kq.columns: df_kq["Link_Dan_Chung"] = ""
        
    df_kpi = pd.read_csv(FILE_KPI)
    
    df_kq_thang = pd.read_csv(FILE_KQ_THANG)
    if "Link_Dan_Chung" not in df_kq_thang.columns: df_kq_thang["Link_Dan_Chung"] = ""
    
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
    
    thang_kq_sum = df_kq[df_kq["Tháng"] == thang_chon].groupby("Kênh_Spotify")[col_kq].sum().reset_index()
    thang_kq_sum.rename(columns={col_kq: "Kết quả tổng"}, inplace=True)
    master = master.merge(thang_kq_sum, on="Kênh_Spotify", how="left")
    master["Kết quả tổng"] = master["Kết quả tổng"].fillna(0)
    master["% Hoàn thành"] = (master["Kết quả tổng"] / master[col_kpi].replace(0, pd.NA) * 100).fillna(0).replace([float('inf'), -float('inf')], 0)
    
    # KẾT QUẢ THÁNG (CÓ LINK)
    chot_thang = df_kq_thang[df_kq_thang["Tháng"] == thang_chon][["Kênh_Spotify", col_kq, "Link_Dan_Chung"]]
    chot_thang = chot_thang.groupby("Kênh_Spotify").agg({
        col_kq: "sum",
        "Link_Dan_Chung": lambda x: " | ".join(x.dropna().astype(str).loc[x != ""])
    }).reset_index()
    chot_thang.rename(columns={col_kq: "Kết quả tháng", "Link_Dan_Chung": "Dẫn chứng tháng"}, inplace=True)
    master = master.merge(chot_thang, on="Kênh_Spotify", how="left")
    master["Kết quả tháng"] = master["Kết quả tháng"].fillna(0)
    master["% Hoàn thành tháng"] = (master["Kết quả tháng"] / master[col_kpi].replace(0, pd.NA) * 100).fillna(0).replace([float('inf'), -float('inf')], 0)
    
    # KẾT QUẢ TUẦN (CÓ LINK)
    tuan_trong_thang = sorted([t for t in df_kq[df_kq["Tháng"] == thang_chon]["Tuần"].unique()])
    for tuan in tuan_trong_thang:
        master[f"{tuan}_Target"] = (master[col_kpi] / master["So_Tuan"]).fillna(0)
        kq_tuan = df_kq[(df_kq["Tháng"] == thang_chon) & (df_kq["Tuần"] == tuan)][["Kênh_Spotify", col_kq, "Link_Dan_Chung"]]
        
        kq_tuan = kq_tuan.groupby("Kênh_Spotify").agg({
            col_kq: "sum",
            "Link_Dan_Chung": lambda x: " | ".join(x.dropna().astype(str).loc[x != ""])
        }).reset_index()
        kq_tuan.rename(columns={col_kq: f"{tuan}_Actual", "Link_Dan_Chung": f"{tuan}_Link"}, inplace=True)
        
        master = master.merge(kq_tuan, on="Kênh_Spotify", how="left")
        master[f"{tuan}_Actual"] = master[f"{tuan}_Actual"].fillna(0)
        master[f"{tuan}_%"] = (master[f"{tuan}_Actual"] / master[f"{tuan}_Target"].replace(0, pd.NA) * 100).fillna(0).replace([float('inf'), -float('inf')], 0)
        
    # ==========================================
    # ĐOẠN CODE THÊM DÒNG TỔNG CỘNG (TOTAL)
    # ==========================================
    if len(master) > 0:
        total_data = {}
        for col in master.columns:
            if col == "Kênh_Spotify":
                total_data[col] = "🔥 TỔNG CỘNG"
            else:
                total_data[col] = pd.to_numeric(master[col], errors='coerce').fillna(0).sum()
        
        val_kpi = total_data.get(col_kpi, 0)
        val_kq_tong = total_data.get("Kết quả tổng", 0)
        val_kq_thang = total_data.get("Kết quả tháng", 0)
        
        if val_kpi > 0:
            total_data["% Hoàn thành"] = (val_kq_tong / val_kpi) * 100
            total_data["% Hoàn thành tháng"] = (val_kq_thang / val_kpi) * 100
        else:
            total_data["% Hoàn thành"] = 0
            total_data["% Hoàn thành tháng"] = 0
            
        for tuan in tuan_trong_thang:
            c_actual = f"{tuan}_Actual"
            c_target = f"{tuan}_Target"
            c_pct = f"{tuan}_%"
            
            val_t_target = total_data.get(c_target, 0)
            val_t_actual = total_data.get(c_actual, 0)
            
            if val_t_target > 0:
                total_data[c_pct] = (val_t_actual / val_t_target) * 100
            else:
                total_data[c_pct] = 0
                
        # Link dòng tổng bằng gạch ngang
        if "Dẫn chứng tháng" in master.columns: total_data["Dẫn chứng tháng"] = "-"
        for tuan in tuan_trong_thang:
            if f"{tuan}_Link" in master.columns: total_data[f"{tuan}_Link"] = "-"
                
        df_total = pd.DataFrame([total_data])
        master = pd.concat([df_total, master], ignore_index=True)
        
    return master, col_kpi

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
            elif "_Link" in col: rename_map[col] = col.replace("Tuần ", "Dẫn chứng Tuần ").replace("_Link", "") 
    
    df_display = df_display.rename(columns=rename_map)
    
    cols = ["Kênh", f"KPI {chiso_sheet}", "Kết quả tổng", "% Hoàn thành", "Kết quả tháng", "% Hoàn thành tháng", "Dẫn chứng tháng"]
    cols = [c for c in cols if c in df_display.columns]
    tuan_cols = [c for c in df_display.columns if "Tuần" in c]
    df_display = df_display[cols + tuan_cols]
    
    df_clean = df_display.copy()
    cols_to_drop = ["So_Tuan", "index", "STT"]
    for col in cols_to_drop:
        if col in df_clean.columns: df_clean = df_clean.drop(columns=[col])

    format_dict = {
        "Doanh Thu": "${:,.0f}", "Lượt Play": "{:,.0f}",
        "Giờ Nghe": "{:,.0f}h", "Số Tập Upload": "{:,.0f}"
    }
    val_fmt = format_dict[chiso_sheet]

    # Render cột link hiển thị siêu đẹp
    col_config = {}
    for c in df_clean.columns:
        if "Dẫn chứng" in c:
            col_config[c] = st.column_config.LinkColumn(
                "🔗 " + c, 
                display_text="Xem dẫn chứng",
                help="Bấm vào để mở đường dẫn"
            )

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
        }), 
        use_container_width=True,
        column_config=col_config
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
            if not danh_sach_kenh_master: st.warning("⚠️ Chưa có kênh nào! Hãy sang tab 'Nhập Mục Tiêu' để tạo kênh trước.")
            kenh_kq = "" if not danh_sach_kenh_master else st.selectbox("Chọn Kênh Báo Cáo:", danh_sach_kenh_master, key=f"c_kq_{rk}")
            trang_thai_bkt_kq = lay_trang_thai_kiem_tien(kenh_kq) if kenh_kq else False
            
            kq_cu = df[(df["Tháng"] == thang_kq) & (df["Tuần"] == tuan_kq) & (df["Kênh_Spotify"] == kenh_kq)]
            if not kq_cu.empty and kenh_kq:
                v_dt_kq, v_p_kq, v_g_kq, v_t_kq = float(kq_cu.iloc[0]["Doanh_Thu_USD"]), int(kq_cu.iloc[0]["Luot_Play"]), float(kq_cu.iloc[0]["So_Gio_Nghe"]), int(kq_cu.iloc[0]["So_Tap_Upload"])
                v_link_kq = str(kq_cu.iloc[0].get("Link_Dan_Chung", ""))
                st.info(f"💡 Đã có dữ liệu của **{kenh_kq}** ({tuan_kq}). Sửa và lưu để GHI ĐÈ.")
            else:
                v_dt_kq, v_p_kq, v_g_kq, v_t_kq, v_link_kq = 0.0, 0, 0.0, 0, ""
                
        with col2:
            dt_kq = st.number_input("Doanh thu Tuần (USD):", min_value=0.0, step=1.0, value=v_dt_kq, key=f"dt_kq_{rk}")
            play_kq = st.number_input("Lượt Play Tuần:", min_value=0, step=100, value=v_p_kq, key=f"p_kq_{rk}")
        with col3:
            gio_kq = st.number_input("Giờ nghe Tuần (h):", min_value=0.0, step=10.0, value=v_g_kq, key=f"g_kq_{rk}")
            tap_kq = st.number_input("Số tập Upload Tuần:", min_value=0, step=1, value=v_t_kq, key=f"tap_kq_{rk}")
            
        link_dan_chung_tuan = st.text_input("🔗 Link dẫn chứng (Drive/Sheet):", value=v_link_kq, placeholder="https://...", key=f"link_tuan_{rk}")
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Lưu Kết Quả Tuần", type="primary", use_container_width=True):
            if not kenh_kq: st.error("⚠️ Bạn chưa chọn Kênh Spotify!")
            else:
                df_filtered = df[~((df["Tháng"] == thang_kq) & (df["Tuần"] == tuan_kq) & (df["Kênh_Spotify"] == kenh_kq))]
                du_lieu_moi = pd.DataFrame([{
                    "Tháng": thang_kq, "Tuần": tuan_kq, "Kênh_Spotify": kenh_kq,
                    "Doanh_Thu_USD": float(dt_kq), "Luot_Play": int(play_kq),
                    "So_Gio_Nghe": float(gio_kq), "So_Tap_Upload": int(tap_kq),
                    "Bat_Kiem_Tien": trang_thai_bkt_kq,
                    "Thoi_Gian_Nhap": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Link_Dan_Chung": link_dan_chung_tuan
                }])
                pd.concat([df_filtered, du_lieu_moi], ignore_index=True).to_csv(FILE_DU_LIEU, index=False)
                st.session_state.rk_kq += 1; st.rerun()
                
    else:
        st.subheader("Cập Nhật Kết Quả Tháng (Chốt Doanh Thu / Final)")
        rk_m = st.session_state.rk_kq_thang
        col1_m, col2_m, col3_m = st.columns(3)
        with col1_m:
            nam_kq_m = st.selectbox("Năm Báo Cáo:", [datetime.now().year, datetime.now().year - 1], key=f"y_m_{rk_m}")
            thang_kq_m = st.selectbox("Tháng Báo Cáo:", [f"Tháng {i}" for i in range(1, 13)], key=f"t_m_{rk_m}")
            kenh_kq_m = "" if not danh_sach_kenh_master else st.selectbox("Chọn Kênh Báo Cáo:", danh_sach_kenh_master, key=f"c_m_{rk_m}")
            trang_thai_bkt_m = lay_trang_thai_kiem_tien(kenh_kq_m) if kenh_kq_m else False
            
            kq_cu_m = df_thang_chot[(df_thang_chot["Năm"] == nam_kq_m) & (df_thang_chot["Tháng"] == thang_kq_m) & (df_thang_chot["Kênh_Spotify"] == kenh_kq_m)]
            if not kq_cu_m.empty and kenh_kq_m:
                v_dt_m, v_p_m, v_g_m, v_t_m = float(kq_cu_m.iloc[0]["Doanh_Thu_USD"]), int(kq_cu_m.iloc[0]["Luot_Play"]), float(kq_cu_m.iloc[0]["So_Gio_Nghe"]), int(kq_cu_m.iloc[0]["So_Tap_Upload"])
                v_link_m = str(kq_cu_m.iloc[0].get("Link_Dan_Chung", ""))
                st.info(f"💡 Đã có dữ liệu chốt tháng của **{kenh_kq_m}**. Sửa và lưu để GHI ĐÈ.")
            else:
                v_dt_m, v_p_m, v_g_m, v_t_m, v_link_m = 0.0, 0, 0.0, 0, ""
                
        with col2_m:
            dt_kq_m = st.number_input("Doanh thu Final ($):", min_value=0.0, step=1.0, value=v_dt_m, key=f"dt_m_{rk_m}")
            play_kq_m = st.number_input("Lượt Play Final:", min_value=0, step=100, value=v_p_m, key=f"p_m_{rk_m}")
        with col3_m:
            gio_kq_m = st.number_input("Giờ nghe Final (h):", min_value=0.0, step=10.0, value=v_g_m, key=f"g_m_{rk_m}")
            tap_kq_m = st.number_input("Số tập Upload Final:", min_value=0, step=1, value=v_t_m, key=f"tap_m_{rk_m}")
            
        link_dan_chung_thang = st.text_input("🔗 Link dẫn chứng (Tháng):", value=v_link_m, placeholder="https://...", key=f"link_thang_{rk_m}")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Lưu Chốt Tháng", type="primary", use_container_width=True):
            if not kenh_kq_m: st.error("⚠️ Bạn chưa chọn Kênh Spotify!")
            else:
                df_m_filtered = df_thang_chot[~((df_thang_chot["Năm"] == nam_kq_m) & (df_thang_chot["Tháng"] == thang_kq_m) & (df_thang_chot["Kênh_Spotify"] == kenh_kq_m))]
                du_lieu_moi_m = pd.DataFrame([{
                    "Năm": nam_kq_m, "Tháng": thang_kq_m, "Kênh_Spotify": kenh_kq_m,
                    "Doanh_Thu_USD": float(dt_kq_m), "Luot_Play": int(play_kq_m),
                    "So_Gio_Nghe": float(gio_kq_m), "So_Tap_Upload": int(tap_kq_m),
                    "Bat_Kiem_Tien": trang_thai_bkt_m,
                    "Thoi_Gian_Nhap": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Link_Dan_Chung": link_dan_chung_thang
                }])
                pd.concat([df_m_filtered, du_lieu_moi_m], ignore_index=True).to_csv(FILE_KQ_THANG, index=False)
                st.session_state.rk_kq_thang += 1; st.rerun()

# ==========================================
# TAB 5: QUẢN LÝ & XÓA DỮ LIỆU
# ==========================================
with tab_xoa_data:
    st.header("🛠️ Quản Lý & Xóa Dữ Liệu")
    st.markdown("Khu vực này giúp bạn dọn dẹp các dữ liệu nhập sai. Vui lòng kiểm tra kỹ trước khi bấm Xóa!")

    loai_dl = st.radio("Thư mục dữ liệu:", ["🎯 Mục tiêu (KPI)", "📥 Kết quả Tuần", "📥 Kết quả Tháng"], horizontal=True)

    if loai_dl == "🎯 Mục tiêu (KPI)":
        file_path = FILE_KPI
    elif loai_dl == "📥 Kết quả Tuần":
        file_path = FILE_DU_LIEU
    else:
        file_path = FILE_KQ_THANG

    if os.path.exists(file_path):
        df_delete = pd.read_csv(file_path)
        
        if len(df_delete) > 0:
            st.dataframe(df_delete, use_container_width=True)

            st.markdown("---")
            st.subheader("🗑️ Chọn dòng cần xóa")
            
            options_dict = {}
            for idx, row in df_delete.iterrows():
                kenh = row.get('Kênh_Spotify', 'Unknown')
                thang = row.get('Tháng', '')
                
                if loai_dl == "📥 Kết quả Tuần":
                    tuan = row.get('Tuần', '')
                    info = f"Dòng {idx}: {kenh} - {thang} - {tuan}"
                else:
                    info = f"Dòng {idx}: {kenh} - {thang}"
                    
                options_dict[info] = idx

            dong_can_xoa = st.multiselect("Nhấp vào đây và chọn các dòng dữ liệu bị sai:", list(options_dict.keys()))

            if st.button("🚨 XÓA CÁC DÒNG ĐÃ CHỌN", type="primary"):
                if dong_can_xoa:
                    idx_to_drop = [options_dict[val] for val in dong_can_xoa]
                    df_delete = df_delete[~df_delete.index.isin(idx_to_drop)]
                    df_delete.to_csv(file_path, index=False)
                    st.success("✅ Đã xóa thành công! Đang tự động cập nhật lại hệ thống...")
                    import time
                    time.sleep(1) 
                    try: st.rerun()
                    except: st.experimental_rerun()
                else:
                    st.warning("⚠️ Boss chưa chọn dòng nào để xóa!")
        else:
            st.info("Bảng dữ liệu này hiện đang trống.")
    else:
        st.error(f"Lỗi: Không tìm thấy file gốc ({file_path}).")

# ==========================================
# TAB 4: DASHBOARD
# ==========================================
with tab_dashboard:
    st.header("📊 Biểu Đồ Trực Quan Hiệu Suất")
    if df.empty and df_thang_chot.empty:
        st.info("Chưa có dữ liệu để vẽ biểu đồ.")
    else:
        col_chart1, col_chart2 = st.columns([1, 1])
        with col_chart1:
            thang_chon_chart = st.selectbox("Chọn Tháng:", [f"Tháng {i}" for i in range(1, 13)], key="chart_thang")
        with col_chart2:
            tieu_chi_chon_m = st.selectbox("Biểu đồ Tỷ Trọng:", ["Doanh_Thu_USD", "Luot_Play", "So_Gio_Nghe", "So_Tap_Upload"], key="chart_chiso")
        
        st.markdown("---")
        
        col_main1, col_main2 = st.columns([2, 1])
        with col_main1:
            st.subheader(f"📈 Xu Hướng Tuần Trong {thang_chon_chart}")
            df_trend = df[df["Tháng"] == thang_chon_chart]
            if df_trend.empty:
                st.warning("Không có dữ liệu Tuần cho tháng này.")
            else:
                df_trend_sum = df_trend.groupby(["Tuần", "Kênh_Spotify"])[tieu_chi_chon_m].sum().reset_index()
                fig_trend = px.line(df_trend_sum, x="Tuần", y=tieu_chi_chon_m, color="Kênh_Spotify", markers=True, title=f"Tiến độ {tieu_chi_chon_m}")
                chart_text_color = '#FAFAFA' if not is_light else '#111827'
                fig_trend.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=chart_text_color))
                st.plotly_chart(fig_trend, use_container_width=True)
                
        with col_main2:
            st.subheader(f"🍩 Tỷ Trọng Các Kênh ({thang_chon_chart})")
            df_pie_m = df_thang_chot[df_thang_chot["Tháng"] == thang_chon_chart]
            if df_pie_m.empty: df_pie_m = df_trend
            if df_pie_m.empty:
                st.warning("Không đủ dữ liệu để vẽ biểu đồ.")
            else:
                df_plot_m = df_pie_m.groupby("Kênh_Spotify")[tieu_chi_chon_m].sum().sort_values(ascending=False).reset_index()
                palette = ['#2E7D32', '#4CAF50', '#81C784', '#A5D6A7', '#DCE775', '#E8F5E9']
                colors = (palette * (len(df_plot_m) // len(palette) + 1))[:len(df_plot_m)]

                fig_pie_m = px.pie(df_plot_m, values=tieu_chi_chon_m, names="Kênh_Spotify", hole=0.4, title=f"Tỷ Trọng theo {tieu_chi_chon_m}", color_discrete_sequence=colors)
                fig_pie_m.update_traces(textinfo='percent', textfont_color="white", textfont_size=12, textposition='inside')
                chart_text_color = '#FAFAFA' if not is_light else '#0C7A33'

                fig_pie_m.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)', 
                    font=dict(color=chart_text_color), 
                    legend=dict(font=dict(color=chart_text_color), orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig_pie_m, use_container_width=True)
