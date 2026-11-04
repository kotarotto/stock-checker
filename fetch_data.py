name: Update Stock Data

on:
  workflow_dispatch: # 手動実行用
  schedule:
    - cron: '0 0 * * *' # 毎日自動実行

jobs:
  run-fetcher:
    runs-on: ubuntu-latest
    permissions:
      contents: write # リポジトリへの書き込み権限
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
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git add stock_data.csv
          git diff --staged --quiet || git commit -m "Update stock_data.csv automatically"
          git push
