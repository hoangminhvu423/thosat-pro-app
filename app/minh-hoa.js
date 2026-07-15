/* =====================================================================
   minh-hoa.js — Vẽ hình minh họa SVG cho mẫu catalogue (UI helper)

   Mục đích: thợ/chủ nhà CHỌN mẫu là thấy ngay hình dáng; sau khi TÍNH
   thì hình cập nhật theo đúng số thanh/khe vừa chia — không phải ảnh
   chết, là sơ đồ sống theo thông số.

   MINHHOA.ve(svgEl, mau, kq, nhap):
   - mau: máy tính mẫu đã nạp ({ma, nhom, dauVao...})
   - kq:  kết quả mau.tinh() (có kq.khe, kq.bien) — null nếu chưa tính
   - nhap: giá trị đang nhập — null thì dùng mặc định của mẫu
   ===================================================================== */
(function (root) {
  'use strict';

  var THEP = '#24303C', CAM = '#F25C1F', XAM = '#8C99A6', KINH = '#BDD7E7';

  function layNhap(mau, nhap) {
    var v = {};
    (mau.dauVao || []).forEach(function (dv) {
      v[dv.ten] = (nhap && nhap[dv.ten] != null) ? nhap[dv.ten]
        : (dv.mac_dinh != null ? dv.mac_dinh : null);
    });
    return v;
  }
  function thanh(x, y, w, h, mau) {
    return '<rect x="' + x + '" y="' + y + '" width="' + Math.max(w, 1) +
      '" height="' + Math.max(h, 1) + '" fill="' + (mau || THEP) + '"/>';
  }
  function khungRong(x, y, w, h, day, mau) { // khung 4 cạnh rỗng ruột
    return thanh(x, y, w, day, mau) + thanh(x, y + h - day, w, day, mau) +
           thanh(x, y, day, h, mau) + thanh(x + w - day, y, day, h, mau);
  }

  /* Mỗi nhóm 1 kiểu vẽ — nhận vùng vẽ X,Y,W,H cố định 320×120 */
  var X = 10, Y = 12, W = 320, H = 120;

  function veLanCan(mau, kq, v) {
    var xien = v.Lng != null; // cầu thang
    var soCot = (kq && kq.bien && kq.bien.so_cot) || 4;
    var kheDs = kq && kq.khe && Object.values(kq.khe)[0];
    var doMoiKhoang = (kheDs && kheDs.n) || 6;
    var s = '', doc = xien ? 0.35 : 0; // độ nghiêng minh họa
    var yTren = function (x) { return Y + doc * (W - x + X) * (H / W); };
    for (var c = 0; c < soCot; c++) {
      var xc = X + c * (W - 8) / (soCot - 1);
      s += thanh(xc, yTren(xc), 8, Y + H - yTren(xc), THEP);
    }
    var khoangW = (W - 8 * soCot) / (soCot - 1);
    for (var k = 0; k < soCot - 1; k++) {
      var x0 = X + 8 + k * (khoangW + 8);
      for (var d = 1; d <= doMoiKhoang; d++) {
        var xd = x0 + d * khoangW / (doMoiKhoang + 1);
        s += thanh(xd, yTren(xd) + 12, 3.5, H - 26, CAM);
      }
    }
    // tay vịn + đế
    s += '<polygon points="' + X + ',' + yTren(X) + ' ' + (X + W) + ',' + yTren(X + W) +
      ' ' + (X + W) + ',' + (yTren(X + W) + 8) + ' ' + X + ',' + (yTren(X) + 8) + '" fill="' + THEP + '"/>';
    s += thanh(X, Y + H - 8, W, 8, THEP);
    return s;
  }

  function veMaiTon(mau, kq, v) {
    var haiDoc = /2/.test(mau.ma) || (mau.ten || '').indexOf('2 dốc') >= 0;
    var s = '', yDay = Y + H - 10, cao = 55;
    if (haiDoc) {
      var dinh = X + W / 2;
      s += '<polygon points="' + X + ',' + yDay + ' ' + dinh + ',' + (yDay - cao) + ' ' +
        (X + W) + ',' + yDay + '" fill="none" stroke="' + THEP + '" stroke-width="5"/>';
      for (var i = 1; i < 6; i++) { // xà gồ 2 bên
        s += '<circle cx="' + (X + i * W / 12) + '" cy="' + (yDay - i * cao / 6 + 3) + '" r="3.5" fill="' + CAM + '"/>';
        s += '<circle cx="' + (X + W - i * W / 12) + '" cy="' + (yDay - i * cao / 6 + 3) + '" r="3.5" fill="' + CAM + '"/>';
      }
      s += thanh(dinh - 14, yDay - cao - 6, 28, 7, CAM); // úp nóc
    } else {
      s += '<polygon points="' + X + ',' + (yDay - cao) + ' ' + (X + W) + ',' + (yDay - 18) + ' ' +
        (X + W) + ',' + (yDay - 12) + ' ' + X + ',' + (yDay - cao + 6) + '" fill="' + THEP + '"/>';
      for (var j = 1; j < 7; j++)
        s += '<circle cx="' + (X + j * W / 7.5) + '" cy="' + (yDay - cao + 10 + j * 4.4) + '" r="3.5" fill="' + CAM + '"/>';
      s += thanh(X + 12, yDay - cao + 8, 6, cao - 8, THEP) + thanh(X + W - 22, yDay - 16, 6, 16, THEP);
    }
    return s;
  }

  // Cửa/cổng nhiều cánh nan đứng (C-02): vẽ n cánh, mỗi cánh khung + nan + băng ngang
  function veCuaNhieuCanh(mau, kq, v) {
    var soCanh = Math.max(2, Math.min(Math.round(v.so_canh || 4), 6));
    var nanCanh = (kq && kq.khe && kq.khe.nan) ? Math.min(kq.khe.nan.n, 8) : 4;
    var x0 = X + 40, w0 = W - 80, s = khungRong(x0, Y, w0, H, 6, THEP);
    var wCanh = w0 / soCanh;
    for (var c = 0; c < soCanh; c++) {
      var cx = x0 + c * wCanh;
      s += khungRong(cx + 3, Y + 5, wCanh - 6, H - 10, 4, THEP); // khung cánh
      for (var i = 1; i <= nanCanh; i++)
        s += thanh(cx + i * (wCanh - 6) / (nanCanh + 1) + 1, Y + 9, 3, H - 18, CAM); // nan
      // 2 băng ngang trang trí
      s += thanh(cx + 6, Y + H * 0.34, wCanh - 12, 5, THEP) +
           thanh(cx + 6, Y + H * 0.64, wCanh - 12, 5, THEP);
    }
    return s;
  }

  function veCuaSat(mau, kq, v) {
    var s = khungRong(X + 60, Y, W - 120, H, 7, THEP);
    var giua = X + 60 + (W - 120) / 2;
    s += thanh(giua - 2, Y, 4, H, THEP); // khe giữa 2 cánh
    [0, 1].forEach(function (canh) {
      var x0 = X + 67 + canh * ((W - 120) / 2), wCanh = (W - 120) / 2 - 11;
      s += khungRong(x0, Y + 7, wCanh + (canh ? 4 : 0), H - 14, 5, CAM);
      s += thanh(x0, Y + H / 2 - 3, wCanh + (canh ? 4 : 0), 5, CAM); // ngang giữa
    });
    return s;
  }

  function veCongNan(mau, kq, v) {
    var soNan = (kq && kq.bien && kq.bien.so_nan) || 18;
    soNan = Math.max(2, Math.min(soNan, 60));
    var s = thanh(X, Y, W, 7, THEP) + thanh(X, Y + H - 7, W, 7, THEP);
    var buoc = (W - 6) / (soNan - 1);
    for (var i = 0; i < soNan; i++)
      s += thanh(X + i * buoc, Y + 7, Math.max(buoc * 0.45, 2.5), H - 14, CAM);
    return s;
  }

  function veMaiKinh(mau, kq, v) {
    var kheDs = kq && kq.khe && kq.khe.kho_kinh;
    var soDonTay = (kheDs && kheDs.n) || 3;
    var s = thanh(X, Y, W, H, KINH); // kính
    s += khungRong(X, Y, W, H, 8, THEP); // khung quanh 5x10
    var buoc = (W - 16) / (soDonTay + 1);
    for (var i = 1; i <= soDonTay; i++)
      s += thanh(X + 8 + i * buoc - 2.5, Y + 8, 5, H - 16, THEP); // đòn tay 4x8
    // cột chống
    s += thanh(X + 20, Y + H, 7, 14, CAM) + thanh(X + W - 27, Y + H, 7, 14, CAM);
    return s;
  }

  function veCauThang(mau, kq, v) {
    var soBac = 8;
    if (kq && kq.phuThem) {
      var p = kq.phuThem.filter(function (x) { return x.ten === 'so_bac'; })[0];
      if (p) soBac = Math.max(3, Math.min(Math.round(p.gia_tri), 24));
    }
    var bRong = (W - 60) / soBac, bCao = (H - 14) / soBac;
    var s = '', x = X + 30, y = Y + H;
    // limon (dầm chéo dưới bậc)
    s += '<line x1="' + (X + 22) + '" y1="' + (Y + H) + '" x2="' + (X + W - 30) + '" y2="' + (Y + 6) +
      '" stroke="' + THEP + '" stroke-width="9"/>';
    for (var i = 0; i < soBac; i++) { // bậc zigzag
      s += thanh(x, y - bCao, bRong, 5, CAM);              // mặt bậc
      if (i < soBac - 1) s += thanh(x + bRong - 2, y - 2 * bCao, 3.5, bCao, THEP); // cổ bậc
      x += bRong; y -= bCao;
    }
    return s;
  }

  function veThangXoan(mau, kq, v) {
    var soMat = 12;
    if (kq && kq.phuThem) {
      var p = kq.phuThem.filter(function (x) { return x.ten === 'so_bac'; })[0];
      if (p) soMat = Math.max(4, Math.min(Math.round(p.gia_tri) - 1, 28));
    }
    var cx = 170, cy = 68, R = 58, r = 10, s = '';
    s += '<circle cx="' + cx + '" cy="' + cy + '" r="' + R + '" fill="none" stroke="' + THEP + '" stroke-width="4"/>';
    for (var i = 0; i < soMat; i++) {
      var a = i * 2 * Math.PI / soMat;
      s += '<line x1="' + (cx + r * Math.cos(a)).toFixed(1) + '" y1="' + (cy + r * Math.sin(a)).toFixed(1) +
        '" x2="' + (cx + R * Math.cos(a)).toFixed(1) + '" y2="' + (cy + R * Math.sin(a)).toFixed(1) +
        '" stroke="' + CAM + '" stroke-width="5"/>';
    }
    s += '<circle cx="' + cx + '" cy="' + cy + '" r="' + r + '" fill="' + THEP + '"/>';
    return s;
  }

  // Khung bảo vệ inox: BV-01 nan ngang xuyên đố / BV-02 cửa nan đứng + băng
  function veBaoVe(mau, kq, v) {
    var n = (kq && kq.khe && kq.khe.nan) ? Math.max(2, Math.min(kq.khe.nan.n, 20))
                                         : (mau.ma === 'BV-01' ? 8 : 6);
    var x0 = X + 88, w0 = W - 176, s = khungRong(x0, Y, w0, H, 6, THEP);
    if (mau.ma === 'BV-01') {
      for (var i = 1; i <= n; i++)
        s += thanh(x0 + 6, Y + i * (H - 12) / (n + 1), w0 - 12, 3.5, CAM);
      s += thanh(x0 + w0 / 2 - 3, Y + 6, 6, H - 12, THEP); // đố đứng xuyên
    } else {
      for (var j = 1; j <= n; j++)
        s += thanh(x0 + j * (w0 - 12) / (n + 1), Y + 6, 3.5, H - 12, CAM);
      s += thanh(x0 + 6, Y + H * 0.3, w0 - 12, 5, THEP) +   // băng ngang
           thanh(x0 + 6, Y + H * 0.62, w0 - 12, 5, THEP);
    }
    return s;
  }

  // Bông cửa sổ: SH-01 caro lưới / SH-02 nan đứng + hoa góc
  function veSenHoa(mau, kq, v) {
    var x0 = X + 80, w0 = W - 160, s = khungRong(x0, Y, w0, H, 5, THEP);
    if (mau.ma === 'SH-01') {
      var nd = (kq && kq.khe && kq.khe.dung) ? Math.min(kq.khe.dung.n, 14) : 7;
      var nn = (kq && kq.khe && kq.khe.ngang) ? Math.min(kq.khe.ngang.n, 12) : 8;
      for (var i = 1; i <= nd; i++) s += thanh(x0 + i * w0 / (nd + 1), Y + 5, 3, H - 10, CAM);
      for (var j = 1; j <= nn; j++) s += thanh(x0 + 5, Y + j * H / (nn + 1), w0 - 10, 3, THEP);
    } else {
      var n = (kq && kq.khe && kq.khe.nan) ? Math.min(kq.khe.nan.n, 14) : 8;
      for (var k = 1; k <= n; k++) s += thanh(x0 + k * w0 / (n + 1), Y + 5, 3, H - 10, CAM);
      // 4 hoa góc — cuộn xoắn lập là
      [[x0 + 16, Y + 16], [x0 + w0 - 16, Y + 16], [x0 + 16, Y + H - 16], [x0 + w0 - 16, Y + H - 16]]
        .forEach(function (g) {
          s += '<circle cx="' + g[0] + '" cy="' + g[1] + '" r="11" fill="none" stroke="' + CAM + '" stroke-width="3"/>' +
               '<circle cx="' + g[0] + '" cy="' + g[1] + '" r="4.5" fill="' + CAM + '"/>';
        });
    }
    return s;
  }

  function veMacDinh(mau) {
    return khungRong(X + 90, Y + 10, W - 180, H - 20, 6, THEP) +
      '<text x="' + (X + W / 2) + '" y="' + (Y + H / 2 + 5) + '" text-anchor="middle" ' +
      'font-size="16" font-weight="bold" fill="' + XAM + '">' + (mau.ma || '?') + '</text>';
  }

  // anChuThich: true khi vẽ ô nhỏ trong lưới chọn mẫu (bỏ dòng chú thích)
  function ve(svg, mau, kq, nhap, anChuThich) {
    if (!svg || !mau) return;
    var v = layNhap(mau, nhap);
    var s;
    if (mau.ma && mau.ma.indexOf('CG') === 0) s = veCongNan(mau, kq, v);
    else if (mau.ma && mau.ma.indexOf('BV') === 0) s = veBaoVe(mau, kq, v);
    else if (mau.ma === 'CT-02') s = veThangXoan(mau, kq, v);
    else if (mau.nhom === 'cau_thang') s = veCauThang(mau, kq, v);
    else if (mau.nhom === 'lan_can') s = veLanCan(mau, kq, v);
    else if (mau.nhom === 'mai_ton') s = veMaiTon(mau, kq, v);
    else if (mau.nhom === 'sen_hoa') s = veSenHoa(mau, kq, v);
    else if (mau.nhom === 'mai_kinh') s = veMaiKinh(mau, kq, v);
    else if (mau.ma === 'C-02') s = veCuaNhieuCanh(mau, kq, v);
    else if (mau.nhom === 'cua_sat') s = veCuaSat(mau, kq, v);
    else s = veMacDinh(mau);
    svg.setAttribute('viewBox', anChuThich ? '0 0 340 140' : '0 0 340 150');
    // Chú thích = SỐ ĐO THẬT sau khi tính (khe lọt lòng, số thanh, bậc...)
    var chuThich, dam = false;
    if (kq) {
      var phan = [];
      Object.keys(kq.khe || {}).forEach(function (t) {
        var k = kq.khe[t];
        if (k.n > 0) phan.push(k.n + ' thanh · khe lọt lòng ' + k.khe + 'mm');
      });
      if (!phan.length && kq.phuThem && kq.phuThem.length)
        kq.phuThem.slice(0, 2).forEach(function (p) { phan.push(p.nhan.split(' — ')[0] + ' ' + p.gia_tri + p.don_vi); });
      chuThich = phan.slice(0, 2).join('  |  ') || 'sơ đồ theo số vừa tính';
      dam = phan.length > 0;
    } else chuThich = 'sơ đồ minh họa — bấm tính để cập nhật';
    svg.innerHTML = s + (anChuThich ? '' :
      '<text x="170" y="147" text-anchor="middle" font-size="' + (dam ? 11 : 10) + '" ' +
      (dam ? 'font-weight="bold" fill="' + CAM + '"' : 'fill="' + XAM + '"') +
      ' font-family="monospace">' + chuThich + '</text>');
  }

  root.MINHHOA = { ve: ve };
})(typeof self !== 'undefined' ? self : this);
