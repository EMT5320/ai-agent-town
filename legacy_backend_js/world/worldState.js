import { AGENTS, INITIAL_RELATIONS, LOCATIONS } from './seedData.js';

const clone = (value) => JSON.parse(JSON.stringify(value));

export function createInitialWorld() {
  const agents = Object.fromEntries(AGENTS.map((agent) => [agent.id, createAgent(agent)]));
  const relations = {};
  for (const [a, b, affection, trust, conflict, kind] of INITIAL_RELATIONS) {
    setRelation(relations, a, b, { affection, trust, conflict, kind });
  }
  return {
    clock: { day: 1, hour: 8, tick: 0, phase: 'morning', paused: false },
    locations: Object.fromEntries(LOCATIONS.map((location) => [location.id, clone(location)])),
    agents,
    relations,
    population: { births: 0, deaths: 0, migrationsIn: 1, migrationsOut: 0, growthEvents: 0 },
    townStats: { funds: 500, harmony: 63, economy: 58, health: 72, curiosity: 80 },
    activeFocus: null,
  };
}

function createAgent(seed) {
  return {
    ...clone(seed),
    status: { energy: seed.lifeStage === 'elder' ? 56 : 78, mood: seed.lifeStage === 'child' ? 82 : 64, stress: seed.personality.includes('轻微焦虑') ? 38 : 22, social: 50, money: seed.money, health: seed.health },
    currentIntent: '观察小镇今日变化',
    todayGoals: seed.longTermGoals.slice(0, 2),
    memories: [{ tick: 0, importance: 0.6, text: `${seed.name} 开始了小镇实验的第一天。` }],
    decisionHistory: [],
    alive: true,
  };
}

export function getRelation(world, a, b) {
  return world.relations[relationKey(a, b)] ?? { affection: 45, trust: 45, conflict: 0, kind: 'acquaintance' };
}

export function setRelation(relations, a, b, patch) {
  relations[relationKey(a, b)] = { ...relations[relationKey(a, b)], ...patch };
}

export function adjustRelation(world, a, b, delta) {
  const current = getRelation(world, a, b);
  setRelation(world.relations, a, b, {
    affection: clamp(current.affection + (delta.affection ?? 0), 0, 100),
    trust: clamp(current.trust + (delta.trust ?? 0), 0, 100),
    conflict: clamp(current.conflict + (delta.conflict ?? 0), 0, 100),
    kind: delta.kind ?? current.kind,
  });
}

export function advanceClock(world) {
  world.clock.tick += 1;
  world.clock.hour += 1;
  if (world.clock.hour >= 22) {
    world.clock.day += 1;
    world.clock.hour = 8;
  }
  world.clock.phase = world.clock.hour < 12 ? 'morning' : world.clock.hour < 18 ? 'afternoon' : 'evening';
}

export function publicWorld(world) {
  return {
    clock: clone(world.clock),
    locations: Object.values(world.locations),
    agents: Object.values(world.agents).map((agent) => ({ ...clone(agent), memories: agent.memories.slice(-5), decisionHistory: agent.decisionHistory.slice(-3) })),
    relations: clone(world.relations),
    population: clone(world.population),
    townStats: clone(world.townStats),
    activeFocus: world.activeFocus,
  };
}

export function livingAgents(world) {
  return Object.values(world.agents).filter((agent) => agent.alive);
}

export function relationKey(a, b) {
  return [a, b].sort().join('::');
}

export function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}
