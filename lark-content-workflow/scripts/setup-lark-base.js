import * as lark from '@larksuiteoapi/node-sdk';
import { config } from 'dotenv';

// Load environment variables
config();

/**
 * Lark Base初期セットアップスクリプト
 * 必要なテーブルとフィールドを自動作成
 */
class LarkBaseSetup {
  constructor() {
    this.client = new lark.Client({
      appId: process.env.LARK_APP_ID,
      appSecret: process.env.LARK_APP_SECRET,
      appType: lark.AppType.SelfBuild,
      domain: lark.Domain.Lark,
    });
    
    this.baseAppToken = process.env.LARK_BASE_APP_TOKEN;
  }

  /**
   * テーブル定義
   */
  getTableDefinitions() {
    return {
      // 記事投稿記録（拡張版）
      articlesTable: {
        name: '記事投稿記録_拡張版',
        fields: [
          { field_name: '記事タイトル', type: 1 }, // Text
          { field_name: 'AIカテゴリ', type: 3, property: { options: [{ name: 'AI活用' }, { name: 'DX' }, { name: '技術解説' }] } }, // Single Select
          { field_name: '記事URL', type: 15 }, // URL
          { field_name: 'ステータス', type: 3, property: { options: [{ name: '新規' }, { name: '確認中' }, { name: '完了' }] } },
          { field_name: '執筆フェーズ', type: 3, property: { options: [{ name: '調査' }, { name: '執筆' }, { name: '編集' }, { name: 'レビュー' }, { name: '公開' }] } },
          { field_name: '文字数', type: 2 }, // Number
          { field_name: '類似度スコア', type: 2 },
          { field_name: 'SEOスコア', type: 2 },
          { field_name: '内部リンク数', type: 2 },
          { field_name: '画像数', type: 2 },
          { field_name: 'H2見出し数', type: 2 },
          { field_name: 'H3見出し数', type: 2 },
          { field_name: 'メタディスクリプション', type: 1, property: { type: 'text' } },
          { field_name: '初稿完成日', type: 5 }, // Date
          { field_name: 'レビュー完了日', type: 5 },
          { field_name: '公開予定日', type: 5 },
          { field_name: 'PV数_1週間', type: 2 },
          { field_name: 'PV数_1ヶ月', type: 2 },
          { field_name: '検索順位', type: 2 },
        ]
      },

      // SEOキーワード管理（拡張版）
      keywordsTable: {
        name: 'SEOキーワード管理_拡張版',
        fields: [
          { field_name: 'キーワード', type: 1 },
          { field_name: 'カテゴリー', type: 3, property: { options: [{ name: 'AI' }, { name: 'DX' }, { name: '技術' }] } },
          { field_name: '優先度', type: 3, property: { options: [{ name: '最優先' }, { name: '第2' }, { name: '第3' }, { name: '低' }] } },
          { field_name: '使用場所', type: 4, property: { options: [{ name: 'タイトル' }, { name: 'H1' }, { name: 'H2' }, { name: '本文' }] } }, // Multi Select
          { field_name: '検索ボリューム', type: 3, property: { options: [{ name: '高' }, { name: '中' }, { name: '低' }] } },
          { field_name: '競合度', type: 3, property: { options: [{ name: '高' }, { name: '中' }, { name: '低' }] } },
          { field_name: '競合記事URL1', type: 15 },
          { field_name: '競合記事URL2', type: 15 },
          { field_name: '競合記事URL3', type: 15 },
          { field_name: '差別化ポイント', type: 1, property: { type: 'text' } },
          { field_name: '関連キーワード', type: 1, property: { type: 'text' } },
          { field_name: 'キーワード抽出日', type: 5 },
        ]
      },

      // 競合分析マスター
      competitorTable: {
        name: '競合分析マスター',
        fields: [
          { field_name: '競合記事URL', type: 15 },
          { field_name: 'サイト名', type: 1 },
          { field_name: '記事タイトル', type: 1 },
          { field_name: '公開日', type: 5 },
          { field_name: '推定文字数', type: 2 },
          { field_name: 'H2見出し構成', type: 1, property: { type: 'text' } },
          { field_name: '使用キーワード', type: 1, property: { type: 'text' } },
          { field_name: '強み', type: 1, property: { type: 'text' } },
          { field_name: '弱み', type: 1, property: { type: 'text' } },
          { field_name: '差別化機会', type: 1, property: { type: 'text' } },
          { field_name: '分析日', type: 5 },
        ]
      },

      // パフォーマンストラッキング
      performanceTable: {
        name: 'パフォーマンストラッキング',
        fields: [
          { field_name: '記事ID', type: 1 },
          { field_name: '計測日', type: 5 },
          { field_name: '検索順位', type: 2 },
          { field_name: 'PV数', type: 2 },
          { field_name: '滞在時間', type: 2 },
          { field_name: '直帰率', type: 2 },
          { field_name: 'スキ数', type: 2 },
          { field_name: 'コメント数', type: 2 },
          { field_name: 'メンバーシップCV', type: 2 },
          { field_name: '改善アクション', type: 1, property: { type: 'text' } },
        ]
      },

      // ライター管理CRM（拡張版）
      writerTable: {
        name: 'ライター管理CRM_拡張版',
        fields: [
          { field_name: 'ライター名', type: 1 },
          { field_name: '投稿記事数', type: 2 },
          { field_name: '主要カテゴリ', type: 3, property: { options: [{ name: 'AI' }, { name: 'DX' }, { name: '技術' }] } },
          { field_name: '月間投稿目標', type: 2 },
          { field_name: '今月の投稿数', type: 2 },
          { field_name: '専門分野', type: 4, property: { options: [{ name: 'AI' }, { name: 'DX' }, { name: '開発' }, { name: 'マーケティング' }] } },
          { field_name: '得意キーワード', type: 4, property: { options: [{ name: 'GPT' }, { name: 'Claude' }, { name: 'Gemini' }, { name: 'プロンプト' }] } },
          { field_name: '時給_記事単価', type: 2 },
          { field_name: '契約形態', type: 3, property: { options: [{ name: '社員' }, { name: '業務委託' }, { name: '外注' }] } },
        ]
      }
    };
  }

