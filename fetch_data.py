import csv
import concurrent.futures
import pandas as pd
import yfinance as yf

def fetch_stock(row):
    code = str(row.get('コード', '')).strip()
    name = str(row.get('銘柄名', '')).strip()
    
    if not code.isdigit() or len(code) != 4:
        return None
        
    ticker = f"{code}.T"
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="2d")
        
        if not hist.empty:
            current_price = round(hist['Close'].iloc[-1])
            if len(hist) >= 2:
                prev_price = hist['Close'].iloc[-2]
                change_val = current_price - prev_price
                change_str = f"+{change_val}" if change_val >= 0 else str(change_val)
            else:
                change_str = "0"
            return [code, name, current_price, change_str]
    except Exception:
        pass
        
    return None

def main():
    print("市場データ取得開始...")
    try:
        jpx_url = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvqpnp0000038ye9-att/data_j.csv"
        df_jpx = pd.read_csv(jpx_url)
        print(f"JPXから銘柄マスター取得成功: {len(df_jpx)} 行")
        
        updated_rows = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(fetch_stock, row) for _, row in df_jpx.iterrows()]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    updated_rows.append(result)

        print(f"有効な取得データ数: {len(updated_rows)} 件")

        if len(updated_rows) > 0:
            with open('stock_data.csv', 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['code', 'name', 'price', 'change'])
                writer.writerows(updated_rows)
            print("stock_data.csv を正常に上書き保存しました。")
        else:
            print("警告: 取得できたデータが0件です。")
            
    except Exception as e:
        print(f"エラー発生: {e}")

if __name__ == '__main__':
    main()
