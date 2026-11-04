import csv
import pandas as pd
import yfinance as yf

def main():
    print("市場の全上場銘柄データを自動で取得・網羅します...")
    
    try:
        # 日本取引所グループ（JPX）の公式上場銘柄一覧CSVを自動取得
        jpx_url = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvqpnp0000038ye9-att/data_j.csv"
        df_jpx = pd.read_csv(jpx_url)
        
        updated_rows = []
        
        # ※まずは動作確認とタイムアウト防止のため、東証プライムなどの主要銘柄（または件数を絞る、あるいは全件）を処理します
        # ここでは取得できたデータから順に株価を取得してCSV用リストを作成します
        count = 0
        for _, row in df_jpx.iterrows():
            code = str(row['コード'])
            name = str(row['銘柄名'])
            market = str(row.get('市場・商品区分', ''))
            
            # 例として「プライム」市場などに絞るか、あるいは全件処理する場合は条件を外します
            if "プライム" in market:
                ticker = f"{code}.T"
                try:
                    # yfinanceで直近のデータを取得
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
                        
                        updated_rows.append([code, name, current_price, change_str])
                        print(f"取得成功: {name} ({code}) = {current_price}円")
                    else:
                        print(f"データなし: {name} ({code})")
                except Exception as ex:
                    print(f"取得エラー ({name}): {ex}")
                
                # テスト動作としてまずは主要な数十件で試す場合はここでbreakを入れられます
                # count += 1
                # if count >= 30: break

        # 取得したデータを `stock_data.csv` に書き込む
        with open('stock_data.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['code', 'name', 'price', 'change'])
            writer.writerows(updated_rows)
            
        print("stock_data.csvの網羅的更新が完了しました。")
        
    except Exception as e:
        print(f"自動取得中にエラーが発生しました: {e}")

if __name__ == '__main__':
    main()
