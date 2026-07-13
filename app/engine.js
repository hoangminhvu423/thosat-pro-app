/* =====================================================================
   engine.js — Lõi tính toán ThợSắt Pro (module thuần, KHÔNG dính UI)

   Quy ước đơn vị:
   - Lan can & sen hoa: MỌI đầu vào bằng mm (UI tự quy đổi m → mm).
   - Mái tôn: đầu vào bằng m (vật tư khổ lớn), độ dốc bằng %.
   - MỌI chiều dài cắt trả ra là mm NGUYÊN. Khe hở làm tròn 1 mm.
   - Góc trả ra bằng ĐỘ (số thực, UI tự format).

   Dùng được 2 nơi:
   - Trình duyệt: <script src="engine.js"> → window.ENGINE
   - Node (test): const ENGINE = require('./engine.js')
   ===================================================================== */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.ENGINE = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  /* ---------- Tiện ích chung ---------- */

  // Chia đều các thanh bề rộng w vào khoảng usable sao cho khe ≤ kheMax.
  // Trả về n (số thanh) và khe (mm, CHƯA làm tròn — nơi gọi tự làm tròn khi xuất).
  function chiaDeu(usable, w, kheMax) {
    if (usable <= kheMax) return { n: 0, khe: usable };
    const n = Math.ceil((usable - kheMax) / (kheMax + w));
    const khe = (usable - n * w) / (n + 1);
    return { n, khe };
  }

  // Quy mét dài sang số cây 6m. Hữu dụng 5.9m/cây. // TẠM - CHỜ CHỐT (hao đầu cây)
  const DAI_HUU_DUNG_CAY_M = 5.9;
  function cay6(met) { return Math.ceil(met / DAI_HUU_DUNG_CAY_M); }

  function radSangDo(rad) { return rad * 180 / Math.PI; }

  function batBuocDuong(giaTri, ten) {
    if (!(giaTri > 0)) throw new Error('Thiếu hoặc sai ' + ten);
  }
  function batBuocKhongAm(giaTri, ten) {
    if (!(giaTri >= 0)) throw new Error('Sai ' + ten + ' (bỏ trống hoặc âm)');
  }
  // Chặn NaN lan tràn: mọi tham số phụ phải là số dương/không âm rõ ràng
  function kiemDuong(ds) { ds.forEach(function (p) { batBuocDuong(p[0], p[1]); }); }
  function kiemKhongAm(ds) { ds.forEach(function (p) { batBuocKhongAm(p[0], p[1]); }); }

  /* ==================== LAN CAN ==================== */

  // Lan can thẳng — mọi đầu vào mm.
  function lanCanThang({ L, H, kcCot = 2200, wCot = 50, wDo = 14, kheMax = 100, tren = 80, duoi = 50 }) {
    batBuocDuong(L, 'chiều dài lan can');
    batBuocDuong(H, 'chiều cao lan can');
    kiemDuong([[kcCot, 'khoảng cách cột'], [wCot, 'bề rộng cột'], [wDo, 'bề rộng đố'], [kheMax, 'khe hở tối đa']]);
    kiemKhongAm([[tren, 'tay vịn + thanh trên'], [duoi, 'thanh đế dưới']]);
    const soKhoang = Math.max(1, Math.ceil(L / kcCot));
    const soCot = soKhoang + 1;
    const khoangTT = (L - soCot * wCot) / soKhoang; // lọt lòng mỗi khoang
    if (khoangTT <= 0) throw new Error('Lan can quá ngắn so với bề rộng cột');
    const cd = chiaDeu(khoangTT, wDo, kheMax);
    const tongDo = cd.n * soKhoang;
    const daiDo = H - tren - duoi;
    if (daiDo <= 0) throw new Error('Chiều cao quá nhỏ so với tay vịn + thanh đế');
    const metCot = soCot * H / 1000, metTayVin = 2 * L / 1000, metDo = tongDo * daiDo / 1000;
    return {
      kieu: 'thang',
      soKhoang, soCot,
      khoangTT: Math.round(khoangTT),
      doMoiKhoang: cd.n, tongDo,
      khe: Math.round(cd.khe), kheRaw: cd.khe,
      daiCot: Math.round(H), daiTayVin: Math.round(L), daiDo: Math.round(daiDo),
      metCot, metTayVin, metDo,
      cay: { cot: cay6(metCot), tayVin: cay6(metTayVin), do: cay6(metDo) }
    };
  }

  // Lan can cầu thang xiên — mọi đầu vào mm.
  // Lng: chiều ngang mặt bằng, Hc: chiều cao lên, H: cao lan can đo thẳng đứng.
  function lanCanXien({ Lng, Hc, H, kcCot = 2200, wCot = 50, wDo = 14, kheMax = 100, tren = 80, duoi = 50 }) {
    batBuocDuong(Lng, 'chiều ngang mặt bằng');
    batBuocDuong(Hc, 'chiều cao lên');
    batBuocDuong(H, 'chiều cao lan can');
    kiemDuong([[kcCot, 'khoảng cách cột'], [wCot, 'bề rộng cột'], [wDo, 'bề rộng đố'], [kheMax, 'khe hở tối đa']]);
    kiemKhongAm([[tren, 'tay vịn + thanh trên'], [duoi, 'thanh đế dưới']]);
    const Lx = Math.sqrt(Lng * Lng + Hc * Hc); // chiều dài xiên tay vịn
    const aRad = Math.atan(Hc / Lng);           // góc dốc
    const soKhoang = Math.max(1, Math.ceil(Lx / kcCot));
    const soCot = soKhoang + 1;
    // Đố đứng → chia đều theo phương NGANG (mặt bằng)
    const khoangNgang = (Lng - soCot * wCot) / soKhoang;
    if (khoangNgang <= 0) throw new Error('Cầu thang quá ngắn so với bề rộng cột');
    const cd = chiaDeu(khoangNgang, wDo, kheMax);
    const tongDo = cd.n * soKhoang;
    // Tay vịn nghiêng: bề dày chiếm theo phương đứng = dày/cos(a)
    const daiDo = H - (tren + duoi) / Math.cos(aRad);
    if (daiDo <= 0) throw new Error('Chiều cao lan can quá nhỏ so với tay vịn + thanh đế (dốc lớn)');
    const metCot = soCot * H / 1000, metTayVin = 2 * Lx / 1000, metDo = tongDo * daiDo / 1000;
    return {
      kieu: 'xien',
      daiXien: Math.round(Lx), daiXienRaw: Lx,
      gocDo: radSangDo(aRad), // độ — cắt vát 2 đầu đố & tay vịn
      soKhoang, soCot,
      khoangNgang: Math.round(khoangNgang),
      doMoiKhoang: cd.n, tongDo,
      khe: Math.round(cd.khe), kheRaw: cd.khe,
      daiCot: Math.round(H), daiDo: Math.round(daiDo),
      metCot, metTayVin, metDo,
      cay: { cot: cay6(metCot), tayVin: cay6(metTayVin), do: cay6(metDo) }
    };
  }

  /* ==================== MÁI TÔN ==================== */
  // Đầu vào bằng m, độ dốc %. Kết quả mét giữ số thực (vật tư, không phải phiếu cắt mm).

  function maiTon1Doc({ D, R, doc, du = 0.1, kho = 1.0, kcXG = 0.85, kcKeo = 3, vitM2 = 8 }) {
    batBuocDuong(D, 'chiều ngang mái');
    batBuocDuong(R, 'chiều sâu mái');
    kiemDuong([[kho, 'khổ tôn'], [kcXG, 'khoảng cách xà gồ'], [kcKeo, 'khoảng cách kèo']]);
    kiemKhongAm([[doc, 'độ dốc'], [du, 'tôn dư'], [vitM2, 'vít/m²']]);
    const heSoDoc = doc / 100;
    const daiDoc = R * Math.sqrt(1 + heSoDoc * heSoDoc) + du;
    const soTam = Math.ceil(D / kho);
    const dienTich = soTam * daiDoc * kho;
    const hangXaGo = Math.floor(daiDoc / kcXG) + 1, metXaGo = hangXaGo * D;
    const soKeo = Math.ceil(D / kcKeo) + 1, metKeo = soKeo * daiDoc;
    const soVit = Math.ceil(dienTich * vitM2);
    return {
      kieu: '1doc', daiDoc, soTam, dienTich,
      hangXaGo, metXaGo, soKeo, metKeo, soVit,
      cayXaGo: cay6(metXaGo)
    };
  }

  function maiTon2Doc({ D, R, doc, du = 0.1, kho = 1.0, kcXG = 0.85, kcKeo = 3, vitM2 = 8 }) {
    batBuocDuong(D, 'chiều ngang mái');
    batBuocDuong(R, 'khẩu độ mái');
    kiemDuong([[kho, 'khổ tôn'], [kcXG, 'khoảng cách xà gồ'], [kcKeo, 'khoảng cách kèo']]);
    kiemKhongAm([[doc, 'độ dốc'], [du, 'tôn dư'], [vitM2, 'vít/m²']]);
    const heSoDoc = doc / 100;
    const sauBen = R / 2;
    const daiDoc = sauBen * Math.sqrt(1 + heSoDoc * heSoDoc) + du;
    const soTamBen = Math.ceil(D / kho), soTam = 2 * soTamBen;
    const dienTich = soTam * daiDoc * kho;
    const hangBen = Math.floor(daiDoc / kcXG) + 1, metXaGo = 2 * hangBen * D;
    const soVi = Math.ceil(D / kcKeo) + 1, metKeo = soVi * 2 * daiDoc;
    const soVit = Math.ceil(dienTich * vitM2);
    return {
      kieu: '2doc', sauBen, daiDoc, soTamBen, soTam, dienTich,
      hangBen, metXaGo, soVi, metKeo, soVit, daiUpNoc: D,
      cayXaGo: cay6(metXaGo)
    };
  }

  function maiVom({ D, R, f, du = 0.1, kho = 1.0, kcXG = 0.85, kcKeo = 3, vitM2 = 8 }) {
    batBuocDuong(D, 'chiều ngang mái');
    batBuocDuong(R, 'khẩu độ mái');
    batBuocDuong(f, 'chiều cao vồng vòm');
    kiemDuong([[kho, 'khổ tôn'], [kcXG, 'khoảng cách xà gồ'], [kcKeo, 'khoảng cách kèo']]);
    kiemKhongAm([[du, 'tôn dư'], [vitM2, 'vít/m²']]);
    const banKinhUon = (f * f + (R / 2) * (R / 2)) / (2 * f); // bán kính uốn kèo
    const theta = Math.asin(Math.min(1, (R / 2) / banKinhUon));
    const cung = 2 * banKinhUon * theta;
    const daiTon = cung + du;
    const soTam = Math.ceil(D / kho);
    const dienTich = soTam * daiTon * kho;
    const hangXaGo = Math.ceil(cung / kcXG) + 1, metXaGo = hangXaGo * D;
    const soKeo = Math.ceil(D / kcKeo) + 1, metKeo = soKeo * cung;
    const soVit = Math.ceil(dienTich * vitM2);
    return {
      kieu: 'vom', banKinhUon, cung, daiTon, soTam, dienTich,
      hangXaGo, metXaGo, soKeo, metKeo, soVit,
      cayXaGo: cay6(metXaGo)
    };
  }

  /* ==================== SEN HOA ==================== */
  // Đầu vào mm. W×H là ô cửa lọt lòng; khung = bề rộng thanh khung bao.

  function khungBao({ W, H, khung, soBo }) {
    batBuocDuong(W, 'chiều rộng ô cửa');
    batBuocDuong(H, 'chiều cao ô cửa');
    batBuocKhongAm(khung, 'bề khung bao');
    const tW = W - 2 * khung, tH = H - 2 * khung; // lọt lòng trong khung
    if (tW <= 0 || tH <= 0) throw new Error('Khung bao quá dày so với ô cửa');
    return { tW, tH, metKhung: 2 * (W + H) / 1000 * soBo };
  }

  // Nan đứng hoặc nan ngang. huong: 'dung' | 'ngang'
  function senHoaNan({ W, H, khung = 20, soBo = 1, wNan = 14, kheMax = 100, huong = 'dung' }) {
    soBo = Math.max(1, soBo);
    const { tW, tH, metKhung } = khungBao({ W, H, khung, soBo });
    kiemDuong([[wNan, 'bề rộng nan'], [kheMax, 'khe hở tối đa']]);
    const usable = (huong === 'dung') ? tW : tH;
    const daiNan = (huong === 'dung') ? tH : tW;
    const cd = chiaDeu(usable, wNan, kheMax);
    const metNan = cd.n * daiNan / 1000 * soBo;
    return {
      mau: 'nan', huong, soBo, tW, tH,
      soNan: cd.n, tongNan: cd.n * soBo,
      khe: Math.round(cd.khe), kheRaw: cd.khe,
      daiNan: Math.round(daiNan),
      metKhung, metNan,
      cay: { khung: cay6(metKhung), nan: cay6(metNan) }
    };
  }

  // Ô caro vuông (đan lưới)
  function senHoaCaro({ W, H, khung = 20, soBo = 1, wNan = 14, kheMax = 100 }) {
    soBo = Math.max(1, soBo);
    const { tW, tH, metKhung } = khungBao({ W, H, khung, soBo });
    kiemDuong([[wNan, 'bề rộng nan'], [kheMax, 'khe hở tối đa']]);
    const cd = chiaDeu(tW, wNan, kheMax); // nan đứng
    const cn = chiaDeu(tH, wNan, kheMax); // nan ngang
    const metNanDung = cd.n * tH / 1000 * soBo, metNanNgang = cn.n * tW / 1000 * soBo;
    return {
      mau: 'caro', soBo, tW, tH,
      nanDung: { n: cd.n, khe: Math.round(cd.khe), kheRaw: cd.khe, dai: Math.round(tH) },
      nanNgang: { n: cn.n, khe: Math.round(cn.khe), kheRaw: cn.khe, dai: Math.round(tW) },
      oLuoi: { cot: cd.n + 1, hang: cn.n + 1 },
      moiHanMoiBo: cd.n * cn.n,
      metKhung, metNanDung, metNanNgang,
      cay: { khung: cay6(metKhung), nan: cay6(metNanDung + metNanNgang) }
    };
  }

  // Caro chéo 45° — mọi nan vát 45° hai đầu, gộp 2 hướng "/" và "\"
  function senHoaCheo({ W, H, khung = 20, soBo = 1, wNan = 14, kheMax = 100 }) {
    soBo = Math.max(1, soBo);
    const { tW, tH, metKhung } = khungBao({ W, H, khung, soBo });
    kiemDuong([[wNan, 'bề rộng nan'], [kheMax, 'khe hở tối đa']]);
    const buoc = kheMax + wNan; // bước tâm-tâm đo vuông góc giữa các nan
    const SQ2 = Math.SQRT2;
    const demTheoDai = {};
    let tongThanhBo = 0, tongMetBo = 0;
    // Đường chéo "/": x + y = c, c chạy theo bội buoc·√2
    for (let c = buoc * SQ2; c < tW + tH - 1; c += buoc * SQ2) {
      const ngang = Math.min(tW, c) - Math.max(0, c - tH);
      if (ngang > wNan) { // bỏ đoạn quá ngắn ở góc
        const dai = Math.round(ngang * SQ2);
        demTheoDai[dai] = (demTheoDai[dai] || 0) + 2; // ×2 vì 2 hướng chéo
        tongThanhBo += 2; tongMetBo += 2 * dai / 1000;
      }
    }
    const thanh = Object.keys(demTheoDai).map(Number).sort((a, b) => b - a)
      .map(dai => ({ dai, slMoiBo: demTheoDai[dai], sl: demTheoDai[dai] * soBo }));
    return {
      mau: 'cheo', soBo, tW, tH,
      buoc, kheVuongGoc: buoc - wNan,
      thanh, tongThanhBo, tongMetBo,
      metKhung,
      cay: { khung: cay6(metKhung), nan: cay6(tongMetBo * soBo) }
    };
  }

  // Hoa rời gắn khung (module) — xếp lưới cột × hàng, khe chia đều
  function senHoaModule({ W, H, khung = 20, soBo = 1, hoaA = 200, hoaB = 200, kheHoaMax = 60 }) {
    soBo = Math.max(1, soBo);
    const { tW, tH, metKhung } = khungBao({ W, H, khung, soBo });
    kiemDuong([[hoaA, 'hoa rộng'], [hoaB, 'hoa cao'], [kheHoaMax, 'khe hoa tối đa']]);
    if (hoaA > tW || hoaB > tH) throw new Error('Bông hoa lớn hơn lọt lòng khung');
    const cot = Math.max(1, Math.floor((tW + kheHoaMax) / (hoaA + kheHoaMax)));
    const hang = Math.max(1, Math.floor((tH + kheHoaMax) / (hoaB + kheHoaMax)));
    const kheNgangRaw = (tW - cot * hoaA) / (cot + 1);
    const kheDocRaw = (tH - hang * hoaB) / (hang + 1);
    return {
      mau: 'hoa', soBo, tW, tH,
      cot, hang,
      hoaMoiBo: cot * hang, tongHoa: cot * hang * soBo,
      kheNgang: Math.round(kheNgangRaw), kheNgangRaw,
      kheDoc: Math.round(kheDocRaw), kheDocRaw,
      metKhung,
      cay: { khung: cay6(metKhung) }
    };
  }

  /* ==================== CẦU THANG ==================== */
  // Chuẩn TCVN 13967:2024: cao bậc hợp lý 150-180 (giới hạn 220), mặt bậc 250-300,
  // nhịp bước Blondel 2h+b = 600±30mm. Cao bậc PHẢI chia đều tuyệt đối.
  // Phong thủy thước lỗ ban: đếm bậc theo Sinh-Lão-Bệnh-Tử, số bậc phải rơi
  // cung SINH (1, 5, 9, 13, 17, 21, 25... = 4k+1). Nhà VN gần như bắt buộc.

  function cungLoBan(soBac) {
    return ['Sinh', 'Lão', 'Bệnh', 'Tử'][(soBac - 1) % 4];
  }

  // Chọn số bậc rơi cung Sinh, cao bậc gần mong muốn nhất trong giới hạn an toàn.
  // Không ép được (cao bậc văng khỏi 120-220) thì trả số chia thường.
  function chonSoBacLoBan(H, caoBacMuon) {
    caoBacMuon = caoBacMuon || 165;
    var base = Math.max(3, Math.round(H / caoBacMuon));
    var tot = null;
    for (var n = base - 4; n <= base + 5; n++) {
      if (n < 3 || (n - 1) % 4 !== 0) continue; // chỉ cung Sinh
      var h = H / n;
      if (h > 220 || h < 120) continue;         // giới hạn an toàn
      if (!tot || Math.abs(h - caoBacMuon) < Math.abs(H / tot - caoBacMuon)) tot = n;
    }
    return tot || base;
  }

  // Cầu thang thẳng 1 vế — mọi đầu vào mm.
  // H: cao tầng sàn→sàn; L: chiều dài mặt bằng vế; W: bề rộng vế thang.
  function cauThang({ H, L, W = 900, caoBacMuon = 165, loBan = true }) {
    batBuocDuong(H, 'chiều cao tầng (đo sàn tới sàn)');
    batBuocDuong(L, 'chiều dài mặt bằng vế thang');
    batBuocDuong(W, 'bề rộng vế thang');
    batBuocDuong(caoBacMuon, 'cao bậc mong muốn');
    var soBac = loBan ? chonSoBacLoBan(H, caoBacMuon)
                      : Math.max(3, Math.round(H / caoBacMuon)); // số cổ bậc
    var caoBac = H / soBac;                               // chia đều tuyệt đối
    var soMatBac = soBac - 1;                             // bậc trên cùng là sàn tầng
    var rongBac = L / soMatBac;
    var gocDo = radSangDo(Math.atan(H / L));
    var daiLimon = Math.sqrt(H * H + L * L);
    var blondel = 2 * caoBac + rongBac;

    var canhBao = [];
    if (caoBac > 220) canhBao.push('Cao bậc ' + caoBac.toFixed(1) + 'mm VƯỢT giới hạn 220mm (TCVN 13967:2024) — nguy hiểm');
    else if (caoBac > 180 || caoBac < 150)
      canhBao.push('Cao bậc ' + caoBac.toFixed(1) + 'mm ngoài khoảng hợp lý 150–180mm (TCVN 13967:2024)');
    if (rongBac < 250) canhBao.push('Mặt bậc ' + rongBac.toFixed(0) + 'mm hẹp hơn chuẩn 250mm — dễ hụt chân');
    else if (rongBac > 300) canhBao.push('Mặt bậc ' + rongBac.toFixed(0) + 'mm rộng hơn chuẩn 300mm — bước bị hẫng');
    if (blondel < 570 || blondel > 630)
      canhBao.push('Nhịp bước 2h+b = ' + blondel.toFixed(0) + 'mm lệch chuẩn 600±30mm — đi lâu sẽ mỏi');
    if (gocDo > 38) canhBao.push('Dốc ' + gocDo.toFixed(1) + '° quá gắt (nhà ở nên 20–38°)');
    var cung = cungLoBan(soBac);
    if (loBan && cung !== 'Sinh')
      canhBao.push('Số bậc ' + soBac + ' rơi cung ' + cung.toUpperCase() +
        ' — không ép được cung Sinh trong giới hạn an toàn, cân nhắc đổi cao bậc mong muốn');

    return {
      soBac, soMatBac, cung,
      caoBac,                       // số thực — thợ chia thước trên tổng H
      rongBac, gocDo, blondel,
      daiLimon: Math.round(daiLimon),
      canhBao,
      chiTiet: [
        { ten: 'Limon (dầm chéo)', dai: Math.round(daiLimon), sl: 2,
          catVat: 'vát ' + gocDo.toFixed(1) + '° hai đầu' },
        { ten: 'Mặt bậc', dai: Math.round(W), sl: soMatBac }
      ]
    };
  }

  // Cầu thang XOẮN ỐC quanh cột tâm — mọi đầu vào mm, góc bằng độ.
  // Dngoai: đường kính ngoài thang; dCot: đường kính cột tâm (ống);
  // gocXoayTong: tổng góc xoay từ chân tới đỉnh (thường 270-450°).
  function cauThangXoan({ H, Dngoai, dCot = 114, gocXoayTong = 360, caoBacMuon = 165, loBan = true }) {
    batBuocDuong(H, 'chiều cao tầng (đo sàn tới sàn)');
    batBuocDuong(Dngoai, 'đường kính ngoài thang');
    batBuocDuong(gocXoayTong, 'tổng góc xoay');
    if (dCot >= Dngoai) throw new Error('Cột tâm to hơn cả thang');
    kiemDuong([[dCot, 'đường kính cột tâm'], [caoBacMuon, 'cao bậc mong muốn']]);
    var soBac = loBan ? chonSoBacLoBan(H, caoBacMuon)
                      : Math.max(3, Math.round(H / caoBacMuon));
    var caoBac = H / soBac;
    var soMatBac = soBac - 1;                    // bậc cuối là sàn tầng
    var gocBacDo = gocXoayTong / soMatBac;
    var R = Dngoai / 2, rCot = dCot / 2;
    var radBac = gocBacDo * Math.PI / 180;
    var rTuyenDi = rCot + (R - rCot) * 2 / 3;    // tuyến đi 2/3 bán kính
    var rongTuyenDi = radBac * rTuyenDi;
    var cungNgoaiBac = radBac * R;
    var sauBac = R - rCot;                       // chiều sâu bậc quạt
    var radTong = gocXoayTong * Math.PI / 180;
    var daiTayVin = Math.sqrt(Math.pow(radTong * R, 2) + H * H); // xoắn helix
    var bacMotVong = 360 / gocBacDo;
    var thongThuyDau = caoBac * Math.min(bacMotVong, soBac);     // khoảng cụng đầu sau 1 vòng

    var canhBao = [];
    if (caoBac > 220) canhBao.push('Cao bậc ' + caoBac.toFixed(1) + 'mm VƯỢT giới hạn 220mm — nguy hiểm');
    else if (caoBac > 180 || caoBac < 150)
      canhBao.push('Cao bậc ' + caoBac.toFixed(1) + 'mm ngoài khoảng hợp lý 150–180mm');
    if (rongTuyenDi < 210)
      canhBao.push('Bậc tại tuyến đi ' + rongTuyenDi.toFixed(0) + 'mm < 210mm — tăng đường kính hoặc giảm góc xoay');
    if (gocXoayTong > 360 && thongThuyDau < 2000)
      canhBao.push('Thông thủy sau 1 vòng ' + thongThuyDau.toFixed(0) + 'mm < 2000mm — cụng đầu');
    var cung = cungLoBan(soBac);
    if (loBan && cung !== 'Sinh')
      canhBao.push('Số bậc ' + soBac + ' rơi cung ' + cung.toUpperCase() + ' — không ép được cung Sinh');

    return {
      soBac, soMatBac, cung, caoBac,
      gocBacDo, rongTuyenDi, cungNgoaiBac: Math.round(cungNgoaiBac),
      sauBac: Math.round(sauBac), daiTayVin: Math.round(daiTayVin),
      canhBao,
      chiTiet: [
        { ten: 'Cột tâm (ống ∅' + dCot + ')', dai: Math.round(H), sl: 1 },
        { ten: 'Bậc quạt (sâu ' + Math.round(sauBac) + ', cung ngoài ' + Math.round(cungNgoaiBac) + ')',
          dai: Math.round(sauBac), sl: soMatBac },
        { ten: 'Tay vịn xoắn (uốn theo thang)', dai: Math.round(daiTayVin), sl: 1 }
      ]
    };
  }

  // Cầu thang CHIẾU NGHỈ (giật cấp chữ L/U) — 2 vế + chiếu nghỉ.
  // QUY ƯỚC (TẠM - CHỜ THỢ CHỐT): chiếu nghỉ tính là 1 bậc trong đếm lỗ ban;
  // vế 1 có soBacVe1 cổ bậc (cổ bậc cuối bước LÊN chiếu nghỉ).
  // L1/L2: dài mặt bằng từng vế KHÔNG kể chiếu nghỉ; W: bề rộng vế = cạnh chiếu nghỉ.
  function cauThangChieuNghi({ H, L1, L2, W = 900, soBacVe1 = 0, caoBacMuon = 165, loBan = true }) {
    batBuocDuong(H, 'chiều cao tầng (đo sàn tới sàn)');
    batBuocDuong(L1, 'chiều dài mặt bằng vế 1');
    batBuocDuong(L2, 'chiều dài mặt bằng vế 2');
    kiemDuong([[W, 'bề rộng vế'], [caoBacMuon, 'cao bậc mong muốn']]);
    var soBac = loBan ? chonSoBacLoBan(H, caoBacMuon)
                      : Math.max(4, Math.round(H / caoBacMuon));
    var caoBac = H / soBac;
    var k = soBacVe1 > 0 ? Math.round(soBacVe1)
                         : Math.max(2, Math.round(soBac * L1 / (L1 + L2)));
    if (k >= soBac - 1) throw new Error('Số bậc vế 1 (' + k + ') quá lớn — vế 2 không còn bậc');
    var matVe1 = k - 1;                 // mặt cuối vế 1 là chiếu nghỉ
    var matVe2 = soBac - k - 1;         // mặt cuối vế 2 là sàn tầng
    if (matVe1 < 1 || matVe2 < 1) throw new Error('Vế quá ngắn — cần ≥ 2 bậc mỗi vế');
    var rong1 = L1 / matVe1, rong2 = L2 / matVe2;
    var goc1 = radSangDo(Math.atan(k * caoBac / L1));
    var goc2 = radSangDo(Math.atan((soBac - k) * caoBac / L2));
    var limon1 = Math.sqrt(Math.pow(k * caoBac, 2) + L1 * L1);
    var limon2 = Math.sqrt(Math.pow((soBac - k) * caoBac, 2) + L2 * L2);

    var canhBao = [];
    if (caoBac > 220) canhBao.push('Cao bậc ' + caoBac.toFixed(1) + 'mm VƯỢT giới hạn 220mm — nguy hiểm');
    else if (caoBac > 180 || caoBac < 150)
      canhBao.push('Cao bậc ' + caoBac.toFixed(1) + 'mm ngoài khoảng hợp lý 150–180mm');
    [['Vế 1', rong1], ['Vế 2', rong2]].forEach(function (v) {
      if (v[1] < 250) canhBao.push(v[0] + ': mặt bậc ' + v[1].toFixed(0) + 'mm hẹp hơn chuẩn 250mm');
      else if (v[1] > 300) canhBao.push(v[0] + ': mặt bậc ' + v[1].toFixed(0) + 'mm rộng hơn chuẩn 300mm');
    });
    var cung = cungLoBan(soBac);
    if (loBan && cung !== 'Sinh')
      canhBao.push('Số bậc ' + soBac + ' (đã đếm chiếu nghỉ là 1 bậc) rơi cung ' + cung.toUpperCase());

    return {
      soBac, cung, caoBac,
      soBacVe1: k, soBacVe2: soBac - k, matVe1, matVe2,
      rongBac1: rong1, rongBac2: rong2, gocDo1: goc1, gocDo2: goc2,
      daiLimon1: Math.round(limon1), daiLimon2: Math.round(limon2),
      canhBao,
      chiTiet: [
        { ten: 'Limon vế 1', dai: Math.round(limon1), sl: 2, catVat: 'vát ' + goc1.toFixed(1) + '° hai đầu' },
        { ten: 'Limon vế 2', dai: Math.round(limon2), sl: 2, catVat: 'vát ' + goc2.toFixed(1) + '° hai đầu' },
        { ten: 'Mặt bậc vế 1', dai: Math.round(W), sl: matVe1 },
        { ten: 'Mặt bậc vế 2', dai: Math.round(W), sl: matVe2 },
        { ten: 'Khung chiếu nghỉ ' + Math.round(W) + '×' + Math.round(W), dai: Math.round(W), sl: 4 }
      ]
    };
  }

  return {
    // tiện ích
    chiaDeu, cay6, DAI_HUU_DUNG_CAY_M,
    // cầu thang
    cauThang, cauThangXoan, cauThangChieuNghi, cungLoBan, chonSoBacLoBan,
    // lan can
    lanCanThang, lanCanXien,
    // mái tôn
    maiTon1Doc, maiTon2Doc, maiVom,
    // sen hoa
    senHoaNan, senHoaCaro, senHoaCheo, senHoaModule
  };
});
