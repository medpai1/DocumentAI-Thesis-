# Research Dataset Specification: Synthetic Bilingual Export Document Pilot

* **Document Version:** `1.0.0`
* **Date:** 2026-10-22
* **Target Milestone:** Phase 1 (Week 1–4) Baseline Research Pipeline

---

## 1. Research Motivation & Scope

In international export workflows, discrepancies between Commercial Invoices (CI) and Packing Lists (PL) cause severe customs delays, penalties, and cargo rejections. Automating information extraction and discrepancy detection requires:
1. **Document AI Models:** Multilingual extraction of key-value pairs and tabular rows from complex document layouts.
2. **Deterministic Validation Rules:** Cross-document normalization and comparison logic.

Before deploying deep learning models on large datasets (the thesis targets ~300 packages in later phases), this **12-package synthetic pilot** serves as the verifiable ground-truth baseline to:
* Validate the end-to-end data contracts and JSON annotation schemas.
* Calibrate OCR engines (RapidOCR vs. Tesseract) against known character and bounding-box coordinates.
* Establish a deterministic evaluation suite for rule-based discrepancy detection.

---

## 2. Document Types & Bilingual Coverage

The pilot dataset comprises **24 documents across 12 packages**:
* **Commercial Invoice (CI):** Captures commercial terms, invoice number, issue date, buyer/seller, Incoterm, currency, product descriptions, quantities, unit prices, line totals, and total invoice amount.
* **Packing List (PL):** Captures logistics packaging, packing list number, issue date, shipper/consignee, port of loading/discharge, package counts, packaging types, net weights, and gross weights.

### Language Balance
* **English (`en`):** 6 packages (`PKG-001`, `PKG-003`, `PKG-005`, `PKG-007`, `PKG-009`, `PKG-012`).
* **Vietnamese (`vi`):** 6 packages (`PKG-002`, `PKG-004`, `PKG-006`, `PKG-008`, `PKG-010`, `PKG-011`).
* All Vietnamese documents use authentic Unicode diacritics (`ă, â, đ, ê, ô, ơ, ư`) rendered using system TrueType fonts (`ArialUnicode`).

---

## 3. Ground-Truth Bounding Box Coordinate System

Ground-truth bounding boxes are recorded to benchmark OCR token localization and layout-aware models (e.g., LayoutLMv3):

```text
(0, 0) Top-Left -----------------------------> X (width = 595.28 pt)
|
|   +------------------------------------+
|   | [x_min, y_min, x_max, y_max]       |
|   +------------------------------------+
v
Y (height = 841.89 pt)
```

### Conventions:
* **Format:** `[x_min, y_min, x_max, y_max]` in 72 DPI PDF points.
* **Origin:** `(0, 0)` is the **Top-Left** corner of the page.
* **Page Indexing:** 1-indexed (`page: 1`).
* **Dimensions:** Standard A4 page: width = `595.28` pt, height = `841.89` pt.
* **Invariants:**
  * $0.0 \le x_{min} < x_{max} \le 595.28$
  * $0.0 \le y_{min} < y_{max} \le 841.89$

---

## 4. Controlled Discrepancy Scenarios & Rule Catalogue

The pilot implements controlled synthetic test cases to evaluate discrepancy recall ($O3$) and false-alarm rejection:

| Rule ID | Rule Name | Compared Elements | Severity | Injected Packages |
| :--- | :--- | :--- | :--- | :--- |
| `QTY-002` | Invoice vs. Packing List Quantity | CI `line_items.quantity` vs. PL `line_items.quantity` | High | `PKG-003` (EN), `PKG-004` (VI) |
| `WT-001` | Comparable Gross / Net Weight | CI Weights vs. PL `total_gross_weight` / `total_net_weight` | High | `PKG-005` (EN), `PKG-006` (VI) |
| `PARTY-001` | Trade Party Identity Consistency | CI Buyer/Seller vs. PL Consignee/Shipper | Critical | `PKG-007` (EN), `PKG-008` (VI) |
| `MONEY-001` | Line Total Arithmetic Consistency | Qty × Unit Price vs. Line Total | High | `PKG-009` (EN) |
| `MONEY-002` | Invoice Total Sum Consistency | $\sum(\text{Line Totals})$ vs. Total Amount | High | `PKG-010` (VI) |
| `ID-001` | Order / Purchase Order Identifier | CI `order_number` vs. PL `order_number` | Medium | `PKG-011` (VI) |
| Benign | Formatting Normalization | Date conventions (`YYYY-MM-DD` vs `DD/MM/YYYY`), casing, separators | None | `PKG-012` (EN/VI) |

* **Clean Baselines (`PKG-001`, `PKG-002`):** Maintain 100% agreement across all rules to measure false-positive rate.
* **Benign Formatting Variations (`PKG-012`):** Tests that harmless variations (e.g. `2026-10-22` vs `22/10/2026`, decimal commas `10,00` vs `10.00`) normalize to a **Match** without false alarms.

---

## 5. Dataset Splitting & Leakage Prevention Policy

To prevent visual layout and party identity leakage across evaluation partitions:

1. **Package Atomicity:** The Commercial Invoice and Packing List of any package must **never be separated**. Both documents strictly reside in the same partition.
2. **Provisional Pilot Splits:**
   * **Train (7 packages / 14 docs):** `PKG-001` through `PKG-007`.
   * **Validation (2 packages / 4 docs):** `PKG-008`, `PKG-009`.
   * **Test (3 packages / 6 docs):** `PKG-010`, `PKG-011`, `PKG-012`.
3. **Template Family Isolation:** Layout templates (`classic_standard` and `modern_grid`) are distributed evenly across splits to prevent layout overfitting in future ML experiments.

---

## 6. Reproducibility Instructions

### Regenerate Entire Dataset
```powershell
.\.venv\Scripts\python.exe scripts/generate_pilot_dataset.py
```

### Validate Dataset Integrity
```powershell
.\.venv\Scripts\python.exe scripts/validate_pilot_dataset.py
```

### Execute Automated Test Suite
```powershell
.\.venv\Scripts\pytest.exe backend/tests/test_dataset_validation.py -vv
```

---

## 7. Known Limitations

* **Single-Page Scope:** The pilot currently generates 1-page documents, which represents ~85% of standard export invoices and packing lists. Multi-page table continuations will be addressed in Phase 2 scaling.
* **Synthetic Simplicity:** Generated documents feature clean digital typography without physical skew, stains, or degraded scans. Scan augmentation (noise, skew, shadows) will be applied during Phase 1 Task 5 OCR benchmarking.
