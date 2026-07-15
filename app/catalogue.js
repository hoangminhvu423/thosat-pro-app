/* =====================================================================
   catalogue.js — Bộ nạp mẫu catalogue ThợSắt Pro (module thuần)

   Nhiệm vụ: đọc bản ghi JSON theo catalogue/schema.json → trả về máy tính
   cho mẫu đó: nhập giá trị dau_vao → ra danh sách chi tiết cắt (mm nguyên).

   Biểu thức trong "sl"/"dai"/"bien"/"chia_khoang" được TỰ PHÂN TÍCH
   (không dùng eval) — chỉ cho phép: số, tên biến, + - * / ^ ( ) ,
   và hàm: ceil floor round sqrt abs min max sin cos tan (radian).

   Biến trong biểu thức được phân giải theo thứ tự:
   1. giá trị người dùng nhập (dau_vao)
   2. hằng số nghề (hang_so.*.gia_tri)
   3. biến trung gian (bien[].cong_thuc) — tính đệ quy, có chặn vòng lặp
   4. kết quả chia khoảng: <ten>_n (số thanh) và <ten>_khe (khe, mm thô)

   Dùng 2 nơi: trình duyệt (window.CATALOGUE, nạp SAU engine.js)
   và Node (require) — test ở tests/catalogue.test.js.
   ===================================================================== */
