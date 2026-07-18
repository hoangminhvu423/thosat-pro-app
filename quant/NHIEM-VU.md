# NHIỆM VỤ — Phòng lab quét phương pháp trên data M1 thật

> File lệnh cho phiên Claude Code local (trên Mac). Đọc xong LÀM THEO, không cần hỏi lại
> trừ khi thiếu data hoặc gặp mâu thuẫn. Ngữ cảnh đầy đủ: `docs/quant-handoff.md` (ĐỌC TRƯỚC TIÊN).

## Đọc trước (bắt buộc, theo thứ tự)
1. `docs/boi-canh-tu-duy.md` — **người dùng là ai + thế giới quan + toàn bộ dòng suy luận** (đọc ĐẦU TIÊN).
2. `docs/quant-handoff.md` — ngữ cảnh kỹ thuật + giao thức 7 bước.
3. `quant/REVIEW-cloud.md` — **4 cảnh báo data từ giám khảo cloud — XỬ LÝ TRƯỚC KHI SWEEP.**
4. `data/GHI-CHU.md` — kiểm kê data thật (18 mã parquet, bẫy tz/khe/mã cụt).
5. `quant/backtest_vote.py` — harness đã chứng thực (selftest random-walk → EV≈0).
6. `.claude/rules/quant-trading.md` — quy tắc dự án quant (MT5/MQL5, no look-ahead...).

## Bối cảnh 1 đoạn
Người dùng: builder-first quant (~2 năm EA/MQL5, đã phá hàng nghìn EA), trade forex + BTC + chỉ số
CFD trên MT5/Exness, đang thi FTMO 100k. Luận đề đã chốt: *logic tĩnh công khai đều bị arbitrage cạn*.
Nhiệm vụ này là **kiểm chứng luận đề đó bằng số liệu thật** — số hoá "bản đồ nghĩa địa" các phương pháp
phổ biến, và xem có con nào sống sót thật không.

## TRẠNG THÁI CODE (phiên cloud đã dựng + selftest xong — ĐỪNG viết lại từ đầu)
- ✅ `quant/logics.py` — 12 logic session-agnostic đã có (PA/SMC/heuristic/đối chứng).
- ✅ `quant/run_all.py` — bộ quét walk-forward (IS60/OOS25/VALID15), phí, bootstrap, ledger, bảng xếp hạng.
- ✅ Đã selftest stdlib: random-walk → EV≈0 (không look-ahead); momentum → lộ edge (pipeline sống).
- **Việc của phiên Mac**: (1) `git pull`; (2) đối chiếu `python3 quant/run_all.py --selftest` — số phải KHỚP
  với phiên cloud; (3) chạy thật `python3 quant/run_all.py --data data --khung H1 H4` (thêm M5 M15 sau);
  (4) tinh chỉnh từng logic trong `logics.py` NẾU muốn (giữ 2 luật: chỉ dùng bars[<=i], trả [-1,1]);
  (5) commit + push `quant/results/ledger.csv` + `BAO-CAO.md`.
- Bổ sung sau (không chặn): logic ICT theo giờ (cần dò tz trước), thêm data BTC M1.

## Việc cần làm (chi tiết tham chiếu — phần lớn ĐÃ có trong code trên)

### 1. Code hoá các phương pháp phổ biến thành hàm score
Mỗi phương pháp = 1 hàm `score(bars, i) -> [-1, +1]` (CHỈ dùng `bars[<=i]`), cắm vào
`DANH_SACH_LOGIC` trong harness (hoặc module riêng `quant/logics/`):
- **Price Action**: pin bar, engulfing, inside/outside bar, break of structure (BOS).
- **SMC/ICT**: order block, fair value gap (FVG), liquidity sweep, BOS/CHoCH, premium/discount.
- **Elliott (heuristic)**: đếm sóng đơn giản hoá (zigzag swing → sóng 3/5) — GHI RÕ đây là *một cách
  diễn giải*, kết quả xấu = "bản code này chết", không kết luận cho phương pháp gốc.
- **Wyckoff (heuristic)**: spring/upthrust quanh trading range.
- **Supply/Demand**: vùng cầu/cung từ swing + phản ứng giá.
(Có thể thêm: divergence RSI/momentum thô, breakout kênh — làm nhóm đối chứng "chỉ báo cổ điển".)

### 2. Viết `quant/run_all.py` — bộ quét tự động
- Đầu vào: mọi file `data/*_m1.parquet` (18 mã, ~145,8 triệu nến M1 — ĐỌC `data/GHI-CHU.md`
  trước: kiểm kê, bẫy múi giờ, mã cụt). **Resample M1 → M5/M15/H1/H4** rồi test từng khung.
- Với mỗi (phương pháp × symbol × khung): chạy backtest theo ĐÚNG giao thức:
  1. Tín hiệu tại nến ĐÃ ĐÓNG index i → vào lệnh OPEN nến i+1. KHÔNG look-ahead.
  2. Walk-forward: calibrate/chọn ngưỡng CHỈ trên in-sample (60% đầu), đóng băng cho OOS.
  3. Cộng phí: spread + commission + slippage theo R (tra spread Exness thật của từng symbol).
  4. SL/TP theo ATR, PnL theo R-multiple — giống nhau cho mọi phương pháp.
  5. Bootstrap CI 95% cho EV.
- Ghi từng dòng vào `quant/results/ledger.csv`:
  `phuong_phap,symbol,khung,doan(IS/OOS),n_lenh,ev_r,win_pct,pf,sharpe,maxdd_r,ci_lo,ci_hi,ghi_chu`
- In **bảng xếp hạng OOS** khi xong. Nếu M1 quá lớn cho stdlib → dùng numpy/pandas.

### 3. Vòng kiểm tra "sống sót" (chống multiple-testing)
⚠️ Với hàng trăm thí nghiệm, con "đẹp nhất" MẶC ĐỊNH là nhiễu. Con nào EV OOS > 0 với CI không
chứa 0 phải qua thêm:
- **Đoạn validation chưa từng đụng** (giữ lại 15% data cuối cùng, KHÔNG dùng ở bước 2).
- **Symbol khác** cùng loại (edge thật thường không chỉ sống trên 1 cặp).
- Chỉ con qua CẢ HAI mới đánh dấu `song_sot=true` trong ledger.

### 4. Kết thúc
- Viết `quant/results/BAO-CAO.md`: tóm tắt bảng xếp hạng, con nào chết/sống, khoảng cách IS↔OOS
  (mức overfit), và nhận định trung thực (kỳ vọng: đa số EV≈0 sau phí — đó KHÔNG phải thất bại,
  đó là dữ liệu).
- Commit + push toàn bộ (code + ledger + báo cáo) lên nhánh `claude/qtq-task-continuation-r4qb04`
  để phiên cloud đọc được. Commit message tiếng Việt, rõ ràng.

## Quy tắc làm việc
- Theo vòng `/research → /plan → /execute → /review` (commands có sẵn trong `.claude/commands/`).
- Selftest harness TRƯỚC khi chạy thật: `python3 quant/backtest_vote.py --selftest` (EV phải ≈ 0).
- Báo cáo trung thực: fail nói fail, số xấu nói xấu. KHÔNG làm đẹp kết quả.
- Nguyên tắc vàng: **mọi đường cong đẹp mặc định là look-ahead/overfit cho tới khi chứng minh ngược lại.**
