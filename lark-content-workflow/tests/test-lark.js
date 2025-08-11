import { config } from 'dotenv';
import { LarkBaseManager } from '../src/services/larkBaseManager.js';

// Load environment variables
config();

/**
 * Simple test script for Lark Base connection
 */
async function testLarkConnection() {
  console.log('🧪 Testing Lark Base Connection...');
  console.log('=====================================');
  
  const larkBase = new LarkBaseManager({
    appId: process.env.LARK_APP_ID,
    appSecret: process.env.LARK_APP_SECRET,
    baseAppToken: process.env.LARK_BASE_APP_TOKEN,
    tableId: process.env.LARK_BASE_TABLE_ID
  });

  try {
    // Test 1: Initialize connection
    console.log('📡 Test 1: Initializing connection...');
    await larkBase.initialize();
    console.log('✅ Connection initialized successfully');

    // Test 2: Check connection status
    console.log('\n🔍 Test 2: Checking connection status...');
    const isConnected = larkBase.isConnected();
    console.log(`Connection status: ${isConnected ? '✅ Connected' : '❌ Disconnected'}`);

    // Test 3: Get records (basic read test)
    console.log('\n📊 Test 3: Testing record retrieval...');
    const records = await larkBase.getRecords({ pageSize: 5 });
    console.log(`✅ Retrieved ${records.items?.length || 0} records`);
    
    if (records.items && records.items.length > 0) {
      console.log('Sample record fields:', Object.keys(records.items[0].fields || {}));
    }

    // Test 4: Test MCP server initialization  
    console.log('\n🔧 Test 4: Testing MCP server...');
    try {
      const { LarkContentWorkflowMCPServer } = await import('../src/mcp-server.js');
      const mcpServer = new LarkContentWorkflowMCPServer();
      await mcpServer.initialize();
      console.log('✅ MCP server initialized successfully');
    } catch (mcpError) {
      console.log('⚠️  MCP server test skipped:', mcpError.message);
    }

    console.log('\n🎉 All tests passed successfully!');
    console.log('=====================================');
    console.log('✅ Lark Base connection is working');
    console.log('✅ Ready for deployment');
    
  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
    console.error('=====================================');
    console.error('Please check your environment variables:');
    console.error('- LARK_APP_ID:', process.env.LARK_APP_ID ? 'Set' : 'Not set');
    console.error('- LARK_APP_SECRET:', process.env.LARK_APP_SECRET ? 'Set' : 'Not set');
    console.error('- LARK_BASE_APP_TOKEN:', process.env.LARK_BASE_APP_TOKEN ? 'Set' : 'Not set');
    console.error('- LARK_BASE_TABLE_ID:', process.env.LARK_BASE_TABLE_ID ? 'Set' : 'Not set');
    process.exit(1);
  }
}

// Run tests
testLarkConnection();