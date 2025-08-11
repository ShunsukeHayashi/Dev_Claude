import { v4 as uuidv4 } from 'uuid';

export class ContentWorkflow {
  constructor(larkBase, sseManager) {
    this.larkBase = larkBase;
    this.sseManager = sseManager;
    this.activeWorkflows = new Map();
  }

  async start(config) {
    const workflowId = `wf_${uuidv4()}`;
    const { topic, parameters, larkConfig } = config;

    // Create initial record in Lark Base
    const record = await this.larkBase.createRecord({
      workflow_id: workflowId,
      topic,
      status: 'initializing',
      stage: 'initialization',
      parameters: JSON.stringify(parameters),
      progress: 0,
      created_by: larkConfig.userId || 'system',
    });

    // Store workflow info
    this.activeWorkflows.set(workflowId, {
      recordId: record.recordId,
      topic,
      parameters,
      startTime: Date.now(),
      status: 'running',
    });

    // Start async processing
    this.processWorkflow(workflowId, topic, parameters, record.recordId);

    return workflowId;
  }

  async processWorkflow(workflowId, topic, parameters, recordId) {
    const stages = [
      { id: 'initialization', name: '初期化', progress: 0 },
      { id: 'research', name: '調査', progress: 15 },
      { id: 'outline_creation', name: 'アウトライン作成', progress: 30 },
      { id: 'content_generation', name: 'コンテンツ生成', progress: 50 },
      { id: 'review', name: 'レビュー', progress: 75 },
      { id: 'finalization', name: '最終化', progress: 90 },
      { id: 'complete', name: '完了', progress: 100 },
    ];

    for (const stage of stages) {
      try {
        // Update Lark Base record
        await this.larkBase.updateRecord(recordId, {
          stage: stage.id,
          stage_name: stage.name,
          progress: stage.progress,
          status: stage.id === 'complete' ? 'completed' : 'processing',
        });

        // Broadcast SSE event
        this.sseManager.broadcast('stage_update', {
          workflowId,
          stage: stage.id,
          stageName: stage.name,
          progress: stage.progress,
          timestamp: new Date().toISOString(),
        });

        // Process stage-specific logic
        const stageData = await this.processStage(
          workflowId,
          stage.id,
          topic,
          parameters,
          recordId
        );

        // Store stage data in Lark Base
        await this.larkBase.updateRecord(recordId, {
          [`${stage.id}_data`]: JSON.stringify(stageData),
          [`${stage.id}_completed_at`]: new Date().toISOString(),
        });

        // Broadcast stage data
        this.sseManager.broadcast('stage_data', {
          workflowId,
          stage: stage.id,
          data: stageData,
        });

        // Add delay between stages
        if (stage.id !== 'complete') {
          await new Promise((resolve) => setTimeout(resolve, 1500));
        }
      } catch (error) {
        console.error(`Error processing stage ${stage.id}:`, error);
        
        // Update error status in Lark Base
        await this.larkBase.updateRecord(recordId, {
          status: 'error',
          error_message: error.message,
          error_stage: stage.id,
        });

        // Broadcast error
        this.sseManager.broadcast('error', {
          workflowId,
          stage: stage.id,
          error: error.message,
        });

        break;
      }
    }

    // Mark workflow as complete
    const workflow = this.activeWorkflows.get(workflowId);
    if (workflow) {
      workflow.status = 'completed';
      workflow.endTime = Date.now();
      workflow.duration = workflow.endTime - workflow.startTime;
    }
  }

