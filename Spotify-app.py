import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime
import re

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
# HÀM SẮP XẾP THỜI GIAN AN TOÀN
# ==========================================
def lay_so_thu_tu(chuoi):
    """Hàm trích xuất số để sắp xếp (VD: 'Tháng 5 - Tuần 2' -> 502, 'Tuần 3' -> 3, 'Tháng 12' -> 12)"""
    nums = re.findall(r'\d+', str(chuoi))
    if len(nums) >= 2: return int(nums[0]) * 100 + int(nums[-1])
    elif len(nums) == 1: return int(nums[0])
    return 0

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN & CUSTOM THEME
# ==========================================
st.set_page_config(page_title="Spotify Performance Hub", layout="wide", page_icon="🎧", initial_sidebar_state="expanded")
 
col_title, col_toggle = st.columns([8, 2])
with col_title:
    st.title("🎧 TRUNG TÂM QUẢN TRỊ HIỆU SUẤT SPOTIFY")
with col_toggle:
    st.write("") 
    theme_choice = st.radio("Giao diện:", ["☀️ Light Mode", "🌙 Dark Mode"], horizontal=True, label_visibility="collapsed")
 
is_light = "Light" in theme_choice

if is_light:
    bg_main, bg_sec, text_c, border_c, primary_bg, primary_text = "#FFFFFF", "#F8F9FA", "#0C7A33", "#E0E0E0", "#FFD1BA", "#111827"
