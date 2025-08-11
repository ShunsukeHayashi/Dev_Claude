# 🚀 Google Cloud Run デプロイメントガイド

## 📋 Cloud Run デプロイ手順

### Step 1: Google Cloud Console設定

#### 1.1 プロジェクト確認
- **プロジェクトID**: `a-ifor-u-kjerms`
- **リージョン**: `europe-west1 (ベルギー)`
- **プロジェクトURL**: https://console.cloud.google.com/run/create?project=a-ifor-u-kjerms

#### 1.2 必要なAPIの有効化
```bash
# Cloud Run Admin API (すでに有効化済み)
# Container Registry API
# Cloud Build API
```

### Step 2: 環境変数の設定（Secret Manager使用）

#### 2.1 Secretの作成
Google Cloud Console > Security > Secret Manager で以下を作成：

```bash
# Secret名とバリュー
LARK_APP_ID: cli_a8d2fdb1f1f8d02d
LARK_APP_SECRET: V7mzILXEgIaqLwLXtyZstekRJsjRsFfJ
LARK_BASE_APP_TOKEN: WaTCbnKSiaJvMcs3cdPjxobKp8C
LARK_BASE_TABLE_ID: tblvQlQXva14zQpa
```

### Step 3: Cloud Run サービス設定

#### 3.1 基本設定
```yaml
サービス名: lark-content-workflow
リージョン: europe-west1 (ベルギー)
認証: 公開アクセスを許可する
課金: リクエストベース
```

#### 3.2 スケーリング設定
```yaml
自動スケーリング:
  最小インスタンス数: 0
  最大インスタンス数: 10
Ingress: すべて
```

#### 3.3 コンテナ設定
```yaml
コンテナポート: 8080
メモリ: 2 GiB
CPU: 2
リクエストタイムアウト: 300秒
同時リクエスト数: 80
```

### Step 4: デプロイ実行

#### 4.1 方法A: GitHub連携（推奨）
1. **GitHub**を選択
2. **リポジトリ接続**: `ShunsukeHayashi/Dev_Claude`
3. **ブランチ**: `main`
4. **Dockerfileパス**: `/lark-content-workflow/Dockerfile.cloudrun`
5. **Cloud Buildトリガー**: 有効化

#### 4.2 方法B: 手動デプロイ
```bash
# ローカルからCloud Buildでデプロイ
gcloud builds submit --config cloudbuild.yaml \
  --project a-ifor-u-kjerms \
  --substitutions COMMIT_SHA=$(git rev-parse HEAD)
```

### Step 5: 環境変数とSecretの設定

#### 5.1 環境変数
```bash
NODE_ENV=production
PORT=8080
SSE_HEARTBEAT_INTERVAL=30000
SSE_MAX_CONNECTIONS=100
CORS_ORIGIN=*
```

#### 5.2 Secretマウント
```bash
LARK_APP_ID: projects/a-ifor-u-kjerms/secrets/LARK_APP_ID/versions/latest
LARK_APP_SECRET: projects/a-ifor-u-kjerms/secrets/LARK_APP_SECRET/versions/latest
LARK_BASE_APP_TOKEN: projects/a-ifor-u-kjerms/secrets/LARK_BASE_APP_TOKEN/versions/latest
LARK_BASE_TABLE_ID: projects/a-ifor-u-kjerms/secrets/LARK_BASE_TABLE_ID/versions/latest
```

---

## 🔧 Cloud Run 最適化設定

### パフォーマンス最適化
```yaml
CPU: 2 vCPU (SSEとリアルタイム処理に最適)
Memory: 2 GiB (Node.jsアプリケーションに十分)
Concurrency: 80 (SSE接続を考慮)
Timeout: 300s (長時間ワークフロー対応)
```

### スケーリング戦略
```yaml
Min Instances: 0 (コスト最適化)
Max Instances: 10 (トラフィック急増対応)
Auto Scaling: 有効
CPU Utilization: 80% (レスポンシブ)
```

