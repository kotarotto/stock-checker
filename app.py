import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Stock Checker Pro", page_icon="📈", layout="centered")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def parse_market_cap(text):
    try:
        clean_text = text.replace(',', '')
        trillion, billion = 0, 0
        if '兆' in clean_text:
            parts = clean_text.split('兆')
            trillion = float(re.sub(r'[^\d\.]', '', parts[0]))
            clean_text = parts[1] if len(parts) > 1 else ''
        if '億' in clean_text:
            billion = float(re.sub(r'[^\d\.]', '', clean_text.split('億')[0]))
        return trillion * 10000 + billion
    except:
        return None

def analyze_single_stock(code, target_per, target_pbr, target_roe, target_yield, min_market_cap):
    url = f"https://finance.yahoo.co.jp/quote/{code}.T"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        return None

    soup = BeautifulSoup(res.text, 'html.parser')

    try:
        title_elem = soup.find('h1')
        title = title_elem.text.strip().replace(" [", "").replace("]", "") if title_elem else f"銘柄コード: {code}"
    except:
        title = f"銘柄コード: {code}"

    market = "東証"
    full_txt = soup.get_text()
    if "プライム" in full_txt: market = "東証プライム"
    elif "スタンダード" in full_txt: market = "東証スタンダード"
    elif "グロース" in full_txt: market = "東証グロース"

    price = "---"
    for span in soup.find_all(['span', 'p', 'div']):
        cls = span.get('class', [])
        cls_str = " ".join(cls) if isinstance(cls, list) else str(cls)
        if 'StyledNumber' in cls_str or 'Price__number' in cls_str or 'price' in cls_str.lower():
            text = span.text.strip()
            clean_p = text.replace(',', '').replace('.', '')
            if clean_p.isdigit() and len(clean_p) > 0:
                price = text
                break

    per, pbr, roe, dyield, mcap = None, None, None, None, None

    per_match = re.search(r'PER[^\d]*([\d\.]+)倍', full_txt)
    if per_match: per = float(per_match.group(1))

    pbr_match = re.search(r'PBR[^\d]*([\d\.]+)倍', full_txt)
    if pbr_match: pbr = float(pbr_match.group(1))

    roe_match = re.search(r'ROE[^\d]*([\d\.]+)%', full_txt)
    if roe_match: roe = float(roe_match.group(1))

    yield_match = re.search(r'配当利回り[^\d]*([\d\.]+)%', full_txt)
    if yield_match: dyield = float(yield_match.group(1))

    cap_match = re.search(r'時価総額[^\d]*([\d,兆億]+円)', full_txt)
    if cap_match: mcap = parse_market_cap(cap_match.group(1))

    return {
        "title": title,
        "market": market,
        "price": price,
        "per": per,
        "pbr": pbr,
        "roe": roe,
        "dyield": dyield,
        "mcap": mcap
    }

st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0rem; }
    .sub-text { font-size: 1rem; color: #4B5563; margin-bottom: 1.5rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📈 Stock Checker Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">銘柄コードまたは社目を入力して詳細な株価・財務情報を取得します。</div>', unsafe_allow_html=True)

query = st.text_input("銘柄コードまたは社名 (例: 7203, トヨタ)")

if query:
    code = query.strip()
    if not code.isdigit():
        if "トヨタ" in code: code = "7203"
        elif "ソニー" in code: code = "6758"
        elif "ソフトバンク" in code: code = "9434"
        else: code = "7203"

    with st.spinner('データを取得中...'):
        data = analyze_single_stock(code, 20, 2.5, 8, 2, 0)

    if data:
        st.subheader(f"🏢 {data['title']}の株価・株式情報")
        st.markdown("### 現在値")
        st.markdown(f"## **{data['price']} 円**")
        st.markdown("### 上場市場")
        st.write(data['market'])

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("PER (株価収益率)", f"{data['per']}倍" if data['per'] else "---")
        col2.metric("PBR (株価純資産倍率)", f"{data['pbr']}倍" if data['pbr'] else "---")
        col3.metric("ROE (自己資本利益率)", f"{data['roe']}%" if data['roe'] else "---")
        col4.metric("配当利回り", f"{data['dyield']}%" if data['dyield'] else "---")
    else:
        st.error("データを取得できませんでした。コードを確認してください。")
