import { livingAgents } from '../world/worldState.js';
import { memorySummary } from '../memory/memoryStore.js';

export function buildAgentContext(world, agent, eventStore) {
  const nearby = livingAgents(world).filter((other) => other.id !== agent.id && other.locationId === agent.locationId).map((other) => ({ id: other.id, name: other.name, job: other.job, mood: other.status.mood }));
  return {
    agent: { id: agent.id, name: agent.name, age: agent.age, job: agent.job, personality: agent.personality, goals: agent.todayGoals, status: agent.status, intent: agent.currentIntent },
    clock: world.clock,
    location: world.locations[agent.locationId],
    nearby,
    memory: memorySummary(agent),
    townStats: world.townStats,
    recentEvents: eventStore.list().slice(-8),
    actions: ['moveTo', 'talkTo', 'work', 'buy', 'rest', 'careFor', 'attendEvent', 'remember', 'planDay'],
  };
}

export function buildPromptMessages(context) {
  // 云端 Provider 使用 OpenAI-compatible messages；RuleBasedProvider 也保存同样结构方便 debug。
  return [
    { role: 'system', content: '你是 AI Agent 小镇实验中的居民。请根据角色、关系、记忆和当前地点，自然地选择一个行动或说一句话。输出可为 JSON，也可为自然语言。' },
    { role: 'user', content: JSON.stringify(context, null, 2) },
  ];
}
