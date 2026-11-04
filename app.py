import os
import streamlit as st
import pandas as pd
import plotly.express as px

# ページ基本設定
st.set_page_config(
    page_title="株式個別分析・スクリーニングツール",
    page_icon="📈",
    layout="wide"
)

# 堅牢なデータ読み込み関数（複数の配置場所を自動で探します）
@st.cache_data
def load_stock_data():
    possible_paths = [
        "stock_data.csv",
        "data/stock_data.csv",
        "stock-checker/stock_data.csv"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                if not df.empty:
                    return df
            except Exception:
                continue
    # 万が一ファイルが見つからない場合の空のデータフレーム
    return pd.DataFrame()

# メインタイトル
st.title("📈 株式個別分析・スクリーニングツール")

# データ読み込み実行
df = load_stock_data()

if df.empty:
    st.warning("⚠️ 該当するデータが見つかりません（0銘柄）")
    st.info(
        "GitHubのリポジトリ内に `stock_data.csv` （または `data/stock_data.csv`）が"
        "正しくアップロードされているか確認してください。"
    )
else:
    st.success(f"✅ データ読み込み成功: {len(df)} 銘柄")

    # タブ構成の定義
    tab1, tab2, tab3 = st.tabs(["個別分析", "スクリーニング", "全データ一覧"])

    # 銘柄名やコードの列名候補を自動判定
    code_col = next((col for col in ["コード", "証券コード", "code", "Code"] if col in df.columns), df.columns[0])
    name_col = next((col for col in ["銘柄名", "名称", "name", "Name"] if col in df.columns), df.columns[1] if len(df.columns) > 1 else code_col)

    with tab1:
        st.subheader("🔍 銘柄個別分析")
        selected_stock = st.selectbox(
            "分析する銘柄を選択してください",
            df[name_col].unique() if name_col in df.columns else df[code_col].unique()
        )
        
        # 該当データの抽出
        stock_data = df[df[name_col] == selected_stock].iloc[0] if name_col in df.columns else df.iloc[0]
        
        # メトリック表示
        cols = st.columns(min(4, len(df.columns)))
        for i, col_name in enumerate(df.columns[:4]):
            with cols[i]:
                st.metric(label=col_name, value=str(stock_data[col_name]))

        st.write("### 詳細データ", stock_data)

    with tab2:
        st.subheader("🎯 条件スクリーニング")
        st.write("絞り込み条件を設定できます（準備中・必要に応じて拡張可能）")
        st.dataframe(df, use_container_width=True)

    with tab3:
        st.subheader("📊 全データ一覧")
        st.dataframe(df, use_container_width=True)
