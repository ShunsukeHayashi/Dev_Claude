import * as lark from '@larksuiteoapi/node-sdk';

export class LarkBaseManager {
  constructor(config) {
    this.appId = config.appId;
    this.appSecret = config.appSecret;
    this.baseAppToken = config.baseAppToken;
    this.tableId = config.tableId;
    this.client = null;
    this.tenantAccessToken = null;
    this.connected = false;
  }

  async initialize() {
    try {
      // Initialize Lark client
      this.client = new lark.Client({
        appId: this.appId,
        appSecret: this.appSecret,
        appType: lark.AppType.SelfBuild,
        domain: lark.Domain.Lark,
      });

      // Get tenant access token
      await this.refreshAccessToken();
      this.connected = true;
      
      // Refresh token every 1.5 hours
      setInterval(() => this.refreshAccessToken(), 1.5 * 60 * 60 * 1000);
      
      return true;
    } catch (error) {
      console.error('Failed to initialize Lark Base:', error);
      throw error;
    }
  }

  async refreshAccessToken() {
    try {
      const res = await this.client.auth.tenantAccessToken.internal({
        data: {
          app_id: this.appId,
          app_secret: this.appSecret,
        },
      });
      
      if (res.code === 0) {
        this.tenantAccessToken = res.tenant_access_token;
        console.log('✅ Lark access token refreshed');
      } else {
        throw new Error(`Failed to get access token: ${res.msg}`);
      }
    } catch (error) {
      console.error('Error refreshing access token:', error);
      throw error;
    }
  }

  async getRecords(options = {}) {
    const { pageSize = 20, pageToken } = options;
    
    try {
      const res = await this.client.bitable.appTableRecord.list({
        path: {
          app_token: this.baseAppToken,
          table_id: this.tableId,
        },
        params: {
          page_size: pageSize,
          page_token: pageToken,
        },
      });

      if (res.code === 0) {
        return {
          records: res.data.items || [],
          hasMore: res.data.has_more,
          pageToken: res.data.page_token,
          total: res.data.total,
        };
      } else {
        throw new Error(`Failed to get records: ${res.msg}`);
      }
    } catch (error) {
      console.error('Error fetching records:', error);
      throw error;
    }
  }

  async createRecord(fields) {
    try {
      const res = await this.client.bitable.appTableRecord.create({
        path: {
          app_token: this.baseAppToken,
          table_id: this.tableId,
        },
        data: {
          fields: {
            ...fields,
            created_at: new Date().toISOString(),
            status: fields.status || 'pending',
          },
        },
      });

      if (res.code === 0) {
        return {
          recordId: res.data.record.record_id,
          fields: res.data.record.fields,
        };
      } else {
        throw new Error(`Failed to create record: ${res.msg}`);
      }
    } catch (error) {
      console.error('Error creating record:', error);
      throw error;
    }
  }

  async updateRecord(recordId, fields) {
    try {
      const res = await this.client.bitable.appTableRecord.update({
        path: {
          app_token: this.baseAppToken,
          table_id: this.tableId,
          record_id: recordId,
        },
        data: {
          fields: {
            ...fields,
            updated_at: new Date().toISOString(),
          },
        },
      });

      if (res.code === 0) {
        return {
          recordId: res.data.record.record_id,
          fields: res.data.record.fields,
        };
      } else {
        throw new Error(`Failed to update record: ${res.msg}`);
      }
    } catch (error) {
      console.error('Error updating record:', error);
      throw error;
    }
  }

  async deleteRecord(recordId) {
    try {
      const res = await this.client.bitable.appTableRecord.delete({
        path: {
          app_token: this.baseAppToken,
          table_id: this.tableId,
          record_id: recordId,
        },
      });

      if (res.code === 0) {
        return { success: true, recordId };
      } else {
        throw new Error(`Failed to delete record: ${res.msg}`);
      }
    } catch (error) {
      console.error('Error deleting record:', error);
      throw error;
    }
  }

  async searchRecords(query, options = {}) {
    const { pageSize = 20, pageToken } = options;
    
    try {
      const res = await this.client.bitable.appTableRecord.search({
        path: {
          app_token: this.baseAppToken,
          table_id: this.tableId,
        },
        data: {
          filter: {
            conjunction: 'and',
            conditions: [
              {
                field_name: 'topic',
                operator: 'contains',
                value: [query],
              },
            ],
          },
          page_size: pageSize,
          page_token: pageToken,
        },
      });

      if (res.code === 0) {
        return {
          records: res.data.items || [],
          hasMore: res.data.has_more,
          pageToken: res.data.page_token,
          total: res.data.total,
        };
      } else {
        throw new Error(`Failed to search records: ${res.msg}`);
      }
    } catch (error) {
      console.error('Error searching records:', error);
      throw error;
    }
  }

  async createTable(name, fields) {
    try {
      const res = await this.client.bitable.appTable.create({
        path: {
          app_token: this.baseAppToken,
        },
        data: {
          table: {
            name,
            default_view_name: 'Default View',
            fields,
          },
        },
      });

      if (res.code === 0) {
        return {
          tableId: res.data.table_id,
          name: res.data.name,
        };
      } else {
        throw new Error(`Failed to create table: ${res.msg}`);
      }
    } catch (error) {
      console.error('Error creating table:', error);
      throw error;
    }
  }

  async getTableSchema() {
    try {
      const res = await this.client.bitable.appTableField.list({
        path: {
          app_token: this.baseAppToken,
          table_id: this.tableId,
        },
      });

      if (res.code === 0) {
        return res.data.items || [];
      } else {
        throw new Error(`Failed to get table schema: ${res.msg}`);
      }
    } catch (error) {
      console.error('Error fetching table schema:', error);
      throw error;
    }
  }

  isConnected() {
    return this.connected;
  }
}