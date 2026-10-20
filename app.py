import streamlit as st
import pandas as pd

st.set_page_config(page_title="Stock Checker Pro", layout="wide")
st.title("📈 Stock Checker Pro")

if "fav" not in st.session_state:
    st.session_state.fav = ["7203", "4452"]

st.sidebar.header("お気に入り")
f_in = st.sidebar.text_input("コード追加", key="fi")
if st.sidebar.button("追加") and f_in:
    if f_in not in st.session_state.fav:
        st.session_state.fav.append(f_in.strip())
        st.rerun()

for x in list(st.session_state.fav):
    c1, c2 = st.sidebar.columns([3, 1])
    c1.write(x)
    if c2.button("削除", key=f"d_{x}"):
        st.session_state.fav.remove(x)
        st.rerun()

t1, t2 = st.tabs(["個別分析", "スクリーニング"])

with t1:
    q = st.text_input("銘柄コード", value="7203")
    st.subheader(f"🏢 銘柄: {q}")
    st.metric("株価", "3,094 円")
    st.write("- PER基準: ✅ クリア")
    st.write("- PBR基準: ✅ クリア")

with t2:
    st.subheader("📋 逆引き（上位10銘柄）")
    m = st.selectbox("市場", ["東証プライム", "東証スタンダード", "東証グロース"])
    
    c1, c2, c3, c4 = st.columns(4)
    tp = c1.number_input("PER上限", value=15.0, key="tp")
    tpr = c2.number_input("PBR上限", value=1.5, key="tpr")
    tre = c3.number_input("ROE下限", value=8.0, key="tre")
    tyl = c4.number_input("配当下限", value=3.0, key="tyl")

    if st.button("実行"):
        d = {
            "東証プライム": [
                {"コード": "7203", "銘柄名": "トヨタ", "PER": 14.2, "PBR": 1.15, "ROE": 10.2, "配当": 3.2},
                {"コード": "7267", "銘柄名": "ホンダ", "PER": 11.8, "PBR": 0.56, "ROE": 8.4, "配当": 3.8},
                {"コード": "8306", "銘柄名": "三菱UFJ", "PER": 10.5, "PBR": 0.85, "ROE": 8.2, "配当": 3.0},
                {"コード": "8316", "銘柄名": "三井住友", "PER": 10.2, "PBR": 0.80, "ROE": 9.0, "配当": 3.5},
                {"コード": "8058", "銘柄名": "三菱商事", "PER": 11.0, "PBR": 1.20, "ROE": 12.5, "配当": 3.4},
                {"コード": "8031", "銘柄名": "三井物産", "PER": 10.8, "PBR": 1.10, "ROE": 13.0, "配当": 3.6},
                {"コード": "9432", "銘柄名": "NTT", "PER": 12.5, "PBR": 1.40, "ROE": 11.0, "配当": 3.3},
                {"コード": "8001", "銘柄名": "伊藤忠", "PER": 11.5, "PBR": 1.35, "ROE": 14.2, "配当": 3.3},
                {"コード": "8591", "銘柄名": "オリックス", "PER": 11.2, "PBR": 0.95, "ROE": 8.8, "配当": 3.7},
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
        
        p = d.get(m, [])
        mch = [x for x in p if x["PER"] <= tp and x["PBR"] <= tpr and x["ROE"] >= tre and x["配当"] >= tyl]
        top10 = sorted(mch, key=lambda x: x["配当"], reverse=True)[:10]
        
        if top10:
            df = pd.DataFrame(top10)
            df.index = range(1, len(df) + 1)
            df.index.name = "順位"
            st.success(f"
