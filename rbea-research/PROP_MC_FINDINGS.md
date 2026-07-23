Prop-as-Structured-Product — Monte Carlo Findings (2026-06-29)
Skinner method: model FTMO account as a convex structured product; price by Monte Carlo with our VALIDATED CTA return distribution. Challenge = barrier (P pass); funded = payout (E withdrawn). Net EV = P(pass)×E[payout 1yr] − fee. Config: FTMO 100k 2-step (P1 +10%, P2 +5%), max loss 10%, daily 5%, fee $540, split 80%, funded 1yr, no resets.
Net EV by edge scenario × risk geometry (vol)
Scenario
	5% vol
	10%
	15%
	20%
	30%
	Backtest (Sh 0.81) NetEV
	+$3.7k
	+$6.1k
	+$6.4k
	+$6.4k
	+$3.0k
	Degraded (Sh 0.40) NetEV
	+$1.8k
	+$3.4k
	+$3.5k
	+$3.5k
	+$2.0k
	Zero edge (Sh 0.0) NetEV
	+$0.2k
	+$1.2k
	+$1.5k
	+$1.6k
	+$1.0k
	P(pass) @ degraded
	68%
	56%
	44%
	39%
	30%
	Kết luận
1. Skinner đúng: payoff lồi → net EV dương kể cả ZERO edge (~+$1.5k/lần) nhờ downside chặn ở phí $540, upside là payout. Với edge thật (Sharpe 0.4 live) → **+$3.5k/lần**.
2. Risk geometry tối ưu ~15–20% vol cho challenge — KHÔNG phải 4% "an toàn". Vì downside đã bị chặn, aggression được thưởng (P(pass) thấp hơn nhưng payout/lần funded cao hơn nhiều → net EV cao hơn).
3. Đảo ngược lời khuyên cũ: challenge nên chạy vol cao (~15%); funded (muốn GIỮ lâu) nên hạ vol (~4–6%) để sống sót → dual-vol: aggressive-to-pass, conservative-to-keep.
⚠️ Caveat trung thực (bắt buuộc)
* Variance khổng lồ: net EV +$3.5k nhưng ~56% số lần mất phí $540. Đây là EV-play qua NHIỀU lần, không phải chắc thắng 1 lần → cần bankroll cho nhiều attempt.
* Counterparty/model risk: giả định firm trả payout đều + không đổi luật. Thực tế prop có thể từ chối/đổi rule → EV thật thấp hơn.
* Input phải trung thực: dùng phân phối M1-validated (đã làm). Nuôi backtest lạc quan → P(pass) phồng. Dùng kịch bản "degraded 0.4" làm cơ sở quyết định.
* Model dùng granularity ngày (không intraday), 2-step config chuẩn, 1 attempt. Cần encode luật chính xác từng firm + reset.
R&D tối ưu (mình tự chốt — kế hoạch hợp nhất)
Hai tài sản đã có: (1) CTA edge thật Sharpe ~0.7 (cho funded/Darwinex steady), (2) Prop MC engine (định giá trò chơi prop).


Kế hoạch deploy hợp nhất:


1. Challenge phase: chạy CTA ở vol ~15% (tối ưu net EV) — coi như mua option rẻ, chấp nhận ~44% pass, net EV +$3.5k/lần.
2. Funded phase: hạ vol xuống ~4怓6% để GIỮ account + rút đều (survival).
3. So nhiều firm: encode luật chính xác FTMO vs The5ers vs FundedNext → engine chọn firm net-EV cao nhất.
4. Track record song song: chạy CTA trên cent/demo để có số liệu thật → vữa cho Darwinex, vừa làm input trung thực cho MC.