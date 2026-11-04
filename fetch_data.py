import csv
import concurrent.futures
import pandas as pd
import yfinance as yf

def fetch_stock(row):
    """1銘柄分のデータを取得する関数（並行処理用）"""
    code = str(row['コード'])
    name = str(row['銘柄名'])
    market = str(row.get('市場・商品区分', ''))
    
    # 東証プライム市場などの銘柄を対象にする（必要に応じて条件を変更可能です）
    if "プライム" in market:
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
                
                print(f"取得成功: {name} ({code}) = {current_price}円")
                return [code, name, current_price, change_str]
        except Exception as ex:
            print(f"取得エラー ({name}): {ex}")
    return None

def main():
    print("市場データを並行処理で高速かつ網羅的に取得します...")
    
    try:
        # 日本取引所グループ（JPX）の公式上場銘柄一覧CSVを自動取得
        jpx_url = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvqpnp0000038ye9-att/data_j.csv"
        df_jpx = pd.read_csv(jpx_url)
        
        updated_rows = []
        
        # ThreadPoolExecutorを使って同時に複数のリクエストを処理（max_workersで同時接続数を指定）
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # 全行に対して並行処理タスクを割り当て
            futures = [executor.submit(fetch_stock, row) for _, row in df_jpx.iterrows()]
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    updated_rows.append(result)

        # 取得したデータをCSVに書き込む
        with open('stock_data.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['code', 'name', 'price', 'change'])
            writer.writerows(updated_rows)
            
        print(f"stock_data.csvの網羅的更新が完了しました。合計 {len(updated_rows)} 銘柄を保存しました。")
        
    except Exception as e:
        print(f"自動取得中にエラーが発生しました: {e}")

if __name__ == '__main__':
    main()
