# G1 — Kết quả compile RB_EA_v0.31.mq5 (2026-07-24, cửa sổ deploy MacBook)

## Kết quả
```
Result: 0 errors, 1 warnings, 2760 msec elapsed, cpu='X64 Regular'
```
→ **G1 CHƯA ĐẠT** theo chuẩn gate "0 error 0 warning" (deploy-vps SKILL). Dừng trước G2 theo STATE.

## Chi tiết warning duy nhất
```
RB_EA_v0.31.mq5(30,11) : warning 68: version '0.31' is incompatible with MQL5 Market, must be xxx.yyy
```
- Dòng 30: `#property version   "0.31"` — MetaEditor đòi format `xxx.yyy` (vd `"0.310"`).
- Bản chất: **metadata cho MQL5 Market, KHÔNG ảnh hưởng logic/runtime**. Binary .ex5 vẫn sinh ra đầy đủ.

## Đề xuất cho phiên R&D (vá theo vòng audit, cửa sổ deploy không tự sửa)
- Sửa 1 dòng: `#property version   "0.310"` → compile lại sạch 0/0.
- Đây là diff metadata thuần — re-audit diff chỉ cần xác nhận đúng 1 dòng đó.
- HOẶC: Sếp phán "warning 68 chấp nhận được cho account cá nhân" → G1 coi như đạt, chạy tiếp G2
  (ghi 1 dòng DECISION_LOG). Người quyết: Sếp.

## Bằng chứng / môi trường
- File nguồn: `rbea-research/RB_EA_v0.31.mq5` @ commit 5dab78b, sha256 `29fe77e1e5009207…` (khớp VPS sau upload).
- Stage tại: Exness tree `MQL5/Experts/QTQ_MultiTF_DEMO/RB_EA_v0.31.mq5` (dir staging compile-validate,
  không đụng EA live). `.ex5` đã sinh, nằm cùng chỗ, chưa attach vào bất kỳ chart nào.
- Pipeline: `quant_lab/safe_compile.py` (backup 3 .ex5 live trước tại `EA_backups/20260724_143906`).
- MetaEditor tree Exness, log đọc qua PowerShell Unicode. 2 terminal live không bị đụng.
