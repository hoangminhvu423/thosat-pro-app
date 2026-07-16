# Bộ khung Agentic Engineering cho Claude Code

> Cách tái sử dụng workflow + skill này cho các dự án khác.
> _How to reuse this Claude Code kit across projects._

## Có gì trong bộ khung / What's inside
```
CLAUDE.md                     # Hub điều phối — Claude đọc đầu mỗi phiên
.claude/
  rules/                      # Quy tắc: core-workflow + từng loại dự án
    core-workflow.md          #   Vòng lặp R→P→E→R→S (mọi dự án)
    thosat-app.md             #   Dự án App Thợ Sắt (PWA)
    quant-trading.md          #   Dự án Quant Trading
  commands/                   # Slash commands: /research /plan /execute /review /ship
  agents/                     # Subagents: researcher, planner, reviewer
  skills/                     # Skills theo dự án: them-mau, phat-hanh (thợ sắt)
  hooks/session-start.sh      # (opt-in) In nhắc workflow + auto-detect dự án
docs/claude-setup/            # Tài liệu + install.sh này
```

## Cài sang dự án khác / Install into another project
Từ **gốc repo này**:
```bash
# Copy .claude/ + CLAUDE.md sang một repo khác
bash docs/claude-setup/install.sh /đường/dẫn/tới/repo-khac

# Hoặc cài toàn máy vào ~/.claude (áp dụng mọi dự án)
bash docs/claude-setup/install.sh --global
```
Sau khi copy: chỉnh `.claude/rules/` cho khớp loại dự án ở đích (thêm rule mới nếu là loại dự án khác).

> ⚠️ **Môi trường Claude Code trên web là container tạm** — `~/.claude` sẽ mất khi hết phiên.
> Cách bền vững: giữ bộ khung trong repo (đã commit) và copy lại khi cần. `--global` chỉ hữu ích trên máy cá nhân.

## Bật hook + quyền (tùy chọn) / Enable hook & permissions (optional)
Vì lý do an toàn, repo **không** kèm `.claude/settings.json` sống (settings tự thay đổi hành vi harness).
Nếu muốn bật SessionStart hook và bớt hỏi quyền cho lệnh an toàn, **tự tạo** `.claude/settings.json` với nội dung mẫu:

```jsonc
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(git status:*)",
      "Bash(git diff:*)",
      "Bash(git log:*)",
      "Bash(python3 -m http.server:*)",
      "Bash(node:*)",
      "Read", "Grep", "Glob"
    ],
    "deny": [ "Read(./**/*.pem)", "Read(./**/.env)", "Read(./**/*.key)" ]
  },
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "bash .claude/hooks/session-start.sh" } ] }
    ]
  }
}
```
Đọc kỹ `.claude/hooks/session-start.sh` trước khi bật — hook TỰ CHẠY mỗi phiên. Chỉnh danh sách `allow` theo mức tin cậy của bạn.

## Quy trình cốt lõi / The core loop
**Research → Plan → Execute → Review → Ship.** Chi tiết: `.claude/rules/core-workflow.md`.
Mô hình điều phối: **Command → Agent → Skill**.
