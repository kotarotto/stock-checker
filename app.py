import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Stock Checker Pro", page_icon="📈", layout="wide")

st.title("📈 Stock Checker Pro")
st.caption("ファンダメンタルズ分析 ＋ 本格テクニカル分析（チャート・移動平均線クロス・RSI） × 逆引きスクリーニング")

# タブ構成
tab1, tab2 = st.tabs(["🔍 個別銘柄・詳細分析", "📋 条件からの逆引きスクリーニング"])

with tab1:
    col_input, col_param = st.columns([1, 2])
    
    with col_input:
        query = st.text_input("銘柄コードまたは社名を入力", value="7203")
        chart_period = st.selectbox("分析対象期間", ["3mo", "6mo", "1y"], index=1, format_func=lambda x: {"3mo":"3ヶ月", "6mo":"6ヶ月", "1y":"1年"}[x])
    
    with col_param:
        st.markdown("**🎯 個別判定用の基準条件設定**")
        c1, c2, c3, c4 = st.columns(4)
        target_per = c1.number_input("PER上限 (倍)", value=15.0, step=1.0)
        target_pbr = c2.number_input("PBR上限 (倍)", value=1.5, step=0.1)
        target_roe = c3.number_input("ROE下限 (%)", value=8.0, step=1.0)
        target_yield = c4.number_input("配当利回り下限 (%)", value=3.0, step=0.5)

    if query:
        code = query.strip()
        if "トヨタ" in code: code = "7203"
        elif "ソニー" in code: code = "6758"
        elif "ソフトバンク" in code: code = "9434"
        
        ticker_symbol = f"{code}.T" if code.isdigit() else code

        with st.spinner('株価データ、テクニカル指標、財務データを分析中...'):
            try:
                ticker = yf.Ticker(ticker_symbol)
                inf = ticker.info
                
                name = inf.get('longName', inf.get('shortName', f"銘柄コード: {code}"))
                current_price = inf.get('currentPrice', inf.get('regularMarketPrice', None))
                
                raw_exchange = inf.get('exchange', '')
                market = "東京証券取引所 (東証)" if ('TSE' in raw_exchange or 'JPX' in raw_exchange or ticker_symbol.endswith('.T')) else (raw_exchange or "東証")

                per = inf.get('trailingPE', None)
                pbr = inf.get('priceToBook', None)
                roe = inf.get('returnOnEquity', None)
                if roe is not None: roe = round(roe * 100, 2)
                
                dividend_yield = inf.get('dividendYield', None)
                if dividend_yield is not None: dividend_yield = round(dividend_yield * 100, 2)

                # 株価履歴取得
                hist = ticker.history(period=chart_period)
                
                if not hist.empty and current_price is not None:
                    st.markdown("---")
                    st.subheader(f"🏢 {name} ({code})")
                    
                    m1, m2, m3, m4, m5 = st.columns(5)
                    m1.metric("現在株価", f"{current_price:,.1f} 円")
                    m2.metric("上場市場", market)
                    m3.metric("PER", f"{per:.2f}倍" if per else "---")
                    m4.metric("PBR", f"{pbr:.2f}倍" if pbr else "---")
                    m5.metric("配当利回り", f"{dividend_yield}%" if dividend_yield else "---")

                    # テクニカル指標の計算（移動平均線・RSI）
                    hist['SMA5'] = hist['Close'].rolling(window=5).mean()
                    hist['SMA25'] = hist['Close'].rolling(window=25).mean()
                    hist['SMA75'] = hist['Close'].rolling(window=75).mean()

                    delta = hist['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss
                    hist['RSI'] = 100 - (100 / (1 + rs))

                    st.markdown("### 📊 本格テクニカル分析チャート（ローソク足・移動平均線・RSI）")

                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, row_heights=[0.7, 0.3])

                    fig.add_trace(go.Candlestick(
                        x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'], name='株価(ローソク足)'
                    ), row=1, col=1)

                    fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA5'], mode='lines', name='5日移動平均', line=dict(color='orange', width=1)), row=1, col=1)
                    fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA25'], mode='lines', name='25日移動平均', line=dict(color='blue', width=1.5)), row=1, col=1)
                    fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA75'], mode='lines', name='75日移動平均', line=dict(color='purple', width=1.5)), row=1, col=1)

                    fig.add_trace(go.Scatter(x=hist.index, y=hist['RSI'], mode='lines', name='RSI(14)', line=dict(color='green', width=1.5)), row=2, col=1)
                    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
                    fig.add_hline(y=30, line_dash="dash", line_color="blue", row=2, col=1)

                    fig.update_layout(xaxis_rangeslider_visible=False, height=500, margin=dict(l=20, r=20, t=20, b=20))
                    st.plotly_chart(fig, use_container_width=True)

                    # テクニカル判定ステータスの抽出
                    recent = hist.dropna(subset=['SMA25', 'SMA75'])
                    cross_score_addition = 0
                    tech_comments = []
                    
                    if len(recent) >= 2:
                        prev_diff = recent['SMA25'].iloc[-2] - recent['SMA75'].iloc[-2]
                        curr_diff = recent['SMA25'].iloc[-1] - recent['SMA75'].iloc[-1]
                        latest_rsi = hist['RSI'].dropna().iloc[-1] if not hist['RSI'].dropna().empty else 50
                        
                        col_sig1, col_sig2 = st.columns(2)
                        with col_sig1:
                            if prev_diff < 0 and curr_diff >= 0:
                                st.success("✨ 【中期ゴールデンクロス発生】25日線が75日線を上抜けしました！")
                                cross_score_addition += 1
                                tech_comments.append("・テクニカル: 中期ゴールデンクロスが発生しており、上昇トレンドへの転換シグナルが出ています。")
                            elif prev_diff > 0 and curr_diff <= 0:
                                st.error("⚠️ 【中期デッドクロス発生】25日線が75日線を下抜けしました！")
                                cross_score_addition -= 1
                                tech_comments.append("・テクニカル: 中期デッドクロスが発生しており、下落トレンドへの警戒が必要です。")
                            else:
                                trend = "上昇基調" if curr_diff > 0 else "下落/もみ合い基調"
                                st.info(f"ℹ️ 現在トレンド: **{trend}** （クロスなし）")
                                tech_comments.append(f"・テクニカル: 現在は大きなクロス発生はありません（トレンド: {trend}）。")
                        
                        with col_sig2:
                            if latest_rsi >= 70:
                                st.warning(f"⚠️ RSI: **{latest_rsi:.1f}%** （買われすぎ水準）")
                                tech_comments.append(f"・RSI: {latest_rsi:.1f}%（買われすぎ圏内のため利益確定に注意）")
                            elif latest_rsi <= 30:
                                st.success(f"✨ RSI: **{latest_rsi:.1f}%** （売られすぎ水準）")
                                cross_score_addition += 1
                                tech_comments.append(f"・RSI: {latest_rsi:.1f}%（売られすぎ圏内のため打診買いチャンス）")
                            else:
                                st.info(f"ℹ️ RSI: **{latest_rsi:.1f}%** （中立圏内）")
                                tech_comments.append(f"・RSI: {latest_rsi:.1f}%（健全な推移圏内）")

                    # AIによるファンダメンタルズ ＋ テクニカル総合判定
                    st.markdown("---")
                    st.markdown("### 🤖 AI総合投資判断・解説（ファンダメンタルズ × チャート分析）")
                    
                    fund_score = 0
                    fund_comments = []
                    
                    if per is not None and per <= target_per:
                        fund_score += 1
                        fund_comments.append(f"・PER: {per:.2f}倍 (割安基準クリア)")
                    else:
                        fund_comments.append(f"・PER: {per if per else '---'} (基準オーバーまたはデータ無)")
                        
                    if pbr is not None and pbr <= target_pbr:
                        fund_score += 1
                        fund_comments.append(f"・PBR: {pbr:.2f}倍 (基準クリア)")
                        
                    if roe is not None and roe >= target_roe:
                        fund_score += 1
                        fund_comments.append(f"・ROE: {roe:.2f}% (資本効率良好)")
                        
                    if dividend_yield is not None and dividend_yield >= target_yield:
                        fund_score += 1
                        fund_comments.append(f"・配当利回り: {dividend_yield:.2f}% (高配当基準クリア)")

                    total_score = fund_score + cross_score_addition
                    
                    st.write(f"**総合判定スコア**: {total_score} 評価 (財務スコア: {fund_score}/4 ＋ テクニカル補正: {cross_score_addition})")
                    
                    st.markdown("**【財務・ファンダメンタルズ評価】**")
                    for fc in fund_comments:
                        st.write(fc)
                        
                    st.markdown("**【チャート・テクニカル評価】**")
                    for tc in tech_comments:
                        st.write(tc)

                else:
                    st.error("データを取得できませんでした。銘柄コードをご確認ください。")
            except Exception as e:
                st.error(f"データ取得・描画中にエラーが発生しました: {e}")

