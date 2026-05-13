export function parseProviderOutput(result) {
  if (result.parsed) return result.parsed;
  const raw = result.rawText?.trim() ?? '';
  const jsonMatch = raw.match(/\{[\s\S]*\}/);
  if (jsonMatch) {
    try { return JSON.parse(jsonMatch[0]); } catch {}
  }
  // 自然语言兜底会保留原文，前端 debug 仍能看到完整输出。
  return { speech: raw || '沉默片刻，继续观察小镇。', action: 'remember', args: {}, memory_to_save: raw.slice(0, 120) || '我进行了一次沉默观察。' };
}
