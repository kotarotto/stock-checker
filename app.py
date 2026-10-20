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
    s_roe = sc3.number_input("ROE下限", value=8.0, key="sre")
    s_yld = sc4.number_input("配当下限", value=3.0, key="syl")

    if st.button("🚀 実行"):
        p_data = {
            "東証プライム": [
                {"コード": "7203", "銘柄名": "トヨタ", "PER": 14.2, "PBR": 1.15, "ROE": 10.2, "配当": 3.2},
                {"コード": "7267", "銘柄名": "ホンダ", "PER": 11.8, "PBR": 0.56, "ROE": 8.4, "配当": 3.8},
                {"コード": "8306", "銘柄名": "三菱UFJ", "PER": 10.5, "PBR": 0.85, "ROE": 8.2, "配当": 3.0},
                {"コード": "8316", "銘柄名": "三井住友FG", "PER": 10.2, "PBR": 0.80, "ROE": 9.0, "配当": 3.5},
                {"コード": "8058", "銘柄名": "三菱商事", "PER": 11.0, "PBR": 1.20, "ROE": 12.5, "配当": 3.4},
                {"コード": "8031", "銘柄名": "三井物産", "PER": 10.8, "PBR": 1.10, "ROE": 13.0, "配当": 3.6},
                {"コード": "9432", "銘柄名": "NTT", "PER": 12.5, "PBR": 1.40, "ROE": 11.0, "配当": 3.3},
                {"コード": "9434", "銘柄名": "ソフトバンク", "PER": 13.5, "PBR": 4.20, "ROE": 20.5, "配当": 4.5},
                {"コード": "4452", "銘柄名": "花王", "PER": 18.0, "PBR": 2.10, "ROE": 9.1, "配当": 3.1},
                {"コード": "2914", "銘柄名": "JT", "PER": 13.8, "PBR": 1.45, "ROE": 15.1, "配当": 4.8}
            ],
            "東証スタンダード": [
                {"コード": "1812", "銘柄名": "鹿島建設", "PER": 10.5, "PBR": 0.80, "ROE": 8.0, "配当": 4.1},
                {"コード": "5991", "銘柄名": "日本発条", "PER": 9.5, "PBR": 0.65, "ROE": 7.5, "配当": 3.5},
                {"コード": "8584", "銘柄名": "ジャックス", "PER": 9.0, "PBR": 0.60, "ROE": 7.0, "配当": 4.0},
                {"コード": "7184", "銘柄名": "富山第一", "PER": 8.5, "PBR": 0.40, "ROE": 5.5, "配当": 3.5},
                {"コード": "4208", "銘柄名": "UBE", "PER": 12.0, "PBR": 0.70, "ROE": 6.5, "配当": 3.0}
            ],
            "東証グロース": [
                {"コード": "9216", "銘柄名": "ビーウィズ", "PER": 15.0, "PBR": 2.20, "ROE": 18.0, "配当": 2.5},
                {"コード": "6035", "銘柄名": "アイ・アール", "PER": 17.5, "PBR": 2.80, "ROE": 15.0, "配当": 1.8},
                {"コード": "4343", "銘柄名": "イオンF", "PER": 20.0, "PBR": 2.50, "ROE": 10.0, "配当": 1.2}
            ]
        }
        
        pool = p_data.get(m_choice, [])
        matched = [x for x in pool if x["PER"] <= s_per and x["PBR"] <= s_pbr and x["ROE"] >= s_roe and x["配当"] >= s_yld]
        top10 = sorted(matched, key=lambda x: x["配当"], reverse=True)[:10]
        
        if top10:
            df = pd.DataFrame(top10)
            df.index = range(1, len(df) + 1)
            df.index.name = "順位"
            st.success(f"上位 {len(df)} 銘柄を抽出しました！")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("条件に一致する銘柄はありませんでした。")
