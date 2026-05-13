import { advanceClock, createInitialWorld, livingAgents, publicWorld } from '../world/worldState.js';
import { EventStore } from '../events/eventStore.js';
import { RuleBasedProvider } from '../providers/ruleBasedProvider.js';
import { CloudApiProvider } from '../providers/cloudApiProvider.js';
import { buildAgentContext, buildPromptMessages } from '../providers/contextBuilder.js';
import { parseProviderOutput } from './actionParser.js';
import { executeAction, maybePopulationEvent } from './actionExecutor.js';

export class AgentRuntime {
  constructor({ providerMode = process.env.AGENT_TOWN_PROVIDER || 'rule', enableLogs = true } = {}) {
    this.world = createInitialWorld();
    this.eventStore = new EventStore();
    this.ruleProvider = new RuleBasedProvider();
    this.cloudProvider = new CloudApiProvider();
    this.providerMode = providerMode;
    this.enableLogs = enableLogs;
    this.eventStore.append('system.ready', { message: 'AI Agent 小镇运行时已启动。' });
  }

  getPublicState() {
    return { ...publicWorld(this.world), events: this.eventStore.list(), snapshots: this.eventStore.snapshots };
  }

  async step({ actorId = 'developer' } = {}) {
    if (this.world.clock.paused) return { skipped: true, reason: 'paused' };
    const actors = this.pickActors();
    const decisions = [];
    for (const agent of actors) {
      const context = buildAgentContext(this.world, agent, this.eventStore);
      const messages = buildPromptMessages(context);
      const provider = this.providerMode === 'cloud' ? this.cloudProvider : this.ruleProvider;
      let result;
      try {
        result = await provider.decide(context, messages);
      } catch (error) {
        result = await this.ruleProvider.decide(context, messages);
        this.eventStore.append('provider.fallback', { agentId: agent.id, error: error.message });
      }
      const parsed = parseProviderOutput(result);
      const executed = executeAction(this.world, agent, parsed, this.eventStore);
      const debug = { tick: this.world.clock.tick, provider: result.provider, messages, rawText: result.rawText, parsed, executed: executed.payload, usage: result.usage };
      agent.decisionHistory.push(debug);
      if (agent.decisionHistory.length > 10) agent.decisionHistory.shift();
      this.eventStore.append('debug.decision', { agentId: agent.id, agentName: agent.name, debug });
      decisions.push(debug);
    }
    maybePopulationEvent(this.world, this.eventStore);
    advanceClock(this.world);
    this.eventStore.addSnapshot(this.world);
    this.eventStore.append('runtime.step', { actorId, tick: this.world.clock.tick, day: this.world.clock.day, hour: this.world.clock.hour, actors: actors.map((agent) => agent.id) });
    return { decisions, state: this.getPublicState() };
  }

  pickActors() {
    const agents = livingAgents(this.world);
    const count = Math.min(3, agents.length);
    const start = this.world.clock.tick % agents.length;
    return Array.from({ length: count }, (_, index) => agents[(start + index) % agents.length]);
  }
}
