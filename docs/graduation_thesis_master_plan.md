# Graduation Thesis Project Master Plan

**Project:** Export Document Management Platform with Document AI\
**Working title:** Development of a Web-Based Export Document Management
Platform Integrating Bilingual Document AI for Information Extraction
and Cross-Document Discrepancy Detection\
**Vietnamese title:** Phát triển nền tảng Web quản lý hồ sơ xuất khẩu
tích hợp Document AI song ngữ để trích xuất thông tin và phát hiện sai
khác giữa các chứng từ\
**Document type:** Project source of truth\
**Status:** Initial planning baseline --- update as decisions are
approved\
**Last updated:** 2026-10-22

------------------------------------------------------------------------

## 1. Purpose of This Document

This document preserves the thesis direction, scope, architecture,
research approach, implementation roadmap, and collaboration protocol.
It is intended to restore context when an AI coding agent loses
conversation history.

This is a planning baseline, not evidence that any feature has already
been implemented. Mark implementation status only after inspecting the
repository and relevant test results.

### How to use it in Antigravity IDE

1.  Read this document before proposing or implementing a feature.
2.  Inspect the actual repository before assuming a technology, file,
    endpoint, or feature exists.
3.  Follow approved architecture and requirements. Do not silently
    replace decisions.
4.  If a change is necessary, explain the reason, alternatives, impact,
    and tests; wait for approval before implementing it.
5.  Update task status and project notes after implementation and
    verification.
6.  Never report tests as passing unless they were actually run and
    their results were inspected.

## 2. Project Vision

Build a web platform that helps export businesses organize export
orders, shipments, document versions, review workflows, and preparation
checklists. Integrate a bilingual English/Vietnamese Document AI
pipeline to extract structured information and detect inconsistencies
across documents.

The platform is a decision-support and document-preparation tool. It
does **not** replace a customs system, legal advice, or the responsible
human reviewer.

### Core workflow

**Create order → Create shipment → Upload documents → Extract fields →
Normalize values → Detect discrepancies → Review source evidence →
Correct or resolve → Approve → Prepare a simulated declaration
checklist.**

### Main objectives

-   **O1 --- Application:** Build a functional export-document
    management workflow.
-   **O2 --- Extraction:** Extract fields and line items from English
    and Vietnamese documents using a pretrained document model and OCR.
-   **O3 --- Validation:** Combine normalization and explicit rules to
    identify missing, inconsistent, or suspicious information across
    documents.
-   **O4 --- Evaluation:** Measure extraction quality,
    discrepancy-detection performance, generalization to unseen
    templates, and the effect of AI-assisted review.

### Research questions

-   **RQ1:** How accurately can the selected pretrained document model
    extract fields from English and Vietnamese export documents?
-   **RQ2:** How much does normalization and rule-based validation
    improve discrepancy detection?
-   **RQ3:** How well does the system generalize to document templates
    not seen during development?
-   **RQ4:** Does AI-assisted review reduce review time without
    increasing missed discrepancies?

## 3. Agreed Direction and Constraints

### Current planning decisions

-   Document languages: **English and Vietnamese**.
-   AI approach: **Pretrained document model plus rules**.
-   Project priority: **Balanced full-stack application and measurable
    AI research**.
-   Initial document types: **Commercial invoice and packing list**.
-   Optional extension: Bill of lading, only if the core system and
    evaluation are on track.
-   Architecture direction: **Modular monolith for the business
    application plus a separately executable Python AI worker**.
-   Validation: Human review remains responsible for corrections and
    approvals.
-   Evaluation: Compare a baseline with the selected pretrained-model
    pipeline; evaluate by language and unseen template where possible.
-   Scope: Customs submission is simulated; no real customs-system
    integration in the MVP.

### Non-negotiable safeguards

1.  Never invent extracted values or silently replace confirmed business
    data.
2.  Every extracted field should retain its source document version and,
    when available, page and bounding-box coordinates.
3.  Preserve original files and document versions. A correction or
    reissue creates a new version rather than overwriting issued
    evidence.
4.  A discrepancy must identify the rule, compared values, normalization
    applied, and supporting evidence.
5.  Do not let an LLM make final decisions about HS classification,
    origin, customs valuation, licensing, or legal compliance.
6.  Do not claim a model is accurate without evaluation on labeled
    held-out data.
7.  Do not leak shipment or template variants across training,
    validation, and test partitions.
8.  Enforce authentication, authorization, and file access in the
    backend.
