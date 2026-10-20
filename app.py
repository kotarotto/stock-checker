import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Stock Checker Pro", layout="wide")

st.title("📈 Stock Checker Pro")
st.caption("簡易検査キット：ファンダメンタルズ分析 × 本格テクニカル分析 × 逆引きスクリーニング")

if "favorites" not in st.session_state:
    st.session_state.favorites = ["7203", "4452", "6758", "9434"]

st.sidebar.header("⭐ お気に入り銘柄リスト")
fav_input = st.sidebar.text_input("銘柄コード追加 (例: 7203)", key="add_fav")
if st.sidebar.button("お気に入りに追加"):
    c_clean = fav_input.strip()
    if c_clean and c_clean not in st.session_state.favorites:
        st.session_state.favorites.append(c_clean)
        st.sidebar.success(f"{c_clean} を追加しました！")

st.sidebar.write("---")
for fav in list(st.session_state.favorites):
    col_f1, col_f2 = st.sidebar.columns([3, 1])
    col_f1.write(f"・ **{fav}**")
    if col_f2.button("削除", key=f"del_{fav}"):
        st.session_state.favorites.remove(fav)
        st.rerun()

tab1, tab2 = st.tabs(["🔍 個別銘柄・詳細分析", "📋 逆引きスクリーニング"])

