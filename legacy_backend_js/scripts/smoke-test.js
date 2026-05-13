// 这个 smoke test 会在不启动 HTTP 服务的情况下验证核心模块是否能被导入。
import { createTownServerApp } from '../backend/server.js';

const app = createTownServerApp({ enableLogs: false });
const initial = app.getPublicState();

if (!initial || initial.agents.length !== 10) {
  throw new Error(`期望 10 个初始 Agent，实际得到 ${initial?.agents?.length ?? '未知'}`);
}

const stepResult = await app.stepSimulation({ actorId: 'smoke-test' });
const afterStep = app.getPublicState();

if (!stepResult || afterStep.events.length === 0) {
  throw new Error('推进一轮后没有产生事件日志');
}

console.log('[smoke] ok', {
  agents: afterStep.agents.length,
  events: afterStep.events.length,
  tick: afterStep.clock.tick,
});