  /**
   * フィールドタイプのマッピング
   */
  getFieldTypeMap() {
    return {
      1: 'テキスト',
      2: '数値',
      3: '単一選択',
      4: '複数選択',
      5: '日付',
      11: 'ユーザー',
      13: 'チェックボックス',
      15: 'URL',
      17: 'リンク',
      18: '数式',
      20: '作成日時',
      21: '更新日時',
      1001: '作成者',
      1002: '更新者',
      1003: '更新時刻'
    };
  }

  /**
   * アクセストークンの取得
   */
  async getAccessToken() {
    try {
      const res = await this.client.auth.tenantAccessToken.internal({
        data: {
          app_id: process.env.LARK_APP_ID,
          app_secret: process.env.LARK_APP_SECRET,
        },
      });
      
      if (res.code === 0) {
        console.log('✅ アクセストークン取得成功');
        return res.tenant_access_token;
      } else {
        throw new Error(`Failed to get access token: ${res.msg}`);
      }
    } catch (error) {
      console.error('❌ アクセストークン取得失敗:', error);
      throw error;
    }
  }

  /**
   * テーブル作成
   */
  async createTable(tableName, fields) {
    try {
      console.log(`\n📊 テーブル作成中: ${tableName}`);
      
      const res = await this.client.bitable.appTable.create({
        path: {
          app_token: this.baseAppToken,
        },
        data: {
          table: {
            name: tableName,
            default_view_name: 'デフォルトビュー',
            fields: fields
          },
        },
      });

      if (res.code === 0) {
        console.log(`✅ テーブル作成成功: ${tableName}`);
        console.log(`   Table ID: ${res.data.table_id}`);
        return {
          tableId: res.data.table_id,
          name: tableName,
          revision: res.data.revision
        };
      } else {
        throw new Error(`Failed to create table ${tableName}: ${res.msg}`);
      }
    } catch (error) {
      console.error(`❌ テーブル作成失敗 (${tableName}):`, error.message);
      return null;
    }
  }

