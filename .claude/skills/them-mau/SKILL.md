---
name: them-mau
description: Thêm hoặc sửa một mẫu catalogue trong app ThợSắt Pro. Dùng khi cần tạo/chỉnh file mẫu JSON — đảm bảo đủ 4 bước để thay đổi thực sự lên app (dễ quên bước rebuild bundle và precache).
---

# Skill — Thêm/Sửa mẫu catalogue (ThợSắt Pro)

> Quy trình lặp lại, **rất dễ quên bước 3–4**. Bỏ sót → thay đổi KHÔNG lên app
> (app đọc bundle `catalogue-all.json`, không đọc file lẻ trừ khi fallback).

## Khi nào dùng
Khi thêm mẫu mới hoặc sửa một mẫu trong `catalogue/mau/*.json`.

## 4 bước bắt buộc

### 1. Sửa/thêm file mẫu
`catalogue/mau/<MÃ>.json` theo `catalogue/schema.json` (draft-07). Trường chính:
- `ma`, `ten`, `nhom` (`lan_can`/`mai_ton`/`sen_hoa`/`cua_sat`/`khung_san`/`mai_kinh`/`cau_thang`), `phien_ban`, `trang_thai`.
- `dau_vao` (input), `hang_so` (hằng số, tạm gắn `cho_chot:true`), `bien` (biểu thức chuỗi),
  `chia_khoang` (chia đều → engine tự sinh `<ten>_n`, `<ten>_khe`), `chi_tiet` (`sl`, `dai` là **chuỗi biểu thức**), `ket_qua_phu`, `audit`.
- Mẫu chưa kiểm chứng để `trang_thai:"nhap"` (**cấm cắt thật**).

### 2. Cập nhật thứ tự
Thêm/sắp lại mã trong `catalogue/mau/danh-sach.json`.

### 3. Rebuild bundle `app/catalogue-all.json`
Bundle 1 dòng dạng `{"thu_tu":[...],"mau":{<MÃ>:<json>}}`, thứ tự theo `danh-sach.json`. Rebuild bằng Node:

```bash
node -e '
const fs=require("fs");
const ds=JSON.parse(fs.readFileSync("catalogue/mau/danh-sach.json","utf8"));
const mau={};
for(const ma of ds) mau[ma]=JSON.parse(fs.readFileSync("catalogue/mau/"+ma+".json","utf8"));
fs.writeFileSync("app/catalogue-all.json", JSON.stringify({thu_tu:ds, mau}));
console.log("Đã rebuild:", ds.length, "mẫu");
'
```

### 4. Thêm file vào precache `VO_APP` trong `app/sw.js`
Thêm dòng `'../catalogue/mau/<MÃ>.json'` vào mảng `VO_APP`. Giữ danh sách khớp file thực tế.

## Kiểm chứng
- `node -e "const j=require('./app/catalogue-all.json'); console.log(j.thu_tu.length, Object.keys(j.mau).length)"` — hai số phải bằng nhau và bằng số mẫu.
- `python3 -m http.server` → mở `/app/`, chọn mẫu mới, nhập số, xem phiếu ra đúng.
- Sau khi ổn → chạy skill `phat-hanh` để bump phiên bản.
