# ADR-002: Python 3.11 Runtime for Backend and Document AI Worker

* **Status:** Accepted
* **Date:** 2026-10-22
* **Deciders:** User, Antigravity Agent

## Context

The host system currently has Python 3.13.2 installed as the global Python runtime. However, the project's technical scope includes Document AI components (OCR engines like PaddleOCR, RapidOCR, PyTorch, torchvision, HuggingFace Transformers, and LayoutLMv3).
As of late 2024 / early 2025, major deep learning libraries and compiled C-extensions either lack official pre-built wheels for Python 3.13 on Windows or experience severe installation and runtime instability.

## Decision

Standardize on **Python 3.11** for the backend and AI worker virtual environment (`.venv`). Python 3.13 will not be used for this project's virtual environment.

## Reasons and Trade-offs

### Reasons
* **Broadest library compatibility:** Python 3.11 has full, mature pre-compiled binary wheel support across PyTorch, ONNX Runtime, OpenCV, PaddlePaddle, and HuggingFace ecosystems.
* **Avoids complex local C++ compilation:** Prevents failures requiring Visual Studio C++ Build Tools on Windows for packages without 3.13 wheels.
* **Modern language features:** Supports modern typing, exception groups, and high performance compared to older Python versions.

### Trade-offs
* Requires installing Python 3.11 alongside the existing Python 3.13 installation on the host system.

## Consequences

* The project virtual environment must be initialized with `py -3.11 -m venv .venv`.
* All dependencies in `backend/pyproject.toml` and `backend/requirements.txt` are constrained to `requires-python = ">=3.11,<3.13"`.

## Verification / Evidence

* Inspected system runtimes: `py -0p` showed only `Python 3.13` at `C:\Users\Daylamaytinh\Python\Python313\python.exe`.
* Checked for 3.11: `py -3.11` confirmed not installed. `winget search --id Python.Python.3.11` confirmed `Python.Python.3.11` (version 3.11.9) is available for direct installation.

## Conditions for Revisit

* Once all required Document AI frameworks (PyTorch, ONNX, OCR libraries) officially release stable Windows wheels for Python 3.12 or 3.13, upgrading may be evaluated.
