import { remember } from '../memory/memoryStore.js';
import { clamp } from '../world/worldState.js';

export function applyDeveloperCommand(runtime, command = {}) {
  const { world, eventStore } = runtime;
  const type = command.type;
  if (type === 'pause') world.clock.paused = true;
  if (type === 'resume') world.clock.paused = false;
  if (type === 'focus') world.activeFocus = command.agentId ?? null;
  if (type === 'injectEvent') {
    eventStore.append(command.eventType ?? 'developer.injected', { message: command.message ?? '开发者注入了一个实验事件。', payload: command.payload ?? {} }, { actor: 'developer' });
  }
  if (type === 'adjustAgent' && world.agents[command.agentId]) {
    const agent = world.agents[command.agentId];
    for (const [key, value] of Object.entries(command.status ?? {})) agent.status[key] = clamp(Number(value), 0, 999);
    remember(agent, command.memory ?? '开发者调整了我的实验状态。', { tick: world.clock.tick, importance: 0.75, tags: ['developer'] });
    eventStore.append('developer.adjust_agent', { agentId: agent.id, status: agent.status });
  }
  return runtime.getPublicState();
}