9.  Do not expand the MVP without documenting the impact on schedule and
    research goals.
10. Do not make unapproved changes, commits, pushes, or branches as part
    of an agent's autonomous work. Ask first when the workflow requires
    approval.

## 4. Proposed Technology Architecture

These are proposed choices and must be checked against the actual
repository before implementation.

  -----------------------------------------------------------------------
  Layer                   Proposed technology     Responsibility
  ----------------------- ----------------------- -----------------------
  Frontend                React + TypeScript +    Dashboard, shipment
                          Vite                    workspace, document
                                                  viewer, review UI

  Backend API             Python + FastAPI        Authentication,
                                                  permissions, business
                                                  workflows, audit

  Database                PostgreSQL              Orders, shipments,
                                                  document metadata,
                                                  extraction results,
                                                  discrepancies

  File storage            S3-compatible storage;  Original documents,
                          local storage for       previews, versions
                          development if useful   

  OCR                     Benchmark PaddleOCR     Text, page coordinates,
                          and/or Tesseract on     OCR confidence
                          representative samples  

  Document model          Evaluate a pretrained   Structured field
                          layout-aware model such extraction
                          as LayoutLMv3 or        
                          another suitable        
                          candidate               

  Validation              Python normalization    Cross-document
                          and rule modules        comparisons

  AI processing           Separate Python worker  OCR, inference,
                                                  extraction, validation,
                                                  evaluation

  Tests                   Pytest plus API and     Unit, integration,
                          frontend tests          regression, workflow
                                                  tests

  Initial deployment      Docker Compose          Reproducible local
                                                  environment
  -----------------------------------------------------------------------

Do not assume a model checkpoint or OCR engine is suitable merely
because it supports multiple languages in general. Run a pilot benchmark
on representative English and Vietnamese commercial documents before
final selection.

Start with a modular monolith. Introduce a queue only when actual
processing needs justify it.

## 5. High-Level Architecture

1.  **React frontend** communicates with the FastAPI application.
2.  **FastAPI** enforces authorization and owns business workflows.
3.  **PostgreSQL** stores structured records and references to file
    storage.
4.  **File storage** holds original documents and immutable versions.
5.  **AI worker** processes an exact document version and writes
    extraction candidates and validation results.
6.  **Review interface** displays evidence, permits corrections, and
    records human decisions.
7.  AI processing must not silently overwrite confirmed business data.

### Suggested processing lifecycle

`Uploaded → Queued → Processing → Review required → Confirmed`

Also support failure and recovery states such as `Failed`, `Cancelled`,
and `Superseded`, as appropriate.

Jobs should have unique IDs. Retrying a job must not create duplicate
versions or duplicate discrepancy cases.

## 6. Core Domain Model

  -----------------------------------------------------------------------
  Entity                              Main purpose
  ----------------------------------- -----------------------------------
  `users`                             User identities and account status

  `roles` / `user_roles`              Authorization roles

  `parties`                           Buyers, sellers, shippers,
                                      consignees, and other parties

  `products`                          SKU, description, unit, reference
                                      weights, optional HS reference

  `orders`                            Order number, buyer, seller,
                                      currency, Incoterm, status

  `order_items`                       Product, quantity, unit price, line
                                      total

  `shipments`                         Shipment identity, linked orders,
                                      route, dates, status

  `shipment_items`                    Products and shipment-specific
                                      quantities/details

  `documents`                         Document type, shipment, current
                                      version, workflow status

  `document_versions`                 Version number, file key, hash,
                                      uploader, timestamp

  `extraction_jobs`                   Model/version, processing state,
                                      timestamps, error information

  `extracted_fields`                  Field key, raw and normalized
                                      values, confidence, source location

  `extracted_line_items`              Extracted table rows and source
                                      locations

  `discrepancy_cases`                 Rule, compared fields, severity,
                                      explanation, resolution state

  `discrepancy_evidence`              References to source values and
                                      document versions

  `review_actions`                    Corrections, resolution decisions,
                                      reviewer, timestamp

  `audit_logs`                        Actor, action, affected entity,
                                      timestamp, before/after summary
  -----------------------------------------------------------------------

### Key relationships

-   One order has many order items.
-   An order can be split across multiple shipments.
-   One shipment has multiple shipment items and documents.
-   One document has many immutable versions.
-   A document version can have multiple extraction jobs.
-   An extraction job produces many fields and line items.
-   A discrepancy may reference fields from multiple documents.
-   A discrepancy can have multiple review actions.

