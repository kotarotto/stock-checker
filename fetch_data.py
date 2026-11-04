import csv
import pandas as pd
import yfinance as yf

def main():
    print("JPXから銘柄マスターを取得しています...")
    jpx_url = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvqpnp0000038ye9-att/data_j.csv"
    df_jpx = pd.read_csv(jpx_url)
    
    updated_rows = []
    
    # まず動作確認と確実な動作のため、最初の50銘柄を確実に取得してテストします
    print("株価データの取得を開始します...")
    for index, row in df_jpx.head(50).iterrows():
        code = str(row.get('コード', '')).strip()
        name = str(row.get('銘柄名', '')).strip()
        
        if not code.isdigit() or len(code) != 4:
            continue
            
        ticker = f"{code}.T"
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="2d")
            if not hist.empty:
                current_price = round(hist['Close'].iloc[-1])
                prev_price = round(hist['Close'].iloc[-2]) if len(hist) >= 2 else current_price
                change_val = current_price - prev_price
                change_str = f"+{change_val}" if change_val >= 0 else str(change_val)
                
                updated_rows.append([code, name, current_price, change_str])
                print(f"取得成功: {name} ({code}) = {current_price}円")
        except Exception as e:
            print(f"取得スキップ ({code}): {e}")
            pass

    # CSVへ書き込み
    with open('stock_data.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['code', 'name', 'price', 'change'])
        writer.writerows(updated_rows)
        
    print(f"保存完了: 合計 {len(updated_rows)} 銘柄を stock_data.csv に書き出しました。")

if __name__ == '__main__':
    main()
