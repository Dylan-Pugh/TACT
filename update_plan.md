# Update Plan — Project TACT

> **Scope:** Fix inconsistencies, standardize architecture, add tests. No new functionality.
> **Approach:** Backend first, then frontend. Tests are the top priority to verify migrations don't break functionality.
> **Decisions:** Pydantic + JSON (not YAML), pytest + Vitest, TypeScript migration included, defer controller split to a separate PR.

---

## Stage 1: Backend — Input Validation & Error Handling

**Goal:** Eliminate all TODOs, standardize error responses, add consistent validation.

| # | File | Issue | Action |
|---|------|-------|--------|
| 1 | `tact/API/tact_api.py:298` | TODO: validate file extension | Add `.csv` / `.nc` validation in upload endpoint |
| 2 | `tact/API/tact_api.py:397` | TODO: validate input | Add `forecastConfig` existence check in `/forecast` endpoint |
| 3 | `tact/API/tact_api.py:444` | TODO: handle `.nc` files | Add NetCDF file support or return explicit error |
| 18 | `tact/API/tact_api.py` (multiple) | TODO: validate input (8 instances across config update endpoints) | Add input validation to `/config/parser`, `/config/transform`, `/config/forecast`, `/config/qa` |
| 19 | `tact/control/controller.py` | `generate_preview()` returns `False` for errors — others raise exceptions (violates `AGENTS.md`) | Standardize: catch exceptions internally, log them, and return `False` or `None` to the API layer |
| 20 | `tact/control/controller.py` | `update_settings()` returns `bool` without error details | Add error message to response or log it explicitly |
| 21 | `tact/util/constants.py:11` | TODO: Consolidate config paths into a class | Create `ConfigType` enum/class for type safety |

### Tests for Stage 1

| # | File | What to test |
|---|------|-------------|
| 22 | `tact/testing/test_api_errors.py` | Error paths: missing files, invalid config, bad inputs, missing keys |
| 23 | `tact/testing/test_api_upload.py` | Upload endpoints with temp files (parser, transform, lookup types) |

---

## Stage 2: Config Schema Validation (Pydantic)

**Goal:** Replace raw JSON reads/writes with typed config objects. Pydantic + JSON format (no YAML).

### Setup

| # | File | Action |
|---|------|--------|
| 24 | `tact/config/schemas.py` | Create new file with Pydantic models: `ParserConfig`, `TransformConfig` (including `lookup` fields), `ForecastConfig`, `QAConfig` |
| 25 | `tact/config/loader.py` | Create new file: `load_config(type)` returns typed object, `save_config(type, data)` validates then writes JSON |
| 26 | `tact/config/defaults.py` | Create new file: default config values (replaces hardcoded defaults scattered across controller) |

### Migration

| # | File | Action |
|---|------|--------|
| 27 | `tact/control/controller.py` | Update `update_settings()` to use Pydantic models — config patches validated before writing |
| 28 | `tact/control/controller.py` | Update `get_data()` to return typed config objects via loader |
| 29 | `tact/API/tact_api.py` | Update all config endpoints to use loader instead of direct JSON file reads/writes |

### Tests for Stage 2

| # | File | What to test |
|---|------|-------------|
| 30 | `tact/testing/test_config_schemas.py` | Pydantic validation: valid/invalid inputs, missing required fields, type coercion, extra fields rejected |
| 31 | `tact/testing/test_config_loader.py` | Load/save roundtrip, missing file handling, invalid JSON handling, default values |

---

## Stage 3: Backend — Controller Hardening

**Goal:** Fix code smells, extract magic numbers, add tests for controller operations.

| # | File | Issue | Action |
|---|------|-------|--------|
| 32 | `tact/control/controller.py` | `fix_times` magic number `15` for time columns | Extract to named constant |
| 33 | `tact/control/controller.py` | `generate_preview()` magic number `10` for nrows | Extract to named constant |
| 34 | `tact/control/controller.py` | `normalize_headers` hardcodes `['mean', 'count']` | Move to config/defaults |
| 35 | `tact/control/controller.py` | `drop_columns` hardcodes index `0` | Make configurable or document rationale |
| 36 | `tact/control/controller.py` | ~690 lines, multiple responsibilities | Defer split to separate PR (per project decision) |
| 37 | `tact/control/controller.py` | `merge_taxa_names()` hardcoded `worms_lut.csv` path | Already completed (uses `constants.WORMS_LOOKUP_PATH`) |
| 38 | `tact/util/csv_utils.py:33` | TODO: Add check for empty data | Add empty DataFrame validation |
| 39 | `tact/util/csv_utils.py:135` | TODO: Add check for empty data | Add empty DataFrame validation |
| 40 | `tact/util/csv_utils.py` | `write()` and `write_concat()` duplicate file existence logic | Extract shared `ensure_output_dir()` helper |

### Tests for Stage 3

| # | File | What to test |
|---|------|-------------|
| 41 | `tact/testing/test_controller_cleaning.py` | `drop_empty`, `drop_duplicates`, `normalize_headers`, `fix_times`, `header_values_replace`, `row_values_replace` |
| 42 | `tact/testing/test_controller_transform.py` | `enumerate_columns`, `pivot_columns`, `combine_rows`, `merge_lookup` |
| 43 | `tact/testing/test_controller_lookup.py` | `merge_lookup_data`, `update_lookup_config` |
| 44 | `tact/testing/test_csv_utils.py` | `write`, `write_concat`, `concat`, `combine_rows`, `drop_columns` |

