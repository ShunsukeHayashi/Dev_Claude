import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import { LarkBaseManager } from './services/larkBaseManager.js';
import { ContentWorkflow } from './services/contentWorkflow.js';
import { SSEManager } from './services/sseManager.js';
import { config } from 'dotenv';

// Load environment variables
config();

/**
 * Lark Content Workflow MCP Server
 * Provides MCP tools for managing content workflow with Lark Base integration
 */
class LarkContentWorkflowMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'lark-content-workflow',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    // Initialize services
    this.larkBase = new LarkBaseManager({
      appId: process.env.LARK_APP_ID,
      appSecret: process.env.LARK_APP_SECRET,
      baseAppToken: process.env.LARK_BASE_APP_TOKEN,
      tableId: process.env.LARK_BASE_TABLE_ID
    });

    this.sseManager = new SSEManager();
    this.contentWorkflow = new ContentWorkflow(this.larkBase, this.sseManager);

    this.setupToolHandlers();
  }

  setupToolHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'start_content_workflow',
            description: 'Start a new content generation workflow with SSE updates',
            inputSchema: {
              type: 'object',
              properties: {
                topic: {
                  type: 'string',
                  description: 'The topic for content generation'
                },
                parameters: {
                  type: 'object',
                  properties: {
                    style: {
                      type: 'string',
                      enum: ['professional', 'casual', 'academic'],
                      description: 'Writing style'
                    },
                    length: {
                      type: 'string',
                      enum: ['short', 'medium', 'long'],
                      description: 'Content length'
                    },
                    language: {
                      type: 'string',
                      default: 'ja',
                      description: 'Content language'
                    }
                  }
                },
                larkConfig: {
                  type: 'object',
                  properties: {
                    userId: {
                      type: 'string',
                      description: 'Lark user ID'
                    },
                    assignedWriter: {
                      type: 'string',
                      description: 'Assigned writer name'
                    }
                  }
                }
              },
              required: ['topic']
            }
          },
          {
            name: 'get_workflow_status',
            description: 'Get the status of a running workflow',
            inputSchema: {
              type: 'object',
              properties: {
                workflowId: {
                  type: 'string',
                  description: 'The workflow ID to check'
                }
              },
              required: ['workflowId']
            }
          },
          {
            name: 'get_lark_records',
            description: 'Retrieve records from Lark Base',
            inputSchema: {
              type: 'object',
              properties: {
                pageSize: {
                  type: 'number',
                  default: 20,
                  description: 'Number of records to retrieve'
                },
                pageToken: {
                  type: 'string',
                  description: 'Token for pagination'
                },
                filter: {
                  type: 'string',
                  description: 'Filter expression for records'
                }
              }
            }
          },
          {
            name: 'create_lark_record',
            description: 'Create a new record in Lark Base',
            inputSchema: {
              type: 'object',
              properties: {
                fields: {
                  type: 'object',
                  description: 'Field values for the new record'
                }
              },
              required: ['fields']
            }
          },
          {
            name: 'update_lark_record',
            description: 'Update an existing record in Lark Base',
            inputSchema: {
              type: 'object',
              properties: {
                recordId: {
                  type: 'string',
                  description: 'The record ID to update'
                },
                fields: {
                  type: 'object',
                  description: 'Field values to update'
                }
              },
              required: ['recordId', 'fields']
            }
          },
          {
            name: 'setup_lark_base',
            description: 'Initialize and setup Lark Base tables',
            inputSchema: {
              type: 'object',
              properties: {
                force: {
                  type: 'boolean',
                  default: false,
                  description: 'Force recreation of tables'
                }
              }
            }
          },
          {
            name: 'get_server_health',
            description: 'Get server health status and active connections',
            inputSchema: {
              type: 'object',
              properties: {}
            }
          }
        ],
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'start_content_workflow':
            return await this.handleStartWorkflow(args);
            
          case 'get_workflow_status':
            return await this.handleGetWorkflowStatus(args);
            
          case 'get_lark_records':
            return await this.handleGetLarkRecords(args);
            
          case 'create_lark_record':
            return await this.handleCreateLarkRecord(args);
            
          case 'update_lark_record':
            return await this.handleUpdateLarkRecord(args);
            
          case 'setup_lark_base':
            return await this.handleSetupLarkBase(args);
            
          case 'get_server_health':
            return await this.handleGetServerHealth(args);
            
          default:
            throw new McpError(
              ErrorCode.MethodNotFound,
              `Unknown tool: ${name}`
            );
        }
      } catch (error) {
        console.error(`Error executing tool ${name}:`, error);
        throw new McpError(
          ErrorCode.InternalError,
          `Tool execution failed: ${error.message}`
        );
      }
    });
  }

  async handleStartWorkflow(args) {
    const { topic, parameters = {}, larkConfig = {} } = args;
    
    if (!topic) {
      throw new McpError(ErrorCode.InvalidParams, 'Topic is required');
    }

    try {
      const workflowId = await this.contentWorkflow.start({
        topic,
        parameters,
        larkConfig
      });

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              success: true,
              workflowId,
              status: 'started',
              message: 'Content workflow initiated successfully',
              larkBase: {
                appToken: process.env.LARK_BASE_APP_TOKEN,
                tableId: process.env.LARK_BASE_TABLE_ID
              },
              estimatedDuration: '15-30 minutes',
              stages: [
                'initialization',
                'research', 
                'outline',
                'generation',
                'review',
                'finalization',
                'completion'
              ]
            }, null, 2)
          }
        ]
      };
    } catch (error) {
      throw new McpError(
        ErrorCode.InternalError,
        `Failed to start workflow: ${error.message}`
      );
    }
  }

  async handleGetWorkflowStatus(args) {
    const { workflowId } = args;
    
    if (!workflowId) {
      throw new McpError(ErrorCode.InvalidParams, 'Workflow ID is required');
    }

    try {
      const status = await this.contentWorkflow.getStatus(workflowId);
      
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(status, null, 2)
          }
        ]
      };
    } catch (error) {
      throw new McpError(
        ErrorCode.InternalError,
        `Failed to get workflow status: ${error.message}`
      );
    }
  }

  async handleGetLarkRecords(args) {
    const { pageSize = 20, pageToken, filter } = args;

    try {
      const records = await this.larkBase.getRecords({ 
        pageSize, 
        pageToken,
        filter 
      });
      
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              success: true,
              records: records.items || [],
              hasMore: records.has_more || false,
              pageToken: records.page_token,
              total: records.total || records.items?.length || 0
            }, null, 2)
          }
        ]
      };
    } catch (error) {
      throw new McpError(
        ErrorCode.InternalError,
        `Failed to get Lark records: ${error.message}`
      );
    }
  }

  async handleCreateLarkRecord(args) {
    const { fields } = args;
    
    if (!fields) {
      throw new McpError(ErrorCode.InvalidParams, 'Fields are required');
    }

    try {
      const record = await this.larkBase.createRecord(fields);
      
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              success: true,
              record: {
                recordId: record.record_id || record.recordId,
                fields: record.fields || fields
              },
              message: 'Record created successfully'
            }, null, 2)
          }
        ]
      };
    } catch (error) {
      throw new McpError(
        ErrorCode.InternalError,
        `Failed to create Lark record: ${error.message}`
      );
    }
  }

  async handleUpdateLarkRecord(args) {
    const { recordId, fields } = args;
    
    if (!recordId || !fields) {
      throw new McpError(
        ErrorCode.InvalidParams, 
        'Record ID and fields are required'
      );
    }

    try {
      const record = await this.larkBase.updateRecord(recordId, fields);
      
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              success: true,
              record: {
                recordId: record.record_id || recordId,
                fields: record.fields || fields
              },
              message: 'Record updated successfully'
            }, null, 2)
          }
        ]
      };
    } catch (error) {
      throw new McpError(
        ErrorCode.InternalError,
        `Failed to update Lark record: ${error.message}`
      );
    }
  }

  async handleSetupLarkBase(args) {
    const { force = false } = args;

    try {
      // Initialize Lark Base connection
      await this.larkBase.initialize();
      
      // Get or create tables
      const setupResults = await this.larkBase.setupTables(force);
      
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              success: true,
              message: 'Lark Base setup completed successfully',
              results: setupResults,
              connection: {
                appToken: process.env.LARK_BASE_APP_TOKEN,
                connected: this.larkBase.isConnected()
              }
            }, null, 2)
          }
        ]
      };
    } catch (error) {
      throw new McpError(
        ErrorCode.InternalError,
        `Failed to setup Lark Base: ${error.message}`
      );
    }
  }

  async handleGetServerHealth(args) {
    try {
      const health = {
        status: 'healthy',
        timestamp: new Date().toISOString(),
        server: {
          name: 'lark-content-workflow-mcp',
          version: '1.0.0',
          uptime: process.uptime()
        },
        connections: {
          activeSSE: this.sseManager.getActiveConnections(),
          maxConnections: process.env.SSE_MAX_CONNECTIONS || 100
        },
        larkBase: {
          connected: this.larkBase.isConnected(),
          appToken: process.env.LARK_BASE_APP_TOKEN ? 'configured' : 'not configured',
          tableId: process.env.LARK_BASE_TABLE_ID ? 'configured' : 'not configured'
        },
        environment: {
          nodeVersion: process.version,
          platform: process.platform,
          memory: process.memoryUsage(),
          env: process.env.NODE_ENV || 'development'
        }
      };

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(health, null, 2)
          }
        ]
      };
    } catch (error) {
      throw new McpError(
        ErrorCode.InternalError,
        `Failed to get server health: ${error.message}`
      );
    }
  }

  async initialize() {
    try {
      // Initialize Lark Base connection
      await this.larkBase.initialize();
      console.log('✅ Lark Content Workflow MCP Server initialized successfully');
      
      return true;
    } catch (error) {
      console.error('❌ Failed to initialize MCP server:', error);
      throw error;
    }
  }

  async start() {
    try {
      // Initialize services
      await this.initialize();
      
      // Start the server
      const transport = new StdioServerTransport();
      await this.server.connect(transport);
      
      console.log('🚀 Lark Content Workflow MCP Server running on stdio transport');
    } catch (error) {
      console.error('Failed to start MCP server:', error);
      process.exit(1);
    }
  }
}

// Start the MCP server if run directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const mcpServer = new LarkContentWorkflowMCPServer();
  mcpServer.start();
}

export { LarkContentWorkflowMCPServer };