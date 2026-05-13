import { adjustRelation, clamp, livingAgents } from '../world/worldState.js';
import { remember } from '../memory/memoryStore.js';

export function executeAction(world, agent, action, eventStore) {
  const type = action.action ?? 'remember';
  const args = action.args ?? {};
  const speech = action.speech ?? '';
  let summary = '';

  if (type === 'moveTo' && world.locations[args.location]) {
    const from = agent.locationId;
    agent.locationId = args.location;
    agent.status.energy = clamp(agent.status.energy - 4, 0, 100);
    summary = `${agent.name} 从 ${world.locations[from].name} 移动到 ${world.locations[agent.locationId].name}`;
  } else if (type === 'talkTo' && world.agents[args.npc]) {
    const target = world.agents[args.npc];
    agent.status.social = clamp(agent.status.social + 9, 0, 100);
    target.status.social = clamp(target.status.social + 5, 0, 100);
    adjustRelation(world, agent.id, target.id, { affection: 2, trust: 1, conflict: -1 });
    summary = `${agent.name} 对 ${target.name} 说：“${args.message ?? speech}”`;
  } else if (type === 'work') {
    agent.status.money = clamp(agent.status.money + 7, 0, 999);
    agent.status.energy = clamp(agent.status.energy - 11, 0, 100);
    world.townStats.economy = clamp(world.townStats.economy + 1, 0, 100);
    summary = `${agent.name} 完成了 ${args.job ?? agent.job} 的工作`;
  } else if (type === 'buy') {
    agent.status.money = clamp(agent.status.money - 4, 0, 999);
    agent.status.mood = clamp(agent.status.mood + 3, 0, 100);
    world.townStats.economy = clamp(world.townStats.economy + 1, 0, 100);
    summary = `${agent.name} 购买了 ${args.item ?? '生活用品'}`;
  } else if (type === 'rest') {
    agent.status.energy = clamp(agent.status.energy + 18, 0, 100);
    agent.status.stress = clamp(agent.status.stress - 8, 0, 100);
    summary = `${agent.name} 休息并恢复精力`;
  } else if (type === 'careFor' && world.agents[args.npc]) {
    const target = world.agents[args.npc];
    target.status.health = clamp(target.status.health + 5, 0, 100);
    target.status.mood = clamp(target.status.mood + 4, 0, 100);
    agent.status.energy = clamp(agent.status.energy - 6, 0, 100);
    adjustRelation(world, agent.id, target.id, { affection: 3, trust: 3 });
    summary = `${agent.name} 照顾了 ${target.name}`;
  } else if (type === 'attendEvent') {
    agent.status.mood = clamp(agent.status.mood + 2, 0, 100);
    world.townStats.harmony = clamp(world.townStats.harmony + 1, 0, 100);
    summary = `${agent.name} 参加了 ${args.event ?? '小镇公共事件'}`;
  } else {
    summary = `${agent.name} 记录了一次想法`;
  }

  if (action.memory_to_save) remember(agent, action.memory_to_save, { tick: world.clock.tick, importance: 0.55, tags: [type] });
  if (speech) eventStore.append('dialogue', { agentId: agent.id, agentName: agent.name, speech, action: type });
  return eventStore.append('action.executed', { agentId: agent.id, agentName: agent.name, type, args, summary });
}

export function maybePopulationEvent(world, eventStore) {
  const tick = world.clock.tick;
  if (tick > 0 && tick % 9 === 0) {
    const elder = livingAgents(world).find((agent) => agent.lifeStage === 'elder' && agent.status.health < 65);
    if (elder) {
      elder.status.health = clamp(elder.status.health - 2, 0, 100);
      eventStore.append('population.health_risk', { agentId: elder.id, agentName: elder.name, message: `${elder.name} 的健康状况需要关注。` });
    }
  }
  if (tick > 0 && tick % 14 === 0) {
    world.population.growthEvents += 1;
    world.townStats.curiosity = clamp(world.townStats.curiosity + 2, 0, 100);
    eventStore.append('population.growth', { message: '孩子们在新的一天学会了新的表达方式，社区开始讨论教育计划。' });
  }
}
