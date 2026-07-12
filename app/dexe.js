/* =====================================================================
   dexe.js — Tối ưu đề-xê 1D cho ThợSắt Pro (module thuần, KHÔNG dính UI)

   Bài toán: có danh sách đoạn cần cắt (mm) → xếp vào cây thương phẩm
   (mặc định 6000mm) và tận dụng đầu thừa tồn kho, sao cho ít cây nhất.

   Thuật toán: First Fit Decreasing (FFD)
   - Xếp đoạn dài trước, đoạn ngắn lấp khe sau.
   - Ưu tiên nhét vào đầu thừa tồn kho (ngắn trước) rồi mới bổ cây mới.
   - Mỗi nhát cắt ăn thêm kerf (bề rộng lưỡi). Nhát cuối sát đầu cây
     không cần kerf → đoạn vừa khít phần còn lại vẫn xếp được.

   Quy ước:
   - Cây mới trừ hao đầu cây (đầu thương phẩm bavia/không vuông).
     kerf mặc định 2mm, hao đầu cây mặc định 50mm // TẠM - CHỜ CHỐT
   - Đầu thừa tồn kho coi như đầu đã cắt vuông → dùng trọn chiều dài.
   - Đoạn dài hơn (cây - hao) nhưng ≤ cây: dùng NGUYÊN CÂY không cắt đầu
     (thực tế cây 6m hay dôi vài mm) — có ghi chú riêng. // TẠM - CHỜ CHỐT
   - Mọi chiều dài là mm nguyên.

   Dùng 2 nơi: trình duyệt (window.DEXE) và Node (require).
   ===================================================================== */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.DEXE = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var MAC_DINH = { cayMoi: 6000, haoDauCay: 50, kerf: 2 }; // TẠM - CHỜ CHỐT

  // chiTiet: [{dai, sl, ten?}] — đoạn cần cắt (mm nguyên)
  // tonKho:  [{dai, sl}]       — đầu thừa có sẵn (mm nguyên)
  function toiUuCat(opts) {
    var tonKho = opts.tonKho || [];
    // Tồn kho chỉ đáng dùng khi giảm được cây mới phải bổ.
    // Nếu số cây mới y hệt thì thôi — giữ đầu thừa trong kho, đỡ băm vụn thêm.
    if (tonKho.length > 0) {
      var coTon = xepFFD(opts, tonKho);
      var khongTon = xepFFD(opts, []);
      return (coTon.tongCayMoi < khongTon.tongCayMoi) ? coTon : khongTon;
    }
    return xepFFD(opts, []);
  }

  function xepFFD(opts, tonKho) {
    var chiTiet = opts.chiTiet || [];
    var cayMoi = opts.cayMoi != null ? opts.cayMoi : MAC_DINH.cayMoi;
    var haoDauCay = opts.haoDauCay != null ? opts.haoDauCay : MAC_DINH.haoDauCay;
    var kerf = opts.kerf != null ? opts.kerf : MAC_DINH.kerf;

    if (!(cayMoi > 0)) throw new Error('Chiều dài cây mới phải > 0');
    if (haoDauCay < 0 || kerf < 0) throw new Error('Kerf và hao đầu cây không được âm');
    var huuDungMoi = cayMoi - haoDauCay;
    if (huuDungMoi <= 0) throw new Error('Hao đầu cây lớn hơn cả cây');

    // Bung danh sách đoạn, kiểm tra đầu vào
    var doan = [];
    chiTiet.forEach(function (d) {
      var dai = Math.round(d.dai), sl = Math.round(d.sl != null ? d.sl : 1);
      if (!(dai > 0)) throw new Error('Chiều dài đoạn phải > 0 (nhận ' + d.dai + ')');
      if (!(sl > 0)) return; // sl 0 → bỏ qua
      if (dai > cayMoi)
        throw new Error('Đoạn ' + dai + 'mm dài hơn cây ' + cayMoi + 'mm — không cắt được');
      for (var i = 0; i < sl; i++) doan.push({ dai: dai, ten: d.ten || '' });
    });
    if (doan.length === 0) throw new Error('Chưa có đoạn nào cần cắt');

    // FFD: dài trước
    doan.sort(function (a, b) { return b.dai - a.dai; });

    // Thùng = đầu thừa tồn kho (ngắn dùng trước) + cây mới mở dần
    var thung = [];
    tonKho.forEach(function (t) {
      var dai = Math.round(t.dai), sl = Math.round(t.sl != null ? t.sl : 1);
      if (!(dai > 0) || !(sl > 0)) return;
      for (var i = 0; i < sl; i++)
        thung.push({ nguon: 'ton_kho', daiCay: dai, conLai: dai, cat: [] });
    });
    thung.sort(function (a, b) { return a.daiCay - b.daiCay; });

    var tongThanhCat = 0, tongMmCat = 0;

    doan.forEach(function (d) {
      tongThanhCat++; tongMmCat += d.dai;

      // Đoạn dài hơn phần hữu dụng cây mới → dùng nguyên cây (không cắt đầu)
      if (d.dai > huuDungMoi) {
        thung.push({ nguon: 'cay_moi', daiCay: cayMoi, conLai: 0,
                     cat: [d], nguyenCay: true });
        return;
      }
      // First fit: thùng nào còn chỗ thì nhét
      for (var i = 0; i < thung.length; i++) {
        var t = thung[i];
        if (!t.nguyenCay && t.conLai >= d.dai) {
          t.cat.push(d);
          t.conLai = Math.max(0, t.conLai - d.dai - kerf);
          return;
        }
      }
      // Không thùng nào chứa nổi → bổ cây mới
      thung.push({ nguon: 'cay_moi', daiCay: cayMoi, conLai: huuDungMoi - d.dai - kerf,
                   cat: [d] });
      var moi = thung[thung.length - 1];
      if (moi.conLai < 0) moi.conLai = 0;
    });

    // Chỉ giữ thùng có cắt (tồn kho không dùng thì thôi)
    var daDung = thung.filter(function (t) { return t.cat.length > 0; });

    // Gộp các cây cắt giống hệt nhau cho phiếu gọn
    var nhom = {};
    var soDo = [];
    daDung.forEach(function (t) {
      var khoa = t.nguon + '|' + t.daiCay + '|' + (t.nguyenCay ? 'ng' : '') + '|' +
        t.cat.map(function (c) { return c.dai + (c.ten ? ':' + c.ten : ''); }).join(',');
      if (nhom[khoa]) { nhom[khoa].soCay++; return; }
      var dong = {
        nguon: t.nguon, daiCay: t.daiCay, soCay: 1,
        cat: t.cat.map(function (c) { return { dai: c.dai, ten: c.ten }; }),
        conLai: Math.round(t.conLai),
        nguyenCay: !!t.nguyenCay
      };
      nhom[khoa] = dong;
      soDo.push(dong);
    });
    // Cây mới trước (nhiều đoạn trước), tồn kho sau — thợ đọc từ trên xuống
    soDo.sort(function (a, b) {
      if (a.nguon !== b.nguon) return a.nguon === 'cay_moi' ? -1 : 1;
      return b.daiCay - a.daiCay || b.cat.length - a.cat.length;
    });

    var tongCayMoi = 0, soTonKhoDung = 0, tongMmDung = 0, tongDeXe = 0;
    soDo.forEach(function (d) {
      if (d.nguon === 'cay_moi') { tongCayMoi += d.soCay; tongMmDung += d.daiCay * d.soCay; }
      else { soTonKhoDung += d.soCay; tongMmDung += d.daiCay * d.soCay; }
      tongDeXe += d.conLai * d.soCay;
    });

    return {
      soDo: soDo,
      tongCayMoi: tongCayMoi,
      soTonKhoDung: soTonKhoDung,
      tongThanhCat: tongThanhCat,
      tongMetCat: tongMmCat / 1000,
      tongDeXe: tongDeXe,                    // mm đầu thừa mới sinh ra
      hieuSuat: tongMmDung > 0 ? tongMmCat / tongMmDung : 0, // phần sắt thành chi tiết
      thongSo: { cayMoi: cayMoi, haoDauCay: haoDauCay, kerf: kerf }
    };
  }

  return { toiUuCat: toiUuCat, MAC_DINH: MAC_DINH };
});
