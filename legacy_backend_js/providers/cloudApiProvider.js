export class CloudApiProvider {
  constructor({ apiKey = process.env.DEEPSEEK_API_KEY || process.env.OPENAI_API_KEY, baseUrl = process.env.AGENT_TOWN_BASE_URL || 'https://api.deepseek.com', model = process.env.AGENT_TOWN_MODEL || 'deepseek-chat' } = {}) {
    this.name = 'CloudApiProvider';
    this.apiKey = apiKey;
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.model = model;
  }

  async decide(_context, messages) {
    if (!this.apiKey) throw new Error('CloudApiProvider 缺少 API Key，请设置 DEEPSEEK_API_KEY 或 OPENAI_API_KEY。');
    const started = Date.now();
    const response = await fetch(`${this.baseUrl}/chat/completions`, {
      method: 'POST',
      headers: { 'content-type': 'application/json', authorization: `Bearer ${this.apiKey}` },
      body: JSON.stringify({ model: this.model, messages, temperature: 0.8 }),
    });
    if (!response.ok) throw new Error(`CloudApiProvider 请求失败：${response.status} ${await response.text()}`);
    const data = await response.json();
    const rawText = data.choices?.[0]?.message?.content ?? '';
    return { provider: this.name, rawText, parsed: null, usage: { tokens: data.usage?.total_tokens ?? 0, cost: 0, latencyMs: Date.now() - started } };
  }
}
