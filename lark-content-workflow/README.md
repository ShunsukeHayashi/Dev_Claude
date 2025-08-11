# Lark Content Workflow System

note.com記事作成・最適化プロセスをLark Baseと統合したリアルタイムワークフローシステム

## 🎯 概要

このシステムは、note.com記事のSEO最適化プロセスをLark Baseで管理し、SSE（Server-Sent Events）によるリアルタイム更新を提供します。

### 主要機能
- 📊 Lark Base統合によるデータ管理
- 🔄 SSEによるリアルタイム進捗表示
- 📝 SEOキーワード管理
- ✅ 品質チェック機能
- 📈 パフォーマンストラッキング

## 🛠️ セットアップ

### 前提条件
- Node.js 16.0以上
- Larkアプリケーション認証情報
- Lark Base App Token

### インストール

```bash
# 依存関係のインストール
npm install

# 環境変数の設定
cp .env.example .env
# .envファイルを編集してLark認証情報を設定
```

### 起動

```bash
# 開発環境
npm run dev

# 本番環境
npm start

# テスト実行
npm test
```

## 📋 Lark Base構成

### テーブル設定

#### 記事投稿記録（tblvQlQXva14zQpa）
- **記事タイトル**: Text (Primary)
- **ステータス**: Single Select (新規/確認中/完了)
- **執筆フェーズ**: Single Select
- **文字数**: Number
- **類似度スコア**: Number
- **SEOスコア**: Number

#### SEOキーワード管理（tbl7kh3ahe0U8i67）
- **キーワード**: Text (Primary)
- **カテゴリー**: Single Select
- **優先度**: Single Select
- **検索ボリューム**: Single Select

## 🔌 API エンドポイント

### SSE Stream
```
GET /api/workflow/stream
```
リアルタイムイベントストリーム

### ワークフロー管理
```
POST /api/workflow/start
```
新しいワークフローを開始

### Lark Base操作
```
GET /api/lark/records      # レコード取得
POST /api/lark/records     # レコード作成
PUT /api/lark/records/:id  # レコード更新
```

## 📊 ワークフローステージ

1. **初期化** - ワークフロー開始
2. **調査** - キーワード調査と競合分析
3. **構成** - 記事アウトライン作成
4. **生成** - コンテンツ生成
5. **レビュー** - 品質チェック
6. **最終化** - 最終調整
7. **完了** - Lark Baseへの保存

## 🔐 環境変数

| 変数名 | 説明 | 必須 |
|--------|------|------|
| LARK_APP_ID | Larkアプリケーション ID | ✅ |
| LARK_APP_SECRET | Larkアプリケーション シークレット | ✅ |
| LARK_BASE_APP_TOKEN | Lark Base App Token | ✅ |
| LARK_BASE_TABLE_ID | 対象テーブルID | ✅ |
| PORT | サーバーポート (デフォルト: 3001) | |

## 🚀 使用方法

### 1. サーバー起動
```bash
npm start
```

### 2. ブラウザでアクセス
```
http://localhost:3001
```

### 3. SSE接続
「SSE接続」ボタンをクリックしてリアルタイムストリームに接続

### 4. ワークフロー実行
- トピックを入力
- スタイルと長さを選択
- 「ワークフロー開始」をクリック

### 5. Lark Baseで確認
「Lark Baseで表示」ボタンで実際のデータを確認

## 📝 開発メモ

### ディレクトリ構成
```
lark-content-workflow/
├── src/
│   ├── server.js           # メインサーバー
│   └── services/
│       ├── larkBaseManager.js    # Lark Base API管理
│       ├── contentWorkflow.js    # ワークフロー処理
│       └── sseManager.js         # SSE接続管理
├── public/
│   └── index.html          # Web UI
├── package.json
├── .env                    # 環境設定
└── README.md
```

## 🔧 トラブルシューティング

### Lark認証エラー
- APP_IDとAPP_SECRETが正しいか確認
- Larkアプリケーションの権限設定を確認

### SSE接続エラー
- ポート3001が使用可能か確認
- ファイアウォール設定を確認

### データ保存エラー
- Lark Base App Tokenが有効か確認
- テーブルIDが正しいか確認
- 権限設定を確認

## 📄 ライセンス

MIT