export class EventStore {
  constructor({ maxEvents = 500 } = {}) {
    this.maxEvents = maxEvents;
    this.events = [];
    this.snapshots = [];
    this.listeners = new Set();
  }

  append(type, payload = {}, meta = {}) {
    const event = { id: `evt_${Date.now()}_${Math.random().toString(16).slice(2)}`, type, payload, meta, createdAt: new Date().toISOString() };
    this.events.push(event);
    if (this.events.length > this.maxEvents) this.events.shift();
    for (const listener of this.listeners) listener(event);
    return event;
  }

  addSnapshot(world) {
    // 快照只保留轻量摘要，避免第一版内存持续膨胀。
    this.snapshots.push({ tick: world.clock.tick, day: world.clock.day, hour: world.clock.hour, agents: Object.keys(world.agents).length, at: new Date().toISOString() });
    if (this.snapshots.length > 80) this.snapshots.shift();
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  list() {
    return this.events.slice();
  }
}
