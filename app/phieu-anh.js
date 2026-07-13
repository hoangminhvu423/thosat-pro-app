/* =====================================================================
   phieu-anh.js — Xuất phiếu cắt thành ảnh PNG để gửi Zalo (UI helper)

   Không thêm thư viện ngoài: vẽ canvas thuần, offline hoàn toàn.
   Ảnh 720px rộng (nét gấp đôi retina), nền phiếu vàng nhạt như giấy,
   chữ monospace dễ đọc trên điện thoại thợ.

   Cách gửi:
   - Điện thoại (có Web Share): bấm nút → mở thẳng khay chia sẻ → chọn Zalo.
   - Máy tính / không hỗ trợ share: tự tải file PNG về, kéo vào Zalo.
   ===================================================================== */
(function (root) {
  'use strict';

  var MAU = {
    nenHeader: '#24303C', cam: '#F25C1F', nenGiay: '#FFFBEE',
    muc: '#1B2129', xam: '#5C6672', vien: '#E8DFC4'
  };
  var RONG = 720, LE = 32, DONG_CAO = 26, TILE = 2; // TILE: vẽ 2x cho nét

  function beDong(ctx, chu, rongToiDa) {
    // Bẻ dòng dài theo bề rộng thực đo được (giữ nguyên từ, không cắt giữa chữ)
    var ket = [];
    chu.split('\n').forEach(function (dong) {
      if (ctx.measureText(dong).width <= rongToiDa) { ket.push(dong); return; }
      var tu = dong.split(' '), hienTai = '';
      tu.forEach(function (t) {
        var thu = hienTai ? hienTai + ' ' + t : t;
        if (ctx.measureText(thu).width <= rongToiDa) hienTai = thu;
        else { if (hienTai) ket.push(hienTai); hienTai = '  ' + t; } // thụt đầu dòng nối
      });
      if (hienTai) ket.push(hienTai);
    });
    return ket;
  }

  // vanBan: text phiếu (dòng đầu làm tiêu đề). Trả về canvas đã vẽ xong.
  function veAnh(vanBan) {
    var cacDong = vanBan.trim().split('\n');
    var tieuDe = cacDong[0];
    var than = cacDong.slice(1).join('\n');

    var nhap = document.createElement('canvas'); // đo trước
    var ctxDo = nhap.getContext('2d');
    ctxDo.font = '15px Menlo, Consolas, monospace';
    var dongThan = beDong(ctxDo, than, RONG - 2 * LE);
    ctxDo.font = 'bold 20px -apple-system, Segoe UI, Roboto, sans-serif';
    var dongTieuDe = beDong(ctxDo, tieuDe, RONG - 2 * LE);

    var caoHeader = 34 + dongTieuDe.length * 28 + 18;
    var caoThan = dongThan.length * DONG_CAO;
    var cao = caoHeader + 24 + caoThan + 64;

    var canvas = document.createElement('canvas');
    canvas.width = RONG * TILE; canvas.height = cao * TILE;
    var ctx = canvas.getContext('2d');
    ctx.scale(TILE, TILE);

    // Nền giấy + header thép
    ctx.fillStyle = MAU.nenGiay; ctx.fillRect(0, 0, RONG, cao);
    ctx.fillStyle = MAU.nenHeader; ctx.fillRect(0, 0, RONG, caoHeader);
    ctx.fillStyle = MAU.cam; ctx.fillRect(0, caoHeader - 4, RONG, 4);

    ctx.fillStyle = '#8C99A6';
    ctx.font = 'bold 11px -apple-system, Segoe UI, Roboto, sans-serif';
    ctx.fillText('THỢ SẮT PRO — PHIẾU CẮT SẮT', LE, 24);
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 20px -apple-system, Segoe UI, Roboto, sans-serif';
    dongTieuDe.forEach(function (d, i) { ctx.fillText(d, LE, 52 + i * 28); });

    // Thân phiếu
    ctx.fillStyle = MAU.muc;
    ctx.font = '15px Menlo, Consolas, monospace';
    dongThan.forEach(function (d, i) {
      ctx.fillText(d, LE, caoHeader + 40 + i * DONG_CAO);
    });

    // Chân phiếu
    var y = cao - 26;
    ctx.strokeStyle = MAU.vien; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(LE, y - 16); ctx.lineTo(RONG - LE, y - 16); ctx.stroke();
    ctx.fillStyle = MAU.xam;
    ctx.font = '12px -apple-system, Segoe UI, Roboto, sans-serif';
    ctx.fillText('Lập lúc ' + new Date().toLocaleString('vi-VN') +
      ' — kích thước mm, kiểm tra lại trước khi cắt', LE, y);
    return canvas;
  }

  function tenFile(khoa) {
    var d = new Date();
    var ngay = d.getFullYear() + ('0' + (d.getMonth() + 1)).slice(-2) + ('0' + d.getDate()).slice(-2);
    return 'phieu-cat-' + khoa + '-' + ngay + '.png';
  }

  // Xuất phiếu: ưu tiên khay chia sẻ (điện thoại → Zalo), không có thì tải PNG
  function xuat(vanBan, khoa, thongBao) {
    var canvas = veAnh(vanBan);
    canvas.toBlob(function (blob) {
      if (!blob) { alert('Không tạo được ảnh phiếu'); return; }
      var file = new File([blob], tenFile(khoa), { type: 'image/png' });
      if (navigator.canShare && navigator.canShare({ files: [file] })) {
        navigator.share({ files: [file], title: 'Phiếu cắt sắt' }).catch(function () {/* thợ bấm hủy */});
      } else {
        var a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = tenFile(khoa);
        document.body.appendChild(a); a.click(); a.remove();
        setTimeout(function () { URL.revokeObjectURL(a.href); }, 5000);
        if (thongBao) thongBao('Đã tải ảnh phiếu — kéo vào Zalo để gửi.');
      }
    }, 'image/png');
    return canvas; // cho kiểm thử/xem trước
  }

  root.PHIEUANH = { veAnh: veAnh, xuat: xuat };
})(typeof self !== 'undefined' ? self : this);
