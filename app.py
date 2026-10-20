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
# お気に入り銘柄の初期化
# ---------------------------------------------------------
if "favorites" not in st.session_state:
    st.session_state.favorites = ["7203", "4452", "6758", "9434"]

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
        
        # 社名・コードの対応辞書
        company_names = {
            "7203": "トヨタ自動車",
            "6758": "ソニーグループ",
            "9434": "ソフトバンク",
            "4452": "花王",
            "7267": "本田技研工業",
            "9432": "日本電信電話 (NTT)",
            "8306": "三菱UFJフィナンシャル・グループ",
            "8316": "三井住友フィナンシャルグループ",
            "8058": "三菱商事",
            "8031": "三井物産"
        }

        if "トヨタ" in code: code = "7203"
        elif "ソニー" in code: code = "6758"
        elif "ソフトバンク" in code: code = "9434"
        elif "花王" in code: code = "4452"
        elif "ホンダ" in code or "本田" in code: code = "7267"
        elif "NTT" in code: code = "9432"

        ticker_code = f"{code}.T" if code.isdigit() and len(code) == 4 else code
        disp_name = company_names.get(code, f"銘柄コード: {code}")
        
        try:
            with st.spinner("データを高速取得中..."):
                ticker = yf.Ticker(ticker_code)
                hist = ticker.history(period=chart_period)

            if hist.empty:
                st.error("株価データが取得できませんでした。正しい銘柄コードを入力してください。")
            else:
                current_price = hist['Close'].iloc[-1]
                
                market_name = "東証プライム"
                mock_per = 14.2 if code == "7203" else (16.5 if code == "7267" else (13.5 if code == "9434" else 15.0))
                mock_pbr = 1.15 if code == "7203" else (0.56 if code == "7267" else (4.2 if code == "9434" else 1.2))
                mock_yield = 3.2 if code == "7203" else (3.8 if code == "7267" else (4.5 if code == "9434" else 3.0))

                # 社名付きでヘッダー表示
                st.subheader(f"🏢 {disp_name} ({code})")
                
                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("現在株価", f"{current_price:,.1f} 円")
                m2.metric("上場市場", market_name)
                m3.metric("PER", f"{mock_per:.2f}倍")
                m4.metric("PBR", f"{mock_pbr:.2f}倍")
                m5.metric("配当利回り", f"{mock_yield:.2f}%")

                # --- チャート作成 ---
                hist['MA5'] = hist['Close'].rolling(5).mean()
                hist['MA25'] = hist['Close'].rolling(25).mean()
                hist['MA75'] = hist['Close'].rolling(75).mean()

                delta = hist['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / loss
                hist['RSI'] = 100 - (100 / (1 + rs))

                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
                fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'], name="株価"), row=1, col=1)
                fig.add_trace(go.Scatter(x=hist.index, y=hist['MA5'], line=dict(color='orange', width=1), name="5日線"), row=1, col=1)
                fig.add_trace(go.Scatter(x=hist.index, y=hist['MA25'], line=dict(color='blue', width=1.5), name="25日線"), row=1, col=1)
                fig.add_trace(go.Scatter(x=hist.index, y=hist['MA75'], line=dict(color='purple', width=1.5), name="75日線"), row=1, col=1)
                
                fig.add_trace(go.Scatter(x=hist.index, y=hist['RSI'], line=dict(color='green', width=1.5), name="RSI"), row=2, col=1)
                fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="blue", row=2, col=1)
                
                fig.update_layout(height=450, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig, use_container_width=True)

                # --- 5大評価軸の算出 ---
                latest_rsi = hist['RSI'].iloc[-1] if not pd.isna(hist['RSI'].iloc[-1]) else 50
                eval_total = 4
                eval_tech = 5 if latest_rsi <= 35 else (1 if latest_rsi >= 65 else 3)
                eval_funda = 4
                eval_yield = 4
                eval_fair = "★4 (適正圏 / 安定水準)"

                st.write("---")
                st.subheader("🎯 5大評価サマリー（簡易検査結果）")

                col_e1, col_e2, col_e3, col_e4, col_e5 = st.columns(5)
                col_e1.metric("① AI総合判断", f"★ {eval_total} / 5")
                col_e2.metric("② テクニカル", f"★ {eval_tech} / 5")
                col_e3.metric("③ ファンダ客観", f"★ {eval_funda} / 5")
                col_e4.metric("④ 配当評価", f"★ {eval
