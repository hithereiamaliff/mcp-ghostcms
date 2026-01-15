#!/usr/bin/env node

/**
 * Ghost CMS MCP Server - HTTP Server Entry Point
 * For self-hosting on VPS with nginx reverse proxy
 * Uses Streamable HTTP transport
 */

import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import fs from 'fs';
import path from 'path';
import { McpServer, ResourceTemplate } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import { FirebaseAnalytics } from './firebase-analytics.js';
import { initGhostApi } from './ghostApi.js';
import {
    handleUserResource,
    handleMemberResource,
    handleTierResource,
    handleOfferResource,
    handleNewsletterResource,
    handlePostResource,
    handleBlogInfoResource
} from './resources.js';
import { registerPostTools } from './tools/posts.js';
import { registerMemberTools } from './tools/members.js';
import { registerUserTools } from './tools/users.js';
import { registerTagTools } from './tools/tags.js';
import { registerTierTools } from './tools/tiers.js';
import { registerOfferTools } from './tools/offers.js';
import { registerNewsletterTools } from './tools/newsletters.js';
import { registerInviteTools } from './tools/invites.js';
import { registerRoleTools } from './tools/roles.js';
import { registerWebhookTools } from './tools/webhooks.js';
import { registerPrompts } from './prompts.js';
import { registerDebugTools } from './tools/debug.js';

// Configuration
const PORT = parseInt(process.env.PORT || '8080', 10);
const HOST = process.env.HOST || '0.0.0.0';
const ANALYTICS_DATA_DIR = process.env.ANALYTICS_DIR || '/app/data';
const ANALYTICS_FILE = path.join(ANALYTICS_DATA_DIR, 'analytics.json');
const SAVE_INTERVAL_MS = 60000; // Save every 60 seconds
const MAX_RECENT_CALLS = 100;

// Ghost API configuration - will be provided per-request via query params
// Environment variables are optional fallbacks for testing
const DEFAULT_GHOST_API_URL = process.env.GHOST_API_URL || '';
const DEFAULT_GHOST_ADMIN_API_KEY = process.env.GHOST_ADMIN_API_KEY || '';
const DEFAULT_GHOST_API_VERSION = process.env.GHOST_API_VERSION || 'v5.0';

// Analytics interface
interface Analytics {
  serverStartTime: string;
  totalRequests: number;
  totalToolCalls: number;
  requestsByMethod: Record<string, number>;
  requestsByEndpoint: Record<string, number>;
  toolCalls: Record<string, number>;
  recentToolCalls: Array<{
    tool: string;
    timestamp: string;
    clientIp: string;
    userAgent: string;
  }>;
  clientsByIp: Record<string, number>;
  clientsByUserAgent: Record<string, number>;
  hourlyRequests: Record<string, number>;
}

// Initialize analytics
let analytics: Analytics = {
  serverStartTime: new Date().toISOString(),
  totalRequests: 0,
  totalToolCalls: 0,
  requestsByMethod: {},
  requestsByEndpoint: {},
  toolCalls: {},
  recentToolCalls: [],
  clientsByIp: {},
  clientsByUserAgent: {},
  hourlyRequests: {},
};

// Ensure data directory exists
function ensureDataDir(): void {
  if (!fs.existsSync(ANALYTICS_DATA_DIR)) {
    fs.mkdirSync(ANALYTICS_DATA_DIR, { recursive: true });
    console.log(`📁 Created analytics data directory: ${ANALYTICS_DATA_DIR}`);
  }
}

// Load analytics from disk on startup
function loadAnalytics(): void {
  try {
    ensureDataDir();
    if (fs.existsSync(ANALYTICS_FILE)) {
      const data = fs.readFileSync(ANALYTICS_FILE, 'utf-8');
      const loaded = JSON.parse(data) as Analytics;
      analytics = {
        ...loaded,
        serverStartTime: loaded.serverStartTime || new Date().toISOString(),
      };
      console.log(`📊 Loaded analytics from ${ANALYTICS_FILE}`);
      console.log(`   Total requests: ${analytics.totalRequests}`);
    } else {
      console.log(`📊 No existing analytics file, starting fresh`);
    }
  } catch (error) {
    console.error(`⚠️ Failed to load analytics:`, error);
  }
}

