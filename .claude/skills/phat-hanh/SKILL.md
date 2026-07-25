---
name: phat-hanh
description: Phát hành một phiên bản mới của app ThợSắt Pro. Dùng khi đã sửa xong code/mẫu và muốn đẩy bản mới lên GitHub Pages — quy trình thủ công với 3 bộ đếm KHÔNG đồng bộ nhau.
---

# Skill — Phát hành ThợSắt Pro

> "Phát hành" = **một commit**. Không có CI, không build tool. **3 bộ đếm phiên bản KHÔNG đồng bộ** — đừng nhầm.

## Khi nào dùng
Sau khi đã sửa code/mẫu và kiểm chứng, muốn đẩy bản mới ra người dùng.

## Các bước

### 1. Bump phiên bản Service Worker (số phát hành chính)
`app/sw.js`: `const TEN_CACHE = 'thosat-pro-vNN';` → tăng `NN` (hiện `v26`).
Đổi `TEN_CACHE` khiến SW xóa cache cũ khi `activate` (stale-while-revalidate).

### 2. Bump cache-buster script
`app/index.html`: tăng chuỗi `?v=NN` ở **tất cả** thẻ `<script src="...js?v=NN">` (hiện `v31` — **khác** số SW).

### 3. Rebuild bundle nếu có đổi mẫu
Nếu đã sửa mẫu (xem skill `them-mau`): rebuild `app/catalogue-all.json` và giữ `VO_APP` trong `sw.js` khớp danh sách file thực tế.

### 4. Kiểm chứng thật trước khi commit
`python3 -m http.server` ở gốc → mở `http://localhost:8000/app/` → thử luồng bị ảnh hưởng (chọn mẫu, nhập số, ra phiếu). Fail thì sửa, đừng phát hành.

### 5. Commit + push
Message đúng phong cách repo:
```
Phát hành thosat-pro-vNN — DD/MM/YYYY HH:MM
```
Push lên nhánh phát triển (hiện `claude/qtq-task-continuation-r4qb04`): `git push -u origin <branch>` (retry backoff nếu lỗi mạng). GitHub Pages tự deploy sau khi push vào nhánh phục vụ trang.

## Nhắc
- 3 bộ đếm: SW `TEN_CACHE` (v26) ≠ `?v=` script (v31) ≠ `phien_ban` từng mẫu. Cập nhật đúng cái cần.
- **Không tạo Pull Request** trừ khi người dùng yêu cầu tường minh.
