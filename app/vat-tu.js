/* =====================================================================
   vat-tu.js — Danh mục thép hộp thương phẩm + tính khối lượng (module thuần)

   Nguồn: bảng quy cách thép hộp mạ kẽm Hòa Phát công bố công khai
   (cào & kiểm chứng 12/07/2026 — xem docs/nghien-cuu/chuan-nghe-tu-web.md).
   Công thức khối lượng chuẩn ngành, đã đối chiếu 5 quy cách với bảng
   nhà máy, sai lệch ≤ 0,5%:

     kg/m = [(2·a + 2·b)·t − 4·t²] × 0,00785   (a, b, t đơn vị mm)

   Dùng để: ghi khối lượng lên phiếu cắt → sau này báo giá vật tư.
   ===================================================================== */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.VATTU = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  // Quy cách thép hộp phổ biến cho cơ khí dân dụng (mm) + độ dày hay dùng
  var DANH_MUC = [
    { a: 12, b: 12, day: [0.8, 1.0, 1.2] },
    { a: 14, b: 14, day: [0.8, 1.0, 1.2] },
    { a: 16, b: 16, day: [0.8, 1.0, 1.2] },
    { a: 20, b: 20, day: [1.0, 1.2, 1.4] },
    { a: 25, b: 25, day: [1.0, 1.2, 1.4] },
    { a: 30, b: 30, day: [1.0, 1.2, 1.4] },
    { a: 40, b: 40, day: [1.2, 1.4, 1.8] },
    { a: 50, b: 50, day: [1.2, 1.4, 1.8, 2.0] },
    { a: 13, b: 26, day: [0.8, 1.0, 1.2] },
    { a: 20, b: 40, day: [1.0, 1.2, 1.4] },
    { a: 25, b: 50, day: [1.0, 1.2, 1.4] },
    { a: 30, b: 60, day: [1.2, 1.4, 1.8] },
    { a: 40, b: 80, day: [1.2, 1.4, 1.8, 2.0] },
    { a: 50, b: 100, day: [1.4, 1.5, 1.8, 2.0] }
  ];

  // Vật liệu thợ hay làm — khối lượng riêng kg/m³ (inox nặng hơn thép ~1%)
  var VAT_LIEU = {
    sat:     { ten: 'Sắt hộp (sơn tĩnh điện)', kgRieng: 7850 },
    inox304: { ten: 'Inox 304',                kgRieng: 7930 },
    inox201: { ten: 'Inox 201',                kgRieng: 7800 }
  };

  // kg trên 1 mét — a, b, t bằng mm; kgRieng theo vật liệu (mặc định sắt)
  function kgMoiMet(a, b, t, kgRieng) {
    if (!(a > 0) || !(b > 0) || !(t > 0)) throw new Error('Quy cách/độ dày phải > 0');
    if (t * 2 >= Math.min(a, b)) throw new Error('Độ dày ' + t + 'mm quá lớn so với hộp ' + a + 'x' + b);
    return ((2 * a + 2 * b) * t - 4 * t * t) * (kgRieng || 7850) / 1e6;
  }

  // Diện tích bề mặt cần sơn tĩnh điện (m²) của 1 chi tiết hộp — 4 mặt ngoài
  function m2ChiTiet(chiTiet) {
    var qc = docQuyCach(chiTiet.quy_cach || chiTiet.quyCach);
    if (!qc) return null;
    return 2 * (qc.a + qc.b) / 1000 * (chiTiet.dai / 1000) * (chiTiet.sl || 1);
  }

  // Đọc "hộp 40x80" / "50×100" / "hộp 14" (vuông) → {a, b} hoặc null
  function docQuyCach(chuoi) {
    if (!chuoi) return null;
    var m = String(chuoi).match(/(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)/i);
    if (m) return { a: parseFloat(m[1]), b: parseFloat(m[2]) };
    m = String(chuoi).match(/hộp\s*(\d+(?:\.\d+)?)/i);
    if (m) return { a: parseFloat(m[1]), b: parseFloat(m[1]) };
    return null;
  }

  // Khối lượng 1 chi tiết phiếu cắt: {quy_cach|quyCach, dai (mm), sl}, t = độ dày mm
  function kgChiTiet(chiTiet, t, kgRieng) {
    var qc = docQuyCach(chiTiet.quy_cach || chiTiet.quyCach);
    if (!qc) return null; // quy cách không phải hộp (tôn, kính...) → không tính
    return kgMoiMet(qc.a, qc.b, t, kgRieng) * (chiTiet.dai / 1000) * (chiTiet.sl || 1);
  }

  return { DANH_MUC: DANH_MUC, VAT_LIEU: VAT_LIEU, kgMoiMet: kgMoiMet,
           docQuyCach: docQuyCach, kgChiTiet: kgChiTiet, m2ChiTiet: m2ChiTiet };
});