---

## Stage 4: Backend — API Layer Standardization

**Goal:** Consistent response format, no raw data in API layer, proper error handling.

| # | Action |
|---|--------|
| 45 | Standardize all API responses to `{ success: bool, data?: any, message?: str }` format (MUST update frontend components simultaneously) |
| 46 | Create `tact/API/api_utils.py` with error response helpers (`error_response()`, `success_response()`) |
| 47 | Add request validation for common patterns (file uploads, config patches) |
| 48 | Remove `# type: ignore` comments and add proper type hints where feasible |

---

## Stage 5: Frontend — Shared Code & TypeScript Migration

**Goal:** Eliminate duplication, add type safety, add tests, migrate to TypeScript.

### Shared Hooks & Utilities

| # | File | Issue | Action |
|---|------|-------|--------|
| 49 | All pages | Duplicate data loading pattern (`fetchJson('/config/parser')`, `fetchJson('/data?nrows=10')`) | Create `useTactData()` hook for shared data fetching + config management |
| 50 | All pages | Duplicate error/message state pattern (`msg: { text, type }`) | Create `useMessage()` hook |
| 51 | `src/utils/fetchJson.js` | Manual NaN/Infinity sanitization masks backend issue | Fix in backend (Stage 2) + simplify `fetchJson` to standard wrapper |
| 52 | `src/components/ConfigForm.jsx:68` | Hardcoded test path `'tact/testing/testData/TACT_test.csv'` | Move to env var or config |

### TypeScript Migration

| # | File | Action |
|---|------|--------|
| 53 | `tact/UI/react/src/types/` | Create new directory with TS types: `ConfigTypes.ts`, `ApiTypes.ts`, `DataTypes.ts` |
| 54 | `tact/UI/react/src/utils/` | Convert `fetchJson.js` → `fetchJson.ts`, `exportToCsv.js` → `exportToCsv.ts` |
| 55 | `tact/UI/react/src/hooks/` | Create new directory with `useTactData.ts`, `useMessage.ts` |
| 56 | `tact/UI/react/src/components/` | Convert each component to `.tsx` incrementally (start with smaller components: `DataEditor`, `MultiSelect`, then pages) |
| 57 | `tact/UI/react/tsconfig.json` | Create TypeScript config |
| 58 | `tact/UI/react/package.json` | Add TypeScript dev dependency, update build scripts |

### Tests for Stage 5

| # | File | What to test |
|---|------|-------------|
| 59 | `tact/UI/react/tests/utils/fetchJson.test.ts` | Response parsing, error handling |
| 60 | `tact/UI/react/tests/utils/exportToCsv.test.ts` | CSV escaping, special characters, null handling |
| 61 | `tact/UI/react/tests/components/DataEditor.test.tsx` | Add/remove rows, key changes for dict mode, array mode |
| 62 | `tact/UI/react/tests/components/MultiSelect.test.tsx` | Select/remove/clear/selectAll behavior |
| 63 | `tact/UI/react/tests/hooks/useTactData.test.ts` | Data fetching, config sync, error states |

---

## Stage 6: Frontend — Component Consolidation

**Goal:** Reduce component sizes, improve maintainability, consistent patterns.

| # | File | Issue | Action |
|---|------|-------|--------|
| 64 | All components | Inline styles throughout | Extract to CSS modules or style constants |
| 65 | `src/components/` | Create `PageLayout.tsx` — shared page shell (header, message display, dataset preview table) |
| 66 | `src/components/` | Create `ConfigSection.tsx` — shared form section for config editing |
| 67 | `src/components/CleanPage.tsx` (378 lines) | Extract settings form to `CleaningSettings.tsx` |
| 68 | `src/components/TransformPage.tsx` (677 lines) | Split into sub-components: `FlipSection.tsx`, `CombineSection.tsx`, `LookupSection.tsx` |
| 69 | `src/components/ForecastPage.tsx` (558 lines) | Extract chart data processing to `useForecastChart()` hook |
| 70 | `src/components/BioDataUtilsPage.tsx` (302 lines) | Extract taxonomic matching UI to `TaxonMatchPanel.tsx` |
| 71 | `tact/UI/react/.eslintrc` | Add rules: max function/component length, no hardcoded paths |
| 72 | `tact/UI/react/package.json` | Add `npm test` script with Vitest |

---

## Summary

| Stage | Items | Category | Effort |
|-------|-------|----------|--------|
| 1 | #1–#23 | Backend validation + tests | Medium |
| 2 | #24–#31 | Config schema (Pydantic) + tests | Medium-High |
| 3 | #32–#44 | Controller hardening + tests | Medium |
| 4 | #45–#48 | API layer standardization | Low-Medium |
| 5 | #49–#63 | Frontend shared code + TypeScript migration + tests | Medium-High |
| 6 | #64–#72 | Frontend component consolidation | Medium |
| **Total** | **72 action items across 6 stages** | | |

---

## Execution Order

1. **Stage 1** — Fix validation TODOs, add `test_api_errors.py` and `test_api_upload.py`
2. **Stage 2** — Create Pydantic schemas, migrate controller/API to use loader
3. **Stage 3** — Fix code smells in controller, add all controller tests
4. **Stage 4** — Standardize API responses
5. **Stage 5** — Set up TypeScript, create shared hooks, convert utilities + small components, add frontend tests
6. **Stage 6** — Refactor large page components, add ESLint rules

Each stage should be committed separately so tests verify nothing breaks between stages.