  async processStage(workflowId, stage, topic, parameters, recordId) {
    let data = {};

    switch (stage) {
      case 'initialization':
        data = {
          message: 'ワークフローを初期化しています',
          topic,
          parameters,
          larkBase: {
            recordId,
            tableId: this.larkBase.tableId,
          },
        };
        break;

      case 'research':
        data = {
          message: 'トピックを調査し情報を収集しています',
          sources: await this.generateResearchSources(topic),
          keyPoints: await this.generateKeyPoints(topic),
        };
        break;

      case 'outline_creation':
        data = {
          message: 'コンテンツのアウトラインを作成しています',
          outline: await this.generateOutline(topic, parameters),
        };
        break;

      case 'content_generation':
        data = {
          message: 'コンテンツセクションを生成しています',
          sections: [],
        };

        // Generate content sections
        for (let i = 1; i <= 5; i++) {
          const section = await this.generateSection(topic, i);
          data.sections.push(section);

          // Update progress in Lark Base
          const progress = 50 + (i * 5);
          await this.larkBase.updateRecord(recordId, {
            progress,
            current_section: i,
            total_sections: 5,
          });

          // Broadcast progress
          this.sseManager.broadcast('content_progress', {
            workflowId,
            section: i,
            total: 5,
            progress: (i / 5) * 100,
            content: section.content.substring(0, 100) + '...',
          });

          await new Promise((resolve) => setTimeout(resolve, 500));
        }
        break;

      case 'review':
        data = {
          message: 'コンテンツをレビューし最適化しています',
          checks: ['文法チェック', '明確性', 'SEO最適化', 'ファクトチェック'],
          improvements: await this.generateImprovements(),
        };
        break;

      case 'finalization':
        data = {
          message: 'コンテンツを最終化し出力を準備しています',
          formats: ['HTML', 'Markdown', 'PDF', 'Lark Doc'],
          metadata: {
            wordCount: Math.floor(Math.random() * 1000) + 1500,
            readingTime: Math.floor(Math.random() * 5) + 3,
            language: parameters.language || 'ja',
          },
        };
        break;

      case 'complete':
        const workflow = this.activeWorkflows.get(workflowId);
        data = {
          message: 'ワークフローが正常に完了しました',
          larkBase: {
            recordId,
            viewUrl: `https://base.larksuite.com/base/${this.larkBase.baseAppToken}?table=${this.larkBase.tableId}&view=vewTbWQZPX`,
          },
          stats: {
            duration: workflow ? `${Math.round(workflow.duration / 1000)}秒` : '不明',
            wordCount: 2000,
            sections: 5,
          },
        };
        break;
    }

    return data;
  }

  async generateResearchSources(topic) {
    return [
      `Wikipedia: ${topic}`,
      '関連する学術論文',
      '業界レポートとホワイトペーパー',
      '専門家のブログとインタビュー',
      '最新のニュース記事',
    ];
  }

  async generateKeyPoints(topic) {
    return [
      `${topic}の基本概念と定義`,
      '歴史的背景と発展',
      '現在のトレンドと応用',
      'ベストプラクティスと推奨事項',
      '将来の展望と課題',
    ];
  }

  async generateOutline(topic, parameters) {
    const style = parameters.style || 'professional';
    const length = parameters.length || 'medium';

    return {
      title: `${topic}の完全ガイド`,
      style,
      length,
      sections: [
        { id: 1, title: 'はじめに', estimatedWords: 200 },
        { id: 2, title: '背景とコンテキスト', estimatedWords: 300 },
        { id: 3, title: 'コア概念', estimatedWords: 500 },
        { id: 4, title: '実装ガイド', estimatedWords: 600 },
        { id: 5, title: 'まとめと次のステップ', estimatedWords: 200 },
      ],
    };
  }

  async generateSection(topic, sectionNumber) {
    const titles = [
      'はじめに',
      '背景とコンテキスト',
      'コア概念',
      '実装ガイド',
      'まとめと次のステップ',
    ];

    return {
      id: sectionNumber,
      title: titles[sectionNumber - 1],
      content: `セクション ${sectionNumber}: ${titles[sectionNumber - 1]}\n\n${topic}についての詳細なコンテンツがここに生成されます。このセクションでは、重要な概念、実践的な例、そして読者が理解すべき主要なポイントを網羅します。`,
      wordCount: 200 + Math.floor(Math.random() * 300),
    };
  }

  async generateImprovements() {
    return [
      '技術用語の説明を追加',
      '実例とケーススタディを含める',
      'ビジュアル要素（図表）の追加を推奨',
      'SEOキーワードの最適化',
      '読みやすさの向上',
    ];
  }

  async getStatus(workflowId) {
    const workflow = this.activeWorkflows.get(workflowId);
    
    if (!workflow) {
      throw new Error('Workflow not found');
    }

    // Get latest status from Lark Base
    const records = await this.larkBase.searchRecords(workflowId);
    const record = records.records[0];

    return {
      workflowId,
      status: workflow.status,
      topic: workflow.topic,
      recordId: workflow.recordId,
      startTime: new Date(workflow.startTime).toISOString(),
      endTime: workflow.endTime ? new Date(workflow.endTime).toISOString() : null,
      duration: workflow.duration || null,
      larkBaseData: record || null,
    };
  }
}