Use relational tables for core business data. Use JSON only where
flexible model-specific metadata is genuinely useful.

### Essential business rules

-   Issued document versions are immutable; corrections create a new
    version.
-   Extraction results reference the exact version processed.
-   Discrepancies record rule IDs and source evidence.
-   Corrections preserve original AI output and review history.
-   Approval requires explicit permission and a valid workflow
    transition.
-   Blocking unresolved discrepancies or missing required documents
    prevent readiness unless an authorized exception is recorded.
-   Server-side access checks protect shipment records and files.
-   Audit records should be append-only at the application level where
    practical.

## 7. AI Pipeline

### Stage 1 --- Ingestion and OCR

-   Validate file type, size, page count, and integrity.
-   Extract embedded text from digital PDFs when reliable.
-   Render and OCR scanned pages.
-   Preserve page numbers, word/region coordinates, and OCR confidence.
-   Classify documents as commercial invoice, packing list, or
    unsupported type.

### Stage 2 --- Structured extraction

Commercial invoice candidate fields: - Invoice number and date - Seller
and buyer - Currency, Incoterm, payment terms - Product descriptions,
quantities, unit prices, line totals - Invoice total

Packing list candidate fields: - Packing-list number and date -
Seller/shipper and buyer/consignee - Product descriptions and
quantities - Package count - Net and gross weight - Dimensions -
Container and seal identifiers where present

Not every field exists on every document. Represent states such as
`present`, `missing`, `not_applicable`, and `unreadable` distinctly.

### Stage 3 --- Normalization

Normalize: - Dates, with explicit date conventions - Decimal and
thousands separators - Currency and amounts - Units such as kg, g,
metric tonnes, and pieces - Names, abbreviations, whitespace,
punctuation, and case - Product and container identifiers -
English/Vietnamese field labels mapped to canonical internal keys

Do not collapse semantically different fields such as quantity, package
count, net weight, and gross weight.

### Stage 4 --- Rule-based discrepancy detection

Initial rules: - `QTY-001`: order quantity vs invoice quantity -
`QTY-002`: invoice quantity vs packing-list quantity - `WT-001`:
comparable gross-weight values - `PARTY-001`: seller/buyer identity
consistency - `DATE-001`: invalid or implausible date sequence -
`MONEY-001`: quantity × unit price vs line total - `MONEY-002`: sum of
line totals vs invoice total - `DOC-001`: required document missing -
`ID-001`: container/shipment identifier inconsistency

Account for partial shipments, legitimate unit conversions, rounding,
multiple currencies, and fields that are not comparable. Each result
should include rule ID, compared values, normalization, severity,
explanation, and evidence.

### Stage 5 --- Human review

The user can inspect the original document, see source regions
highlighted, correct or mark fields unreadable, compare related
documents, resolve discrepancies with a reason, approve a version, and
inspect the history.

AI confidence is not proof of correctness. Evaluate it empirically and
record reviewer corrections.

## 8. Dataset Strategy

### Initial target

Target approximately **300 synthetic shipment packages**, each with a
commercial invoice and packing list, yielding approximately 600 document
files before additional variants. This is an initial engineering target,
not a guarantee of statistical sufficiency.

A possible starting split: - Training: 180 packages - Validation: 60
packages - Test: 60 packages

Target roughly balanced English-primary and Vietnamese-primary packages.
Include mixed-language documents if feasible and relevant.

### Dataset construction

1.  Define a canonical shipment schema with correct parties, products,
    quantities, weights, dates, prices, and identifiers.
2.  Generate clean documents using several layouts/templates.
3.  Inject controlled discrepancies: quantities, weights, dates,
    identifiers, totals, missing fields, and missing documents.
4.  Include harmless formatting differences to test false-positive
    behavior.
5.  Store ground-truth field values and discrepancy labels independently
    of model outputs.
6.  Independently annotate a meaningful subset twice and reconcile
    disagreements.
7.  Split by shipment and template family to prevent leakage from
    variants or near-duplicate templates.

### Example field annotation

``` json
{
  "document_id": "INV-0001",
  "document_type": "commercial_invoice",
  "language": "en",
  "field_key": "invoice_number",
  "raw_value": "INV-2026-001",
  "normalized_value": "INV-2026-001",
  "page": 1,
  "bbox": [110, 90, 300, 125],
  "annotation_status": "verified"
}
```

Document and standardize the bounding-box coordinate system.

FUNSD and XFUND may be supplementary resources for
document-understanding experiments, but they are not direct substitutes
for a labeled commercial invoice/packing-list dataset.

