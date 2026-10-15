import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
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

    # 条件判定ロジック
    reasons = []
    is_good = True

    if per is not None and target_per > 0:
        if per <= target_per:
            reasons.append(f"✅ PERが基準値以下 ({per}倍 ≦ {target_per}倍)")
        else:
            reasons.append(f"❌ PERが基準値より高い ({per}倍 > {target_per}倍)")
            is_good = False
    else:
        is_good = False

    if pbr is not None and target_pbr > 0:
        if pbr <= target_pbr:
            reasons.append(f"✅ PBRが基準値以下 ({pbr}倍 ≦ {target_pbr}倍)")
        else:
            reasons.append(f"❌ PBRが基準値より高い ({pbr}倍 > {target_pbr}倍)")
            is_good = False
    else:
        is_good = False

    if roe is not None:
        if roe >= target_roe:
            reasons.append(f"✅ ROEが基準値以上 ({roe}% ≧ {target_roe}%)")
        else:
            reasons.append(f"❌ ROEが基準値より低い ({roe}% < {target_roe}%)")
            is_good = False
    else:
        is_good = False

    if dyield is not None:
        if dyield >= target_yield:
            reasons.append(f"✅ 配当利回りが基準値以上 ({dyield}% ≧ {target_yield}%)")
        else:
            reasons.append(f"❌ 配当利回りが基準値より低い ({dyield}% < {target_yield}%)")
            is_good = False
    else:
        is_good = False

    return {
        "title": title,
        "market": market,
        "price": price,
        "per": per,
        "pbr": pbr,
        "roe": roe,
        "dyield": dyield,
        "mcap": mcap,
        "is_good": is_good,
        "reasons": reasons
    }

st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0rem; }
    .sub-text { font-size: 1rem; color: #4B5563; margin-bottom: 1.5rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📈 Stock Checker Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">銘柄の個別チェックと、条件に合う銘柄の逆引き（スクリーニング）ができます。</div>', unsafe_allow_html=True)

# サイドバーまたはタブで機能を切り替え
tab1, tab2 = st.tabs(["🔍 個別銘柄チェック・判定", "📋 条件から逆引き検索"])

with tab1:
    query = st.text_input("銘柄コードまたは社名を入力 (例: 7203, トヨタ)")
    
    st.markdown("### 🎯 判定用の基準条件設定")
    col_a, col_b = st.columns(2)
    with col_a:
        target_per = st.number_input("PER上限 (倍以下)", value=15.0, step=1.0)
        target_pbr = st.number_input("PBR上限 (倍以下)", value=1.5, step=0.1)
    with col_b:
        target_roe = st.number_input("ROE下限 (%以上)", value=8.0, step=1.0)
        target_yield = st.number_input("配当利回り下限 (%以上)", value=3.0, step=0.5)

    if query:
        code = query.strip()
        if not code.isdigit():
            if "トヨタ" in code: code = "7203"
            elif "ソニー" in code: code = "6758"
            elif "ソフトバンク" in code: code = "9434"
            else: code = "7203"

        with st.spinner('データを取得・判定中...'):
            data = analyze_single_stock(code, target_per, target_pbr, target_roe, target_yield, 0)

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

            st.markdown("---")
            st.markdown("### 📋 投資基準の判定結果")
            if data['is_good']:
                st.success("✨ 設定した基準をすべてクリアしています！")
            else:
                st.warning("⚠️ 設定した基準のいずれかを満たしていません。")
            
            for reason in data['reasons']:
                st.write(reason)
        else:
            st.error("データを取得できませんでした。コードを確認してください。")

with tab2:
    st.markdown("### 📋 条件に合う代表銘柄の逆引きスクリーニング")
    st.write("ボタンを押すと、主要な高配当・割安銘柄の中から条件に合うものを一括チェックします。")
    
    rev_per = st.number_input("逆引き用 PER上限", value=20.0, step=1.0, key="r_per")
    rev_yield = st.number_input("逆引き用 配当利回り下限", value=3.0, step=0.5, key="r_yield")
    
    if st.button("逆引き実行"):
        sample_codes = ["7203", "9434", "8316", "9432", "2914"] # トヨタ、ソフトバンク、三井住友、NTT、JTなど
        results = []
        with st.spinner('一括スキャン中...'):
            for c in sample_codes:
                res = analyze_single_stock(c, rev_per, 10.0, 0.0, rev_yield, 0)
                if res and res['per'] and res['dyield']:
                    if res['per'] <= rev_per and res['dyield'] >= rev_yield:
                        results.append(res)
        
        if results:
            st.success(f"{len(results)}件の銘柄が条件にヒットしました！")
            for r in results:
                st.markdown(f"**{r['title']}** (現在値: {r['price']}円 / PER: {r['per']}倍 / 配当: {r['dyield']}%)")
        else:
            st.info("条件に一致する銘柄が見つかりませんでした。条件を緩めてお試しください。")
