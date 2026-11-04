import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==========================================
# ページ基本設定
# ==========================================
st.set_page_config(
    page_title="株式分析＆スクリーニングツール",
    page_icon="📈",
    layout="wide",
)

st.title("📈 株式個別分析・スクリーニングツール")


# ==========================================
# 1. 堅牢なデータ読み込み処理
# ==========================================
@st.cache_data(ttl=3600)
def load_data():
  # ファイルが存在しそうなパスを順番に探索（パスのズレを自動解消）
  possible_paths = [
      "stock_data.csv",
      "data/stock_data.csv",
      "./stock_data.csv",
      "../stock_data.csv",
  ]

  for path in possible_paths:
    if os.path.exists(path):
      try:
        df = pd.read_csv(path)
        if not df.empty:
          return df, path
      except Exception:
        continue

  return pd.DataFrame(), None


df, found_path = load_data()

# ==========================================
# 2. データ読み込み判定
# ==========================================
if df.empty:
  st.error("⚠️ 該当するデータが見つかりません（0 銘柄）")
  st.warning(
      "GitHub ActionsによるCSV更新・コミットが成功しているか、リポジトリ内のCSVファイル名を確認してください。"
  )
  st.stop()
else:
  # 画面上部に読み込み状態を表示
  st.success(
      f"✅ データ読み込み成功: **{len(df)} 銘柄** （取得元: `{found_path}`）"
  )

# ==========================================
# 3. メインコンテンツ（タブ切り替え）
# ==========================================
tab1, tab2, tab3 = st.tabs(
    ["🔍 個別銘柄分析", "🎯 割安・高配当スクリーニング", "📋 全データ一覧"]
)

# ------------------------------------------
# TAB 1: 個別銘柄分析（基本指標・チャート・客観評価）
# ------------------------------------------
with tab1:
  st.header("🔍 個別銘柄分析")

  # 銘柄選択（コード＋銘柄名）
  # CSV内に 'Ticker', 'Name' 列がある前提（無ければ適宜自動調整）
  if "Name" in df.columns and "Ticker" in df.columns:
    df["Select_Label"] = df["Ticker"].astype(str) + " : " + df["Name"]
  elif "Ticker" in df.columns:
    df["Select_Label"] = df["Ticker"].astype(str)
  else:
    df["Select_Label"] = df.index.astype(str)

  selected_label = st.selectbox("分析する銘柄を選択してください", df["Select_Label"])
  stock_info = df[df["Select_Label"] == selected_label].iloc[0]

  st.markdown("---")

  # 主要指標のカード表示 (Metrics)
  col1, col2, col3, col4, col5 = st.columns(5)

  # データ列が存在するかチェックしながら表示
  price = stock_info.get("Close", stock_info.get("株価", "N/A"))
  per = stock_info.get("PER", stock_info.get("PER(倍)", "N/A"))
  pbr = stock_info.get("PBR", stock_info.get("PBR(倍)", "N/A"))
  div_yield = stock_info.get(
      "DividendYield", stock_info.get("配当利回り(%)", "N/A")
  )
  roe = stock_info.get("ROE", stock_info.get("ROE(%)", "N/A"))

  col1.metric(
      "現在株価",
      f"{price:,} 円" if isinstance(price, (int, float)) else str(price),
  )
  col2.metric("PER (株価収益率)", f"{per} 倍" if pd.notnull(per) else "N/A")
  col3.metric("PBR (株価純資産倍率)", f"{pbr} 倍" if pd.notnull(pbr) else "N/A")
  col4.metric(
      "予想配当利回り",
      f"{div_yield} %" if pd.notnull(div_yield) else "N/A",
  )
  col5.metric("ROE (自己資本利益率)", f"{roe} %" if pd.notnull(roe) else "N/A")

  st.markdown("### 📊 ファンダメンタルズ客観評価")

  # 割安度・安全性の簡易チェックロジック
  eval_comments = []
  if pd.notnull(pbr) and isinstance(pbr, (int, float)):
    if pbr < 1.0:
      eval_comments.append(
          "✅ **PBR 1.0倍割れ**: 解散価値を下回っており、資産面から割安・下値が硬い傾向があります。"
      )
    else:
      eval_comments.append(
          "ℹ️ **PBR 1.0倍以上**: 資本効率への期待が織り込まれているか、割安感は限定的です。"
      )

  if pd.notnull(per) and isinstance(per, (int, float)):
    if per < 15.0:
      eval_comments.append(
          "✅ **PER 15倍未満**: 収益面から見て割安な水準に位置しています。"
      )

  if pd.notnull(div_yield) and isinstance(div_yield, (int, float)):
    if div_yield >= 3.5:
      eval_comments.append(
          "✅ **高配当インカム銘柄**: 配当利回り3.5%以上。株価の下値を支えるサポート要因となります。"
      )

  for comment in eval_comments:
    st.write(comment)

  # 全詳細データの開閉表示
  with st.expander("📝 選択銘柄の全データを表示"):
    st.json(stock_info.to_dict())