For real documents, obtain permission and redact sensitive information.
Record source, language, template family, scan quality, annotation
version, and whether the sample is synthetic or real.

## 9. Evaluation Methodology

### Experiment A --- OCR and extraction

-   Compare a rule/template baseline with the pretrained-model pipeline.
-   Evaluate English and Vietnamese separately.
-   Report by field type and document type.

### Experiment B --- Normalization and discrepancy detection

-   Compare rules on raw values with the same rules after normalization.
-   Keep the underlying rule set fixed when comparing extraction
    methods.
-   Report results per discrepancy category.

### Experiment C --- Generalization

-   Test on unseen document templates.
-   Report performance by language, document type, template family, and
    synthetic/real origin when available.

### Experiment D --- Workflow effectiveness

-   Compare manual review with AI-assisted review.
-   Measure review time, seeded discrepancies detected, missed
    discrepancies, false alarms, and correction effort.
-   Counterbalance task order where possible and document reviewer
    experience.

### Metrics

-   Document classification accuracy
-   Field-level precision, recall, F1, and exact match
-   Character error rate (CER) for OCR
-   Table-cell exact match or F1
-   Discrepancy precision, recall, and F1
-   False-negative rate
-   Median review time and correction rate
-   Confidence intervals where practical

For numeric values, report exact match and a separately defined
tolerance-based comparison where legitimate rounding or unit conversion
applies. Do not use tolerance-based scoring for identifiers or currency
codes.

### Provisional success targets

These are engineering goals, not guaranteed results: - At least 90%
exact match on selected high-priority fields. - At least 90% discrepancy
recall on predefined synthetic test cases. - Measurable discrepancy F1
improvement over the raw-value rules baseline. - Lower median review
time without an unacceptable increase in missed discrepancies.

Review targets after a pilot, then freeze them before evaluating the
final test set. Never tune model choices or thresholds against the final
test set.

## 10. Suggested Repository Organization

Adapt this to the existing repository rather than creating duplicate
structures.

``` text
backend/
├── app/
│   ├── api/
│   ├── domain/
│   │   ├── orders/
│   │   ├── shipments/
│   │   ├── documents/
│   │   └── compliance/
│   ├── services/
│   ├── repositories/
│   ├── schemas/
│   └── main.py
├── ai_worker/
│   ├── ingestion/
│   ├── ocr/
│   ├── classification/
│   ├── extraction/
│   ├── normalization/
│   ├── validation/
│   └── evaluation/
├── tests/
└── migrations/
```

### Essential API candidates

-   `POST /api/orders`
-   `POST /api/shipments`
-   `GET /api/shipments/{id}`
-   `POST /api/shipments/{id}/documents`
-   `GET /api/documents/{id}/versions`
-   `POST /api/document-versions/{id}/extractions`
-   `GET /api/extraction-jobs/{id}`
-   `GET /api/shipments/{id}/discrepancies`
-   `POST /api/discrepancies/{id}/resolve`
-   `POST /api/documents/{id}/approve`
-   `GET /api/shipments/{id}/audit`

These are proposed contracts, not implemented endpoints.

## 11. Sixteen-Week Roadmap

  -----------------------------------------------------------------------
  Weeks                   Focus                   Expected deliverable
  ----------------------- ----------------------- -----------------------
  1--2                    Scope, architecture,    Requirements, BPMN,
                          pilot dataset           ERD, annotations,
                                                  sample documents

  3--4                    OCR and baseline        OCR benchmark, baseline
                          experiments             extractor, evaluation
                                                  script

  5--6                    Backend and database    Auth, roles, products,
                                                  parties, orders,
                                                  shipments, document
                                                  versioning

  7--8                    Frontend workflow       Dashboard, shipment
                                                  workspace, document
                                                  viewer, approvals

  9--10                   Pretrained model        Worker, structured
                          integration             fields, source
                                                  evidence, confidence,
                                                  error handling

  11--12                  Validation and review   Normalization, rules,
                                                  discrepancy evidence,
                                                  resolution and audit

  13--14                  Evaluation and          Held-out experiments,
                          hardening               generalization results,
                                                  security and regression
                                                  tests

  15--16                  Thesis and defense      Final report, diagrams,
                                                  limitations, demo,
                                                  defense slides
  -----------------------------------------------------------------------

### Milestones

-   **End of Week 4:** OCR and baseline run on representative bilingual
    documents.
-   **End of Week 8:** Users can create shipments and manage document
    versions.
