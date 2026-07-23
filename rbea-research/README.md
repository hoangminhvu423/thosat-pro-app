# rbea-research — RB_EA strategy R&D (log cho agent nối tiếp)

Đọc **PROJECT_STATE_HANDOFF.md** trước — nó tóm tắt trạng thái, đã-chứng-minh / đã-bác / việc-tiếp-theo, và inventory file.

## Entry points
- `PROJECT_STATE_HANDOFF.md` — trạng thái + handoff (đọc đầu tiên).
- `RB_EA_DEEP_AUDIT_20260722.md` — audit đối kháng v0.1.
- `RESULTS_v0.2.md`, `NSHAPE_STUDY_RESULTS.md` — kết quả đã kiểm chứng (net phí, OOS).
- `RB_EA_v0.2.mq5` — EA đã vá (chưa compile/audit/demo).
- `PREREG_ENTRY_TP_STUDY.md`, `JOURNAL_R1_schema.md`, `PLAN_v0.2.md`.

## Harness (Python stdlib, `python3 X.py <ohlc_csv> [cost_R]`)
- `entry_study.py` (H4), `entry_study_v2.py` (M30 + wick setup), `prod_engine.py` (replica A/B E1), `nshape_study.py` (chữ N).

## Tài liệu gốc dự án (đồng bộ từ Drive folder RB_EA)
PHASE1_FINAL, PHASE2_REPORT, FABLE_A_FINDINGS, LOGIC_FRAMEWORK, V02_CONTROL_RUN, MC003_EXPERIMENT,
MIRROR_STUDY, SETUP_DECAY_STUDY, META_LESSONS, RESEARCH_PROGRAM, PROP_MC_FINDINGS (Skinner), RB_EA_v0.1.mq5.

INDICATIVE: mọi số chạy trên proxy + tick-volume; phải chạy lại trên engine Fable-A/B để vào hồ sơ chính thức.
