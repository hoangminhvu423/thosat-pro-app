---
name: deploy-vps
description: Lấy EA chuẩn từ GitHub (nhánh air-drop, file chuẩn xem hq/projects/rbea/STATE.md) và deploy lên VPS qua các cổng Guardian G1-G5. Dùng khi Sếp yêu cầu deploy EA từ bất kỳ cửa sổ MacBook nào. CẤM cắm thẳng account thật.
---

# SKILL: deploy-vps — lấy EA chuẩn từ GitHub và deploy lên VPS (cho cửa sổ local MacBook)
Dùng khi: Sếp yêu cầu "deploy EA lên VPS" từ bất kỳ cửa sổ Claude nào trên MacBook
(nơi đã có sẵn cầu nối VPS: quản lý file, risk, audit MQL5).

## NGUỒN CHUẨN (duy nhất — không lấy file từ nơi khác)
```
git clone --depth 1 -b claude/du-an-air-drop-y3ifan https://github.com/hoangminhvu423/thosat-pro-app
# hoặc pull nếu đã có clone
```
- File EA chuẩn hiện hành: xem dòng "File chuẩn" trong `hq/projects/rbea/STATE.md` — KHÔNG hardcode
  version trong đầu. (Tại 2026-07-24: `rbea-research/RB_EA_v0.31.mq5`.)
- Kiểm tra chống nhầm bản: header file phải có đúng version khớp STATE.md; file có banner
  "DA THAY THE" là bản cũ — CẤM deploy.

## CỔNG BẮT BUỘC TRƯỚC KHI FILE ĐƯỢC CHẠM VÀO TIỀN (Guardian Rules — không được bỏ bậc)
1. **G1 Compile**: MetaEditor trên VPS (`metaeditor64.exe /compile:"<file>" /log`) — 0 error 0 warning.
2. **G2 Tester**: Strategy Tester visual 3 tháng gần, CẢ 2 profile (XAU semi + BTC auto). Không lệnh phi logic.
3. Chỉ sau G1+G2 sạch → cắm **DEMO** (G4, ≥4 tuần & ≥40 lệnh). **CẤM cắm thẳng account thật/FTMO.**
4. G5 go/no-go (so demo vs backtest) → mới tới FTMO Swing.

## SET-FILE KHI DEPLOY (đọc kỹ STATE.md mục "FTMO set-file cần nhớ")
| Tham số | XAU chart 1 (SEMI) | BTC chart 2 (AUTO) |
|---|---|---|
| I_AutoZone | false | **true** |
| I_RangeEnabled | true | **false** |
| I_Magic | 20260723 | 20260724 |
| I_RiskPct | 0.15 | 0.15 |
| **I_InitBalance** | **BẮT BUỘC = $ account** (vd 200000) | như bên |
| I_FridayCleanup | true | (vô hiệu với AUTO — code tự bỏ qua) |
| I_TGToken/ChatID | token + chat-id của Sếp | như bên |
- MT5: Tools→Options→Expert Advisors: whitelist `https://api.telegram.org`.
- Account demo/FTMO phải là loại **Swing** (hold 192h + weekend).

## SAU KHI DEPLOY
- Chụp/ghi log OnInit ("RB_EA v0.31 online") + /status Telegram trả lời đúng.
- Ghi 1 dòng vào `hq/decisions/DECISION_LOG.md` (ngày, version, account, ai duyệt) — commit push lên
  nhánh `claude/du-an-air-drop-y3ifan` để mọi phiên khác biết trạng thái deploy.
- Tuần đầu: chạy checklist 5' (spec mục 6) mỗi ngày thay vì mỗi tuần.

## CẤM
- Sửa bất kỳ dòng code nào trong lúc deploy ("tiện tay fix") — mọi sửa đổi phải quay về vòng
  audit → re-audit trên repo trước.
- Deploy bản chưa qua G1/G2 lên bất kỳ terminal nào có kết nối account thật.
