export class RuleBasedProvider {
  constructor() {
    this.name = 'RuleBasedProvider';
  }

  async decide(context) {
    const { agent, nearby, clock } = context;
    let response;
    if (agent.status.energy < 35) {
      response = { speech: `${agent.name}觉得有点累，决定先恢复精力。`, action: 'rest', args: {}, memory_to_save: '我今天意识到需要保留体力。' };
    } else if (nearby.length > 0 && agent.status.social < 72) {
      const target = nearby[(clock.tick + agent.id.length) % nearby.length];
      response = { speech: `${target.name}，今天小镇的气氛有些不同，我们聊聊近况吧。`, action: 'talkTo', args: { npc: target.id, topic: 'daily_check', message: '今天感觉怎么样？如果需要帮助可以告诉我。' }, memory_to_save: `我主动和 ${target.name} 交流了今日近况。` };
    } else if (agent.job.includes('医生')) {
      response = { speech: '我需要巡查看看老人和孩子的健康状况。', action: 'careFor', args: { npc: 'orren' }, memory_to_save: '我把公共健康放在今天的优先级。' };
    } else if (agent.job.includes('店主') || agent.job.includes('木匠') || agent.job.includes('农夫') || agent.job.includes('农场主')) {
      response = { speech: '先把工作处理好，小镇稳定需要每个人尽责。', action: 'work', args: { job: agent.job }, memory_to_save: '我完成了一段职业工作。' };
    } else {
      const destinations = ['plaza', 'shop', 'clinic', 'tavern', 'home-north'];
      response = { speech: '我想换个地方观察大家今天的状态。', action: 'moveTo', args: { location: destinations[(clock.tick + agent.name.length) % destinations.length] }, memory_to_save: '我根据小镇气氛调整了当前位置。' };
    }
    return { provider: this.name, rawText: JSON.stringify(response), parsed: response, usage: { tokens: 0, cost: 0, latencyMs: 1 } };
  }
}
