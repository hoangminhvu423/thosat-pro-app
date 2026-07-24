# GIẢI PHÁP TRIỆT ĐỂ — EA DevOps: rút vòng sửa→deploy→theo dõi→đánh giá từ "loằng ngoằng" xuống 1 lệnh

## Chẩn đoán gốc rễ (vì sao hôm nay chậm + nhiều bước)
| Ma sát quan sát hôm nay | Nguyên nhân gốc |
|---|---|
| Sếp phải đóng terminal ~5 lần | **CHỈ 1 MT5 trên VPS, dùng CHUNG live + test** → mọi G2/deploy đụng live → cần đóng tay |
| Không chạy được tester khi live mở | Cùng 1 data-folder, MT5 không cho 2 instance |
| Agent không tự đóng được | Cấm force-kill (đúng) + MT5 treo dialog "Are you sure exit?" |
| Lỗi âm thầm (min-lot 13 lệnh, shadow log hỏng, Fund EA chết 9 ngày) | **Không có monitor chủ động** — chỉ query log thủ công từng lần |
| Deploy = chuyển profile/gắn chart tay | Deploy ghép chặt với GUI |
→ **Nút thắt #1 = 1 MT5 dùng chung.** Gỡ nó là gỡ 80% ma sát.

## 3 TRỤ giải pháp

### Trụ 1 — Terminal TEST riêng (portable) trên VPS  [an toàn, KHÔNG đụng live]
Cài MT5 thứ 2 (portable, thư mục `C:\MT5_TEST`, login demo lấy data). Mọi compile + G2 + sweep chạy ở đây.
→ Agent G1/G2 bất cứ lúc nào, KHÔNG cần Sếp đóng gì, KHÔNG rủi ro live. Giết nút thắt #1.

### Trụ 2 — 1 LỆNH = cả vòng audit  (`/rbea-ship`)  [an toàn]
Một pipeline: sửa .mq5 → compile (test instance) → G2 headless 2 profile → diff-verify logic vs bản vàng
→ báo PASS/FAIL + bảng số (lệnh, PF, DD, tần suất, min-lot check) → nếu PASS: stage sẵn profile deploy.
Tất cả headless, không GUI. Vòng "sửa→đánh giá" từ ~30 phút + nhiều lượt xuống **1 lệnh ~2 phút**.

### Trụ 3 — Deploy nóng + monitor chủ động + rollback  [đụng live — CẦN SẾP DUYỆT CƠ CHẾ]
- **Deploy nóng**: controlled graceful restart — script VPS gửi WM_CLOSE + tự bấm "Yes" hộp thoại exit
  (KHÔNG force-kill, GV vẫn lưu) → watchdog mở lại profile mới → verify EA loaded + đúng mode. Bỏ Sếp khỏi vòng.
  ⚠️ RỦI RO: nếu restart hỏng giữa chừng (đóng nhưng không mở lại / mở sai profile) → live không có EA.
  Cần: maintenance-flag + verify 2 lớp + fallback. Đây là phần NHẠY CẢM — Sếp duyệt trước khi tôi build.
- **Monitor chủ động** (bắt lỗi âm thầm SỚM): heartbeat EA mỗi 5' + anomaly detector:
  EA rụng · không trade >X ngày khi lẽ ra phải · min-lot skip · DD tới 80% ngưỡng · lệch live-vs-backtest.
  → Telegram cảnh báo NGAY. (Thay deadman cũ đã gỡ, nhưng KEYED đúng EA hiện tại.)
- **Rollback 1 lệnh**: giữ .ex5 + profile last-known-good; `/rbea-rollback` về bản trước tức thì.

## Đề xuất triển khai (ưu tiên rủi ro thấp trước)
1. **Trụ 1 + 2 NGAY** — an toàn tuyệt đối (không đụng live), gỡ 80% ma sát. Tôi build được luôn.
2. **Trụ 3**: build monitor chủ động trước (chỉ đọc, an toàn); còn **deploy nóng auto-restart** cần Sếp
   duyệt cơ chế (đụng vòng đời terminal tiền thật) — hoặc giữ đóng-tay làm cổng an toàn cuối.

## Quyết định cần Sếp
(a) Build Trụ 1+2 ngay? (khuyến nghị YES — an toàn, tác động lớn)
(b) Trụ 3 deploy-nóng auto-restart: build (tôi lo restart an toàn 2 lớp) HAY giữ 1 click tay Sếp làm gate?
