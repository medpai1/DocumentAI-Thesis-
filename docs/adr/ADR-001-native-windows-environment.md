# ADR-001: Native Windows Development Environment with Local PostgreSQL 17

* **Status:** Accepted
* **Date:** 2026-10-22
* **Deciders:** User, Antigravity Agent

## Context

The master plan proposed Docker Compose for local development reproducibility. However, inspection of the host system shows:
1. Docker and Docker Compose are not installed (`docker` command not found in PATH).
2. WSL has no installed Linux distributions.
3. A native PostgreSQL 17.5 service (`postgresql-x64-17`) is already installed and actively running on Windows.
4. Installing Docker Desktop introduces virtualization overhead, requires WSL2 configuration, and may introduce friction for hardware-accelerated GPU passthrough on Windows.

## Decision

Adopt native Windows 11 as the primary local development environment for Phase 1. Use the existing native PostgreSQL 17.5 service directly on `localhost:5432`. Structure configuration via environment variables (`.env`) to ensure the platform remains container-ready for future deployment.

## Reasons and Trade-offs

### Reasons
* **Zero setup latency:** Leverages an already running, healthy PostgreSQL 17.5 instance.
* **Direct GPU access:** Simplifies direct access to the NVIDIA GeForce RTX 5060 without WSL2 container passthrough complications.
* **Lower resource consumption:** Avoids running the Docker Desktop VM daemon alongside heavy ML workloads.

### Trade-offs
* Native OS differences: Dependencies with native C/C++ extensions or binary tools (e.g., Poppler, Tesseract) require Windows-specific binaries or pure-Python alternatives instead of standard Linux packages.

## Consequences

* Development commands in documentation must use Windows PowerShell syntax.
* Database connections will target `localhost:5432` with credentials defined in `.env`.
* Code and file paths must use `pathlib.Path` or standard cross-platform path handling.

## Verification / Evidence

* Inspected Windows service: `Get-Service postgresql-x64-17` returned `Running`.
* Verified database connectivity: `psql -h localhost -U postgres -w -c "SELECT version();"` successfully returned `PostgreSQL 17.5 on x86_64-windows`.

## Conditions for Revisit

* Team members onboarding on macOS or Linux who require identical containerized environments.
* Production deployment to a container orchestration platform (e.g., Kubernetes or Docker Compose on a Linux VPS).
