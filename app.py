import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---------------------------------------------------------
# ページ設定
# ---------------------------------------------------------
st.set_page_config(page_title="Stock Checker Pro", layout="wide")

st.title("📈 Stock Checker Pro")
st.caption("簡易検査キット：ファンダメンタルズ分析 × 本格テクニカル分析 × 逆引きスクリーニング")

# ---------------------------------------------------------
# お気に入り銘柄の初期化（Session State）
# ---------------------------------------------------------
if "favorites" not in st.session_state:
    st.session_state.favorites = ["7203", "4452", "6758", "9434"]

# サイドバーでお気に入り管理
st.sidebar.header("⭐ お気に入り銘柄リスト")
fav_input = st.sidebar.text_input("銘柄コード追加 (例: 7203)", key="add_fav")
if st.sidebar.button("お気に入りに追加"):
    code_clean = fav_input.strip()
    if code_clean and code_clean not in st.session_state.favorites:
        st.session_state.favorites.append(code_clean)
        st.sidebar.success(f"{code_clean} を追加しました！")

st.sidebar.write("---")
st.sidebar.write("登録済み銘柄:")
for fav in list(st.session_state.favorites):
    col_f1, col_f2 = st.sidebar.columns([3, 1])
    col_f1.write(f"・ **{fav}**")
    if col_f2.button("削除", key=f"del_{fav}"):
        st.session_state.favorites.remove(fav)
        st.rerun()

# ---------------------------------------------------------
# 補助関数：市場名の短縮化
# ---------------------------------------------------------
def format_market_name(raw_exchange):
    if not raw_exchange or raw_exchange == "---":
        return "東証"
    raw_str = str(raw_exchange).upper()
    if "PRIM" in raw_str or "JPX" in raw_str:
        return "東証プライム"
    elif "STAN" in raw_str:
        return "東証スタンダード"
    elif "GROW" in raw_str or "MOTH" in raw_str:
        return "東証グロース"
    elif "TOKYO" in raw_str or "TSE" in raw_str:
        return "東証プライム（推定）"
    return str(raw_exchange)

# ---------------------------------------------------------
# 補助関数：配当利回り・データの正規化
# ---------------------------------------------------------
def clean_financial_data(info):
    # PER
    per = info.get("trailingPE") or info.get("forwardPE")
    # PBR
    pbr = info.get("priceToBook")
    # ROE
    roe = info.get("returnOnEquity")
    if roe is not None:
        roe = roe * 100 if roe < 1.0 else roe

    # 配当利回り (yfinanceの単位異常バグ修正)
    div_yield = info.get("dividendYield")
    if div_yield is not None:
        if div_yield > 1.0:
            if div_yield > 50:
                div_yield = div_yield / 100.0
        else:
            div_yield = div_yield * 100.0
    else:
        div_yield = 0.0

    # EPS / BPS
    eps = info.get("trailingEps") or info.get("forwardEps")
    bps = info.get("bookValue")
    
    return {
        "per": per,
        "pbr": pbr,
        "roe": roe,
        "yield": div_yield,
        "eps": eps,
        "bps": bps,
        "market": format_market_name(info.get("exchange")),
        "name": info.get("shortName") or info.get("longName") or "不明銘柄"
    }

# ---------------------------------------------------------
# タブ構成
# ---------------------------------------------------------
tab1, tab2 = st.tabs(["🔍 個別銘柄・詳細分析", "📋 条件からの逆引きスクリーニング"])

# =========================================================
# TAB 1: 個別銘柄・詳細分析
# =========================================================
with tab1:
    col_input, col_param = st.columns([1, 2])
    
    with col_input:
        selected_fav = st.selectbox("⭐ お気に入りから選択", ["（直接入力する）"] + st.session_state.favorites)
        default_query = selected_fav if selected_fav != "（直接入力する）" else "7203"
        query = st.text_input("銘柄コードまたは社名を入力", value=default_query)
        chart_period = st.selectbox("分析対象期間", ["3mo", "6mo", "1y", "2y"], index=1)
        
    with col_param:
        st.markdown("**🎯 個別判定用の基準条件設定**")
        c1, c2, c3, c4 = st.columns(4)
        target_per = c1.number_input("PER上限 (倍)", value=15.0, step=0.5)
        target_pbr = c2.number_input("PBR上限 (倍)", value=1.5, step=0.1)
        target_roe = c3.number_input("ROE下限 (%)", value=8.0, step=0.5)
        target_yield = c4.number_input("配当利回り下限 (%)", value=3.0, step=0.1)

    if query:
        code = query.strip()
        # 社名入力時の簡易コード変換
        
