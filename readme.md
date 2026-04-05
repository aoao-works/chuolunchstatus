chuolunchstatus/
├── .github/
│   └── workflows/
│       └── scrape.yml      # GitHub Actionsの設定ファイル
├── scraper/
│   ├── requirements.txt    # Pythonのライブラリリスト
│   └── main.py             # スクレイピングを実行するPythonスクリプト
└── public/
    ├── index.html          # フロントエンドのHTML（Next.jsの静的エクスポートでもOK）
    └── data.json           # Actionsが自動生成するJSONファイル（初期は空でOK）