# ------------------------------------------
# TAB 2: スクリーニング（条件絞り込み）
# ------------------------------------------
with tab2:
  st.header("🎯 割安・高配当・ディフェンシブ スクリーニング")
  st.write(
      "ご自身の投資基準（軸）に合わせて条件を設定し、合致する銘柄を客観的に抽出します。"
  )

  col_s1, col_s2, col_s3 = st.columns(3)

  with col_s1:
    min_div = st.number_input(
        "最低配当利回り (%)", value=3.0, step=0.5, format="%.1f"
    )
  with col_s2:
    max_pbr = st.number_input(
        "上限 PBR (倍)", value=1.2, step=0.1, format="%.1f"
    )
  with col_s3:
    max_per = st.number_input(
        "上限 PER (倍)", value=15.0, step=1.0, format="%.1f"
    )

  # データの絞り込み処理
  filtered_df = df.copy()

  # 列名の表記表記ゆれ（英語表記・日本語表記）を考慮して絞り込み
  div_col = (
      "DividendYield" if "DividendYield" in df.columns else "配当利回り(%)"
  )
  pbr_col = "PBR" if "PBR" in df.columns else "PBR(倍)"
  per_col = "PER" if "PER" in df.columns else "PER(倍)"

  if div_col in filtered_df.columns:
    filtered_df = filtered_df[filtered_df[div_col] >= min_div]
  if pbr_col in filtered_df.columns:
    filtered_df = filtered_df[filtered_df[pbr_col] <= max_pbr]
  if per_col in filtered_df.columns:
    filtered_df = filtered_df[filtered_df[per_col] <= max_per]

  st.markdown("---")
  st.subheader(f"🔍 条件合致銘柄 : {len(filtered_df)} 件")

  if not filtered_df.empty:
    # 抽出結果のテーブル表示
    disp_cols = [
        col
        for col in ["Ticker", "Name", per_col, pbr_col, div_col, "Close"]
        if col in filtered_df.columns
    ]
    st.dataframe(
        filtered_df[disp_cols]
        if disp_cols
        else filtered_df,
        use_container_width=True,
    )

    # PER vs PBR の散布図（位置関係の可視化）
    if per_col in filtered_df.columns and pbr_col in filtered_df.columns:
      st.markdown("### 📈 割安度マップ (PER vs PBR)")
      fig = px.scatter(
          filtered_df,
          x=per_col,
          y=pbr_col,
          text=filtered_df["Name"] if "Name" in filtered_df.columns else None,
          labels={per_col: "PER (倍)", pbr_col: "PBR (倍)"},
          title="スクリーニング結果の相対評価",
      )
      fig.update_traces(textposition="top center")
      st.plotly_chart(fig, use_container_width=True)
  else:
    st.info("条件に合致する銘柄が見つかりませんでした。条件を緩和してください。")

# ------------------------------------------
# TAB 3: 全データ一覧
# ------------------------------------------
with tab3:
  st.header("📋 取得済みデータ一覧")
  st.dataframe(df, use_container_width=True)
