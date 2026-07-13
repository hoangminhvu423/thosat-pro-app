# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ThợSắt Pro** — an offline-first PWA (in Vietnamese) for iron/steel workers ("thợ sắt") to compute steel cut sheets: railings (lan can), metal roofs (mái tôn), decorative grilles (sen hoa), staircases, and 1D cutting-stock optimization (đề-xê). Users pick a type or catalogue template, enter dimensions, and get a printable/shareable cut ticket ("phiếu cắt sắt").

Pure vanilla HTML/CSS/JS static site. **No package.json, no build step, no dependencies, no framework, no test runner in this repo.** Deployed as static files (GitHub Pages style — note `.nojekyll`).

## Running & Testing

- Serve from the **repo root**, not `app/`: the app fetches `../catalogue/mau/*.json`, so e.g. `python3 -m http.server 8000` in the root, then open `http://localhost:8000/app/`. Root `index.html` just redirects to `app/`.
- The calculation modules are UMD-style and load in Node for quick verification, e.g.:
  ```bash
  node -e "const E=require('./app/engine.js'); console.log(E.lanCanThang({L:6000,H:900}))"
  node -e "const C=require('./app/catalogue.js'); const m=C.napMau(require('./catalogue/mau/LC-01.json')); console.log(m.tinh({L:6, H:0.9}))"
  ```
- Comments reference `tests/catalogue.test.js` and `docs/nghien-cuu/…`, but no `tests/` or `docs/` directory exists in this repo — don't assume they're available.
- The service worker caches aggressively; when testing UI changes in a browser, hard-reload or bump versions (see "Cache versioning" below).

## Architecture

Strict separation between UI and calculation logic:

- **`app/index.html`** — the entire UI: all markup, CSS, and inline glue JS (tab switching, reading inputs, rendering tickets, localStorage history under key `tsp_lichsu`, max 30 entries). Rule stated in the file itself: **no formulas in the UI — all math lives in engine modules so it can be tested.** UI reads inputs → calls a pure module → renders the returned object.
- **Pure calculation modules** (UMD: `window.X` in browser, `require()` in Node; no DOM access):
  - `app/engine.js` (`ENGINE`) — core math: railings straight/inclined, roofs (1-slope, 2-slope, arched), grille patterns, staircases (incl. "thước lỗ ban" step selection), plus shared helpers `chiaDeu` (even spacing) and `cay6` (6m-bar count, 5.9m usable).
  - `app/dexe.js` (`DEXE`) — 1D cutting-stock optimizer, First Fit Decreasing; accounts for kerf, bar-end waste (hao đầu cây), and reusing stock offcuts (tồn kho) only when it actually reduces new bars.
  - `app/catalogue.js` (`CATALOGUE`) — loads JSON templates and evaluates their formulas with a **hand-written expression parser (no `eval`)**; allowed: numbers, variables, `+ - * / ^ ( ) ,` and functions `ceil floor round sqrt abs min max sin cos tan atan bac_lo_ban`. Variables resolve in order: user inputs → `hang_so` constants → `bien` intermediates (recursive, cycle-checked) → `chia_khoang` results as `<ten>_n` / `<ten>_khe`.
  - `app/vat-tu.js` (`VATTU`) — catalog of commercial box-steel sections and weight formula (`kg/m = [(2a+2b)t − 4t²] × 0.00785`) for iron/inox 304/inox 201.
- **UI helpers** (browser-only): `app/phieu-anh.js` (`PHIEUANH`) renders the ticket to a PNG via canvas for sharing on Zalo (Web Share API with download fallback); `app/minh-hoa.js` (`MINHHOA`) draws live SVG diagrams of templates that update with computed results.
- **`app/sw.js`** — service worker, stale-while-revalidate for same-origin GETs, precache list `VO_APP`.
- **`catalogue/`** — data-driven template system: `schema.json` (JSON Schema for templates), `mau/*.json` (templates: LC=lan can, CT=cầu thang, MT=mái tôn, C=cửa, CG=cổng, MK=mái kính), `mau/danh-sach.json` (registry of template codes the app loads).

Load order matters in `app/index.html`: `catalogue.js` must load **after** `engine.js` (it delegates `chiaDeu` and `bac_lo_ban` to `ENGINE`).

## Key Conventions

- **Everything is in Vietnamese**: identifiers, comments, JSON keys, commit messages, UI text. Follow this — do not rename to English.
- **Units** (documented in `engine.js` header): lan can & sen hoa take **mm** inputs; mái tôn takes **m** (slope in %). All returned cut lengths are **integer mm**; gaps (khe) rounded to 1mm for display; angles returned in degrees.
- **`// TẠM - CHỜ CHỐT`** marks provisional trade constants awaiting confirmation from the project owner/real workers (e.g. kerf 2mm, bar-end waste 50mm, 5.9m usable per bar). In templates the same idea is `"cho_chot": true` on a `hang_so` entry. Preserve these markers; don't silently "finalize" such values.
- **Template lifecycle**: `trang_thai` is `nhap` (draft) → `da_audit` → `da_kiem_chung_cong_trinh`, with an `audit` record (date, person, result). New/changed templates stay `nhap` until audited.
- **Safety checks**: the UI warns per QCXDVN 05:2008/BXD (railing gap > 100mm, height < 1100mm for 9th floor+). Keep such warnings when touching railing code.

## Cache Versioning — required on every change

Two manual version bumps keep the PWA fresh; forgetting them ships stale code to installed users:

1. Changing any JS: bump the `?v=N` query string on **all** `<script src>` tags in `app/index.html` (currently `?v=14`).
2. Changing anything precached: bump `TEN_CACHE` in `app/sw.js` (currently `thosat-pro-v9`).

## Adding a Catalogue Template

1. Create `catalogue/mau/<MA>.json` following `catalogue/schema.json` (required: `ma`, `ten`, `nhom`, `phien_ban`, `dau_vao`, `hang_so`, `chi_tiet`). Formulas in `sl`/`dai`/`bien`/`chia_khoang` use only the expression-language subset above.
2. Add the code to `catalogue/mau/danh-sach.json`.
3. Add the file to the `VO_APP` precache list in `app/sw.js` and bump `TEN_CACHE`.
4. Verify via Node with `CATALOGUE.napMau(...).tinh({...})` (throws descriptive Vietnamese errors on bad input/formulas).
5. Optionally add a diagram case for the template's `nhom`/`ma` in `app/minh-hoa.js`.
