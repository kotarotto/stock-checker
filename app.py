import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import pandas as pd

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
        title = title_elem.text.strip().replace("【", "").replace("】", "") if title_elem else f"銘柄コード: {code}"
        
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
        
        per_match = re.search(r'PER[^\d]*([\d\.]+)\s*倍', full_txt)
        if per_match: per = float(per_match.group(1))
        
        pbr_match = re.search(r'PBR[^\d]*([\d\.]+)\s*倍', full_txt)
        if pbr_match: pbr = float(pbr_match.group(1))

        roe_match = re.search(r'ROE[^\d]*([\d\.]+)\s*%', full_txt)
        if roe_match: roe = float(roe_match.group(1))

        yield_match = re.search(r'配当利回り[^\d]*([\d\.]+)\s*%', full_txt)
        if yield_match: dyield = float(yield_match.group(1))

        cap_match = re.search(r'時価総額[^\d]*([\d,兆億]+円)', full_txt)
        if cap_match: mcap = parse_market_cap(cap_match.group(1))

    except Exception:
        pass

    fund_score = 0
    metrics_detail = []
    
    if per is not None:
        if per < target_per:
            fund_score += 25
            status_per = f"割安 (基準 {target_per}倍以下)"
        else:
            status_per = f"割高/標準 (基準 {target_per}倍)"
        val_per = f"{per:.1f} 倍"
    else:
        status_per = "データなし/赤字"
        val_per = "---"
    metrics_detail.append({"指標": "PER (株価収益率)", "実績値": val_per, "評価・判定": status_per})

    if pbr is not None:
        if pbr < target_pbr:
            fund_score += 25
            status_pbr = f"割安 (基準 {target_pbr}倍以下)"
        else:
            status_pbr = f"割高/標準 (基準 {target_pbr}倍)"
        val_pbr = f"{pbr:.2f} 倍"
    else:
        status_pbr = "データなし"
        val_pbr = "---"
    metrics_detail.append({"指標": "PBR (株価純資産倍率)", "実績値": val_pbr, "評価・判定": status_pbr})

    if roe is not None:
        if roe >= target_roe:
            fund_score += 25
            status_roe = f"高収益性 (基準 {target_roe}%以上)"
        else:
            status_roe = f"収益性低め (基準 {target_roe}%)"
        val_roe = f"{roe:.1f} %"
    else:
        status_roe = "データなし"
        val_roe = "---"
    metrics_detail.append({"指標": "ROE (自己資本利益率)", "実績値": val_roe, "評価・判定": status_roe})

    if dyield is not None:
        if dyield >= target_yield:
            fund_score += 25
            status_yield = f"高配当 (基準 {target_yield}%以上)"
        else:
            status_yield = f"低・中配当 (基準 {target_yield}%)"
        val_yield = f"{dyield:.2f} %"
    else:
        status_yield = "無配/データなし"
        val_yield = "---"
    metrics_detail.append({"指標": "配当利回り", "実績値": val_yield, "評価・判定": status_yield})

    if mcap is not None:
        if mcap >= min_market_cap:
            status_mcap = f"十分な規模 (基準 {min_market_cap:,.0f}億円以上)"
        else:
            status_mcap = f"小型株 (基準 {min_market_cap:,.0f}億円未満)"
        val_mcap = f"{mcap:,.0f} 億円"
    else:
        status_mcap = "データなし"
        val_mcap = "---"
    metrics_detail.append({"指標": "時価総額", "実績値": val_mcap, "評価・判定": status_mcap})

    if fund_score >= 75:
        recommendation = "【買い検討】主要指標をクリアしており、割安感または高い還元性が期待できます。"
    elif fund_score >= 50:
        recommendation = "【押し目買い・監視】指標は平均的です。株価の調整局面を待つのが推奨されます。"
    else:
        recommendation = "【様子見】指標面の魅力が限定的、またはIPO/赤字成長株のためテクニカル重視の取引が望ましいです。"

    return {
        "code": code, "title": title, "market": market, "price": price,
        "fund_score": fund_score, "recommendation": recommendation, "metrics_detail": metrics_detail
    }

st.title("📈 Stock Checker Pro")

st.sidebar.header("⚙️ 判定基準の設定")
target_per = st.sidebar.number_input("PER 基準 (倍以下)", value=15.0, step=0.5)
target_pbr = st.sidebar.number_input("PBR 基準 (倍以下)", value=1.0, step=0.1)
target_roe = st.sidebar.number_input("ROE 基準 (%以上)", value=8.0, step=0.5)
target_yield = st.sidebar.number_input("配当利回り (%以上)", value=3.5, step=0.1)
min_market_cap = st.sidebar.number_input("時価総額 (億円以上)", value=100.0, step=50.0)

user_input = st.text_input("銘柄コードまたは社名（例: 290A, 7203, トヨタ）", value="7203")

if st.button("🚀 詳細分析を実行", type="primary"):
    if user_input:
        with st.spinner("詳細データを解析中..."):
            code = user_input.upper().strip()
            if not (len(code) == 4 and code.isalnum()):
                search_url = f"https://finance.yahoo.co.jp/search?query={urllib.parse.quote(user_input)}"
                res = requests.get(search_url, headers=HEADERS)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    for a in soup.find_all('a', href=True):
                        m = re.search(r'/quote/([A-Za-z0-9]{4})\.T', a['href'])
                        if m:
                            code = m.group(1)
                            break
            
            data = analyze_single_stock(code, target_per, target_pbr, target_roe, target_yield, min_market_cap)
            if data:
                st.markdown(f"## 🏢 {data['title']} ({data['code']})")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("現在値", f"{data['price']} 円")
                col2.metric("上場市場", data['market'])
                col3.metric("スコア", f"{data['fund_score']}/100")

                st.info(f"**【判定アドバイス】**: {data['recommendation']}")
                
                st.subheader("📊 詳細指標チェックリスト")
                df = pd.DataFrame(data['metrics_detail'])
                st.table(df)
            else:
                st.error("銘柄データが見つかりませんでした。")
