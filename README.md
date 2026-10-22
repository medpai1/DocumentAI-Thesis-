# Export Document Management Platform with Document AI

> **Graduation Thesis Project**  
> **Vietnamese Title:** Phát triển nền tảng Web quản lý hồ sơ xuất khẩu tích hợp Document AI song ngữ để trích xuất thông tin và phát hiện sai khác giữa các chứng từ  
> **Working Title:** Development of a Web-Based Export Document Management Platform Integrating Bilingual Document AI for Information Extraction and Cross-Document Discrepancy Detection

---

## Overview

This repository contains the source code, research benchmarks, datasets, and documentation for a web-based export document management platform. The system assists export operations by organizing shipments, tracking immutable document versions, extracting structured data from bilingual (English and Vietnamese) Commercial Invoices and Packing Lists, and performing cross-document discrepancy detection.

---

## Architecture at a Glance

* **Frontend:** React + TypeScript + Vite (planned for Phase 2).
* **Backend API:** Python + FastAPI (modular monolith architecture).
* **Database:** PostgreSQL 17 (relational core data: orders, shipments, documents, versions, discrepancies).
* **File Storage:** Local filesystem storage abstraction (extensible to S3-compatible storage).
* **Document AI Pipeline:**
  * Ingestion & OCR: RapidOCR (ONNX PP-OCRv4) and Tesseract baseline.
  * Extraction: Rule-based baseline followed by pretrained layout-aware models (e.g., LayoutLMv3).
  * Validation: Normalization rules for quantities, dates, weights, parties, and money.

---

## Documentation Links

* **[Master Plan](docs/graduation_thesis_master_plan.md):** The comprehensive thesis blueprint, domain model, research questions, and 16-week roadmap.
* **[Phase 1 Implementation Plan](docs/implementation_plan.md):** The concrete 7-task roadmap towards the Week 5–6 working prototype.
* **[Local Setup Guide](docs/setup_guide.md):** PowerShell instructions for setting up Python 3.11, PostgreSQL, and development dependencies on Windows.
* **Architecture Decision Records (ADRs):**
  * [ADR-001: Native Windows Development with PostgreSQL 17](docs/adr/ADR-001-native-windows-environment.md)
  * [ADR-002: Python 3.11 Runtime for Backend and AI](docs/adr/ADR-002-python-runtime-version.md)
  * [ADR-003: Local Filesystem Storage with Abstract Service](docs/adr/ADR-003-local-filesystem-storage.md)
  * [ADR-004: RapidOCR and Tesseract for Initial Bilingual OCR Pilot](docs/adr/ADR-004-ocr-pilot-selection.md)

---

## Quickstart (Development Setup)

Refer to [docs/setup_guide.md](docs/setup_guide.md) for full setup instructions.

```powershell
# 1. Verify Python 3.11 is installed
py -3.11 --version

# 2. Create and activate virtual environment
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install minimal backend dependencies
pip install -r backend/requirements-dev.txt

# 4. Copy environment configuration
Copy-Item .env.example .env

# 5. Run tests
pytest backend/tests/test_health.py
```