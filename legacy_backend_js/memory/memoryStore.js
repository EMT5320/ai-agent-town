export function remember(agent, text, { tick = 0, importance = 0.5, tags = [] } = {}) {
  agent.memories.push({ tick, importance, tags, text });
  if (agent.memories.length > 30) agent.memories.shift();
}

export function memorySummary(agent) {
  return agent.memories.slice(-6).map((memory) => `D${memory.tick}: ${memory.text}`).join('\n');
}
