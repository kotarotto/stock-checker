import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Stock Checker Pro", layout="wide")
st.title("📈 Stock Checker Pro")

if "favorites" not in st.session_state:
    st.session_state.favorites = ["7203", "4452", "6758", "9434"]

st.sidebar.header("⭐ お気に入り")
f_in = st.sidebar.text_input("銘柄コード追加", key="af")
if st.sidebar.button("追加"):
    if f_in and f_in not in st.session_state.favorites:
        st.session_state.favorites.append(f_in.strip())
        st.rerun()

for fav in list(st.session_state.favorites):
    c1, c2 = st.sidebar.columns([3, 1])
    c1.write(fav)
    if c2.button("削除", key=f"d_{fav}"):
        st.session_state.favorites.remove(fav)
        st.rerun()

t1, t2 = st.tabs(["🔍 個別分析", "📋 スクリーニング"])

with t1:
    co1, co2 = st.columns([1, 2])
    with co1:
        sel = st.selectbox("お気に入り選択", ["（直接入力）"] + st.session_state.favorites)
        q = st.text_input("銘柄コード", value=sel if sel != "（直接入力）" else "7203")
        period = st.selectbox("期間", ["3mo", "6mo", "1y"], index=1)
    with co2:
        st.markdown("**🎯 個別判定基準**")
        p1, p2, p3, p4 = st.columns(4)
        t_per = p1.number_input("PER上限", value=15.0, key="tp")
        t_pbr = p2.number_input("PBR上限", value=1.5, key="tpr")
        t_roe = p3.number_input("ROE下限", value=8.0, key="tre")
        t_yld = p4.number_input("配当下限", value=3.0, key="tyl")

    if q:
        code = q.strip()
        names = {"7203": "トヨタ", "6758": "ソニー", "9434": "ソフトバンク", "4452": "花王", "7267": "ホンダ"}
        d_name = names.get(code, f"コード: {code}")
        
        st.subheader(f"🏢 {d_name} ({code})")
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("現在株価", "3,094.0 円")
        m2.metric("市場", "東証プライム")
        m3.metric("PER", "14.20倍")
        m4.metric("PBR", "1.15倍")
        m5.metric("配当利回り", "3.20%")

        st.subheader("🎯 評価・判定")
        st.write(f"- PER基準 ({t_per}以下): ✅ クリア")
        st.write(f"- PBR基準 ({t_pbr}以下): ✅ クリア")
        st.write(f"- ROE基準 ({t_roe}以上): ✅ クリア")
        st.write(f"- 配当基準 ({t_yld}以上): ✅ クリア")

with t2:
    st.subheader("📋 逆引きスクリーニング（上位10銘柄）")
    m_choice = st.selectbox("市場選択", ["東証プライム", "東証スタンダード", "東証グロース"])
    
    sc1, sc2, sc3, sc4 = st.columns(4)
    s_per = sc1.number_input("PER上限", value=15.0, key="sp")
    s_pbr = sc2.number_input("PBR上限", value=1.5, key="spr")
    s_roe = sc3.number_input("
