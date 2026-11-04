import csv
import urllib.request
import json

# 取得したい銘柄のリスト（コードと名称）
stocks = [
    {"code": "7203", "name": "トヨタ自動車"},
    {"code": "9984", "name": "ソフトバンクG"},
    {"code": "6758", "name": "ソニーグループ"},
    {"code": "9432", "name": "ＮＴＴ"},
    {"code": "8306", "name": "三菱ＵＦＪフィナンシャル・グループ"}
]

# 簡単なサンプル価格データを生成してCSVに書き込むスクリプト
# ※実際の株価取得API等に置き換えることも可能です
def main():
    print("株価データの更新を開始します...")
    
    # stock_data.csvを書き込みモードで開く
    with open('stock_data.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        # ヘッダーの書き込み
        writer.writerow(['code', 'name', 'price', 'change'])
        
        # 各銘柄のデータを書き込む（サンプルのため固定値または仮の計算値）
        for i, stock in enumerate(stocks):
            # ダミーの価格・変動値（動的に取得する場合はここにスクレイピングやAPI処理を書きます）
            price = 1000 + (i * 500)
            change = "+10"
            writer.writerow([stock['code'], stock['name'], price, change])
            
    print("stock_data.csvの更新が完了しました。")

if __name__ == "__main__":
    main()

