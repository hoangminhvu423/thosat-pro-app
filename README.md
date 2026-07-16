# ThợSắt Pro

**PWA offline-first tính toán cắt sắt cho thợ sắt Việt Nam.**
Luồng dùng: **chọn mẫu → nhập kích thước → ra phiếu cắt sắt → xuất PNG gửi Zalo**.
Chạy 100% trên điện thoại tại công trình, **không cần mạng**.

Repo này gồm 2 phần:
1. **Sản phẩm** — app ThợSắt Pro (thư mục `app/` + `catalogue/`).
2. **Bộ khung Agentic Engineering cho Claude Code** — workflow + skill dùng lại cho mọi dự án (`CLAUDE.md`, `.claude/`, `docs/claude-setup/`).

---

## 1. Sản phẩm — ThợSắt Pro

### Tính năng
Tính chia khoảng đều, tối ưu cắt cây (đề-xê), cảnh báo khe an toàn (QCVN/TCVN), đếm bậc theo lỗ ban.
Các nhóm công cụ: Tính nhanh, **Mẫu** (catalogue), **Đề-xê** (tối ưu cắt cây), **Lan can**, **Mái tôn**, **Sen hoa**, **Sổ** (lịch sử phiếu, lưu `localStorage`).

### Tech stack
- **Vanilla JavaScript thuần** — KHÔNG framework, KHÔNG build tool, KHÔNG bundler, KHÔNG `package.json`/`node_modules`.
- Phụ thuộc ngoài duy nhất: Google Fonts (CDN). Deploy tĩnh trên **GitHub Pages**.
- Sửa file → commit → push là xong, không có bước compile.

### Chạy thử local
```bash
python3 -m http.server        # ở gốc repo
# mở http://localhost:8000/app/
```
Engine viết kiểu UMD nên thử được hàm lõi bằng Node mà không cần trình duyệt:
```bash
node -e "const E=require('./app/engine.js'); console.log(Object.keys(E))"
```

### Cấu trúc
```
index.html                 # redirect sang app/ (.nojekyll giữ file nguyên trạng)
app/
  index.html               # CHỈ view logic — đọc input, gọi engine, render
  engine.js    → ENGINE    # toán lõi (chia đều, lan can, mái tôn, sen hoa, cầu thang)
  catalogue.js → CATALOGUE # thông dịch mẫu + tính biểu thức (KHÔNG dùng eval)
  dexe.js      → DEXE      # tối ưu cắt cây 1D (First Fit Decreasing)
  vat-tu.js    → VATTU     # danh mục thép + công thức cân nặng/diện tích
  minh-hoa.js  → MINHHOA   # vẽ minh họa SVG động
  phieu-anh.js → PHIEUANH  # render phiếu ra PNG + Web Share API
  sw.js                    # service worker (offline, stale-while-revalidate)
  catalogue-all.json       # bundle 1 dòng gộp tất cả mẫu (đường nạp ưu tiên)
catalogue/
  schema.json              # JSON Schema (draft-07) cho mẫu
  mau/*.json               # 21 mẫu; danh-sach.json giữ thứ tự
```

### Quy ước quan trọng
- Mọi độ dài nội bộ là **số nguyên mm**; lan can/sen hoa nhập mm; mái tôn nhập m + độ dốc %.
- **Mọi logic tính nằm trong engine** — cấm đặt công thức trong `app/index.html`.
- Toàn bộ định danh/UI/comment **tiếng Việt** — giữ nguyên khi viết code mới.

### Thêm mẫu / Phát hành
Xem skill trong `.claude/skills/`: `them-mau` (thêm mẫu — 4 bước) và `phat-hanh` (phát hành — 3 bộ đếm phiên bản).
Chi tiết đầy đủ ở `.claude/rules/thosat-app.md`.

---

## 2. Bộ khung Agentic Engineering (Claude Code)

> "STOP VIBE CODING" — từ vibe coding sang **agentic engineering**. Cảm hứng từ
> [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice).

Vòng lặp cốt lõi: **Research → Plan → Execute → Review → Ship**. Mô hình: **Command → Agent → Skill**.

- **CLAUDE.md** — hub điều phối, Claude đọc đầu mỗi phiên; tự nhận diện dự án (thợ sắt / quant).
- **`.claude/commands/`** — `/research` `/plan` `/execute` `/review` `/ship`.
- **`.claude/agents/`** — `researcher`, `planner`, `reviewer`.
- **`.claude/skills/`** — `them-mau`, `phat-hanh` (dự án thợ sắt).
- **`.claude/rules/`** — `core-workflow`, `thosat-app`, `quant-trading`.

Cách dùng lại cho dự án khác (kể cả cài `~/.claude`): xem **`docs/claude-setup/README.md`**.