// Save analytics to disk
function saveAnalytics(): void {
  try {
    ensureDataDir();
    fs.writeFileSync(ANALYTICS_FILE, JSON.stringify(analytics, null, 2));
    console.log(`💾 Saved analytics to ${ANALYTICS_FILE}`);
  } catch (error) {
    console.error(`⚠️ Failed to save analytics:`, error);
  }
}

// Track HTTP request
function trackRequest(req: Request, endpoint: string): void {
  analytics.totalRequests++;
  
  const method = req.method;
  analytics.requestsByMethod[method] = (analytics.requestsByMethod[method] || 0) + 1;
  
  analytics.requestsByEndpoint[endpoint] = (analytics.requestsByEndpoint[endpoint] || 0) + 1;
  
  const clientIp = (req.headers['x-forwarded-for'] as string)?.split(',')[0]?.trim() || req.ip || 'unknown';
  analytics.clientsByIp[clientIp] = (analytics.clientsByIp[clientIp] || 0) + 1;
  
  const userAgent = req.headers['user-agent'] || 'unknown';
  const shortAgent = userAgent.substring(0, 50);
  analytics.clientsByUserAgent[shortAgent] = (analytics.clientsByUserAgent[shortAgent] || 0) + 1;
  
  const hour = new Date().toISOString().substring(0, 13);
  analytics.hourlyRequests[hour] = (analytics.hourlyRequests[hour] || 0) + 1;
}

// Track tool call
function trackToolCall(toolName: string, req: Request): void {
  analytics.totalToolCalls++;
  analytics.toolCalls[toolName] = (analytics.toolCalls[toolName] || 0) + 1;
  
  const toolCall = {
    tool: toolName,
    timestamp: new Date().toISOString(),
    clientIp: (req.headers['x-forwarded-for'] as string)?.split(',')[0]?.trim() || req.ip || 'unknown',
    userAgent: (req.headers['user-agent'] || 'unknown').substring(0, 50),
  };
  
  analytics.recentToolCalls.unshift(toolCall);
  if (analytics.recentToolCalls.length > MAX_RECENT_CALLS) {
    analytics.recentToolCalls.pop();
  }
}

// Calculate uptime
function getUptime(): string {
  const start = new Date(analytics.serverStartTime).getTime();
  const now = Date.now();
  const diff = now - start;
  
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  
  if (days > 0) return `${days}d ${hours}h ${minutes}m`;
  if (hours > 0) return `${hours}h ${minutes}m`;
  return `${minutes}m`;
}

// Initialize Firebase Analytics
const firebaseAnalytics = new FirebaseAnalytics('mcp-ghostcms');

// Load analytics on startup (try Firebase first, then local)
async function initializeAnalytics() {
  if (firebaseAnalytics.isInitialized()) {
    const firebaseData = await firebaseAnalytics.loadAnalytics();
    if (firebaseData) {
      analytics = firebaseData;
      console.log('📊 Loaded analytics from Firebase');
      return;
    }
  }
  
  // Fallback to local file
  loadAnalytics();
}

initializeAnalytics();

// Periodic save (to both Firebase and local)
const saveInterval = setInterval(async () => {
  saveAnalytics(); // Local backup
  if (firebaseAnalytics.isInitialized()) {
    await firebaseAnalytics.saveAnalytics(analytics); // Firebase primary
  }
}, SAVE_INTERVAL_MS);

// Create and configure MCP server with user-provided credentials
function createMcpServer(ghostUrl: string, ghostKey: string, ghostVersion: string = 'v5.0') {
  // Initialize Ghost API client with user-provided credentials
  initGhostApi({
    url: ghostUrl,
    key: ghostKey,
    version: ghostVersion,
  });
  
  const keyId = (ghostKey || '').split(':')[0] || 'unknown';
  console.log(`[ghost-mcp] Using Ghost Admin API: url=${ghostUrl}, version=${ghostVersion}, keyId=${keyId}`);

  const server = new McpServer({
    name: 'ghost-mcp-ts',
    version: '0.1.0',
    capabilities: {
      resources: {},
      tools: {},
      prompts: {},
      logging: {}
    }
  });

  // Register resources
  server.resource('user', new ResourceTemplate('user://{user_id}', { list: undefined }), handleUserResource);
  server.resource('member', new ResourceTemplate('member://{member_id}', { list: undefined }), handleMemberResource);
  server.resource('tier', new ResourceTemplate('tier://{tier_id}', { list: undefined }), handleTierResource);
  server.resource('offer', new ResourceTemplate('offer://{offer_id}', { list: undefined }), handleOfferResource);
  server.resource('newsletter', new ResourceTemplate('newsletter://{newsletter_id}', { list: undefined }), handleNewsletterResource);
  server.resource('post', new ResourceTemplate('post://{post_id}', { list: undefined }), handlePostResource);
  server.resource('blog-info', new ResourceTemplate('blog-info://{blog_id}', { list: undefined }), handleBlogInfoResource);

  // Register tools
  registerPostTools(server);
  registerMemberTools(server);
  registerUserTools(server);
  registerTagTools(server);
  registerTierTools(server);
  registerOfferTools(server);
  registerNewsletterTools(server);
  registerInviteTools(server);
  registerRoleTools(server);
  registerWebhookTools(server);
  registerPrompts(server);
  registerDebugTools(server);

  return server;
}

