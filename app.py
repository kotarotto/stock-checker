import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Stock Checker Pro", page_icon="📈", layout="centered")

st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0rem; }
    .sub-text { font-size: 1rem; color: #4B5563; margin-bottom: 1.5rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📈 Stock Checker Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">銘柄コードを入力して詳細な株価・財務情報を取得します。</div>', unsafe_allow_html=True)

query = st.text_input("銘柄コード (例: 7203)")

if query:
    code = query.strip()
    ticker_symbol = f"{code}.T" if code.isdigit() else code

    with st.spinner('データを取得中...'):
        try:
            ticker = yf.Ticker(ticker_symbol)
            inf = ticker.info
            
            name = inf.get('longName', inf.get('shortName', f"銘柄コード: {code}"))
            current_price = inf.get('currentPrice', inf.get('regularMarketPrice', inf.get('previousClose', None)))
            market = inf.get('exchange', '東証')
            
            per = inf.get('trailingPE', None)
            pbr = inf.get('priceToBook', None)
            roe = inf.get('returnOnEquity', None)
            if roe is not None:
                roe = round(roe * 100, 2)
                
            dividend_yield = inf.get('dividendYield', None)
            if dividend_yield is not None:
                dividend_yield = round(dividend_yield * 100, 2)

            if current_price:
                st.subheader(f"🏢 {name} ({code}) の株価・株式情報")
                st.markdown("### 現在値")
                st.markdown(f"## **{current_price:,.1f} 円**" if isinstance(current_price, (int, float)) else f"## **{current_price} 円**")
                
                st.markdown("### 上場市場")
                st.write(market)

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("PER (株価収益率)", f"{per:.2f}倍" if per else "---")
                col2.metric("PBR (株価純資産倍率)", f"{pbr:.2f}倍" if pbr else "---")
                col3.metric("ROE (自己資本利益率)", f"{roe}%" if roe else "---")
                col4.metric("配当利回り", f"{dividend_yield}%" if dividend_yield else "---")
            else:
                st.error("データを取得できませんでした。正しい銘柄コードを入力してください。")
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
