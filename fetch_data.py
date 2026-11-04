name: Update Stock Data

on:
  workflow_dispatch: # 手動実行用
  schedule:
    - cron: '0 0 * * *' # 毎日自動実行する場合

jobs:
  run-fetcher:
    runs-on: ubuntu-latest
    permissions:
      contents: write # 変更をリポジトリに書き込む権限
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install pandas yfinance

      - name: Run fetch script
        run: python fetch_data.py

      - name: Commit and push changes
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "Update stock_data.csv automatically"
          file_pattern: stock_data.csv
    ```

### 今後の手順
1. `.github/workflows/` 内のYAMLファイルを上記の内容で保存します。
2. Actionsタブからもう一度 **「Run workflow」** で手動実行します。
3. 実行が完了したあと、リポジトリのファイル一覧に戻ると、`stock_data.csv` の更新日時が今に変わり、中身が更新されているのが確認できます。
4. その後、Streamlit Cloudの画面を再起動（Reboot）すれば、新しいデータが反映されます！
