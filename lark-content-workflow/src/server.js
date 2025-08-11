import express from 'express';
import cors from 'cors';
import { config } from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { LarkBaseManager } from './services/larkBaseManager.js';
import { ContentWorkflow } from './services/contentWorkflow.js';
import { SSEManager } from './services/sseManager.js';

// Load environment variables
config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(join(__dirname, '../public')));

// Initialize services
const larkBase = new LarkBaseManager({
  appId: process.env.LARK_APP_ID,
  appSecret: process.env.LARK_APP_SECRET,
  baseAppToken: process.env.LARK_BASE_APP_TOKEN,
  tableId: process.env.LARK_BASE_TABLE_ID
});

const sseManager = new SSEManager();
const contentWorkflow = new ContentWorkflow(larkBase, sseManager);

// SSE endpoint for workflow updates
app.get('/api/workflow/stream', (req, res) => {
  sseManager.addClient(req, res);
});

// Start content generation workflow
app.post('/api/workflow/start', async (req, res) => {
  const { topic, parameters, larkConfig } = req.body;
  
  if (!topic) {
    return res.status(400).json({ error: 'Topic is required' });
  }

  try {
    const workflowId = await contentWorkflow.start({
      topic,
      parameters: parameters || {},
      larkConfig: larkConfig || {}
    });
    
    res.json({ 
      workflowId, 
      status: 'started',
      message: 'Workflow initiated successfully',
      larkBase: {
        appToken: process.env.LARK_BASE_APP_TOKEN,
        tableId: process.env.LARK_BASE_TABLE_ID
      }
    });
  } catch (error) {
    console.error('Error starting workflow:', error);
    res.status(500).json({ error: 'Failed to start workflow', details: error.message });
  }
});

// Get Lark Base records
app.get('/api/lark/records', async (req, res) => {
  try {
    const { pageSize = 20, pageToken } = req.query;
    const records = await larkBase.getRecords({ pageSize, pageToken });
    res.json(records);
  } catch (error) {
    console.error('Error fetching records:', error);
    res.status(500).json({ error: 'Failed to fetch records', details: error.message });
  }
});

// Create Lark Base record
app.post('/api/lark/records', async (req, res) => {
  try {
    const { fields } = req.body;
    const record = await larkBase.createRecord(fields);
    res.json(record);
  } catch (error) {
    console.error('Error creating record:', error);
    res.status(500).json({ error: 'Failed to create record', details: error.message });
  }
});

// Update Lark Base record
app.put('/api/lark/records/:recordId', async (req, res) => {
  try {
    const { recordId } = req.params;
    const { fields } = req.body;
    const record = await larkBase.updateRecord(recordId, fields);
    res.json(record);
  } catch (error) {
    console.error('Error updating record:', error);
    res.status(500).json({ error: 'Failed to update record', details: error.message });
  }
});

// Get workflow status from Lark Base
app.get('/api/workflow/:workflowId/status', async (req, res) => {
  try {
    const { workflowId } = req.params;
    const status = await contentWorkflow.getStatus(workflowId);
    res.json(status);
  } catch (error) {
    console.error('Error fetching workflow status:', error);
    res.status(500).json({ error: 'Failed to fetch status', details: error.message });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    activeConnections: sseManager.getActiveConnections(),
    larkBase: {
      connected: larkBase.isConnected(),
      appToken: process.env.LARK_BASE_APP_TOKEN ? 'configured' : 'not configured'
    },
    timestamp: new Date().toISOString()
  });
});

// Initialize Lark Base connection
async function initialize() {
  try {
    await larkBase.initialize();
    console.log('✅ Lark Base connected successfully');
    
    // Start server
    app.listen(PORT, () => {
      console.log(`🚀 Lark Content Workflow Server running on http://localhost:${PORT}`);
      console.log(`📊 Lark Base App Token: ${process.env.LARK_BASE_APP_TOKEN || 'Not configured'}`);
      console.log(`📋 Active endpoints:`);
      console.log(`  - GET  /api/workflow/stream     - SSE stream`);
      console.log(`  - POST /api/workflow/start      - Start workflow`);
      console.log(`  - GET  /api/lark/records        - Get Lark Base records`);
      console.log(`  - POST /api/lark/records        - Create record`);
      console.log(`  - PUT  /api/lark/records/:id    - Update record`);
      console.log(`  - GET  /api/workflow/:id/status - Get workflow status`);
      console.log(`  - GET  /health                  - Health check`);
    });
  } catch (error) {
    console.error('Failed to initialize:', error);
    process.exit(1);
  }
}

// Start the application
initialize();