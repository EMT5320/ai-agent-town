// 跨平台检查脚本：逐个执行语法检查和 smoke test，避免 Windows shell 分号差异。
import { spawnSync } from 'node:child_process';

const commands = [
  ['node', ['--check', 'backend/server.js']],
  ['node', ['--check', 'frontend/app.js']],
  ['node', ['scripts/smoke-test.js']],
];

for (const [command, args] of commands) {
  const result = spawnSync(command, args, { stdio: 'inherit', shell: false });
  if (result.status !== 0) process.exit(result.status ?? 1);
}