-   **End of Week 12:** Extraction, discrepancy review, evidence, and
    audit work end-to-end.
-   **End of Week 14:** Test set is frozen, experiments are completed,
    and results are reproducible.
-   **End of Week 16:** Thesis and defense demonstration are ready.

If the deadline becomes shorter, reduce peripheral workflow scope before
sacrificing evaluation.

## 12. Thesis Report Structure

1.  **Chapter 1 --- Introduction:** Problem, objectives, scope, research
    questions, contributions.
2.  **Chapter 2 --- Background and Related Work:** Export documentation,
    OCR, document understanding, information extraction, record linkage,
    validation.
3.  **Chapter 3 --- Requirements and System Design:** Stakeholders, use
    cases, BPMN, ERD, architecture, APIs, security, state machines.
4.  **Chapter 4 --- Implementation:** Web platform, versioning, AI
    pipeline, normalization, validation, human review.
5.  **Chapter 5 --- Experiments and Results:** Dataset, protocol,
    extraction results, discrepancy metrics, language/template
    comparisons, workflow evaluation.
6.  **Chapter 6 --- Conclusion and Future Work:** Achievements,
    limitations, implications, and extensions.

## 13. Collaboration Protocol: User, Antigravity, and ChatGPT

### ChatGPT's role

-   Reviewer of plans, architecture, code changes, tests, and research
    methodology.
-   Creator of scoped, ready-to-paste Antigravity prompts.
-   Helper for debugging, test design, result interpretation, and
    documentation.
-   Challenger of unsupported claims and inconsistent decisions.

### Antigravity's role

-   Inspect the repository and relevant documentation.
-   Propose a plan before significant changes.
-   Implement only the approved scope.
-   Run applicable tests and report exact commands/results.
-   Summarize files changed, design decisions, known issues, and
    follow-up tasks.

### Required work cycle

**Inspect → Review → Propose → Wait for approval → Implement → Verify →
Record.**

No silent architecture changes, scope expansion, unapproved
commits/pushes, or unsupported completion claims. If a necessary change
conflicts with this document, explain the reason and wait for approval.

### Definition of done

A task is complete only when: - The implementation matches the approved
requirements. - Relevant tests have actually run and results are
recorded. - The diff has been reviewed for unrelated changes. - Known
limitations and remaining issues are documented. - Project status and
the next handoff are updated.

## 14. Project State and Handoff Template

Update this section as work progresses.

-   **Current phase:** Phase 1 (Foundation & Setup)
-   **Current task:** P1-01 Repository Scaffolding & P1-02 Python Environment Setup
-   **Last verified commit:** fcda73f (Initial commit)
-   **Tests last run:** None run (Python 3.11 virtual environment pending user installation)
-   **Completed tasks:**
    - P1-01 Repository Scaffolding (.gitignore, .env.example, backend minimal dependency manifests, README.md, docs/adr/, docs/setup_guide.md, docs/implementation_plan.md)
    - ADR-001 (Native Windows Development with PostgreSQL 17), ADR-002 (Python 3.11 Runtime), ADR-003 (Local Storage Abstraction), ADR-004 (RapidOCR + Tesseract Pilot)
-   **In progress:** P1-02 Python 3.11 installation and virtual environment initialization
-   **Blockers:** Python 3.11 needs to be installed by the user (winget command provided; system currently only has global Python 3.13)
-   **Approved architecture changes:** Adopted native Windows 11 + local PostgreSQL 17.5 + local filesystem storage for Phase 1; standardized on Python 3.11 for AI/backend venv; selected RapidOCR and Tesseract for initial OCR pilot benchmark.
-   **Next action:** User runs `winget install --id Python.Python.3.11`, creates `.venv`, and approves Task 2 (Domain Models & Database Baseline)
-   **Next reviewer prompt:** Review P1-01/P1-02 completion report, confirm Python 3.11 installation, and approve kickoff of Task 2 (Domain Model and Database Baseline).

### Handoff report format

After each implementation session, record: 1. Task IDs attempted and
completed. 2. Files created or changed. 3. Commands and tests actually
run, with outcomes. 4. Screenshots or other verification evidence where
useful. 5. Known issues and deviations from the approved plan. 6.
Decisions requiring user approval. 7. Exact next task and proposed
prompt.

------------------------------------------------------------------------

**Source-of-truth rule:** This document is the planning baseline. Actual
repository contents and verified test results determine implementation
status. Approved decisions should be recorded here or in a linked
decision log so that future AI sessions can recover the context.
