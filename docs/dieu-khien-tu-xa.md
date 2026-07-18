# ĐIỀU KHIỂN CLAUDE TRÊN MAC TỪ ĐIỆN THOẠI (5G)

> Mục tiêu: ngồi bất cứ đâu, dùng **iPhone + 5G**, điều khiển phiên **Claude Code CLI chạy trên MacBook
> (WiFi ở nhà)**. Thiết kế ưu tiên **bảo mật** — vì máy này liên quan tài khoản **FTMO**.
> Nguyên tắc: **KHÔNG mở port ra internet, KHÔNG dùng WiFi lạ, mọi thứ mã hoá đầu-cuối.**

## Sơ đồ

```
📱 iPhone (5G)  ──Tailscale (mã hoá E2E, xuyên NAT)──►  💻 MacBook (WiFi nhà)
   Termius (SSH)                                          tmux ← claude (CLI)
```

Điện thoại và Mac ở hai mạng khác nhau → **Tailscale** dựng một mạng riêng ảo giữa đúng 2 thiết bị của cậu,
xuyên NAT tự động, **không cần mở port trên router nhà**. Đây là điểm mấu chốt về an toàn.

---

## PHẦN A — Cài đặt một lần (~15 phút)

### 1. Tailscale (trên cả 2 máy)
- **Mac**: tải Tailscale (`brew install --cask tailscale` hoặc từ tailscale.com) → đăng nhập.
- **iPhone**: cài app **Tailscale** từ App Store → đăng nhập **cùng tài khoản**.
- Sau khi đăng nhập, mỗi máy có một IP dạng `100.x.y.z`. Ghi lại IP của Mac (mở app Tailscale trên Mac để xem).
- Bật **MFA** cho tài khoản Tailscale (Settings trên trang tailscale.com).

### 2. Bật SSH trên Mac (chỉ trong mạng Tailscale)
- **System Settings → General → Sharing → Remote Login: BẬT.**
- Giới hạn user được phép (chọn "Only these users" → chỉ user của cậu).

### 3. SSH bằng KHOÁ, không dùng mật khẩu (quan trọng cho FTMO)
- Trên **Termius (iPhone)**: tạo một cặp khoá (Keychain → New Key → ED25519). Copy **public key**.
- Trên **Mac**, dán public key vào file uỷ quyền:
  ```bash
  mkdir -p ~/.ssh && chmod 700 ~/.ssh
  echo "ssh-ed25519 AAAA...KHOÁ_PUBLIC_TỪ_TERMIUS... iphone" >> ~/.ssh/authorized_keys
  chmod 600 ~/.ssh/authorized_keys
  ```
- (Tuỳ chọn, chặt hơn) tắt đăng nhập bằng mật khẩu: sửa `/etc/ssh/sshd_config` →
  `PasswordAuthentication no` → `sudo launchctl kickstart -k system/com.openssh.sshd`.
  **CHỈ làm sau khi đã đăng nhập bằng khoá thành công**, kẻo tự khoá mình ra ngoài.

### 4. tmux (giữ phiên "bất tử")
```bash
brew install tmux
```

---

## PHẦN B — Mỗi lần rời nhà: khởi động lab (làm trên Mac, ~30 giây)

```bash
# 1. Cắm SẠC (bắt buộc nếu muốn đóng nắp / chạy đêm)
# 2. Chống Mac ngủ:
caffeinate -dis &

# 3. Vào thư mục lab + mở phiên tmux bất tử:
cd ~/quant-lab
tmux new -s lab

# 4. Trong tmux, chạy Claude:
claude
# (giao nhiệm vụ: "Đọc quant/NHIEM-VU.md và làm theo.")
```

> Muốn **đóng nắp** mà máy vẫn chạy: phải **cắm nguồn** + đóng nắp (clamshell). An toàn nhất: **để nắp mở**,
> úp máy ở nhà. Kiểm tra `System Settings → Battery → Options` để máy không ngủ khi cắm điện.

---

