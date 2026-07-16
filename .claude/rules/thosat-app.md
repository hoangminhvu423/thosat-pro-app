# Rule — Dự án App Thợ Sắt (ThợSắt Pro PWA)

> Áp dụng khi làm việc trong repo `thosat-pro-app`. Đọc file này trước khi sửa code.
> _Applies when working in the `thosat-pro-app` repo. Read before editing._

## Sản phẩm / Product
**ThợSắt Pro** — PWA offline-first tính cắt sắt cho thợ sắt Việt Nam:
**chọn mẫu → nhập kích thước → ra phiếu cắt → xuất PNG gửi Zalo**. Chạy 100% client-side.

## Tech stack — ĐỌC KỸ / READ CAREFULLY
- **Vanilla JavaScript thuần. KHÔNG framework, KHÔNG build tool, KHÔNG bundler, KHÔNG `package.json`, KHÔNG `node_modules`.**
- Phụ thuộc ngoài duy nhất: Google Fonts (CDN). Deploy tĩnh trên **GitHub Pages**.
- State lưu `localStorage` (key `tsp_lichsu`, tối đa 30 phiếu). Sửa file → commit → push là xong, không compile.

## Kiến trúc & QUY TẮC BẤT DI BẤT DỊCH / Architecture — hard rules
- **MỌI logic tính toán nằm trong module engine kiểu UMD** (chạy được cả `<script>` lẫn `require()` trong Node):
  - `app/engine.js` → `window.ENGINE` — toán lõi: chia đều, lan can, mái tôn, sen hoa, cầu thang + lỗ ban.
  - `app/catalogue.js` → `window.CATALOGUE` — thông dịch mẫu + **bộ tính biểu thức tự viết (KHÔNG dùng `eval`)**.
  - `app/dexe.js` → `window.DEXE` — tối ưu cắt cây 1D (First Fit Decreasing, kerf 2mm, hao đầu cây 50mm).
  - `app/vat-tu.js` → `window.VATTU` — danh mục thép + công thức cân nặng/diện tích (đối chiếu bảng Hòa Phát).
  - `app/minh-hoa.js` → `window.MINHHOA` — vẽ minh họa SVG động theo kết quả.
  - `app/phieu-anh.js` → `window.PHIEUANH` — render phiếu ra PNG (canvas 2×) + Web Share API.
- **`app/index.html` CHỈ chứa view logic** (đọc input, gọi engine, render). **CẤM đặt công thức tính ở đây** — theo đúng comment gốc: _"KHÔNG đặt công thức ở đây — mọi logic tính nằm trong engine.js để test được."_
- `index.html` gốc repo chỉ là meta-refresh redirect sang `app/`. `.nojekyll` giữ GitHub Pages phục vụ file nguyên trạng.

## Quy ước dữ liệu / Data conventions
- Mọi độ dài nội bộ là **số nguyên mm**. Lan can/sen hoa nhập **mm**; mái tôn nhập **m + độ dốc %**. Góc tính bằng độ.
- **Toàn bộ định danh, UI, comment bằng tiếng Việt — GIỮ NGUYÊN** khi viết code mới.

## Hệ thống mẫu (catalogue)
- Mẫu là JSON ở `catalogue/mau/*.json`, tuân theo `catalogue/schema.json` (JSON Schema draft-07). Hiện có **21 mẫu**.
- Trường chính: `dau_vao` (input), `hang_so` (hằng số xưởng), `bien` (biến trung gian = chuỗi biểu thức), `chia_khoang` (chia đều → engine tự sinh `<ten>_n`, `<ten>_khe`), `chi_tiet` (danh sách cắt; `sl` và `dai` là **chuỗi biểu thức**), `ket_qua_phu`, `audit`.
- Trạng thái (`trang_thai`): `nhap` = nháp, **cấm cắt thật** / `da_audit` / `da_kiem_chung_cong_trinh`.
- Hằng số tạm gắn cờ `cho_chot: true` + comment `// TẠM - CHỜ CHỐT`. Đừng coi là số cuối cùng.

## ⚠️ Quy trình SỬA/THÊM MẪU — làm đủ 4 bước (dùng skill `them-mau`)
1. Sửa/thêm `catalogue/mau/<MÃ>.json` (theo `schema.json`).
2. Cập nhật thứ tự trong `catalogue/mau/danh-sach.json`.
3. **Rebuild `app/catalogue-all.json`** — bundle 1 dòng gộp tất cả mẫu (đường nạp ưu tiên).
4. **Thêm file mẫu vào `VO_APP` trong `app/sw.js`** (precache).
Bỏ sót bước 3–4 → thay đổi **không lên app**.

## ⚠️ Quy trình PHÁT HÀNH — thủ công, 3 bộ đếm KHÔNG đồng bộ (dùng skill `phat-hanh`)
1. Bump `TEN_CACHE = 'thosat-pro-vNN'` trong `app/sw.js` — **số phiên bản phát hành** (hiện `v26`).
2. Bump `?v=NN` các thẻ `<script>` trong `app/index.html` (hiện `v31` — khác số SW, đừng nhầm).
3. Rebuild `app/catalogue-all.json` nếu đổi mẫu; giữ `VO_APP` khớp danh sách file.
4. Commit: `Phát hành thosat-pro-vNN — DD/MM/YYYY HH:MM`. Push → GitHub Pages tự deploy.

## Bẫy thường gặp / Gotchas
- Repo **KHÔNG có** `tests/`, `docs/`, `package.json` dù comment có nhắc. Đừng giả định có test harness.
- Không CI. "Phát hành" = một commit. Nhánh phát triển: `claude/qtq-task-continuation-r4qb04`.

## Kiểm chứng / Verify (không có test tự động)
- Chạy tĩnh: `python3 -m http.server` ở gốc repo → mở `http://localhost:8000/app/`.
- Engine là UMD: `node -e "const E=require('./app/engine.js'); console.log(Object.keys(E))"` để thử hàm lõi.
