---
name: catalogue-audit
description: Audit đối kháng công thức mẫu catalogue ThợSắt Pro trước khi phát hành. Dùng BẮT BUỘC mỗi khi thêm/sửa mẫu. Checklist các lỗi "âm thầm" làm phiếu cắt lệch thực tế — tương tự lỗi làm live khác backtest bên EA.
---

# Catalogue Audit — Checklist chống lỗi công thức

Nguyên tắc: đọc công thức với tư duy "nó SAI ở đâu", không phải "nó đúng chưa".
Mỗi mục dưới đây từng là (hoặc chắc chắn sẽ là) một cây sắt cắt hỏng ngoài đời.

## A. Lỗi kích thước gốc
- [ ] Nhầm LỌT LÒNG với PHỦ BÌ: kích thước nhập là ô chờ (lọt lòng tường) hay
      phủ bì khung? Mọi công thức phải ghi rõ gốc quy chiếu.
- [ ] Quên trừ 2 lần bề dày khung khi tính không gian trong (trừ 1 lần là lỗi kinh điển).
- [ ] Trừ khe MỘT phía trong khi khe có ở HAI phía (cánh–khung trái và phải).
- [ ] Đơn vị lẫn lộn m/mm trong cùng công thức. Test với số lẻ (vd 1237mm) để lộ lỗi.

## B. Lỗi chia khoảng
- [ ] Chia đều nhưng khoang cuối lệch: kiểm tra tổng = n*w + (n+1)*khe khớp usable ±1mm.
- [ ] Khe tối đa bị VƯỢT do làm tròn số nan xuống thay vì lên (an toàn trẻ em: khe
      lan can không được vượt chuẩn — luôn ceil số nan).
- [ ] Nhiều khoang: đố chia theo từng khoang lọt lòng hay chia suốt cả chiều dài?
      Hai cách ra kết quả khác nhau — phải khớp thói quen thợ.
- [ ] Trường hợp biên: ô quá nhỏ (usable < khe tối đa) phải trả 0 nan, không âm.

## C. Lỗi cắt xiên / vát
- [ ] Cắt vát: chiều dài ghi trên phiếu là cạnh DÀI hay cạnh NGẮN của thanh vát?
      Phải ghi rõ trên phiếu, mặc định ghi cạnh dài.
- [ ] Vát 2 đầu CÙNG chiều (hình bình hành — đố cầu thang) khác vát NGƯỢC chiều
      (hình thang). Ghi sai là thợ cắt hỏng cả loạt.
- [ ] Góc vát tính từ phương nào (so với trục thanh hay so với mặt cắt vuông)?
      Thống nhất: góc lệch so với nhát cắt vuông, khớp thang chia máy cắt phổ thông.
- [ ] Bề dày tay vịn nghiêng chiếm chiều đứng = dày/cos(α), không phải dày.

## D. Lỗi tối ưu đề-xê
- [ ] Quên kerf: N nhát cắt ăn N*kerf mm. Quên là cây cuối hụt.
- [ ] Quên hao đầu cây (đầu cây thương phẩm thường không vuông, phải xén).
- [ ] Cây "6m" thực tế có thể 6000–6020mm: dùng 6000 làm chuẩn an toàn, không dùng số dôi.
- [ ] Đoạn dư < ngưỡng giữ lại (mặc định 300mm) phải tính là phế, không ghi là "tận dụng".

## E. Lỗi quy trình
- [ ] Mẫu mới chưa có đủ 3 bộ test (chuẩn / lẻ / biên nhỏ) → không được phát hành.
- [ ] Còn hằng số `TẠM - CHỜ CHỐT` → mẫu chỉ được gắn nhãn "nháp", cấm gắn "đã kiểm chứng".
- [ ] Nhãn "đã kiểm chứng công trình thật" chỉ chủ dự án được gắn, agent không tự gắn.
- [ ] Sửa công thức mẫu cũ → chạy lại TOÀN BỘ test của mọi mẫu (sửa hàm chung dễ vỡ dây chuyền).

## Cách dùng
1. Chạy checklist trên từng mẫu mới/sửa, ghi kết quả vào cuối file JSON của mẫu
   (trường "audit": {ngay, nguoi, ket_qua}).
2. Bất kỳ mục nào FAIL → sửa xong chạy lại từ đầu checklist, không tick tiếp.
