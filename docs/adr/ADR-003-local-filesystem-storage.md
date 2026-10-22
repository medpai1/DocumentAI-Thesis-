# ADR-003: Local Filesystem Storage with Abstract Storage Service

* **Status:** Accepted
* **Date:** 2026-10-22
* **Deciders:** User, Antigravity Agent

## Context

The master plan proposes S3-compatible object storage (e.g., MinIO or AWS S3) for uploaded export documents and immutable versions, but allows local filesystem storage for early development. Running MinIO would introduce an additional service dependency (either via Docker or native binary).

## Decision

Use local filesystem storage (under `./storage/uploads/`) for Phase 1 development and testing, implemented strictly behind a `StorageService` abstract interface.

## Reasons and Trade-offs

### Reasons
* **Minimal infrastructure footprint:** No need to configure, manage, or authenticate with an S3/MinIO server during initial schema and baseline work.
* **Rapid inspection:** Stored PDF and image files can be directly inspected, opened, or debugged on the local machine.
* **Encapsulation:** By defining an abstract `StorageService` interface (e.g., `save_file()`, `get_file()`, `calculate_sha256()`), switching to an `S3StorageService` in later phases requires no changes to business logic or database schemas.

### Trade-offs
* Distributed access: Local storage does not natively support multi-node scaling, which is acceptable for single-machine thesis development and evaluation.

## Consequences

* Uploaded files will be stored in a directory ignored by Git (`storage/uploads/` in `.gitignore`).
* Database records (`document_versions`) will store storage keys (relative paths or UUID keys) and SHA-256 hashes rather than raw paths.
* A clear clean-up policy is required for test artifacts.

## Verification / Evidence

* Confirmed storage directory is excluded in `.gitignore` and `.env.example` contains `STORAGE_BACKEND=local` and `LOCAL_STORAGE_DIR=./storage/uploads`.

## Conditions for Revisit

* Deployment of the system to a multi-container or cloud environment requiring centralized S3 object storage.
