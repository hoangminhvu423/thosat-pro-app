# G2 KIT — Strategy Tester visual cho Sếp (~15 phút, 2 profile)
Cập nhật chiều 24/07: dùng **v0.32** (vá halt-file). BTC AUTO đã ĐẠT qua headless — chỉ còn RUN XAU SEMI.

## Đã chuẩn bị sẵn trên VPS (không phải làm gì thêm)
- EA đã compile: `Experts\QTQ_MultiTF_DEMO\RB_EA_v0.32.ex5` (terminal Exness).
- 2 set-file đã nằm trong `MQL5\Presets\` của terminal Exness:
  `RB_EA_v031_XAU_SEMI_G2.set` · `RB_EA_v031_BTC_AUTO_G2.set` (I_InitBalance=4600, risk 0.15, magic đúng bảng).
- Tester chạy NGAY TRÊN terminal Exness live vẫn an toàn (tester là sandbox, không đụng chart/lệnh live).

## RUN 1 — BTC AUTO (soi kỹ nhất — sleeve tự động 100%)
1. RDP vào VPS → terminal Exness → View → Strategy Tester (Ctrl+R).
2. Settings: Expert = `QTQ_MultiTF_DEMO\RB_EA_v0.32` · Symbol = **BTCUSD** · Timeframe **H4**
   · Dates: **2026.04.24 → 2026.07.24** · Deposit **4600 USD** · Model "Every tick based on real ticks"
   · Visual mode ✅.
3. Inputs → Load → `RB_EA_v031_BTC_AUTO_G2.set` → Start.

## RUN 2 — XAU SEMI
Như trên nhưng Symbol = **XAUUSD**, Load `RB_EA_v031_XAU_SEMI_G2.set`.
Lưu ý SEMI cần NGƯỜI vẽ zone: khi visual chạy, vẽ 2 đường ngang tên `RB_HI` / `RB_LO` quanh một vùng
sideway thấy rõ. Chưa vẽ → EA đứng im = ĐÚNG thiết kế (soi luôn điều này: không được tự trade khi chưa có zone).

## CHECKLIST MẮT NGƯỜI (gate G2 = "không lệnh phi logic")
- [ ] SL/TP đúng hình học: break-trade SL ~1×ATR, TP ~2×ATR tính từ giá fill (1R/2R).
- [ ] KHÔNG lệnh size bất thường (risk/lệnh ~0.15% của 4600 ≈ 7 USD rủi ro).
- [ ] BTC AUTO: có lệnh đều (chuẩn đo ~10-13 lệnh/tháng ±40% — điều kiện audit flag b); KHÔNG 0 lệnh (Đ1 đã vá).
- [ ] BTC AUTO: vẫn hoạt động sau các ngày thứ Sáu (Đ2 đã vá — không tự disarm weekend).
- [ ] Nếu gặp chuỗi thua trong kỳ test: breaker daily/weekly cắt đúng, weekly KHÔNG "tự lành" giữa tuần (Đ3).
- [ ] Không spam lệnh liên tiếp <60 phút (I_MinGapMin), không lệnh ngược logic zone.
- [ ] XAU SEMI: chỉ trade sau khi có zone người vẽ; range-trade bám mép zone, không trade giữa box.

## SAU KHI XONG
- Đạt cả 2 run → nhắn "G2 đạt" vào cửa sổ deploy: tôi cập nhật STATE/DECISION_LOG và soạn
  checklist cắm live (bước attach chart + AutoTrading do Sếp bấm, có checklist verify Telegram).
- Có lệnh phi logic → chụp màn hình + nhắn lại: tôi ghi hồ sơ đưa về vòng R&D, KHÔNG deploy.