else:
    bg_main, bg_sec, text_c, border_c, primary_bg, primary_text = "#0E1117", "#262730", "#FAFAFA", "rgba(29, 185, 84, 0.2)", "#E22134", "#FAFAFA"
 
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;600;800&display=swap');
    html, body, [class*="css"], [class*="st-"] {{ font-family: 'Lexend', sans-serif !important; }}
    .stApp, [data-testid="stAppViewContainer"] {{ background-color: {bg_main} !important; }}
    [data-testid="stSidebar"] {{ background-color: {bg_sec} !important; }}
    [data-testid="stToolbar"] {{ visibility: hidden !important; }}
    #MainMenu {{ display: none !important; }}
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, label, li, span, div[data-testid="stMarkdownContainer"] {{ color: {text_c} !important; }}
    span[data-baseweb="tag"] {{ background-color: {primary_bg} !important; color: {primary_text} !important; }}
    span[data-baseweb="tag"] span {{ color: {primary_text} !important; }}
    div.stButton > button[kind="primary"] {{ background-color: {primary_bg} !important; color: {primary_text} !important; border: none !important; }}
    div.stButton > button[kind="primary"] * {{ color: {primary_text} !important; }}
    .spotify-card {{ background-color: {bg_sec} !important; border: 1px solid {border_c} !important; border-radius: 12px; padding: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }}
    .text-success, .text-success * {{ color: #1DB954 !important; }}
    .text-danger, .text-danger * {{ color: #E22134 !important; }}
    .badge-green {{ background-color: rgba(29, 185, 84, 0.15) !important; color: #1DB954 !important; }}
    .badge-red {{ background-color: rgba(226, 33, 52, 0.15) !important; color: #E22134 !important; }}
    li[role="option"] div[data-testid="stMarkdownContainer"] p, li[role="option"] span {{
        color: {'#111827' if is_light else '#000000'} !important;
        -webkit-text-fill-color: {'#111827' if is_light else '#000000'} !important;
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
    if not os.path.exists(FILE_DU_LIEU): 
        pd.DataFrame(columns=["Tháng", "Tuần", "Kênh_Spotify", "Doanh_Thu_USD", "Luot_Play", "So_Gio_Nghe", "So_Tap_Upload", "Bat_Kiem_Tien", "Thoi_Gian_Nhap", "Link_Dan_Chung"]).to_csv(FILE_DU_LIEU, index=False)
    else:
        df_hien_tai = pd.read_csv(FILE_DU_LIEU)
        changed = False
        if "Bat_Kiem_Tien" not in df_hien_tai.columns: df_hien_tai["Bat_Kiem_Tien"] = False; changed = True
        if "Link_Dan_Chung" not in df_hien_tai.columns: df_hien_tai["Link_Dan_Chung"] = ""; changed = True
        if changed: df_hien_tai.to_csv(FILE_DU_LIEU, index=False)
            
    if not os.path.exists(FILE_KPI): 
        pd.DataFrame(columns=["Tháng", "Kênh_Spotify", "KPI_Doanh_Thu", "KPI_Luot_Play", "KPI_So_Gio", "KPI_So_Tap", "So_Tuan", "Bat_Kiem_Tien"]).to_csv(FILE_KPI, index=False)
    else:
        df_kpi_hien_tai = pd.read_csv(FILE_KPI)
        if "Bat_Kiem_Tien" not in df_kpi_hien_tai.columns: df_kpi_hien_tai["Bat_Kiem_Tien"] = False; df_kpi_hien_tai.to_csv(FILE_KPI, index=False)
        
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
    badge_html = f"<span class='{'badge-green' if pct >= 100 else 'badge-red'}'>{pct:.1f}% KPI</span>" if pct is not None else ""
    return f'<div class="spotify-card"><div class="spotify-label">{label}</div><div class="spotify-value">{value}</div><div>{badge_html}</div></div>'

def tao_sheet_tong_hop(thang_chon, chiso_chon):
    df_kq = pd.read_csv(FILE_DU_LIEU)
    if "Link_Dan_Chung" not in df_kq.columns: df_kq["Link_Dan_Chung"] = ""
    df_kpi = pd.read_csv(FILE_KPI)
    df_kq_thang = pd.read_csv(FILE_KQ_THANG)
    if "Link_Dan_Chung" not in df_kq_thang.columns: df_kq_thang["Link_Dan_Chung"] = ""
    
    map_col = { "Doanh Thu": {"kq": "Doanh_Thu_USD", "kpi": "KPI_Doanh_Thu"}, "Lượt Play": {"kq": "Luot_Play", "kpi": "KPI_Luot_Play"}, "Giờ Nghe": {"kq": "So_Gio_Nghe", "kpi": "KPI_So_Gio"}, "Số Tập Upload": {"kq": "So_Tap_Upload", "kpi": "KPI_So_Tap"} }
    col_kq, col_kpi = map_col[chiso_chon]["kq"], map_col[chiso_chon]["kpi"]
    
    kpi_thang = df_kpi[df_kpi["Tháng"] == thang_chon]
    master = pd.DataFrame(danh_sach_kenh_master, columns=["Kênh_Spotify"]).merge(kpi_thang[["Kênh_Spotify", col_kpi, "So_Tuan"]], on="Kênh_Spotify", how="left")
    master[col_kpi] = master[col_kpi].fillna(0)

    if col_kq not in df_kq.columns: return pd.DataFrame(), col_kpi
    
    thang_kq_sum = df_kq[df_kq["Tháng"] == thang_chon].groupby("Kênh_Spotify")[col_kq].sum().reset_index().rename(columns={col_kq: "Kết quả tổng"})
    master = master.merge(thang_kq_sum, on="Kênh_Spotify", how="left")
    master["Kết quả tổng"] = master["Kết quả tổng"].fillna(0)
    master["% Hoàn thành"] = (master["Kết quả tổng"] / master[col_kpi].replace(0, pd.NA) * 100).fillna(0).replace([float('inf'), -float('inf')], 0)
    
    chot_thang = df_kq_thang[df_kq_thang["Tháng"] == thang_chon][["Kênh_Spotify", col_kq, "Link_Dan_Chung"]].groupby("Kênh_Spotify").agg({col_kq: "sum", "Link_Dan_Chung": lambda x: " | ".join(x.dropna().astype(str).loc[x != ""])}).reset_index().rename(columns={col_kq: "Kết quả tháng", "Link_Dan_Chung": "Dẫn chứng tháng"})
    master = master.merge(chot_thang, on="Kênh_Spotify", how="left")
    master["Kết quả tháng"] = master["Kết quả tháng"].fillna(0)
    master["% Hoàn thành tháng"] = (master["Kết quả tháng"] / master[col_kpi].replace(0, pd.NA) * 100).fillna(0).replace([float('inf'), -float('inf')], 0)
    
    tuan_trong_thang = sorted([t for t in df_kq[df_kq["Tháng"] == thang_chon]["Tuần"].unique()], key=lay_so_thu_tu)
    for tuan in tuan_trong_thang:
        master[f"{tuan}_Target"] = (master[col_kpi] / master["So_Tuan"]).fillna(0)
        kq_tuan = df_kq[(df_kq["Tháng"] == thang_chon) & (df_kq["Tuần"] == tuan)][["Kênh_Spotify", col_kq, "Link_Dan_Chung"]].groupby("Kênh_Spotify").agg({col_kq: "sum", "Link_Dan_Chung": lambda x: " | ".join(x.dropna().astype(str).loc[x != ""])}).reset_index().rename(columns={col_kq: f"{tuan}_Actual", "Link_Dan_Chung": f"{tuan}_Link"})
        master = master.merge(kq_tuan, on="Kênh_Spotify", how="left")
        master[f"{tuan}_Actual"] = master[f"{tuan}_Actual"].fillna(0)
        master[f"{tuan}_%"] = (master[f"{tuan}_Actual"] / master[f"{tuan}_Target"].replace(0, pd.NA) * 100).fillna(0).replace([float('inf'), -float('inf')], 0)
        
    if len(master) > 0:
        total_data = {}
        for col in master.columns:
            if col == "Kênh_Spotify": total_data[col] = "Total các kênh"
            else: total_data[col] = pd.to_numeric(master[col], errors='coerce').fillna(0).sum()
        
        val_kpi, val_kq_tong, val_kq_thang = total_data.get(col_kpi, 0), total_data.get("Kết quả tổng", 0), total_data.get("Kết quả tháng", 0)
        total_data["% Hoàn thành"] = (val_kq_tong / val_kpi * 100) if val_kpi > 0 else 0
        total_data["% Hoàn thành tháng"] = (val_kq_thang / val_kpi * 100) if val_kpi > 0 else 0
            
        for tuan in tuan_trong_thang:
            c_actual, c_target, c_pct = f"{tuan}_Actual", f"{tuan}_Target", f"{tuan}_%"
            val_t_target, val_t_actual = total_data.get(c_target, 0), total_data.get(c_actual, 0)
            total_data[c_pct] = (val_t_actual / val_t_target * 100) if val_t_target > 0 else 0
                
        if "Dẫn chứng tháng" in master.columns: total_data["Dẫn chứng tháng"] = "NA"
        for tuan in tuan_trong_thang:
            if f"{tuan}_Link" in master.columns: total_data[f"{tuan}_Link"] = "NA"
                
        master = pd.concat([pd.DataFrame([total_data]), master], ignore_index=True)
        
    return master, col_kpi

# TABS
tab_dashboard, tab_master, tab_nhap_kpi, tab_nhap_kq, tab_xoa_data, tab_backup, tab_huong_dan = st.tabs([
    "📊 Dashboard", "📑 Sheet Tổng Hợp", "🎯 Nhập Mục Tiêu", "📥 Nhập Kết Quả", "🛠️ Quản Lý", "💾 Backup", "🔄 Hướng Dẫn"
])

# ==========================================
# TAB 1: DASHBOARD CHÍNH 
# ==========================================
with tab_dashboard:
    loai_dashboard = st.radio("📊 Chọn cấp độ báo cáo:", ["📅 Báo cáo Tuần (Tiến độ)", "📆 Báo cáo Tháng (Final)"], horizontal=True, label_visibility="collapsed")
    st.markdown("---")
    
    if loai_dashboard == "📅 Báo cáo Tuần (Tiến độ)":
        if df.empty: st.info("Hệ thống chưa có dữ liệu kết quả TUẦN nào.")
        else:
            # === TẠO CỘT THỜI GIAN GỘP "THÁNG - TUẦN" ===
            if not df.empty and "Tháng" in df.columns and "Tuần" in df.columns:
                df["Tháng_Tuần"] = df["Tháng"].astype(str) + " - " + df["Tuần"].astype(str)

            # Chia lại bộ lọc thành 3 cột cho gọn gàng
            col_loc_thoigian, col_loc_kenh, col_loc_bkt = st.columns([2.5, 2.5, 1.5])
            
            with col_loc_thoigian:
                if not df.empty and "Tháng_Tuần" in df.columns:
                    thoigian_hien_co = df["Tháng_Tuần"].dropna().unique().tolist()
                    thoigian_hien_co.sort(key=lay_so_thu_tu)
                else:
                    thoigian_hien_co = []
                
                tuan_chon = st.multiselect("🗓️ Chọn Thời Gian:", options=thoigian_hien_co, default=thoigian_hien_co, key="loc_thoigian_w")

            with col_loc_kenh: 
                danh_sach_kenh_hien_co = list(df["Kênh_Spotify"].unique())
                kenh_duoc_chon = st.multiselect("🎧 Lọc theo Kênh:", options=danh_sach_kenh_hien_co, default=danh_sach_kenh_hien_co, key="loc_kenh_w")
                
            with col_loc_bkt: 
                loc_bkt = st.selectbox("🚦 Kiếm Tiền:", ["Tất cả", "Đã bật", "Chưa bật"], key="loc_bkt_w")
            
            kenh_hien_thi_cuoi_cung = [k for k in kenh_duoc_chon if (loc_bkt == "Tất cả") or (loc_bkt == "Đã bật" and lay_trang_thai_kiem_tien(k)) or (loc_bkt == "Chưa bật" and not lay_trang_thai_kiem_tien(k))]
            
            # Bọc thép
            tuan_chon = locals().get('tuan_chon', [])
            kenh_hien_thi_cuoi_cung = locals().get('kenh_hien_thi_cuoi_cung', [])

            if len(kenh_hien_thi_cuoi_cung) == 0 or len(tuan_chon) == 0: 
                st.warning("⚠️ App đang chờ lệnh! Boss vui lòng đảm bảo đã chọn ít nhất 1 Kênh VÀ 1 Mốc Thời Gian ở bộ lọc phía trên nhé.")
            else:
                df_final = df[df["Kênh_Spotify"].isin(kenh_hien_thi_cuoi_cung) & df["Tháng_Tuần"].isin(tuan_chon)].copy()
                df_final["Tuần"] = df_final["Tháng_Tuần"]
                
                thang_lien_quan = df_final["Tháng"].unique().tolist()
                df_kpi_filter = df_kpi[df_kpi["Kênh_Spotify"].isin(kenh_hien_thi_cuoi_cung) & df_kpi["Tháng"].isin(thang_lien_quan)].copy()
                    
                so_tuan_chon = len(tuan_chon)
                target_dt = (df_kpi_filter["KPI_Doanh_Thu"] / df_kpi_filter["So_Tuan"].fillna(4)).sum() * so_tuan_chon if len(tuan_chon) < len(thoigian_hien_co) else df_kpi_filter["KPI_Doanh_Thu"].sum()
                target_play = (df_kpi_filter["KPI_Luot_Play"] / df_kpi_filter["So_Tuan"].fillna(4)).sum() * so_tuan_chon if len(tuan_chon) < len(thoigian_hien_co) else df_kpi_filter["KPI_Luot_Play"].sum()

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
                
                # Sắp xếp biểu đồ xu hướng bằng hàm an toàn
                df_trend["SortKey"] = df_trend["Tuần"].apply(lay_so_thu_tu)
                df_trend = df_trend.sort_values("SortKey").drop(columns=["SortKey"])
                
                df_trend["Đường_Mục_Tiêu"] = round(df_kpi_filter["Muc_Tieu_Tuan_Hien_Tai"].sum(), 2)
                
                fig_vs = go.Figure()
                fig_vs.add_trace(go.Scatter(x=df_trend["Tuần"], y=df_trend[cot_kq], mode='lines+markers+text', name='Kết Quả', textposition="top center", line=dict(color='#1DB954', width=3)))
                fig_vs.add_trace(go.Scatter(x=df_trend["Tuần"], y=df_trend["Đường_Mục_Tiêu"], mode='lines+markers', name='Mục Tiêu', line=dict(color='#E22134', width=3, dash='dash')))
                
                chart_text_color = '#FAFAFA' if not is_light else '#0C7A33'
                grid_line_color = 'rgba(255, 255, 255, 0.2)' if not is_light else '#E0E0E0'
                
                fig_vs.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=chart_text_color),
                    xaxis=dict(gridcolor=grid_line_color, griddash='dot', tickfont=dict(color=chart_text_color)),
                    yaxis=dict(gridcolor=grid_line_color, griddash='dot', rangemode='tozero', tickfont=dict(color=chart_text_color))
                )
                st.plotly_chart(fig_vs, use_container_width=True, theme=None)
                
                # --- PIE CHART (SỬA LỖI SẮP XẾP Ở ĐÂY) ---
                col_sl1_w, col_sl2_w = st.columns(2)
                with col_sl1_w:
                    st.markdown("##### 📌 Tỷ Trọng Kênh")
                    # Dùng hàm an toàn để sắp xếp (Không còn lỗi ValueError)
                    tuan_co_data = list(df_final["Tuần"].unique())
                    tuan_co_data.sort(key=lay_so_thu_tu)
                    
                    if tuan_co_data:
                        tuan_chon_donut = st.selectbox("Chọn mốc thời gian:", tuan_co_data, key="t_donut_w")
                    else:
                        tuan_chon_donut = None
                        
                    tieu_chi_map_w = {"Doanh thu": "Doanh_Thu_USD", "Lượt Play": "Luot_Play", "Giờ nghe": "So_Gio_Nghe"}
                    tieu_chi_chon_w = st.selectbox("Tiêu chí so sánh:", list(tieu_chi_map_w.keys()), key="tc_donut_w")
                    cot_tieu_chi_w = tieu_chi_map_w[tieu_chi_chon_w]
                    
                with col_sl2_w:
                    kenh_all_w = df_final["Kênh_Spotify"].unique()
                    kenh_chon_w = st.multiselect("Chọn kênh:", options=kenh_all_w, default=kenh_all_w, key="kc_donut_w")
                    
                df_pie_w = df_final[(df_final["Kênh_Spotify"].isin(kenh_chon_w)) & (df_final["Tuần"] == tuan_chon_donut)] if tuan_chon_donut else pd.DataFrame()
                
                if df_pie_w.empty:
                    st.info("Vui lòng chọn dữ liệu hợp lệ để hiển thị biểu đồ.")
                else:
                    df_plot_w = df_pie_w.groupby("Kênh_Spotify")[cot_tieu_chi_w].sum().sort_values(ascending=False).reset_index()
                    palette = ['#2E7D32', '#4CAF50', '#81C784', '#A5D6A7', '#DCE775', '#E8F5E9']
                    colors = (palette * (len(df_plot_w) // len(palette) + 1))[:len(df_plot_w)]
                    fig_pie_w = px.pie(df_plot_w, values=cot_tieu_chi_w, names="Kênh_Spotify", hole=0.4, title=f"Tỷ Trọng theo {tieu_chi_chon_w} ({tuan_chon_donut})", color_discrete_sequence=colors)
                    fig_pie_w.update_traces(textinfo='percent', textfont_color="white", textfont_size=12, textposition='inside')
                    fig_pie_w.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=chart_text_color), legend=dict(font=dict(color=chart_text_color), orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5))
                    st.plotly_chart(fig_pie_w, use_container_width=True, theme=None)
                    
    else:
        # DASHBOARD THÁNG (FINAL)
        if df_thang_chot.empty: st.info("Hệ thống chưa có dữ liệu chốt THÁNG nào.")
        else:
            col_loc1_m, col_loc_thang_m, col_loc2_m, col_loc3_m = st.columns([1, 1.5, 2, 1])
            with col_loc1_m:
                nam_hien_co = list(df_thang_chot["Năm"].dropna().unique())
                nam_chon_db = st.selectbox("📌 Chọn Năm:", nam_hien_co, key="loc_nam_m")
            
            df_nam = df_thang_chot[df_thang_chot["Năm"] == nam_chon_db]
            
            with col_loc_thang_m:
                thang_hien_co_m = list(df_nam["Tháng"].dropna().unique())
                thang_hien_co_m.sort(key=lay_so_thu_tu)
                thang_chon_m = st.multiselect("📅 Chọn Tháng hiển thị:", options=thang_hien_co_m, default=thang_hien_co_m, key="loc_thang_m")
                
            danh_sach_kenh_hien_co_m = list(df_nam["Kênh_Spotify"].unique())
            with col_loc2_m: kenh_duoc_chon_m = st.multiselect("🎧 Lọc theo Kênh:", options=danh_sach_kenh_hien_co_m, default=danh_sach_kenh_hien_co_m, key="loc_kenh_m")
            with col_loc3_m: loc_bkt_m = st.selectbox("🚦 Kiếm Tiền:", ["Tất cả", "Đã bật", "Chưa bật"], key="loc_bkt_m")
            
            kenh_hien_thi_cuoi_cung_m = [k for k in kenh_duoc_chon_m if (loc_bkt_m == "Tất cả") or (loc_bkt_m == "Đã bật" and lay_trang_thai_kiem_tien(k)) or (loc_bkt_m == "Chưa bật" and not lay_trang_thai_kiem_tien(k))]

            if not kenh_hien_thi_cuoi_cung_m or not thang_chon_m:
                st.warning("⚠️ App đang chờ lệnh! Boss vui lòng đảm bảo đã chọn ít nhất 1 Kênh VÀ 1 Tháng ở bộ lọc phía trên nhé.")
            else:
                df_final_m = df_nam[df_nam["Kênh_Spotify"].isin(kenh_hien_thi_cuoi_cung_m) & df_nam["Tháng"].isin(thang_chon_m)]
                df_kpi_filter_m = df_kpi[df_kpi["Kênh_Spotify"].isin(kenh_hien_thi_cuoi_cung_m) & df_kpi["Tháng"].isin(thang_chon_m)]
                
                target_dt_m = df_kpi_filter_m["KPI_Doanh_Thu"].sum()
                target_play_m = df_kpi_filter_m["KPI_Luot_Play"].sum()

                st.markdown("### 🏆 1. Chỉ Số Tháng Tổng Quan")
                dt_pct_m = (df_final_m['Doanh_Thu_USD'].sum() / target_dt_m * 100) if target_dt_m > 0 else 0
                play_pct_m = (df_final_m['Luot_Play'].sum() / target_play_m * 100) if target_play_m > 0 else 0
                
                sm1, sm2, sm3, sm4 = st.columns(4)
                sm1.markdown(make_card("🏢 Tổng Kênh", len(kenh_hien_thi_cuoi_cung_m)), unsafe_allow_html=True)
                sm2.markdown(make_card("💸 Đã Bật KT", sum([1 for k in kenh_hien_thi_cuoi_cung_m if lay_trang_thai_kiem_tien(k)])), unsafe_allow_html=True)
                sm3.markdown(make_card("💰 Doanh Thu", f"${df_final_m['Doanh_Thu_USD'].sum():,.0f}", dt_pct_m), unsafe_allow_html=True)
                sm4.markdown(make_card("▶️ Lượt Play", f"{df_final_m['Luot_Play'].sum():,.0f}", play_pct_m), unsafe_allow_html=True)
                
                st.markdown("### 🚀 2. Xu Hướng Các Tháng")
                chiso_chon_m = st.radio("🛠️ Chọn chỉ số:", ["Doanh Thu", "Lượt Play", "Giờ Nghe"], horizontal=True, key="cs_m")
                map_chiso_m = { "Doanh Thu": {"kq": "Doanh_Thu_USD", "kpi": "KPI_Doanh_Thu"}, "Lượt Play": {"kq": "Luot_Play", "kpi": "KPI_Luot_Play"}, "Giờ Nghe": {"kq": "So_Gio_Nghe", "kpi": "KPI_So_Gio"} }
                cot_kq_m, cot_kpi_m = map_chiso_m[chiso_chon_m]["kq"], map_chiso_m[chiso_chon_m]["kpi"]
                
                df_trend_m = df_final_m.groupby("Tháng")[cot_kq_m].sum().reset_index()
                # Sửa lỗi sắp xếp tháng
                df_trend_m["Sort"] = df_trend_m["Tháng"].apply(lay_so_thu_tu)
                df_trend_m = df_trend_m.sort_values(by="Sort").drop(columns=["Sort"])
                
                df_kpi_trend = df_kpi_filter_m.groupby("Tháng")[cot_kpi_m].sum().reset_index()
                df_trend_m = df_trend_m.merge(df_kpi_trend, on="Tháng", how="left")
                
                fig_vs_m = go.Figure()
                fig_vs_m.add_trace(go.Scatter(x=df_trend_m["Tháng"], y=df_trend_m[cot_kq_m], mode='lines+markers+text', name='Kết Quả Tháng', textposition="top center", line=dict(color='#1DB954', width=3)))
                fig_vs_m.add_trace(go.Scatter(x=df_trend_m["Tháng"], y=df_trend_m[cot_kpi_m], mode='lines+markers', name='Mục Tiêu Tháng', line=dict(color='#E22134', width=3, dash='dash')))
                
                chart_text_color = '#FAFAFA' if not is_light else '#0C7A33'
                grid_line_color = 'rgba(255, 255, 255, 0.2)' if not is_light else '#E0E0E0'
                
                fig_vs_m.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=chart_text_color), xaxis=dict(gridcolor=grid_line_color, griddash='dot', tickfont=dict(color=chart_text_color)), yaxis=dict(gridcolor=grid_line_color, griddash='dot', rangemode='tozero', tickfont=dict(color=chart_text_color)))
                st.plotly_chart(fig_vs_m, use_container_width=True, theme=None)
                
                # --- PIE CHART THÁNG ---
                col_sl1_m, col_sl2_m = st.columns(2)
                with col_sl1_m:
                    st.markdown("##### 📌 Tỷ Trọng Kênh (Tháng)")
                    thang_co_data = list(df_final_m["Tháng"].unique())
                    thang_co_data.sort(key=lay_so_thu_tu)
                    thang_chon_donut_m = st.selectbox("Chọn tháng:", thang_co_data, key="t_donut_m")
                    tieu_chi_map_m = {"Doanh thu": "Doanh_Thu_USD", "Lượt Play": "Luot_Play", "Giờ nghe": "So_Gio_Nghe"}
                    tieu_chi_chon_m = st.selectbox("Tiêu chí so sánh:", list(tieu_chi_map_m.keys()), key="tc_donut_m")
                    cot_tieu_chi_m = tieu_chi_map_m[tieu_chi_chon_m]
                with col_sl2_m:
                    kenh_all_m = df_final_m["Kênh_Spotify"].unique()
                    kenh_chon_m_donut = st.multiselect("Chọn kênh:", options=kenh_all_m, default=kenh_all_m, key="kc_donut_m")
                    
                df_pie_m = df_final_m[(df_final_m["Kênh_Spotify"].isin(kenh_chon_m_donut)) & (df_final_m["Tháng"] == thang_chon_donut_m)]
                if df_pie_m.empty:
                    st.info("Vui lòng chọn kênh để hiển thị biểu đồ.")
                else:
                    df_plot_m = df_pie_m.groupby("Kênh_Spotify")[cot_tieu_chi_m].sum().sort_values(ascending=False).reset_index()
                    palette = ['#2E7D32', '#4CAF50', '#81C784', '#A5D6A7', '#DCE775', '#E8F5E9']
                    colors = (palette * (len(df_plot_m) // len(palette) + 1))[:len(df_plot_m)]
                    fig_pie_m = px.pie(df_plot_m, values=cot_tieu_chi_m, names="Kênh_Spotify", hole=0.4, title=f"Tỷ Trọng theo {tieu_chi_chon_m} ({thang_chon_donut_m})", color_discrete_sequence=colors)
                    fig_pie_m.update_traces(textinfo='percent', textfont_color="white", textfont_size=12, textposition='inside')
                    fig_pie_m.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=chart_text_color), legend=dict(font=dict(color=chart_text_color), orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5))
                    st.plotly_chart(fig_pie_m, use_container_width=True, theme=None)

# ==========================================
# TAB 2: SHEET TỔNG HỢP
# ==========================================
with tab_master:
    st.header("📑 Sheet Tổng Hợp Hiệu Suất")
    col1, col2 = st.columns(2)
    with col1: chon_thang = st.selectbox("📅 Chọn tháng:", [f"Tháng {i}" for i in range(1, 13)])
    with col2: chiso_sheet = st.selectbox("🛠️ Chọn chỉ số hiển thị:", ["Doanh Thu", "Lượt Play", "Giờ Nghe", "Số Tập Upload"])
    
    df_raw, col_kpi_name = tao_sheet_tong_hop(chon_thang, chiso_sheet)
    df_display = df_raw.copy()
    
    rename_map = { "Kênh_Spotify": "Kênh", col_kpi_name: f"KPI {chiso_sheet}" }
    for col in df_display.columns:
        if "Tuần" in col:
            if "_Target" in col: rename_map[col] = col.replace("Tuần ", "KPI Tuần ").replace("_Target", "")
            elif "_Actual" in col: rename_map[col] = col.replace("Tuần ", "Kết quả Tuần ").replace("_Actual", "")
            elif "_%" in col: rename_map[col] = col.replace("Tuần ", "% Hoàn thành Tuần ").replace("_%", "")
            elif "_Link" in col: rename_map[col] = col.replace("Tuần ", "Link Dẫn chứng Tuần ").replace("_Link", "")
            
    df_display.rename(columns=rename_map, inplace=True)
    
    # Format số liệu
    for col in df_display.columns:
        if "KPI" in col or "Kết quả" in col or "Total" in col:
            if chiso_sheet == "Doanh Thu": df_display[col] = df_display[col].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) and isinstance(x, (int, float)) else x)
            else: df_display[col] = df_display[col].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) and isinstance(x, (int, float)) else x)
        elif "%" in col:
            df_display[col] = df_display[col].apply(lambda x: f"{x:,.1f}%" if pd.notnull(x) and isinstance(x, (int, float)) else x)
            
    # Format URL
    link_columns = [col for col in df_display.columns if "Link" in col or "Dẫn chứng" in col]
    def make_clickable(url):
        if pd.isna(url) or str(url).strip() == "" or url == "NA": return ""
        links = str(url).split(" | ")
        html_links = [f'<a href="{l.strip()}" target="_blank" style="color: #1DB954; text-decoration: underline;">🔗 Link</a>' for l in links if l.strip()]
        return " | ".join(html_links)
        
    for col in link_columns:
        df_display[col] = df_display[col].apply(make_clickable)

    html_table = df_display.to_html(escape=False, index=False, classes='spotify-table')
    css = f"""
    <style>
    .spotify-table {{ width: 100%; border-collapse: collapse; font-family: 'Lexend', sans-serif; color: {'#111827' if is_light else '#FAFAFA'}; font-size: 13px; }}
    .spotify-table th {{ background-color: {'#E22134' if is_light else '#E22134'}; color: white; padding: 12px 8px; text-align: center; border: 1px solid {'#E0E0E0' if is_light else '#404040'}; position: sticky; top: 0; z-index: 1; }}
    .spotify-table td {{ padding: 10px 8px; text-align: center; border: 1px solid {'#E0E0E0' if is_light else '#404040'}; }}
    .spotify-table tr:nth-child(even) {{ background-color: {'#F8F9FA' if is_light else '#262730'}; }}
    .spotify-table tr:hover {{ background-color: {'#FFD1BA' if is_light else '#404040'}; }}
    .spotify-table tr:first-child {{ font-weight: bold; background-color: {'#FFE5D9' if is_light else '#303030'} !important; border-bottom: 2px solid #E22134; }}
    .spotify-table tr:first-child td {{ color: {'#E22134' if is_light else '#FFD1BA'} !important; }}
    .table-container {{ overflow-x: auto; max-height: 600px; border-radius: 8px; border: 1px solid {'#E0E0E0' if is_light else '#404040'}; }}
    </style>
    """
    st.markdown(css + f'<div class="table-container">{html_table}</div>', unsafe_allow_html=True)
    st.download_button(label="📥 Xuất Excel (Sheet này)", data=df_display.to_csv(index=False).encode('utf-8-sig'), file_name=f"BaoCao_{thang_chon}_{chiso_sheet}.csv", mime='text/csv')

# ==========================================
# TAB 3: NHẬP KPI
# ==========================================
with tab_nhap_kpi:
    st.header("🎯 Cài đặt Mục Tiêu (KPI)")
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
        v_dt, v_p, v_g, v_t = float(kpi_cu.iloc[0]["KPI_Doanh_Thu"]), int(kpi_cu.iloc[0]["KPI_Luot_Play"]), float(kpi_cu.iloc[0]["KPI_So_Gio"]), int(kpi_cu.iloc[0]["KPI_So_Tap"])
        st.info(f"💡 Đang hiển thị Mục tiêu cũ của **{kenh_kpi}**. Bạn có thể sửa số và bấm Lưu để GHI ĐÈ.")
    else:
        v_w, v_dt, v_p, v_g, v_t = 4, 0.0, 0, 0.0, 0

    with col_kpi2:
        so_tuan_kpi = st.number_input("Tháng này có bao nhiêu Tuần?", min_value=1, max_value=5, value=v_w, key=f"w_kpi_{rk_kpi}")
        dt_kpi = st.number_input("KPI Doanh thu (USD):", min_value=0.0, step=10.0, value=v_dt, key=f"dt_kpi_{rk_kpi}")
        play_kpi = st.number_input("KPI Lượt Play:", min_value=0, step=1000, value=v_p, key=f"p_kpi_{rk_kpi}")
    with col_kpi3:
        gio_kpi = st.number_input("KPI Giờ nghe (h):", min_value=0.0, step=100.0, value=v_g, key=f"g_kpi_{rk_kpi}")
        tap_kpi = st.number_input("KPI Số tập Upload:", min_value=0, step=1, value=v_t, key=f"tap_kpi_{rk_kpi}")
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("Lưu KPI", type="primary", use_container_width=True):
            if not kenh_kpi:
                st.error("⚠️ Vui lòng nhập Tên Kênh!")
            else:
                df_kpi_filter = df_kpi[~((df_kpi["Tháng"] == thang_kpi) & (df_kpi["Kênh_Spotify"] == kenh_kpi))]
                kpi_moi = pd.DataFrame([{ "Tháng": thang_kpi, "Kênh_Spotify": kenh_kpi, "KPI_Doanh_Thu": float(dt_kpi), "KPI_Luot_Play": int(play_kpi), "KPI_So_Gio": float(gio_kpi), "KPI_So_Tap": int(tap_kpi), "So_Tuan": int(so_tuan_kpi), "Bat_Kiem_Tien": bkt_kpi }])
                df_kpi_new = pd.concat([df_kpi_filter, kpi_moi], ignore_index=True)
                df_kpi_new.to_csv(FILE_KPI, index=False)
                
                df_update_bkt = pd.read_csv(FILE_DU_LIEU)
                df_update_bkt.loc[df_update_bkt["Kênh_Spotify"] == kenh_kpi, "Bat_Kiem_Tien"] = bkt_kpi
                df_update_bkt.to_csv(FILE_DU_LIEU, index=False)
                
                df_thang_update = pd.read_csv(FILE_KQ_THANG)
                df_thang_update.loc[df_thang_update["Kênh_Spotify"] == kenh_kpi, "Bat_Kiem_Tien"] = bkt_kpi
                df_thang_update.to_csv(FILE_KQ_THANG, index=False)
                
                st.session_state.rk_kpi += 1
                st.success("✅ Đã lưu KPI thành công!")
                import time; time.sleep(0.5); st.rerun()

# ==========================================
# TAB 4: NHẬP KẾT QUẢ
# ==========================================
with tab_nhap_kq:
    st.header("📥 Nhập Kết Quả Thực Tế")
    loai_nhap = st.radio("Chọn loại báo cáo nhập:", ["Báo cáo Tuần", "Báo cáo Tháng (Chốt)"], horizontal=True)
    st.markdown("---")
    
    if loai_nhap == "Báo cáo Tuần":
        rk = st.session_state.rk_kq
        col1, col2, col3 = st.columns(3)
        with col1:
            thang_kq = st.selectbox("Chọn Tháng:", [f"Tháng {i}" for i in range(1, 13)], key=f"t_kq_{rk}")
            tuan_kq = st.selectbox("Chọn Tuần:", [f"Tuần {i}" for i in range(1, 6)], key=f"w_kq_{rk}")
            kenh_kq = st.selectbox("Chọn Kênh Báo Cáo:", danh_sach_kenh_master, key=f"c_kq_{rk}") if danh_sach_kenh_master else ""
            trang_thai_bkt_kq = lay_trang_thai_kiem_tien(kenh_kq) if kenh_kq else False
            
        kq_cu = df[(df["Tháng"] == thang_kq) & (df["Tuần"] == tuan_kq) & (df["Kênh_Spotify"] == kenh_kq)]
        if not kq_cu.empty and kenh_kq:
            v_dt_kq, v_p_kq, v_g_kq, v_t_kq = float(kq_cu.iloc[0]["Doanh_Thu_USD"]), int(kq_cu.iloc[0]["Luot_Play"]), float(kq_cu.iloc[0]["So_Gio_Nghe"]), int(kq_cu.iloc[0]["So_Tap_Upload"])
            v_link_kq = str(kq_cu.iloc[0].get("Link_Dan_Chung", ""))
            if v_link_kq == "nan": v_link_kq = ""
            st.info(f"💡 Đã có dữ liệu của **{kenh_kq}** ({tuan_kq}). Sửa và lưu để GHI ĐÈ.")
        else:
            v_dt_kq, v_p_kq, v_g_kq, v_t_kq, v_link_kq = 0.0, 0, 0.0, 0, ""
            
        with col2:
            dt_kq = st.number_input("Doanh thu Tuần (USD):", min_value=0.0, step=1.0, value=v_dt_kq, key=f"dt_kq_{rk}")
            play_kq = st.number_input("Lượt Play Tuần:", min_value=0, step=100, value=v_p_kq, key=f"p_kq_{rk}")
        with col3:
            gio_kq = st.number_input("Giờ nghe Tuần (h):", min_value=0.0, step=10.0, value=v_g_kq, key=f"g_kq_{rk}")
            tap_kq = st.number_input("Số tập Upload Tuần:", min_value=0, step=1, value=v_t_kq, key=f"tap_kq_{rk}")
            link_dan_chung = st.text_input("🔗 Link dẫn chứng (Drive, Ảnh...):", value=v_link_kq, placeholder="https://...", key=f"link_{rk}")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Lưu Kết Quả Tuần", type="primary", use_container_width=True):
                if not kenh_kq:
                    st.error("⚠️ Vui lòng chọn Tên Kênh!")
                else:
                    df_filter = df[~((df["Tháng"] == thang_kq) & (df["Tuần"] == tuan_kq) & (df["Kênh_Spotify"] == kenh_kq))]
                    du_lieu_moi = pd.DataFrame([{ "Tháng": thang_kq, "Tuần": tuan_kq, "Kênh_Spotify": kenh_kq, "Doanh_Thu_USD": float(dt_kq), "Luot_Play": int(play_kq), "So_Gio_Nghe": float(gio_kq), "So_Tap_Upload": int(tap_kq), "Bat_Kiem_Tien": trang_thai_bkt_kq, "Thoi_Gian_Nhap": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Link_Dan_Chung": link_dan_chung }])
                    df_new = pd.concat([df_filter, du_lieu_moi], ignore_index=True)
                    df_new.to_csv(FILE_DU_LIEU, index=False)
                    st.session_state.rk_kq += 1
                    st.success("✅ Đã lưu kết quả TUẦN thành công!")
                    import time; time.sleep(0.5); st.rerun()
                    
    else:
        rk_m = st.session_state.rk_kq_thang
        col1_m, col2_m, col3_m = st.columns(3)
        with col1_m:
            nam_kq_m = st.number_input("Nhập Năm:", min_value=2020, max_value=2050, value=datetime.now().year, step=1, key=f"nam_m_{rk_m}")
            thang_kq_m = st.selectbox("Chọn Tháng Chốt:", [f"Tháng {i}" for i in range(1, 13)], key=f"t_m_{rk_m}")
            kenh_kq_m = st.selectbox("Chọn Kênh Báo Cáo:", danh_sach_kenh_master, key=f"c_m_{rk_m}") if danh_sach_kenh_master else ""
            trang_thai_bkt_m = lay_trang_thai_kiem_tien(kenh_kq_m) if kenh_kq_m else False

        kq_cu_m = df_thang_chot[(df_thang_chot["Năm"] == nam_kq_m) & (df_thang_chot["Tháng"] == thang_kq_m) & (df_thang_chot["Kênh_Spotify"] == kenh_kq_m)]
        if not kq_cu_m.empty and kenh_kq_m:
            v_dt_m, v_p_m, v_g_m, v_t_m = float(kq_cu_m.iloc[0]["Doanh_Thu_USD"]), int(kq_cu_m.iloc[0]["Luot_Play"]), float(kq_cu_m.iloc[0]["So_Gio_Nghe"]), int(kq_cu_m.iloc[0]["So_Tap_Upload"])
            v_link_m = str(kq_cu_m.iloc[0].get("Link_Dan_Chung", ""))
            if v_link_m == "nan": v_link_m = ""
            st.info(f"💡 Đã có dữ liệu chốt của **{kenh_kq_m}** ({thang_kq_m}). Sửa và lưu để GHI ĐÈ.")
        else:
            v_dt_m, v_p_m, v_g_m, v_t_m, v_link_m = 0.0, 0, 0.0, 0, ""

        with col2_m:
            dt_kq_m = st.number_input("Chốt Doanh thu Tháng (USD):", min_value=0.0, step=1.0, value=v_dt_m, key=f"dt_m_{rk_m}")
            play_kq_m = st.number_input("Chốt Lượt Play Tháng:", min_value=0, step=100, value=v_p_m, key=f"p_m_{rk_m}")
        with col3_m:
            gio_kq_m = st.number_input("Chốt Giờ nghe Tháng (h):", min_value=0.0, step=10.0, value=v_g_m, key=f"g_m_{rk_m}")
            tap_kq_m = st.number_input("Chốt Số tập Upload Tháng:", min_value=0, step=1, value=v_t_m, key=f"tap_m_{rk_m}")
            link_dan_chung_thang = st.text_input("🔗 Link dẫn chứng (Tháng):", value=v_link_m, placeholder="https://...", key=f"link_thang_{rk_m}")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Lưu Chốt Số Tháng", type="primary", use_container_width=True):
                if not kenh_kq_m:
                    st.error("⚠️ Vui lòng chọn Tên Kênh!")
                else:
                    df_kq_m_filter = df_thang_chot[~((df_thang_chot["Năm"] == nam_kq_m) & (df_thang_chot["Tháng"] == thang_kq_m) & (df_thang_chot["Kênh_Spotify"] == kenh_kq_m))]
                    du_lieu_moi_m = pd.DataFrame([{ "Năm": nam_kq_m, "Tháng": thang_kq_m, "Kênh_Spotify": kenh_kq_m, "Doanh_Thu_USD": float(dt_kq_m), "Luot_Play": int(play_kq_m), "So_Gio_Nghe": float(gio_kq_m), "So_Tap_Upload": int(tap_kq_m), "Bat_Kiem_Tien": trang_thai_bkt_m, "Thoi_Gian_Nhap": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Link_Dan_Chung": link_dan_chung_thang }])
                    df_new_m = pd.concat([df_kq_m_filter, du_lieu_moi_m], ignore_index=True)
                    df_new_m.to_csv(FILE_KQ_THANG, index=False)
                    st.session_state.rk_kq_thang += 1
                    st.success("✅ Đã lưu kết quả THÁNG thành công!")
                    import time; time.sleep(0.5); st.rerun()

# ==========================================
# TAB 5: QUẢN LÝ DỮ LIỆU (XÓA)
# ==========================================
with tab_xoa_data:
    st.header("🛠️ Quản Lý Dữ Liệu (Xóa)")
    st.warning("⚠️ Cẩn thận: Dữ liệu đã xóa không thể khôi phục từ màn hình này (Trừ khi Boss dùng file Backup).")
    col_xoa1, col_xoa2 = st.columns(2)
    
    with col_xoa1:
        st.subheader("Xóa Kết Quả Tuần")
        if not df.empty:
            thang_xoa = st.selectbox("Chọn Tháng:", df["Tháng"].unique(), key="x_thang")
            tuan_xoa = st.selectbox("Chọn Tuần:", df[df["Tháng"] == thang_xoa]["Tuần"].unique(), key="x_tuan")
            kenh_xoa = st.selectbox("Chọn Kênh:", df[(df["Tháng"] == thang_xoa) & (df["Tuần"] == tuan_xoa)]["Kênh_Spotify"].unique(), key="x_kenh")
            if st.button("🗑️ Xóa bản ghi này"):
                df_con_lai = df[~((df["Tháng"] == thang_xoa) & (df["Tuần"] == tuan_xoa) & (df["Kênh_Spotify"] == kenh_xoa))]
                df_con_lai.to_csv(FILE_DU_LIEU, index=False)
                st.success("Đã xóa thành công!"); import time; time.sleep(0.5); st.rerun()
        else: st.info("Chưa có kết quả Tuần nào.")
        
    with col_xoa2:
        st.subheader("Xóa Mục Tiêu (KPI)")
        if not df_kpi.empty:
            thang_xoa_kpi = st.selectbox("Chọn Tháng KPI:", df_kpi["Tháng"].unique(), key="xk_thang")
            kenh_xoa_kpi = st.selectbox("Chọn Kênh KPI:", df_kpi[df_kpi["Tháng"] == thang_xoa_kpi]["Kênh_Spotify"].unique(), key="xk_kenh")
            if st.button("🗑️ Xóa KPI này"):
                df_kpi_con_lai = df_kpi[~((df_kpi["Tháng"] == thang_xoa_kpi) & (df_kpi["Kênh_Spotify"] == kenh_xoa_kpi))]
                df_kpi_con_lai.to_csv(FILE_KPI, index=False)
                st.success("Đã xóa KPI!"); import time; time.sleep(0.5); st.rerun()
        else: st.info("Chưa có KPI nào.")

# ==========================================
# TAB 6: BACKUP & RESTORE
# ==========================================
with tab_backup:
    st.header("💾 Backup & Khôi Phục Dữ Liệu")
    st.error("⚠️ LƯU Ý: Máy chủ Streamlit có thể tự reset. Hãy tải dữ liệu về máy sau khi nhập xong!")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("⬇️ Tải dữ liệu về máy")
        def read_file(path):
            if os.path.exists(path):
                with open(path, "rb") as f: return f.read()
            return None
        data_master = read_file(FILE_DU_LIEU)
        if data_master: st.download_button("📥 Tải MasterData (Kết quả Tuần)", data=data_master, file_name="MasterData.csv", mime="text/csv", use_container_width=True)
        else: st.button("📥 MasterData (Đang trống)", disabled=True, use_container_width=True)
        data_month = read_file(FILE_KQ_THANG)
        if data_month: st.download_button("📥 Tải MonthlyData (Kết quả Tháng)", data=data_month, file_name="MonthlyData.csv", mime="text/csv", use_container_width=True)
        else: st.button("📥 MonthlyData (Đang trống)", disabled=True, use_container_width=True)
        data_kpi = read_file(FILE_KPI)
        if data_kpi: st.download_button("📥 Tải KPI (Mục tiêu)", data=data_kpi, file_name="KPI.csv", mime="text/csv", use_container_width=True)
        else: st.button("📥 KPI (Đang trống)", disabled=True, use_container_width=True)

    with col2:
        st.subheader("⬆️ Khôi phục / Thêm dữ liệu")
        st.markdown("Boss có thể tải lên file CSV mới. Dữ liệu sẽ tự động được **GỘP CHUNG** với các tháng cũ (không lo bị mất)!")
        uploaded_files = st.file_uploader("Upload các file CSV (MasterData, MonthlyData, KPI):", type=['csv'], accept_multiple_files=True)
        if uploaded_files:
            if st.button("🚀 XÁC NHẬN CẬP NHẬT DỮ LIỆU", type="primary", use_container_width=True):
                so_luong_thanh_cong = 0
                for file in uploaded_files:
                    if "MasterData" in file.name or "Tuần" in file.name:
                        target_path, subset_keys = FILE_DU_LIEU, ["Tháng", "Tuần", "Kênh_Spotify"]
                    elif "MonthlyData" in file.name or "Tháng" in file.name:
                        target_path, subset_keys = FILE_KQ_THANG, ["Tháng", "Kênh_Spotify"]
                    elif "KPI" in file.name or "Mục tiêu" in file.name:
                        target_path, subset_keys = FILE_KPI, ["Tháng", "Kênh_Spotify"]
                    else: continue
                    try:
                        new_df = pd.read_csv(file)
                        if os.path.exists(target_path):
                            old_df = pd.read_csv(target_path)
                            combined_df = pd.concat([old_df, new_df], ignore_index=True)
                            combined_df = combined_df.drop_duplicates(subset=subset_keys, keep="last")
                        else:
                            combined_df = new_df
                        combined_df.to_csv(target_path, index=False)
                        so_luong_thanh_cong += 1
                    except Exception as e:
                        st.error(f"❌ Lỗi khi gộp file {file.name}: {e}")
                
                if so_luong_thanh_cong > 0:
                    st.success(f"✅ Đã CẬP NHẬT GỘP thành công {so_luong_thanh_cong} file! Đang làm mới...")
                    import time; time.sleep(1); st.rerun()
                else: st.error("❌ Không tìm thấy file hợp lệ. Vui lòng kiểm tra lại tên file.")

# ==========================================
# TAB 7: HƯỚNG DẪN CONVERT EXCEL SANG CSV
# ==========================================
with tab_huong_dan:
    st.header("🔄 Hướng Dẫn Convert Dữ Liệu")
    st.info("Khu vực này hướng dẫn cách chuyển đổi file Excel (.xlsx) gốc thành định dạng CSV chuẩn để upload vào hệ thống.")
    st.markdown("""
    ### 🚀 Các bước thực hiện:
    **Bước 1: Truy cập công cụ chuyển đổi tự động**
    * Mở đường link Google Colab dưới đây (đã được cấu hình sẵn hệ thống tự động bóc tách): 
    👉 [**NHẤN VÀO ĐÂY ĐỂ MỞ TOOL CONVERT (GOOGLE COLAB)**](https://colab.research.google.com/drive/1Qk4zOFsObtJAdCsUc-PV7CO6BF01NY7u?usp=sharing)
    **Bước 2: Tải file Excel gốc lên Colab**
    * Tại giao diện Google Colab, nhìn sang thanh menu bên trái, chọn biểu tượng **Thư mục (Files)** 📁.
    * Kéo thả file Excel của bạn (ví dụ: `Spotify_Performance_DB.xlsx`) vào khoảng trống, hoặc bấm biểu tượng mũi tên tải lên 📄.
    **Bước 3: Chạy tiến trình Convert**
    * Ở giữa màn hình Colab sẽ có một khối chứa mã code. Đưa chuột vào góc trái trên cùng của khối code đó, bấm vào nút **Play (Hình tam giác ▶️)** để chạy.
    **Bước 4: Tải file CSV về máy tính**
    * Nhìn lại sang thanh menu thư mục bên trái, bấm biểu tượng **Làm mới (Refresh 🔄)** ở ngay trên danh sách file.
    * Sẽ xuất hiện 2 file mới sinh ra là `MasterData.csv` và `KPI.csv`. Bấm vào **dấu 3 chấm ⋮** ở cuối tên mỗi file ➡️ Chọn **Download (Tải xuống)**.
    **Bước 5: Upload vào hệ thống Dashboard**
    * Quay lại trang Web Dashboard này. Chuyển sang Tab **"💾 Backup"**.
    * Tại mục **Khôi phục / Thêm dữ liệu**, kéo thả cả 2 file CSV vừa tải về vào khung Upload và bấm **Xác nhận**. Hệ thống sẽ tự động cập nhật biểu đồ!
    """)
