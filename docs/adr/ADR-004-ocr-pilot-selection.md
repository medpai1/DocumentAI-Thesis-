# ADR-004: RapidOCR and Tesseract for Initial Bilingual OCR Pilot

* **Status:** Accepted
* **Date:** 2026-10-22
* **Deciders:** User, Antigravity Agent

## Context

The master plan requires extracting text, page coordinates (bounding boxes), and OCR confidence from English and Vietnamese commercial documents (Commercial Invoices and Packing Lists). The master plan proposed benchmarking PaddleOCR and/or Tesseract on representative samples before final selection.

On Windows 11:
1. Native Tesseract requires installing the Windows binary installer and downloading `vie.traineddata` for Vietnamese support.
2. Full PaddleOCR / PaddlePaddle with GPU acceleration on the NVIDIA RTX 5060 (Blackwell architecture) requires specific CUDA builds that may encounter compatibility friction.
3. RapidOCR is an ONNX-based, self-contained Python implementation of the PP-OCR models that runs out-of-the-box on CPU and GPU without requiring complex native system-level dependencies.

## Decision

Select **RapidOCR** and **Tesseract** as the primary candidates for the Phase 1 OCR research pilot benchmark. RapidOCR will serve as the primary ONNX/deep-learning baseline, and Tesseract (with English and Vietnamese traineddata) will serve as the traditional OCR comparison baseline. Additional engines (e.g., PyMuPDF digital text extractor, full PaddleOCR) will be included only if justified by pilot benchmark results.

## Reasons and Trade-offs

### Reasons
* **Portability and Ease of Setup:** RapidOCR runs via `onnxruntime` wheels on Python without installing external native system installers.
* **Bilingual Support:** RapidOCR uses PP-OCRv4 models which have demonstrated strong performance on multilingual and Asian text, while Tesseract provides an established academic baseline with `vie` and `eng`.
* **Standardized Coordinate Output:** Both can output normalized bounding boxes `[ymin, xmin, ymax, xmax]` and confidence scores required by the thesis schema.

### Trade-offs
* Tesseract still requires the external Windows installer and language packs when evaluated.
* Deep learning model fine-tuning or custom training on RapidOCR requires separate training pipelines if default ONNX models need domain adaptation.

## Consequences

* The pilot benchmark task (P1-06) will evaluate CER (Character Error Rate), word/field bounding box accuracy, and inference latency on 10 synthetic bilingual invoice and packing list samples.
* Results will be compiled into an empirical evaluation report before freezing the Stage 1 OCR component.

## Verification / Evidence

* Inspection of host system confirmed `tesseract` is currently not in PATH.
* Python packages for RapidOCR (`rapidocr-onnxruntime`) are available on PyPI for Python 3.11.

## Conditions for Revisit

* If RapidOCR exhibits poor accuracy on Vietnamese diacritics or non-standard invoice fonts during the pilot benchmark.
* If a dedicated LayoutLMv3 or end-to-end multimodal model directly subsumes separate OCR tokenization.
