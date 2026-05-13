import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { extname, join, normalize, resolve } from 'node:path';
import { AgentRuntime } from './runtime/agentRuntime.js';
import { applyDeveloperCommand } from './developer/developerCommands.js';

const MIME = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8' };

export function createTownServerApp(options = {}) {
  const runtime = new AgentRuntime(options);
  return {
    runtime,
    getPublicState: () => runtime.getPublicState(),
    stepSimulation: (payload) => runtime.step(payload),
    command: (payload) => applyDeveloperCommand(runtime, payload),
  };
}

export function createHttpServer(app = createTownServerApp()) {
  const clients = new Set();
  app.runtime.eventStore.subscribe((event) => {
    for (const res of clients) res.write(`data: ${JSON.stringify(event)}\n\n`);
  });

  return createServer(async (req, res) => {
    try {
      const url = new URL(req.url, `http://${req.headers.host}`);
      if (url.pathname === '/api/state') return json(res, app.getPublicState());
      if (url.pathname === '/api/step' && req.method === 'POST') return json(res, await app.stepSimulation(await body(req)));
      if (url.pathname === '/api/developer' && req.method === 'POST') return json(res, app.command(await body(req)));
      if (url.pathname === '/api/events') {
        res.writeHead(200, { 'content-type': 'text/event-stream; charset=utf-8', 'cache-control': 'no-cache', connection: 'keep-alive' });
        clients.add(res);
        req.on('close', () => clients.delete(res));
        return;
      }
      return serveStatic(url.pathname, res);
    } catch (error) {
      json(res, { error: error.message }, 500);
    }
  });
}

async function serveStatic(pathname, res) {
  const safePath = pathname === '/' ? '/index.html' : pathname;
  const file = normalize(join(process.cwd(), 'frontend', safePath));
  if (!file.startsWith(normalize(join(process.cwd(), 'frontend')))) return json(res, { error: 'bad path' }, 400);
  const content = await readFile(file);
  res.writeHead(200, { 'content-type': MIME[extname(file)] ?? 'application/octet-stream' });
  res.end(content);
}

function json(res, data, status = 200) {
  res.writeHead(status, { 'content-type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(data));
}

async function body(req) {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  const raw = Buffer.concat(chunks).toString('utf8');
  return raw ? JSON.parse(raw) : {};
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const port = Number(process.env.PORT || 8787);
  const app = createTownServerApp();
  createHttpServer(app).listen(port, () => console.log(`AI Agent 小镇已启动：http://localhost:${port}`));
}