### ネットワーク設定
```yaml
Ingress: All traffic (パブリックアクセス)
VPC Connector: 不要 (外部API統合)
Load Balancer: Cloud Run内蔵
CDN: Cloud CDNオプション
```

---

## 📊 予想されるパフォーマンス

### レスポンス時間
- **ヘルスチェック**: < 50ms
- **API エンドポイント**: < 200ms
- **SSE接続確立**: < 100ms
- **ワークフロー開始**: < 500ms

### スケーラビリティ
- **同時接続**: 最大800 SSE接続
- **スループット**: 1,000 req/sec
- **ワークフロー並列処理**: 10並列

### コスト予想
```yaml
無料枠内の使用（月間）:
- vCPU秒: 180,000秒以内
- メモリ: 360,000 GiB秒以内
- リクエスト: 200万以内

推定コスト（無料枠超過時）:
- 小規模: $0-10/月
- 中規模: $10-50/月
- 大規模: $50-100/月
```

---

## 🔍 デプロイ後の確認

### 1. ヘルスチェック
```bash
curl https://lark-content-workflow-276159858808.europe-west1.run.app/health
```

**期待レスポンス:**
```json
{
  "status": "healthy",
  "activeConnections": 0,
  "larkBase": {
    "connected": true,
    "appToken": "configured"
  },
  "timestamp": "2025-08-11T15:00:00.000Z"
}
```

### 2. SSE接続テスト
```bash
curl -H "Accept: text/event-stream" \
  https://lark-content-workflow-276159858808.europe-west1.run.app/api/workflow/stream
```

### 3. Lark Base連携確認
```bash
curl https://lark-content-workflow-276159858808.europe-west1.run.app/api/lark/records
```

### 4. ワークフロー実行テスト
```bash
curl -X POST \
  https://lark-content-workflow-276159858808.europe-west1.run.app/api/workflow/start \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Cloud Run デプロイテスト",
    "parameters": {
      "style": "professional",
      "length": "medium"
    }
  }'
```

---

## 🛠️ CI/CD自動化

### GitHub Actions設定
```yaml
# .github/workflows/deploy-cloudrun.yml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]
    paths: ['lark-content-workflow/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - id: 'auth'
        uses: 'google-github-actions/auth@v1'
        with:
          credentials_json: '${{ secrets.GCP_SA_KEY }}'
      
      - name: 'Deploy to Cloud Run'
        uses: 'google-github-actions/deploy-cloudrun@v1'
        with:
          service: 'lark-content-workflow'
          image: 'gcr.io/a-ifor-u-kjerms/lark-content-workflow:latest'
          region: 'europe-west1'
```

---

## 📈 監視・運用

### Cloud Monitoring設定
```yaml
監視項目:
- Response Latency: < 2秒
- Error Rate: < 1%
- Instance Count: 適切なスケーリング
- Memory Utilization: < 80%
- CPU Utilization: < 70%

アラート設定:
- Error Rate > 5%: Email + SMS
- Latency > 5秒: Email通知
- Instance > 8: スケール監視
```

### ログ監視
```bash
# Cloud Loggingでログ確認
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=lark-content-workflow" --limit=50
```

---

## 🎯 Cloud Run デプロイの利点

### サーバーレスの利点
- **自動スケーリング**: トラフィックに応じた自動調整
- **コスト効率**: 使用分のみ課金
- **高可用性**: Google インフラの信頼性
- **管理不要**: インフラ保守が不要

### SSEアプリケーションに最適
- **持続的接続**: WebSocket類似の機能
- **リアルタイム**: 低遅延通信
- **スケーラブル**: 多数同時接続対応
- **統合**: Google Cloud サービス連携

---

**🚀 Cloud Run Console で「作成」ボタンをクリックしてデプロイを開始してください！**

設定が完了したら、生成されるサービスURLをお知らせください。