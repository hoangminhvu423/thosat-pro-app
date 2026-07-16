#!/usr/bin/env bash
# SessionStart hook — nhắc quy trình + tự nhận diện dự án.
# Chỉ chạy khi bạn tự đăng ký trong .claude/settings.json (xem docs/claude-setup).
# _Prints the workflow reminder and detects which project ruleset applies._
set -euo pipefail

echo "──────────────────────────────────────────────"
echo " Agentic Engineering — STOP VIBE CODING"
echo " Vòng lặp / Loop: Research → Plan → Execute → Review → Ship"

if [ -f "app/engine.js" ] && [ -f "catalogue/schema.json" ]; then
  echo " Dự án / Project: App Thợ Sắt (ThợSắt Pro PWA)"
  echo " Rule: .claude/rules/thosat-app.md"
elif [ -d "backtest" ] || [ -d "strategy" ] || [ -d "backtests" ]; then
  echo " Dự án / Project: Quant Trading"
  echo " Rule: .claude/rules/quant-trading.md"
else
  echo " Dự án / Project: chưa nhận diện — hỏi người dùng / ask the user."
fi

echo " Lệnh / Commands: /research /plan /execute /review /ship"
echo "──────────────────────────────────────────────"