## PHẦN C — Từ điện thoại (5G): điều khiển

1. Bật **Tailscale** trên iPhone (gạt ON).
2. Mở **Termius** → New Host: địa chỉ = **IP Tailscale của Mac** (`100.x.y.z`), user = user Mac, Key = khoá đã tạo.
3. Kết nối → gõ:
   ```bash
   tmux attach -t lab
   ```
4. **Toàn bộ màn hình Claude CLI của Mac hiện trên điện thoại.** Gõ lệnh, duyệt quyền, xem sweep chạy.
5. Xong việc: **thoát tmux mà không tắt phiên** → bấm `Ctrl-b` rồi `d` (detach). Claude vẫn chạy tiếp ở nhà.
   Đóng app cũng được — lần sau `tmux attach -t lab` là vào lại đúng chỗ.

---

## PHẦN D — BẢO MẬT (vì đang cầm tài khoản FTMO — đọc kỹ)

1. **Chỉ Tailscale, không bao giờ mở port 22 ra internet.** Không port-forward trên router nhà.
2. **SSH bằng khoá, tắt mật khẩu** (Phần A.3). Khoá đặt passphrase; bật Face ID mở Termius.
3. **MFA** cho: tài khoản Tailscale, Apple ID, tài khoản Claude.
4. **Không WiFi lạ** — cậu đã đúng. 5G của cậu + WiFi nhà là đủ; Tailscale mã hoá E2E nên kể cả mạng nào cũng an toàn, nhưng cứ giữ thói quen này.
5. **Cổng an toàn cho thao tác LIVE/VPS/FTMO** — điều khiển từ xa mà lỡ tay thì nguy:
   - **KHÔNG bật auto-accept toàn phần** khi phiên có thể chạm VPS / compile / deploy EA. Bắt **duyệt tay** — đúng `guardian-rules`. Nghiên cứu/backtest thì nới lỏng được.
   - Nhớ sự cố **10/06/2026** (agent phá VPS): điều khiển từ xa làm rủi ro đó lớn hơn, không nhỏ đi.
   - Việc động vào tài khoản FTMO live nên làm khi **ngồi trước máy**, không phải qua điện thoại lúc di chuyển.
6. **Khoá màn hình Mac** khi rời nhà (`Ctrl-Cmd-Q`) — SSH vẫn vào được, nhưng người khác ngồi vào máy thì không.
7. Nếu mất điện thoại: vào tailscale.com **xoá thiết bị iPhone khỏi mạng** ngay → cắt đường vào.

---

## PHẦN E — Cầu dự phòng: điều khiển qua REPO (không cần setup)

Khi không tiện SSH (hoặc chỉ muốn giao việc bất đồng bộ), dùng vòng lặp qua GitHub:
```
📱 nói với phiên CLOUD (claude.ai): "sửa quant/NHIEM-VU.md: thêm test XAUUSD M5" → cloud push
💻 phiên Mac đang chạy: bảo nó "git pull" → làm → "commit + push kết quả"
📱 quay lại cloud: "đọc quant/results/ledger.csv" → phân tích ngay trên điện thoại
```
Chậm hơn SSH nhưng **zero setup, an toàn tuyệt đối** (không mở gì cả), hợp việc chạy dài.

---

## Tóm tắt phân vai
| Kênh | Realtime? | Setup | Dùng khi |
|---|---|---|---|
| **SSH + tmux** (Tailscale) | ✅ | 15' một lần | Cần can thiệp trực tiếp, xem sweep, duyệt quyền |
| **Qua repo** (cloud ↔ Mac) | ❌ (bất đồng bộ) | 0 | Giao việc, đọc kết quả, chạy dài qua đêm |

> Quy tắc vàng khi điều khiển từ xa: **quyền càng rộng, càng phải duyệt tay ở khâu chạm tiền thật.**
> Máy quét cả đêm được — nhưng nút bấm vào lệnh FTMO thì để dành cho lúc cậu tỉnh táo ngồi trước máy.