// Create Express app
const app = express();
app.use(express.json());

// Enhanced CORS configuration for Claude iOS and other MCP clients
app.use(cors({
  origin: '*',
  methods: ['GET', 'POST', 'OPTIONS', 'PUT', 'DELETE'],
  allowedHeaders: [
    'Content-Type', 
    'Authorization', 
    'X-API-Key',
    'Accept',
    'Accept-Encoding',
    'Cache-Control',
    'Connection',
    'User-Agent',
    'X-Requested-With'
  ],
  exposedHeaders: ['Content-Type', 'Cache-Control'],
  credentials: false,
  maxAge: 86400, // 24 hours
}));

// Handle OPTIONS preflight requests explicitly
app.options('*', cors());

// Store MCP servers per Ghost credentials (reused across requests)
const mcpServers = new Map<string, McpServer>();

// Smithery server-card.json endpoint for external MCP discovery
app.get('/.well-known/mcp/server-card.json', (req: Request, res: Response) => {
  trackRequest(req, '/.well-known/mcp/server-card.json');
  res.json({
    name: 'ghost-mcp-ts',
    version: '0.1.0',
    description: 'MCP server for Ghost CMS Admin API - manage posts, members, newsletters, tags, and more',
    homepage: 'https://github.com/hithereiamaliff/mcp-ghostcms',
    transport: {
      type: 'streamable-http',
      url: '/mcp'
    },
    capabilities: {
      tools: true,
      resources: true,
      prompts: true
    },
    authentication: {
      type: 'query-params',
      params: [
        { name: 'url', required: true, description: 'Your Ghost site URL (e.g., https://your-site.com)' },
        { name: 'key', required: true, description: 'Your Ghost Admin API key (format: id:secret)' },
        { name: 'version', required: false, description: 'Ghost API version (default: v5.0)' }
      ]
    }
  });
});

// Smithery mcp-config endpoint for session configuration
app.get('/.well-known/mcp-config', (req: Request, res: Response) => {
  trackRequest(req, '/.well-known/mcp-config');
  res.json({
    schema: {
      type: 'object',
      properties: {
        url: {
          type: 'string',
          description: 'Your Ghost site URL (e.g., https://your-site.com)',
          title: 'Ghost URL'
        },
        key: {
          type: 'string',
          description: 'Your Ghost Admin API key (format: id:secret)',
          title: 'Admin API Key',
          format: 'password'
        },
        version: {
          type: 'string',
          description: 'Ghost API version',
          title: 'API Version',
          default: 'v5.0'
        }
      },
      required: ['url', 'key']
    }
  });
});

// Health check endpoint
app.get('/health', (req: Request, res: Response) => {
  trackRequest(req, '/health');
  res.json({
    status: 'healthy',
    server: 'Ghost CMS MCP Server',
    version: '0.1.0',
    transport: 'streamable-http',
    uptime: getUptime(),
    timestamp: new Date().toISOString(),
  });
});

// Root endpoint - server info
app.get('/', (req: Request, res: Response) => {
  trackRequest(req, '/');
  res.json({
    name: 'Ghost CMS MCP Server',
    version: '0.1.0',
    description: 'MCP server for Ghost CMS Admin API',
    transport: 'streamable-http',
    usage: {
      mcpUrl: 'https://mcp.techmavie.digital/ghostcms/mcp?url=YOUR_GHOST_URL&key=YOUR_ADMIN_KEY',
      parameters: {
        url: 'Your Ghost site URL (e.g., https://your-site.com)',
        key: 'Your Ghost Admin API key',
        version: 'Ghost API version (optional, default: v5.0)'
      }
    },
    endpoints: {
      health: '/health',
      mcp: '/mcp?url=YOUR_GHOST_URL&key=YOUR_ADMIN_KEY',
      analytics: '/analytics',
      dashboard: '/analytics/dashboard',
    },
    uptime: getUptime(),
  });
});

