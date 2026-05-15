"""生成 Agent Valley 上下文 brief 草稿，并检查关键文档是否存在。"""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]

# Windows PowerShell 通过管道读取 Python 输出时可能出现编码漂移，统一用 UTF-8 输出。
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 这些文档构成新对话上下文的最小来源集合。
REQUIRED_DOCS = [
    "docs/agent_context.md",
    "docs/goal_board.md",
    "docs/README.md",
    "docs/project_vision.md",
    "docs/current_status.md",
    "docs/agentic_game_design.md",
    "docs/vertical_slice_spec.md",
]


def read_text(relative_path: str) -> str:
    """按 UTF-8 读取仓库内文档。"""
    return (ROOT / relative_path).read_text(encoding="utf-8")


def extract_section_after_heading(text: str, heading: str, max_lines: int = 2) -> str:
    """提取某个 Markdown 标题下的首段文本。"""
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == heading:
            collected: list[str] = []
            for next_line in lines[index + 1 :]:
                stripped = next_line.strip()
                if stripped.startswith("#"):
                    break
                if stripped:
                    collected.append(stripped)
                if len(collected) >= max_lines:
                    break
            return " ".join(collected)
    return ""


def extract_bullet_section(text: str, heading: str, max_items: int = 6) -> list[str]:
    """提取某个标题下的首批列表项，供 brief 输出当前入口。"""
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == heading:
            collected: list[str] = []
            for next_line in lines[index + 1 :]:
                stripped = next_line.strip()
                if stripped.startswith("#"):
                    break
                # 支持普通列表和编号列表，避免状态文档格式变化后 brief 失效。
                if stripped.startswith("- ") or (stripped[:2].strip(".").isdigit() and ". " in stripped[:4]):
                    collected.append(stripped)
                if len(collected) >= max_items:
                    break
            return collected
    return []


def collect_missing_docs() -> list[str]:
    """返回当前缺失的关键文档路径。"""
    return [path for path in REQUIRED_DOCS if not (ROOT / path).exists()]


def build_brief() -> str:
    """基于现有文档生成轻量 brief 草稿。"""
    agent_context = read_text("docs/agent_context.md")
    goal_board = read_text("docs/goal_board.md")
    vision = read_text("docs/project_vision.md")
    status = read_text("docs/current_status.md")

    one_liner = extract_section_after_heading(vision, "## 一句话定位", max_lines=1)
    phase = extract_section_after_heading(status, "## 1. 当前阶段判断", max_lines=6)
    next_steps = extract_bullet_section(agent_context, "## 6. 下一轮最短开发入口", max_items=6)
    schedule = extract_bullet_section(goal_board, "## 8. 下一轮推荐排程", max_items=5)

    return "\n".join(
        [
            "# Agent Valley brief 草稿",
            "",
            "## 一句话定位",
            "",
            one_liner or "- 未能从 `docs/project_vision.md` 提取定位。",
            "",
            "## 当前阶段",
            "",
            phase or "- 未能从 `docs/current_status.md` 提取阶段判断。",
            "",
            "## 最近下一步",
            "",
            "\n".join(next_steps) or "- 未能从 `docs/agent_context.md` 提取下一步。",
            "",
            "## 推荐排程",
            "",
            "\n".join(schedule) or "- 未能从 `docs/goal_board.md` 提取推荐排程。",
            "",
            "## 建议下一步",
            "",
            "- 先读 `docs/agent_context.md`。",
            "- 再按任务线读取 `docs/goal_board.md` 和对应源文档。",
            "- 修改后运行 `npm.cmd run check` 与 `git diff --check`。",
        ]
    )


def main() -> int:
    """命令行入口：先检查文档，再输出 brief 草稿。"""
    missing_docs = collect_missing_docs()
    if missing_docs:
        print("[agent-context] 缺少关键文档：")
        for path in missing_docs:
            print(f"- {path}")
        return 1

    print("[agent-context] 关键文档检查通过。")
    print()
    print(build_brief())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