  /**
   * 既存テーブルの確認
   */
  async checkExistingTables() {
    try {
      console.log('\n🔍 既存テーブルを確認中...');
      
      const res = await this.client.bitable.appTable.list({
        path: {
          app_token: this.baseAppToken,
        },
        params: {
          page_size: 100,
        },
      });

      if (res.code === 0) {
        const tables = res.data.items || [];
        console.log(`📋 既存テーブル数: ${tables.length}`);
        
        tables.forEach(table => {
          console.log(`   - ${table.name} (ID: ${table.table_id})`);
        });
        
        return tables;
      } else {
        throw new Error(`Failed to list tables: ${res.msg}`);
      }
    } catch (error) {
      console.error('❌ テーブル一覧取得失敗:', error);
      return [];
    }
  }

  /**
   * 初期データの挿入
   */
  async insertInitialData(tableId, tableName) {
    try {
      console.log(`\n📝 初期データ挿入中: ${tableName}`);
      
      let initialData = {};
      
      // テーブルごとの初期データ
      switch (tableName) {
        case 'SEOキーワード管理_拡張版':
          initialData = {
            'キーワード': 'claude code windows',
            'カテゴリー': 'AI開発',
            '優先度': '最優先',
            '検索ボリューム': '中',
            '競合度': '低',
            'キーワード抽出日': new Date().toISOString().split('T')[0],
          };
          break;
          
        case 'ライター管理CRM_拡張版':
          initialData = {
            'ライター名': 'ハヤシシュンスケ',
            '投稿記事数': 0,
            '月間投稿目標': 10,
            '今月の投稿数': 0,
            '契約形態': '社員',
          };
          break;
          
        default:
          console.log(`   ⏭️ ${tableName}の初期データはスキップ`);
          return;
      }
      
      const res = await this.client.bitable.appTableRecord.create({
        path: {
          app_token: this.baseAppToken,
          table_id: tableId,
        },
        data: {
          fields: initialData,
        },
      });

      if (res.code === 0) {
        console.log(`   ✅ 初期データ挿入成功`);
      } else {
        console.log(`   ⚠️ 初期データ挿入失敗: ${res.msg}`);
      }
    } catch (error) {
      console.error(`❌ 初期データ挿入エラー:`, error);
    }
  }

  /**
   * セットアップ実行
   */
  async runSetup() {
    console.log('🚀 Lark Base セットアップ開始');
    console.log('================================\n');
    
    try {
      // アクセストークン取得
      await this.getAccessToken();
      
      // 既存テーブル確認
      const existingTables = await this.checkExistingTables();
      const existingTableNames = existingTables.map(t => t.name);
      
      // テーブル定義取得
      const tableDefinitions = this.getTableDefinitions();
      const createdTables = [];
      
      // 各テーブルを作成
      for (const [key, definition] of Object.entries(tableDefinitions)) {
        if (existingTableNames.includes(definition.name)) {
          console.log(`⏭️ ${definition.name} は既に存在します`);
          continue;
        }
        
        const result = await this.createTable(definition.name, definition.fields);
        if (result) {
          createdTables.push(result);
          
          // 初期データ挿入
          await this.insertInitialData(result.tableId, result.name);
        }
      }
      
      // 結果サマリー
      console.log('\n================================');
      console.log('📊 セットアップ完了サマリー');
      console.log('================================');
      console.log(`✅ 作成成功: ${createdTables.length}テーブル`);
      
      if (createdTables.length > 0) {
        console.log('\n作成されたテーブル:');
        createdTables.forEach(table => {
          console.log(`  - ${table.name}`);
          console.log(`    Table ID: ${table.tableId}`);
        });
      }
      
      // 設定ファイル更新の提案
      if (createdTables.length > 0) {
        console.log('\n💡 .envファイルに以下のTable IDを追加してください:');
        createdTables.forEach(table => {
          const envKey = table.name.replace(/[_\s]/g, '_').toUpperCase() + '_TABLE_ID';
          console.log(`${envKey}=${table.tableId}`);
        });
      }
      
      console.log('\n✨ セットアップが完了しました！');
      console.log(`🔗 Lark Base URL: https://base.larksuite.com/base/${this.baseAppToken}`);
      
    } catch (error) {
      console.error('\n❌ セットアップ中にエラーが発生しました:', error);
      process.exit(1);
    }
  }
}

// 実行
const setup = new LarkBaseSetup();
setup.runSetup();