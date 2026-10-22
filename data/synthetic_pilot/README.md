# Synthetic Bilingual Export Document Pilot Dataset (v1.0.0)

This directory contains the synthetic pilot dataset developed for the thesis project:
**"Development of a Web-Based Export Document Management Platform Integrating Bilingual Document AI for Information Extraction and Cross-Document Discrepancy Detection."**

---

## 1. Dataset Overview

* **Dataset Version:** `1.0.0`
* **Total Packages:** 12 shipment packages (`PKG-001` through `PKG-012`).
* **Total Documents:** 24 documents (12 Commercial Invoices, 12 Packing Lists).
* **Languages:** 6 English-primary (`en`), 6 Vietnamese-primary (`vi`).
* **Visual Templates:** 2 layout templates (`classic_standard`, `modern_grid`).
* **Cross-Document Comparisons:** 50 explicit, deterministic ground-truth comparison records.
* **Provisional Partitions:**
  * Train: 7 packages (`PKG-001` to `PKG-007`)
  * Validation: 2 packages (`PKG-008`, `PKG-009`)
  * Test: 3 packages (`PKG-010` to `PKG-012`)

---

## 2. Directory Layout

```text
data/synthetic_pilot/
├── README.md                           # This documentation file
├── manifest.json                       # Master package manifest
├── expected_comparisons.json           # Ground-truth cross-document expected comparison results
├── schema/
│   ├── ground_truth_annotation.schema.json # JSON schema for document annotations
│   ├── manifest.schema.json            # JSON schema for manifest.json
│   └── expected_comparisons.schema.json# JSON schema for cross-document comparisons
├── documents/                          # 24 rendered PDF documents
│   ├── PKG-001_commercial_invoice.pdf
│   ├── PKG-001_packing_list.pdf
│   └── ...
└── annotations/                        # 24 ground-truth JSON annotation files
    ├── PKG-001_commercial_invoice.json
    ├── PKG-001_packing_list.json
    └── ...
```

---

## 3. Ground-Truth Bounding Box Convention

* **Coordinate System:** `[x_min, y_min, x_max, y_max]` in 72 DPI PDF points.
* **Origin:** Top-Left corner `(0, 0)` of page 1.
* **Reference Dimensions:** Standard A4 (`595.28` pt width × `841.89` pt height).
* **Page Indexing:** 1-indexed (`page: 1`).
* **Coordinate Invariant:** `0 <= x_min < x_max <= 595.28` and `0 <= y_min < y_max <= 841.89`.

---

## 4. Scenario Distribution

| Package | Language | Split | Template | Scenario Category | Injected Condition / Verification Target |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `PKG-001` | English | Train | `classic_standard` | Clean | Perfect cross-document agreement (Cashew W240). |
| `PKG-002` | Vietnamese | Train | `modern_grid` | Clean | Hoàn toàn khớp chứng từ (Tiêu đen 500g/l). |
| `PKG-003` | English | Train | `modern_grid` | Discrepancy | `QTY-002`: Invoice 500 Bags vs Packing List 480 Bags. |
| `PKG-004` | Vietnamese | Train | `classic_standard` | Discrepancy | `QTY-002`: Hóa đơn 1.500 Bao vs Phiếu đóng gói 1.450 Bao. |
| `PKG-005` | English | Train | `classic_standard` | Discrepancy | `WT-001`: Gross weight 25,500 KG vs 26,800 KG. |
| `PKG-006` | Vietnamese | Train | `modern_grid` | Discrepancy | `WT-001`: Trọng lượng tịnh 15.000 KG vs 14.200 KG. |
| `PKG-007` | English | Train | `modern_grid` | Discrepancy | `PARTY-001`: Buyer Atlantic Foods vs Consignee Pacific Maritime. |
| `PKG-008` | Vietnamese | Validation | `classic_standard` | Discrepancy | `PARTY-001`: Người bán Cty Sài Gòn vs Người gửi Cty Hoàng Gia. |
| `PKG-009` | English | Validation | `classic_standard` | Discrepancy | `MONEY-001`: Line item 50 MT x $1,650 printed as $72,500 (not $82,500). |
| `PKG-010` | Vietnamese | Test | `modern_grid` | Discrepancy | `MONEY-002`: Tổng cộng 25.000 + 25.000 in thành 60.000 USD. |
| `PKG-011` | Vietnamese | Test | `classic_standard` | Discrepancy | `ID-001`: Hóa đơn ghi ĐH DH-2026-LON-901 vs PĐG ghi DH-2026-LON-999. |
| `PKG-012` | English | Test | `modern_grid` | Benign Variation | Date `2026-10-22` vs `22/10/2026`, casing & decimal comma variations. Normalizes to Match. |

---

## 5. Dataset Regeneration & Validation

### Regenerate Dataset (Deterministic Seed = 42)
```powershell
.\.venv\Scripts\python.exe scripts/generate_pilot_dataset.py
```

### Validate Dataset Integrity
```powershell
.\.venv\Scripts\python.exe scripts/validate_pilot_dataset.py
```

### Run Automated Pytest Test Suite
```powershell
.\.venv\Scripts\pytest.exe backend/tests/test_dataset_validation.py -vv
```