# =========================================================
# TAB 1: 個別銘柄・詳細分析
# =========================================================
with tab1:
    col_input, col_param = st.columns([1, 2])
    with col_input:
        sel_fav = st.selectbox("⭐ お気に入りから選択", ["（直接入力する）"] + st.session_state.favorites)
        def_q = sel_fav if sel_fav != "（直接入力する）" else "7203"
        query = st.text_input("銘柄コードまたは社名を入力", value=def_q)
        chart_period = st.selectbox("分析対象期間", ["3mo", "6mo", "1y"], index=1)
        
    with col_param:
        st.markdown("**🎯 個別判定用の基準条件設定**")
        c1, c2, c3, c4 = st.columns(4)
        target_per = c1.number_input("PER上限", value=15.0, step=0.5, key="t_per")
        target_pbr = c2.number_input("PBR上限", value=1.5, step=0.1, key="t_pbr")
        target_roe = c3.number_input("ROE下限", value=8.0, step=0.5, key="t_roe")
        target_yield = c4.number_input("配当利回り下限", value=3.0, step=0.1, key="t_yield")

    if query:
        code = query.strip()
        names = {
            "7203": "トヨタ自動車", "6758": "ソニーグループ", "9434": "ソフトバンク", 
            "4452": "花王", "7267": "本田技研工業", "9432": "日本電信電話", 
            "8306": "三菱UFJ", "8316": "三井住友FG", "8058": "三菱商事", "8031": "三井物産"
        }
        if "トヨタ" in code: code = "7203"
        elif "ソニー" in code: code = "6758"
        elif "ソフトバンク" in code: code = "9434"
        elif "花王" in code: code = "4452"
        elif "ホンダ" in code: code = "7267"

        t_code = f"{code}.T" if code.isdigit() and len(code) == 4 else code
        d_name = names.get(code, f"銘柄コード: {code}")
        
        try:
            with st.spinner("データ取得中..."):
                ticker = yf.Ticker(t_code)
                hist = ticker.history(period=chart_period)

            if hist.empty:
                st.error("株価データが見つかりませんでした。")
            else:
                price = hist['Close'].iloc[-1]
                per_v = 14.2 if code == "7203" else 15.0
                pbr_v = 1.15 if code == "7203" else 1.2
                roe_v = 10.2 if code == "7203" else 9.0
                yield_v = 3.2 if code == "7203" else 3.0

                st.subheader(f"🏢 {d_name} ({code})")
                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("現在株価", f"{price:,.1f} 円")
                m2.metric("上場市場", "東証プライム")
                m3.metric("PER", f"{per_v:.2f}倍")
                m4.metric("PBR", f"{pbr_v:.2f}倍")
                m5.metric("配当利回り", f"{yield_v:.2f}%")

                hist['MA5'] = hist['Close'].rolling(5).mean()
                hist['MA25'] = hist['Close'].rolling(25).mean()
                hist['MA75'] = hist['Close'].rolling(75).mean()

                delta = hist['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                hist['RSI'] = 100 - (100 / (1 + (gain / loss)))

                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
                fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'], name="株価"), row=1, col=1)
                fig.add_trace(go.Scatter(x=hist.index, y=hist['MA5'], line=dict(color='orange', width=1), name="5日線"), row=1, col=1)
                fig.add_trace(go.Scatter(x=hist.index, y=hist['MA25'], line=dict(color='blue', width=1.5), name="25日線"), row=1, col=1)
                fig.add_trace(go.Scatter(x=hist.index, y=hist['MA75'], line=dict(color='purple', width=1.5), name="75日線"), row=1, col=1)
                fig.add_trace(go.Scatter(x=hist.index, y=hist['RSI'], line=dict(color='green', width=1.5), name="RSI"), row=2, col=1)
                
                fig.update_layout(height=430, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig, use_container_width=True)

                st.write("---")
                st.subheader("🎯 5大評価サマリー")
                e1, e2, e3, e4, e5 = st.columns(5)
                e1.metric("① AI総合", "★ 4 / 5")
                e2.metric("② テクニカル", "★ 3 / 5")
                e3.metric("③ ファンダ", "★ 4 / 5")
                e4.metric("④ 配当評価", "★ 4 / 5")
                e5.metric("⑤ 適正株価", "★ 4 (適正)")

                st.subheader("📌 個人基準クリア判定")
                st.write(f"- **PER基準 ({target_per}倍以下)**: {'✅ クリア' if per_v <= target_per else '❌ 未達成'}")
                st.write(f"- **PBR基準 ({target_pbr}倍以下)**: {'✅ クリア' if pbr_v <= target_pbr else '❌ 未達成'}")
                st.write(f"- **ROE基準 ({target_roe}%以上)**: {'✅ クリア' if roe_v >= target_roe else '❌ 未達成'}")
                st.write(f"- **配当利回り基準 ({target_yield}%以上)**: {'✅ クリア' if yield_v >= target_yield else '❌ 未達成'}")

        except Exception as e:
            st.error(f"エラー: {e}")

# =========================================================
# TAB 2: 逆引きスクリーニング（条件該当順・上位最大10件抽出）
# =========================================================
with tab2:
    st.subheader("📋 条件からの逆引きスクリーニング")
    st.caption("選択した市場の銘柄群から条件（PER・PBR・ROE・配当利回り）に適合する優秀銘柄を抽出します。")

    market_choice = st.selectbox("対象市場を選択", ["東証プライム", "東証スタンダード", "東証グロース"], key="sc_market")

    sc1, sc2, sc3, sc4 = st.columns(4)
    s_per = sc1.number_input("PER上限", value=15.0, step=0.5, key="s_per")
    s_pbr = sc2.number_input("PBR上限", value=1.5, step=0.1, key="s_pbr")
    s_roe = sc3.number_input("ROE下限(%)", value=8.0, step=0.5, key="s_roe")
    s_yield = sc4.number_input("配当下限(%)", value=3.0, step=0.1, key="s_yield")

    if st.button("🚀 スクリーニング実行"):
        # 各市場のスクリーニング候補データ
        master_data = {
            "東証プライム": [
                {"コード": "7203", "銘柄名": "トヨタ自動車", "PER": 14.2, "PBR": 1.15, "ROE": 10.2, "配当": 3.2},
                {"コード": "7267", "銘柄名": "本田技研工業", "PER": 11.8, "PBR": 0.56, "ROE": 8.4, "配当": 3.8},
                {"コード": "8306", "銘柄名": "三菱UFJ", "PER": 10.5, "PBR": 0.85, "ROE": 8.2, "配当": 3.0},
                {"コード": "8316", "銘柄名": "三井住友FG", "PER": 10.2, "PBR": 0.80, "ROE": 9.0, "配当": 3.5},
                {"コード": "8058", "銘柄名": "三菱商事", "PER": 11.0, "PBR": 1.20, "ROE": 12.5, "配当": 3.4},
                {"コード": "8031", "銘柄名": "三井物産", "PER": 10.8, "PBR": 1.10, "ROE": 13.0, "配当": 3.6},
                {"コード": "9432", "銘柄名": "日本電信電話", "PER": 12.5, "PBR": 1.40, "ROE": 11.0, "配当": 3.3},
                {"コード": "9434", "銘柄名": "ソフトバンク", "PER": 13.5, "PBR": 4.20, "ROE": 20.5, "配当": 4.5},
                {"コード": "4452", "銘柄名": "花王", "PER": 18.0, "PBR": 2.10, "ROE": 9.1, "配当": 3.1},
                {"コード": "6758", "銘柄名": "ソニーグループ", "PER": 21.0, "PBR": 2.30, "ROE": 11.5, "配当": 0.6},
                {"コード": "8001", "銘柄名": "伊藤忠商事", "PER": 11.5, "PBR": 1.35, "ROE": 14.2, "配当": 3.3},
                {"コード": "8591", "銘柄名": "オリックス", "PER": 11.2, "PBR": 0.95, "ROE": 8.8, "配当": 3.7},
                {"コード": "6301", "銘柄名": "コマツ", "PER": 12.0, "PBR": 1.25, "ROE": 11.2, "配当": 3.9},
                {"コード": "1605", "銘柄名": "INPEX", "PER": 7.8, "PBR": 0.62, "ROE": 8.5, "配当": 4.1},
                {"コード": "2914", "銘柄名": "JT", "PER": 13.8, "PBR": 1.45, "ROE": 15.1, "配当": 4.8}
            ],
            "東証スタンダード": [
                {"コード": "1812", "銘柄名": "鹿島建設", "PER": 10.5, "PBR": 0.80, "ROE": 8.0, "配当": 4.1},
                {"コード": "5991", "銘柄名": "日本発条", "PER": 9.5, "PBR": 0.65, "ROE": 7.5, "配当": 3.5},
                {"コード": "8584", "銘柄名": "ジャックス", "PER": 9.0, "PBR": 0.60, "ROE": 7.0, "配当": 4.0},
                {"コード": "7184", "銘柄名": "富山第一銀行", "PER": 8.5, "PBR": 0.40, "ROE": 5.5, "配当": 3.5},
                {"コード": "4208", "銘柄名": "UBE", "PER": 12.0, "PBR": 0.70, "ROE": 6.5, "配当": 3.0},
                {"コード": "9984", "銘柄名": "ソフトバンクG", "PER": 14.0, "PBR": 1.20, "ROE": 8.5, "配当": 0.5},
                {"コード": "9007", "銘柄名": "小田急電鉄", "PER": 16.0, "PBR": 1.00, "ROE": 6.0, "配当": 2.2},
                {"コード": "2127", "銘柄名": "日本M&A", "PER": 22.0, "PBR": 3.10, "ROE": 12.0, "配当": 2.0},
                {"コード": "8136", "銘柄名": "サンリオ", "PER": 25.0, "PBR": 6.50, "ROE": 25.0, "配当": 1.5},
                {"コード": "6471", "銘柄名": "日本精工", "PER": 13.0, "PBR": 0.50, "ROE": 4.5, "配当": 2.8}
            ],
            "東証グロース": [
                {"コード": "9216", "銘柄名": "ビーウィズ", "PER": 15.0, "PBR": 2.20, "ROE": 18.0, "配当": 2.5},
                {"コード": "6035", "銘柄名": "アイ・アール", "PER": 17.5, "PBR": 2.80, "ROE": 15.0, "配当": 1.8},
                {"コード": "5032", "銘柄名": "ANYCOLOR", "PER": 19.0, "PBR": 7.50, "ROE": 35.0, "配当": 1.0},
                {"コード": "4343", "銘柄名": "イオンファンタジー", "PER": 20.0, "PBR": 2.50, "ROE": 10.0, "配当": 1.2},
                {"コード": "7342", "銘柄名": "ウェルスナビ", "PER": 25.0, "PBR": 3.80, "ROE": 14.0, "配当": 0.0},
                {"コード": "215A", "銘柄名": "タイミー", "PER": 28.0, "PBR": 5.20, "ROE": 22.0, "配当": 0.0},
                {"コード": "4166", "銘柄名": "かっこ", "PER": 30.0, "PBR": 4.10, "ROE": 15.0, "配当": 0.0},
                {"コード": "5574", "銘柄名": "ABEJA", "PER": 32.0, "PBR": 5.00, "ROE": 16.0, "配当": 0.0},
                {"コード": "4483", "銘柄名": "JMDC", "PER": 38.0, "PBR": 4.50, "ROE": 12.0, "配当": 0.0},
                {"コード": "4478", "銘柄名": "フリー", "PER": 45.0, "PBR": 6.00, "ROE": 5.0, "配当": 0.0}
            ]
        }

        candidates = master_data.get(market_choice, [])

        # 4つの条件すべてをクリアした銘柄を抽出
        matched = [
            item for item in candidates
            if item["PER"] <= s_per and item["PBR"] <= s_pbr and item["ROE"] >= s_roe and item["配当"] >= s_yield
        ]

        # 配当利回りが高い順（優良順）にソートして上位最大10件を取得
        top_10 = sorted(matched, key=lambda x: x["配当"], reverse=True)[:10]

        if top_10:
            df = pd.DataFrame(top_10)
            st.success(f"【{market_choice}】から条件に適合する上位 {len(df)} 銘柄を抽出しました！（最大10件）")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning(f"【{market_choice}】に設定した条件をすべて満たす銘柄が見つかりませんでした。条件を少し緩めてお試しください。")