with tab2:
    st.markdown("### 📋 条件からの逆引きスクリーニング")
    st.write("ご指定の条件（市場・PER・配当利回りなど）に合致する銘柄をスクリーニングします。")
    
    col_s1, col_s2, col_s3 = st.columns(3)
    target_market = col_s1.selectbox("対象市場", ["すべて", "東証プライム", "東証スタンダード", "東証グロース"])
    scr_per = col_s2.number_input("PER上限 (倍)", value=15.0, step=1.0, key="scr_per")
    scr_yield = col_s3.number_input("配当利回り下限 (%)", value=3.0, step=0.5, key="scr_yield")
    
    if st.button("スクリーニングを実行"):
        st.info(f"条件 [市場: {target_market} / PER上限: {scr_per}倍 / 配当利回り下限: {scr_yield}%] に基づくサンプルスクリーニングを実施中...")
        # サンプル用の代表銘柄リスト（必要に応じて拡張可能）
        sample_stocks = [
            {"code": "7203", "name": "トヨタ自動車", "market": "東証プライム", "per": 10.5, "yield": 3.2},
            {"code": "9434", "name": "ソフトバンク", "market": "東証プライム", "per": 14.2, "yield": 4.1},
            {"code": "6758", "name": "ソニーグループ", "market": "東証プライム", "per": 21.0, "yield": 0.6},
        ]
        
        filtered = []
        for s in sample_stocks:
            if target_market != "すべて" and s["market"] != target_market:
                continue
            if s["per"] <= scr_per and s["yield"] >= scr_yield:
                filtered.append(s)
                
        if filtered:
            df_res = pd.DataFrame(filtered)
            st.dataframe(df_res, use_container_width=True)
        else:
            st.warning("条件に一致する銘柄が見つかりませんでした。条件を緩和してお試しください。")
