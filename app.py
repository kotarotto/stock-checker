import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Stock Checker Pro", layout="wide")
st.title("📈 Stock Checker Pro (本格スクリーニング版)")

# 保存されたCSVデータがあれば読み込む、なければ空のリスト
@st.cache_data
def load_stock_data():
    if os.path.exists("stock_data.csv"):
        return pd.read_csv("stock_data.csv")
    return pd.DataFrame(columns=["コード", "銘柄名", "PER", "PBR", "ROE", "配当"])

df_all = load_stock_data()

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
    match = df_all[df_all["コード"].astype(str) == str(q)]
    if not match.empty:
        r = match.iloc[0]
        st.metric("株価データ（取得済）", f"PER: {r['PER']}倍 / PBR: {r['PBR']}倍")
        st.write(f"- 銘柄名: {r['銘柄名']}")
        st.write(f"- ROE: {r['ROE']}%")
        st.write(f"- 配当利回り: {r['配当']}%")
    else:
        st.info("データがまだありません。スクリーニングタブでデータを更新するか、銘柄を追加してください。")

with t2:
    st.subheader("📋 本格スクリーニング")
    st.write(f"現在保持しているデータ数: {len(df_all)} 銘柄")
    
    c1, c2, c3, c4 = st.columns(4)
    tp = c1.number_input("PER上限", value=15.0, key="tp")
    tpr = c2.number_input("PBR上限", value=1.5, key="tpr")
    tre = c3.number_input("ROE下限", value=8.0, key="tre")
    tyl = c4.number_input("配当下限", value=3.0, key="tyl")

    if st.button("スクリーニング実行") and not df_all.empty:
        mch = df_all[
            (df_all["PER"] <= tp) & 
            (df_all["PBR"] <= tpr) & 
            (df_all["ROE"] >= tre) & 
            (df_all["配当"] >= tyl)
        ]
        top10 = mch.sort_values(by="配当", ascending=False).head(10)
        
        if not top10.empty:
            res_df = top10.reset_index(drop=True)
            res_df.index = range(1, len(res_df) + 1)
            res_df.index.name = "順位"
            st.success(f"条件に一致する {len(res_df)} 銘柄を抽出しました！")
            st.dataframe(res_df, use_container_width=True)
        else:
            st.warning("条件に一致する銘柄はありませんでした。")
