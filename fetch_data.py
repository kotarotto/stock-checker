import csv

# 取得する銘柄のサンプルデータ
stocks = [
    {"code": "7203", "name": "トヨタ自動車", "price": 2650, "change": "+15"},
    {"code": "9984", "name": "ソフトバンクG", "price": 8500, "change": "-40"},
    {"code": "6758", "name": "ソニーグループ", "price": 13000, "change": "+120"},
    {"code": "9432", "name": "ＮＴＴ", "price": 160, "change": "+1"},
    {"code": "8306", "name": "三菱ＵＦＪ", "price": 1500, "change": "+25"}
]

def main():
    print("CSVファイルへの書き込みを開始します...")
    with open('stock_data.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['code', 'name', 'price', 'change'])
        for s in stocks:
            writer.writerow([s['code'], s['name'], s['price'], s['change']])
    print("書き込みが完了しました。")

if __name__ == '__main__':
    main()
