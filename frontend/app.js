const state = { data: null, auto: null };

const $ = (id) => document.getElementById(id);

async function api(path, options = {}) {
  const response = await fetch(path, { headers: { 'content-type': 'application/json' }, ...options });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

async function load() {
  state.data = await api('/api/state');
  render();
}

function render() {
  const data = state.data;
  if (!data) return;
  $('clock').textContent = `Day ${data.clock.day} · ${String(data.clock.hour).padStart(2, '0')}:00 · ${data.clock.phase}${data.clock.paused ? ' · Paused' : ''}`;
  renderStats(data);
  renderMap(data);
  renderAgents(data);
  renderEvents(data);
  renderDebug(data);
}

function renderStats(data) {
  $('stats').innerHTML = Object.entries({ 和谐: data.townStats.harmony, 经济: data.townStats.economy, 健康: data.townStats.health, 好奇: data.townStats.curiosity, 出生: data.population.births, 成长: data.population.growthEvents }).map(([k, v]) => `<div class="stat"><span>${k}</span><b>${v}</b></div>`).join('');
}

function renderMap(data) {
  const map = $('map');
  map.innerHTML = '';
  for (const location of data.locations) {
    const el = document.createElement('div');
    el.className = 'location';
    el.style.left = `${location.x}%`; el.style.top = `${location.y}%`; el.style.boxShadow = `0 0 32px ${location.color}55`;
    el.innerHTML = `<b>${location.name}</b><small>${location.description}</small>`;
    map.appendChild(el);
  }
  for (const agent of data.agents.filter((a) => a.alive)) {
    const location = data.locations.find((item) => item.id === agent.locationId);
    const jitter = hash(agent.id) % 12 - 6;
    const dot = document.createElement('div');
    dot.className = 'agent-dot'; dot.style.left = `${location.x + jitter / 2}%`; dot.style.top = `${location.y + jitter}%`; dot.title = `${agent.name} · ${agent.job}`; dot.textContent = agent.name.slice(0, 1);
    map.appendChild(dot);
    const last = agent.decisionHistory.at(-1)?.parsed?.speech;
    if (last) {
      const bubble = document.createElement('div');
      bubble.className = 'bubble'; bubble.style.left = dot.style.left; bubble.style.top = dot.style.top; bubble.textContent = `${agent.name}: ${last}`;
      map.appendChild(bubble);
    }
  }
}

function renderAgents(data) {
  $('agents').innerHTML = data.agents.map((agent) => `<div class="agent"><div><b>${agent.name}</b><br><small>${agent.job} · ${agent.lifeStage} · ${data.locations.find((l) => l.id === agent.locationId)?.name}</small></div><div>心情 ${agent.status.mood}<br>精力 ${agent.status.energy}</div></div>`).join('');
}

function renderEvents(data) {
  $('events').innerHTML = data.events.slice(-18).reverse().map((event) => `<div class="event"><b>${event.type}</b><br><small>${new Date(event.createdAt).toLocaleTimeString()}</small><div>${event.payload.summary ?? event.payload.message ?? event.payload.speech ?? ''}</div></div>`).join('');
}

function renderDebug(data) {
  const latest = [...data.agents].flatMap((agent) => agent.decisionHistory.map((debug) => ({ agent: agent.name, ...debug }))).sort((a, b) => b.tick - a.tick)[0];
  $('debug').textContent = latest ? JSON.stringify(latest, null, 2) : '等待第一轮决策...';
}

function hash(text) { return [...text].reduce((sum, ch) => sum + ch.charCodeAt(0), 0); }

$('stepBtn').onclick = async () => { await api('/api/step', { method: 'POST', body: '{}' }); await load(); };
$('autoBtn').onclick = () => { if (state.auto) { clearInterval(state.auto); state.auto = null; return; } state.auto = setInterval(async () => { await api('/api/step', { method: 'POST', body: '{}' }); await load(); }, 1400); };
$('pauseBtn').onclick = async () => { await api('/api/developer', { method: 'POST', body: JSON.stringify({ type: state.data.clock.paused ? 'resume' : 'pause' }) }); await load(); };
$('eventBtn').onclick = async () => { await api('/api/developer', { method: 'POST', body: JSON.stringify({ type: 'injectEvent', eventType: 'town.festival', message: '开发者注入：今晚中央广场临时举办星灯节。' }) }); await load(); };

try { const es = new EventSource('/api/events'); es.onmessage = () => load(); } catch {}
load();
