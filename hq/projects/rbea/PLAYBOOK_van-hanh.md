# RB_EA — SÁCH KỊCH BẢN VẬN HÀNH (runbook + escalation matrix) — như phòng Risk/Ops của quỹ

Nguyên tắc: mỗi sự cố có (a) DẤU HIỆU phát hiện, (b) AI xử — tầng nào, (c) HÀNH ĐỘNG, (d) leo thang.
3 tầng quyền: **[EA]** tự động tick-level (nhanh nhất) · **[AGENT]** giám sát, chỉ được HÀNH ĐỘNG GIẢM
RỦI RO trong phạm vi red-line + báo cáo · **[NGƯỜI]** duyệt mọi thứ mở-rủi-ro / đổi param / phi thường.
Bất biến: agent CHỈ 1 chiều an toàn (`/halt`, cảnh báo); KHÔNG tự arm/vào lệnh/đổi tham số/deploy.

## A. KẾT NỐI & DATA
| Kịch bản | Dấu hiệu | Xử lý |
|---|---|---|
| Terminal Exness chết | watch: process mất / log im | [EA-external] MT5_Watchdog tự mở lại (5'). [AGENT] báo. [NGƯỜI] nếu >15' chưa lên. |
| Mất kết nối broker | watch: connected=false | [AGENT] báo ngay. Nếu >Y phút + có vị thế hở → [AGENT] gửi `/halt` (red-line). |
| Account bị đổi (kick) | log "account changed" | [AGENT] báo NGAY (bài học Fund EA chết 9 ngày). [NGƯỜI] khôi phục login. |
| Data feed lỗi/gap | ship: bar thiếu/nhảy | [AGENT] hoãn tối ưu trên data đó, báo. [NGƯỜI] xác minh. |

## B. SỨC KHOẺ EA
| Kịch bản | Dấu hiệu | Xử lý |
|---|---|---|
| EA rụng khỏi chart | log "removed" cuối | [AGENT] báo NGAY. [NGƯỜI] gắn lại (profile). |
| perm_halt=1 (breaker tổng) | file halt / panel | [EA] đã đóng hết + dừng (đúng thiết kế). [AGENT] báo + lý do. [NGƯỜI] điều tra trước khi reset. |
| Algo tắt ngoài ý muốn | watch: algo=OFF khi phải ON | [AGENT] báo. [NGƯỜI] quyết bật lại. |
| min-lot skip nhiều | ship: clear thấp ở balance hiện tại | [AGENT] cảnh báo under-trade. [NGƯỜI] tăng balance/đổi mode. |

## C. RỦI RO / DD (quan trọng nhất)
| Kịch bản | Dấu hiệu | Xử lý |
|---|---|---|
| Daily/Weekly breaker | EA tự NEUTRAL hết kỳ | [EA] tự xử. [AGENT] báo. |
| DD tổng tới 80% ngưỡng | watch: eq vs init_bal | [AGENT] cảnh báo SỚM (chưa halt). [NGƯỜI] theo dõi. |
| DD tổng chạm RED-LINE (vd 28%) | watch | **[AGENT] tự gửi `/halt`** (1 chiều an toàn) + báo. [NGƯỜI] hậu kiểm. |
| Vị thế hở khi EA rụng/mất kết nối | watch: pos>0 + EA/conn lỗi | **[AGENT] `/halt`** nếu quá ngưỡng thời gian. |

## D. THỰC THI & LỆCH BACKTEST
| Kịch bản | Dấu hiệu | Xử lý |
|---|---|---|
| Live lệch backtest (RRR/tần suất) | ship định kỳ so live-vs-model | [AGENT] báo edge-decay. [NGƯỜI] quyết giảm risk/xếp kho (KHÔNG tự đổi). |
| Slippage/spread bất thường | deals vs kỳ vọng | [AGENT] báo. [NGƯỜI] xem lại. |
| Chuỗi thua bất thường | ship: WR/PF rớt khỏi dải OOS | [AGENT] báo + đề xuất; [NGƯỜI] quyết. |

## E. THAY ĐỔI / DEPLOY (maker-checker)
| Kịch bản | Xử lý |
|---|---|
| Sửa code/param | [NGƯỜI] sửa → `rbea_ship` PASS → MT5 tester → [NGƯỜI] duyệt → deploy 1-click. KHÔNG agent tự deploy. |
| Tối ưu tham số | [AGENT] chạy sweep/MC trên data mới → ĐỀ XUẤT → [NGƯỜI] duyệt. Cấm auto-nạp-live. |
| Rollback | [NGƯỜI] hoặc [AGENT-nếu-red-line] về bản last-known-good. |

## RED-LINES — SẾP PHÊ DUYỆT 24/07/2026 (guard tự flatten+halt, 1 chiều an toàn)
- DD tổng ≥ **28%**
- Mất kết nối > **15 phút** khi có vị thế hở (flatten khi nối lại)
- EA rụng + còn vị thế hở > **10 phút**
THỰC THI: `rbea_guard` chạy NGAY TRÊN VPS (schtasks RBEA_Guard, 5 phút/lần, 24/7 — KHÔNG phụ thuộc
MacBook). Cảnh báo + heartbeat 6h qua Telegram (C:\qtq\tg_secret.txt). Halt = flatten qua MT5 python
+ ghi halt-file; EA v0.51 đọc lại file mỗi 60s (kill-switch [K1]) nên perm-halt cả EA đang chạy.

## POSTMORTEM (bắt buộc như quỹ)
Mỗi lần chạm red-line / sự cố lớn → ghi 1 mục DECISION_LOG + finding Drive: chuyện gì, vì sao,
đã xử ra sao, sửa gì để không lặp. (Không đổ lỗi — sửa hệ thống.)