(function (root, factory) {
  if (typeof module === 'object' && module.exports)
    module.exports = factory(require('./engine.js'));
  else root.CATALOGUE = factory(root.ENGINE);
})(typeof self !== 'undefined' ? self : this, function (ENGINE) {
  'use strict';

  /* ---------- Trình tính biểu thức ---------- */

  var HAM = {
    ceil: Math.ceil, floor: Math.floor, round: Math.round,
    sqrt: Math.sqrt, abs: Math.abs, min: Math.min, max: Math.max,
    sin: Math.sin, cos: Math.cos, tan: Math.tan, atan: Math.atan,
    // chọn số bậc cầu thang rơi cung Sinh (thước lỗ ban) — ủy quyền cho engine
    bac_lo_ban: function (H, caoBacMuon) { return ENGINE.chonSoBacLoBan(H, caoBacMuon); }
  };

  function tachToken(chuoi) {
    var ds = [], i = 0;
    while (i < chuoi.length) {
      var c = chuoi[i];
      if (c === ' ' || c === '\t') { i++; continue; }
      if (/[0-9.]/.test(c)) {
        var so = '';
        while (i < chuoi.length && /[0-9.]/.test(chuoi[i])) so += chuoi[i++];
        ds.push({ loai: 'so', gt: parseFloat(so) });
        continue;
      }
      if (/[A-Za-z_]/.test(c)) {
        var ten = '';
        while (i < chuoi.length && /[A-Za-z0-9_]/.test(chuoi[i])) ten += chuoi[i++];
        ds.push({ loai: 'ten', gt: ten });
        continue;
      }
      if ('+-*/^(),'.indexOf(c) >= 0) { ds.push({ loai: c }); i++; continue; }
      throw new Error('Ký tự lạ "' + c + '" trong biểu thức: ' + chuoi);
    }
    return ds;
  }

  // Văn phạm: bieuThuc = hang (+|- hang)* ; hang = luyThua (*|/ luyThua)* ;
  // luyThua = donVi (^ luyThua)? ; donVi = so | ten | ten(ds) | (bieuThuc) | -donVi
  function tinhBieuThuc(chuoi, layBien) {
    var tk = tachToken(chuoi), vt = 0;
    function nhin() { return tk[vt]; }
    function an(loai) {
      if (!tk[vt] || tk[vt].loai !== loai)
        throw new Error('Biểu thức hỏng tại vị trí ' + vt + ': ' + chuoi);
      return tk[vt++];
    }
    function bieuThuc() {
      var v = hang();
      while (nhin() && (nhin().loai === '+' || nhin().loai === '-')) {
        var op = tk[vt++].loai;
        v = (op === '+') ? v + hang() : v - hang();
      }
      return v;
    }
    function hang() {
      var v = luyThua();
      while (nhin() && (nhin().loai === '*' || nhin().loai === '/')) {
        var op = tk[vt++].loai;
        var p = luyThua();
        if (op === '/' && p === 0) throw new Error('Chia cho 0 trong: ' + chuoi);
        v = (op === '*') ? v * p : v / p;
      }
      return v;
    }
    function luyThua() {
      var v = donVi();
      if (nhin() && nhin().loai === '^') { vt++; v = Math.pow(v, luyThua()); }
      return v;
    }
    function donVi() {
      var t = nhin();
      if (!t) throw new Error('Biểu thức thiếu vế: ' + chuoi);
      if (t.loai === '-') { vt++; return -donVi(); }
      if (t.loai === 'so') { vt++; return t.gt; }
      if (t.loai === '(') { vt++; var v = bieuThuc(); an(')'); return v; }
      if (t.loai === 'ten') {
        vt++;
        if (nhin() && nhin().loai === '(') { // gọi hàm
          if (!HAM[t.gt]) throw new Error('Không có hàm "' + t.gt + '" (chỉ có: ' + Object.keys(HAM).join(' ') + ')');
          vt++;
          var doiSo = [bieuThuc()];
          while (nhin() && nhin().loai === ',') { vt++; doiSo.push(bieuThuc()); }
          an(')');
          return HAM[t.gt].apply(null, doiSo);
        }
        return layBien(t.gt);
      }
      throw new Error('Biểu thức hỏng: ' + chuoi);
    }
    var kq = bieuThuc();
    if (vt !== tk.length) throw new Error('Biểu thức thừa đuôi: ' + chuoi);
    if (typeof kq !== 'number' || !isFinite(kq))
      throw new Error('Biểu thức không ra số: ' + chuoi);
    return kq;
  }

  /* ---------- Bộ nạp mẫu ---------- */

  function napMau(mau) {
    ['ma', 'ten', 'dau_vao', 'hang_so', 'chi_tiet'].forEach(function (tr) {
      if (mau[tr] == null) throw new Error('Mẫu thiếu trường "' + tr + '"');
    });
    var hangSoChoChot = Object.keys(mau.hang_so)
      .filter(function (k) { return mau.hang_so[k].cho_chot; });

    // giaTriNhap: {tenDauVao: số} — đơn vị đúng như khai báo trong dau_vao
    function tinh(giaTriNhap) {
      mau.dau_vao.forEach(function (dv) {
        var gt = giaTriNhap[dv.ten];
        if (gt == null || isNaN(gt)) {
          if (dv.mac_dinh != null) { giaTriNhap[dv.ten] = dv.mac_dinh; return; }
          throw new Error('Thiếu đầu vào "' + (dv.nhan || dv.ten) + '"');
        }
        if (!(gt > 0)) throw new Error('"' + (dv.nhan || dv.ten) + '" phải > 0');
      });

      // Hằng số thợ sửa tay (ghi đè qua giaTriNhap) cũng phải > 0 — chặn NaN
      Object.keys(giaTriNhap).forEach(function (k) {
        if (mau.hang_so[k] && !(giaTriNhap[k] > 0))
          throw new Error('Hằng số "' + k + '" sửa tay phải > 0');
      });

      var dnBien = {};
      (mau.bien || []).forEach(function (b) { dnBien[b.ten] = b.cong_thuc; });
      var dnChia = {};
      (mau.chia_khoang || []).forEach(function (c) { dnChia[c.ten] = c; });

      var cache = {}, dangTinh = {};
      function layBien(ten) {
        if (ten in cache) return cache[ten];
        if (dangTinh[ten]) throw new Error('Vòng lặp công thức tại biến "' + ten + '"');
        dangTinh[ten] = true;
        var gt;
        if (giaTriNhap[ten] != null) gt = giaTriNhap[ten];
        else if (mau.hang_so[ten]) gt = mau.hang_so[ten].gia_tri;
        else if (dnBien[ten] != null) gt = tinhBieuThuc(dnBien[ten], layBien);
        else {
          var m = ten.match(/^(.+)_(n|khe)$/);
          if (m && dnChia[m[1]]) {
            var ck = dnChia[m[1]];
            var usable = tinhBieuThuc(ck.usable, layBien);
            var rongThanh = tinhBieuThuc(ck.be_rong_thanh, layBien);
            var kheToiDa = tinhBieuThuc(ck.khe_toi_da, layBien);
            // Chặn khe ÂM lên phiếu: khoang chia phải dương, thanh/khe phải dương
            if (!(rongThanh > 0) || !(kheToiDa > 0))
              throw new Error('Mẫu ' + mau.ma + ': bề thanh/khe tối đa của "' + m[1] + '" phải > 0');
            if (!(usable > 0))
              throw new Error('Khoang chia "' + m[1] + '" ra ' + Math.round(usable) +
                'mm — kích thước nhập quá nhỏ so với mẫu');
            var cd = ENGINE.chiaDeu(usable, rongThanh, kheToiDa);
            cache[m[1] + '_n'] = cd.n;
            cache[m[1] + '_khe'] = cd.khe;
            gt = cache[ten];
          }
          else throw new Error('Mẫu ' + mau.ma + ': không biết biến "' + ten + '"');
        }
        delete dangTinh[ten];
        cache[ten] = gt;
        return gt;
      }

      var chiTiet = mau.chi_tiet.map(function (ct) {
        var sl = Math.round(tinhBieuThuc(ct.sl, layBien));
        var dai = Math.round(tinhBieuThuc(ct.dai, layBien));
        if (sl < 0) throw new Error('Chi tiết "' + ct.ten + '": số lượng âm (' + sl + ') — kiểm tra kích thước nhập');
        if (dai <= 0 && sl > 0) throw new Error('Chi tiết "' + ct.ten + '": chiều dài ≤ 0 — kích thước nhập quá nhỏ so với mẫu');
        return { ten: ct.ten, quy_cach: ct.quy_cach, sl: sl, dai: dai,
                 cat_vat: ct.cat_vat || '', ghi_chu: ct.ghi_chu || '' };
      }).filter(function (r) { return r.sl > 0; });

      // Khe chia khoảng: xuất kèm để phiếu ghi rõ (làm tròn 1mm) + mục đích + bề thanh
      // muc_dich: 'an_toan' (mặc định — cảnh báo khi >100mm) | 'trang_tri' (khe đẹp theo tỉ lệ)
      var khe = {};
      Object.keys(dnChia).forEach(function (ten) {
        layBien(ten + '_n');
        khe[ten] = {
          n: cache[ten + '_n'], khe: Math.round(cache[ten + '_khe']),
          mucDich: dnChia[ten].muc_dich || 'an_toan',
          wThanh: Math.round(tinhBieuThuc(dnChia[ten].be_rong_thanh, layBien))
        };
      });

      // Kết quả phụ khai báo trong mẫu (số bậc, góc vát...) — hiện lên phiếu
      var phuThem = (mau.ket_qua_phu || []).map(function (k) {
        return { ten: k.ten, nhan: k.nhan || k.ten, don_vi: k.don_vi || '',
                 gia_tri: Math.round(layBien(k.ten) * 10) / 10 };
      });

      return { chiTiet: chiTiet, khe: khe, bien: cache, phuThem: phuThem };
    }

    return {
      ma: mau.ma, ten: mau.ten, nhom: mau.nhom,
      dauVao: mau.dau_vao, hangSo: mau.hang_so,
      hangSoChoChot: hangSoChoChot,
      trangThai: mau.trang_thai || 'nhap',
      tinh: tinh
    };
  }

  return { napMau: napMau, tinhBieuThuc: tinhBieuThuc };
});