// Analytics JSON endpoint
app.get('/analytics', (req: Request, res: Response) => {
  trackRequest(req, '/analytics');
  
  const sortedHourly = Object.entries(analytics.hourlyRequests)
    .sort((a, b) => b[0].localeCompare(a[0]))
    .slice(0, 24)
    .reduce((acc, [k, v]) => ({ ...acc, [k]: v }), {});
  
  res.json({
    ...analytics,
    hourlyRequests: sortedHourly,
    uptime: getUptime(),
    currentTime: new Date().toISOString(),
  });
});

// Analytics tools endpoint
app.get('/analytics/tools', (req: Request, res: Response) => {
  trackRequest(req, '/analytics/tools');
  res.json({
    totalToolCalls: analytics.totalToolCalls,
    toolCalls: analytics.toolCalls,
    recentToolCalls: analytics.recentToolCalls.slice(0, 20),
  });
});

// Analytics dashboard HTML endpoint
app.get('/analytics/dashboard', (req: Request, res: Response) => {
  trackRequest(req, '/analytics/dashboard');
  
  const dashboardHtml = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ghost CMS MCP - Analytics Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; padding: 20px; min-height: 100vh; }
    .container { max-width: 1400px; margin: 0 auto; }
    h1 { font-size: 1.8rem; margin-bottom: 20px; color: #f8fafc; display: flex; align-items: center; gap: 10px; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 25px; }
    .stat-card { background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; }
    .stat-card h3 { font-size: 0.85rem; color: #94a3b8; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; }
    .stat-card .value { font-size: 2rem; font-weight: 700; color: #f8fafc; }
    .stat-card .sub { font-size: 0.8rem; color: #64748b; margin-top: 4px; }
    .charts-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin-bottom: 25px; }
    .chart-card { background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; }
    .chart-card h3 { font-size: 1rem; color: #f8fafc; margin-bottom: 15px; }
    .chart-container { position: relative; height: 250px; }
    .recent-activity { background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; }
    .recent-activity h3 { font-size: 1rem; color: #f8fafc; margin-bottom: 15px; }
    .activity-list { max-height: 300px; overflow-y: auto; }
    .activity-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #334155; }
    .activity-item:last-child { border-bottom: none; }
    .activity-tool { font-weight: 600; color: #60a5fa; }
    .activity-time { font-size: 0.8rem; color: #64748b; }
    .activity-ip { font-size: 0.75rem; color: #475569; }
    .refresh-btn { position: fixed; bottom: 20px; right: 20px; background: #3b82f6; color: white; border: none; padding: 12px 20px; border-radius: 8px; cursor: pointer; font-size: 0.9rem; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4); }
    .refresh-btn:hover { background: #2563eb; }
    .loading { text-align: center; padding: 40px; color: #64748b; }
  </style>
</head>
<body>
  <div class="container">
    <h1>👻 Ghost CMS MCP - Analytics Dashboard</h1>
    
    <div class="stats-grid">
      <div class="stat-card">
        <h3>Total Requests</h3>
        <div class="value" id="totalRequests">-</div>
        <div class="sub" id="requestsPerHour">- req/hour</div>
      </div>
      <div class="stat-card">
        <h3>Tool Calls</h3>
        <div class="value" id="totalToolCalls">-</div>
        <div class="sub" id="uniqueTools">- unique tools</div>
      </div>
      <div class="stat-card">
        <h3>Uptime</h3>
        <div class="value" id="uptime">-</div>
        <div class="sub" id="startTime">Started: -</div>
      </div>
      <div class="stat-card">
        <h3>Unique Clients</h3>
        <div class="value" id="uniqueClients">-</div>
        <div class="sub" id="topClient">Top: -</div>
      </div>
    </div>
    
    <div class="charts-grid">
      <div class="chart-card">
        <h3>Tool Usage</h3>
        <div class="chart-container"><canvas id="toolsChart"></canvas></div>
      </div>
      <div class="chart-card">
        <h3>Hourly Requests (Last 24h)</h3>
        <div class="chart-container"><canvas id="hourlyChart"></canvas></div>
      </div>
      <div class="chart-card">
        <h3>Requests by Endpoint</h3>
        <div class="chart-container"><canvas id="endpointChart"></canvas></div>
      </div>
      <div class="chart-card">
        <h3>Clients by User Agent</h3>
        <div class="chart-container"><canvas id="clientsChart"></canvas></div>
      </div>
    </div>
    
    <div class="recent-activity">
      <h3>Recent Tool Calls</h3>
      <div class="activity-list" id="activityList">
        <div class="loading">Loading...</div>
      </div>
    </div>
  </div>
  
  <button class="refresh-btn" onclick="loadData()">🔄 Refresh</button>
  
  <script>
    let toolsChart, hourlyChart, endpointChart, clientsChart;
    const chartColors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'];
    
    async function loadData() {
      try {
        const basePath = window.location.pathname.replace(/\\/analytics\\/dashboard\\/?$/, '');
        const res = await fetch(basePath + '/analytics');
        const data = await res.json();
        updateDashboard(data);
      } catch (err) {
        console.error('Failed to load analytics:', err);
      }
    }
    
    function updateDashboard(data) {
      document.getElementById('totalRequests').textContent = data.totalRequests.toLocaleString();
      document.getElementById('totalToolCalls').textContent = data.totalToolCalls.toLocaleString();
      document.getElementById('uptime').textContent = data.uptime;
      document.getElementById('startTime').textContent = 'Started: ' + new Date(data.serverStartTime).toLocaleString();
      document.getElementById('uniqueTools').textContent = Object.keys(data.toolCalls || {}).length + ' unique tools';
      document.getElementById('uniqueClients').textContent = Object.keys(data.clientsByIp || {}).length;
      
      const hourlyValues = Object.values(data.hourlyRequests || {});
      const avgPerHour = hourlyValues.length > 0 ? Math.round(hourlyValues.reduce((a, b) => a + b, 0) / hourlyValues.length) : 0;
      document.getElementById('requestsPerHour').textContent = avgPerHour + ' avg req/hour';
      
      const topClient = Object.entries(data.clientsByUserAgent || {}).sort((a, b) => b[1] - a[1])[0];
      document.getElementById('topClient').textContent = topClient ? 'Top: ' + topClient[0].substring(0, 20) : 'Top: -';
      
      updateToolsChart(data.toolCalls || {});
      updateHourlyChart(data.hourlyRequests || {});
      updateEndpointChart(data.requestsByEndpoint || {});
      updateClientsChart(data.clientsByUserAgent || {});
      updateActivityList(data.recentToolCalls || []);
    }
    
    function updateToolsChart(toolCalls) {
      const ctx = document.getElementById('toolsChart').getContext('2d');
      const labels = Object.keys(toolCalls).slice(0, 10);
      const values = Object.values(toolCalls).slice(0, 10);
      
      if (toolsChart) toolsChart.destroy();
      toolsChart = new Chart(ctx, {
        type: 'bar',
        data: { labels, datasets: [{ label: 'Calls', data: values, backgroundColor: chartColors }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { color: '#94a3b8' } }, x: { ticks: { color: '#94a3b8', maxRotation: 45 } } } }
      });
    }
    
    function updateHourlyChart(hourlyRequests) {
      const ctx = document.getElementById('hourlyChart').getContext('2d');
      const sorted = Object.entries(hourlyRequests).sort((a, b) => a[0].localeCompare(b[0])).slice(-24);
      const labels = sorted.map(([h]) => h.substring(11) + ':00');
      const values = sorted.map(([, v]) => v);
      
      if (hourlyChart) hourlyChart.destroy();
      hourlyChart = new Chart(ctx, {
        type: 'line',
        data: { labels, datasets: [{ label: 'Requests', data: values, borderColor: '#3b82f6', backgroundColor: 'rgba(59, 130, 246, 0.1)', fill: true, tension: 0.3 }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { color: '#94a3b8' } }, x: { ticks: { color: '#94a3b8' } } } }
      });
    }
    
    function updateEndpointChart(endpoints) {
      const ctx = document.getElementById('endpointChart').getContext('2d');
      const sorted = Object.entries(endpoints).sort((a, b) => b[1] - a[1]).slice(0, 8);
      const labels = sorted.map(([e]) => e);
      const values = sorted.map(([, v]) => v);
      
      if (endpointChart) endpointChart.destroy();
      endpointChart = new Chart(ctx, {
        type: 'doughnut',
        data: { labels, datasets: [{ data: values, backgroundColor: chartColors }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { color: '#94a3b8', boxWidth: 12 } } } }
      });
    }
    
    function updateClientsChart(clients) {
      const ctx = document.getElementById('clientsChart').getContext('2d');
      const sorted = Object.entries(clients).sort((a, b) => b[1] - a[1]).slice(0, 6);
      const labels = sorted.map(([c]) => c.substring(0, 25));
      const values = sorted.map(([, v]) => v);
      
      if (clientsChart) clientsChart.destroy();
      clientsChart = new Chart(ctx, {
        type: 'pie',
        data: { labels, datasets: [{ data: values, backgroundColor: chartColors }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { color: '#94a3b8', boxWidth: 12 } } } }
      });
    }
    
    function updateActivityList(recentCalls) {
      const list = document.getElementById('activityList');
      if (recentCalls.length === 0) {
        list.innerHTML = '<div class="loading">No recent tool calls</div>';
        return;
      }
      list.innerHTML = recentCalls.slice(0, 15).map(call => \`
        <div class="activity-item">
          <div>
            <span class="activity-tool">\${call.tool}</span>
            <div class="activity-ip">\${call.clientIp} - \${call.userAgent}</div>
          </div>
          <span class="activity-time">\${new Date(call.timestamp).toLocaleString()}</span>
        </div>
      \`).join('');
    }
    
    loadData();
    setInterval(loadData, 30000);
  </script>
</body>
</html>`;
  
  res.type('html').send(dashboardHtml);
});

// Analytics import endpoint
app.post('/analytics/import', (req: Request, res: Response) => {
  trackRequest(req, '/analytics/import');
  try {
    const importData = req.body;
    if (importData.totalRequests) {
      analytics.totalRequests += importData.totalRequests;
    }
    if (importData.totalToolCalls) {
      analytics.totalToolCalls += importData.totalToolCalls;
    }
    saveAnalytics();
    res.json({ 
      message: 'Analytics imported successfully',
      currentStats: {
        totalRequests: analytics.totalRequests,
        totalToolCalls: analytics.totalToolCalls,
      }
    });
  } catch (error) {
    res.status(400).json({ error: 'Failed to import analytics', details: String(error) });
  }
});

// MCP endpoint - handle all MCP protocol requests
app.all('/mcp', async (req: Request, res: Response) => {
  // Fix Accept header for MCP SDK compatibility
  // The SDK requires text/event-stream, but we want to accept */* and other common headers
  const acceptHeader = req.headers['accept'] || '';
  if (!acceptHeader.includes('text/event-stream')) {
    // Inject text/event-stream into Accept header so SDK accepts the request
    req.headers['accept'] = acceptHeader ? `${acceptHeader}, text/event-stream` : 'text/event-stream';
  }
  trackRequest(req, '/mcp');
  
  // Track tool calls
  if (req.body && req.body.method === 'tools/call' && req.body.params?.name) {
    trackToolCall(req.body.params.name, req);
  }
  
  try {
    // Extract Ghost credentials from query parameters
    let ghostUrl = req.query.url as string || DEFAULT_GHOST_API_URL;
    const ghostKey = req.query.key as string || DEFAULT_GHOST_ADMIN_API_KEY;
    const ghostVersion = req.query.version as string || DEFAULT_GHOST_API_VERSION;
    
    // Debug logging
    console.log(`[DEBUG] Received URL param: ${ghostUrl}`);
    
    // Auto-add https:// if missing protocol
    if (ghostUrl && !ghostUrl.match(/^https?:\/\//)) {
      ghostUrl = `https://${ghostUrl}`;
      console.log(`[DEBUG] Added https:// prefix: ${ghostUrl}`);
    }
    
    // Handle Smithery discovery/scanning requests (no credentials)
    // Smithery sends POST with MCP initialize/tools/list methods to discover server capabilities
    // We create a temporary demo server to handle these requests without real Ghost credentials
    const hasCredentials = ghostUrl && ghostKey;
    const mcpMethod = req.body?.method;
    const isDiscoveryRequest = !hasCredentials && mcpMethod && (
      mcpMethod === 'initialize' ||
      mcpMethod === 'tools/list' ||
      mcpMethod === 'resources/list' ||
      mcpMethod === 'prompts/list' ||
      mcpMethod === 'notifications/initialized'
    );
    
    if (isDiscoveryRequest) {
      // Create a demo MCP server for discovery (no real Ghost connection)
      console.log(`[DEBUG] Handling discovery request: ${mcpMethod}`);
      
      const demoServer = new McpServer({
        name: 'ghost-mcp-ts',
        version: '0.1.0',
        capabilities: {
          resources: {},
          tools: {},
          prompts: {},
          logging: {}
        }
      });
      
      // Register minimal demo tools for discovery
      demoServer.tool('ghost_list_posts', 'List all posts from Ghost CMS', {}, async () => ({
        content: [{ type: 'text', text: 'Demo: Requires Ghost credentials' }]
      }));
      demoServer.tool('ghost_create_post', 'Create a new post in Ghost CMS', {}, async () => ({
        content: [{ type: 'text', text: 'Demo: Requires Ghost credentials' }]
      }));
      demoServer.tool('ghost_list_members', 'List all members from Ghost CMS', {}, async () => ({
        content: [{ type: 'text', text: 'Demo: Requires Ghost credentials' }]
      }));
      demoServer.tool('ghost_list_tags', 'List all tags from Ghost CMS', {}, async () => ({
        content: [{ type: 'text', text: 'Demo: Requires Ghost credentials' }]
      }));
      demoServer.tool('ghost_list_newsletters', 'List all newsletters from Ghost CMS', {}, async () => ({
        content: [{ type: 'text', text: 'Demo: Requires Ghost credentials' }]
      }));
      
      const transport = new StreamableHTTPServerTransport({
        sessionIdGenerator: undefined,
      });
      
      res.on('close', () => {
        transport.close();
      });
      
      await demoServer.connect(transport);
      await transport.handleRequest(req, res, req.body);
      return;
    }
    
    // Validate required parameters for actual MCP requests
    if (!ghostUrl || !ghostKey) {
      return res.status(400).json({ 
        error: 'Missing required parameters',
        message: 'Please provide Ghost API credentials via query parameters: ?url=YOUR_GHOST_URL&key=YOUR_ADMIN_KEY',
        example: '/mcp?url=https://your-ghost-site.com&key=your-admin-api-key'
      });
    }
    
    // Create unique key for Ghost credentials (for server instance reuse)
    const credentialsKey = `${ghostUrl}:${ghostKey.split(':')[0]}`;
    
    // Get or create MCP server for these credentials
    let mcpServer = mcpServers.get(credentialsKey);
    if (!mcpServer) {
      mcpServer = createMcpServer(ghostUrl, ghostKey, ghostVersion);
      mcpServers.set(credentialsKey, mcpServer);
    }
    
    // Create a NEW transport for EACH request (stateless mode)
    // This allows multiple clients to connect without session conflicts
    const transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: undefined, // Let SDK generate unique session IDs
    });
    
    // Clean up transport after response is sent
    res.on('close', () => {
      transport.close();
    });
    
    await mcpServer.server.connect(transport);
    await transport.handleRequest(req, res, req.body);
  } catch (error) {
    console.error('MCP request error:', error);
    if (!res.headersSent) {
      res.status(500).json({ error: 'Internal server error', details: String(error) });
    }
  }
});

// Graceful shutdown
async function gracefulShutdown(signal: string) {
  console.log(`\nReceived ${signal}, shutting down gracefully...`);
  clearInterval(saveInterval);
  saveAnalytics(); // Save to local file
  if (firebaseAnalytics.isInitialized()) {
    await firebaseAnalytics.saveAnalytics(analytics); // Save to Firebase
  }
  console.log('Analytics saved. Goodbye!');
  process.exit(0);
}

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// Start server
app.listen(PORT, HOST, () => {
  console.log(`\n🚀 Ghost CMS MCP Server (HTTP) running on http://${HOST}:${PORT}`);
  console.log(`   Health: http://${HOST}:${PORT}/health`);
  console.log(`   MCP:    http://${HOST}:${PORT}/mcp`);
  console.log(`   Analytics: http://${HOST}:${PORT}/analytics`);
  console.log(`   Dashboard: http://${HOST}:${PORT}/analytics/dashboard`);
  console.log(`\n📊 Analytics will be saved to: ${ANALYTICS_FILE}`);
});
