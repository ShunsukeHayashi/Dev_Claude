export class SSEManager {
  constructor() {
    this.clients = new Map();
    this.heartbeatInterval = parseInt(process.env.SSE_HEARTBEAT_INTERVAL) || 30000;
    this.startHeartbeat();
  }

  addClient(req, res) {
    const clientId = Date.now().toString();
    
    // Set SSE headers
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
      'X-Accel-Buffering': 'no',
    });

    // Store client
    this.clients.set(clientId, res);

    // Send initial connection event
    this.sendToClient(clientId, 'connected', {
      clientId,
      message: 'Connected to Lark Content Workflow stream',
      timestamp: new Date().toISOString(),
    });

    // Handle client disconnect
    req.on('close', () => {
      this.clients.delete(clientId);
      console.log(`Client ${clientId} disconnected`);
    });

    console.log(`Client ${clientId} connected. Active connections: ${this.clients.size}`);
  }

  sendToClient(clientId, eventType, data) {
    const client = this.clients.get(clientId);
    if (client) {
      try {
        client.write(`event: ${eventType}\n`);
        client.write(`data: ${JSON.stringify(data)}\n\n`);
      } catch (error) {
        console.error(`Error sending to client ${clientId}:`, error);
        this.clients.delete(clientId);
      }
    }
  }

  broadcast(eventType, data) {
    const message = `event: ${eventType}\ndata: ${JSON.stringify(data)}\n\n`;
    
    this.clients.forEach((client, clientId) => {
      try {
        client.write(message);
      } catch (error) {
        console.error(`Error broadcasting to client ${clientId}:`, error);
        this.clients.delete(clientId);
      }
    });

    console.log(`Broadcast ${eventType} to ${this.clients.size} clients`);
  }

  startHeartbeat() {
    setInterval(() => {
      this.broadcast('heartbeat', {
        timestamp: new Date().toISOString(),
        activeConnections: this.clients.size,
      });
    }, this.heartbeatInterval);
  }

  getActiveConnections() {
    return this.clients.size;
  }

  disconnectAll() {
    this.clients.forEach((client, clientId) => {
      try {
        this.sendToClient(clientId, 'disconnect', {
          message: 'Server is shutting down',
        });
        client.end();
      } catch (error) {
        console.error(`Error disconnecting client ${clientId}:`, error);
      }
    });
    this.clients.clear();
  }
}