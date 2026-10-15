import streamlit as st
import yfinance as yf
import pandas as pd

# ページの設定
st.set_page_config(
    page_title="Stock Checker Pro",
    page_icon="📈",
    layout="centered"
)

st.title("📈 Stock Checker Pro")
st.write("銘柄コードまたは社名を入力して詳細な株価・財務情報を取得します。")

# 入力フォーム
query = st.text_input("銘柄コードまたは社名 (例: 7203, トヨタ)", value="7203")

if query:
    # 入力されたのがコードのみ（数字4桁など）の場合は '.T' を付与
    ticker_symbol = query.strip()
    if ticker_symbol.isdigit() and len(ticker_symbol) == 4:
        ticker_symbol += ".T"
    
    try:
        # yfinanceからデータを取得
        stock = yf.Ticker(ticker_symbol)
        inf = stock.info
        
        # データの存在確認
        if "regularMarketPrice" in inf or "currentPrice" in inf or "longName" in inf:
            name = inf.get("longName", inf.get("shortName", query))
            
            # 株価の取得（取れるキーを優先順位順に探す）
            price = inf.get("regularMarketPrice", inf.get("currentPrice", inf.get("previousClose", None)))
            
            # 市場情報の取得
            exchange = inf.get("exchange", "不明")
            # 東証の判定を分かりやすく整形
            market_map = {
                "JPX": "東証プライム",
                "TSE": "東証プライム",
                "TYO": "東京証券取引所"
            }
            market_name = market_map.get(exchange, inf.get("market", "東証プライム"))
            
            # 画面表示
            st.subheader(f"🏢 {name} ({query.upper()})の株価・株式情報")
            
            st.markdown("### 現在値")
            if price:
                st.markdown(f"## **{price:,.1f} 円**" if isinstance(price, float) else f"## **{price:,} 円**")
            else:
                st.warning("現在値の取得ができませんでした。")
                
            st.markdown("### 上場市場")
            st.write(f"**{market_name}** (取引所コード: {exchange})")
            
            # その他の財務指標（PER, PBRなど）
            col1, col2, col3 = st.columns(3)
            with col1:
                per = inf.get("trailingPE", "N/A")
                st.metric("PER (株価収益率)", f"{per:.2f}" if isinstance(per, (int, float)) else per)
            with col2:
                pbr = inf.get("priceToBook", "N/A")
                st.metric("PBR (株価純資産倍率)", f"{pbr:.2f}" if isinstance(pbr, (int, float)) else pbr)
            with col3:
                roe = inf.get("returnOnEquity", None)
                roe_str = f"{roe*100:.2f}%" if isinstance(roe, (int, float)) else "N/A"
                st.metric("ROE (自己資本利益率)", roe_str)
                
        else:
            st.error(f"「{query}」に該当する株価データが見つかりませんでした。正しい銘柄コードを入力してください。")
            
    except Exception as e:
        st.error(f"データの取得中にエラーが発生しました: {e}")
