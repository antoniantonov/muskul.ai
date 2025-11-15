<!--
Sync Impact Report
Version change: (none prior) → 1.0.0
Modified principles: N/A (initial definition)
Added sections: Core Principles (4), Non-Functional Standards, Development Workflow & Quality Gates, Governance
Removed sections: Template placeholder for Principle 5 (not required per user instruction)
Templates requiring updates:
	.specify/templates/plan-template.md ✅ updated
	.specify/templates/spec-template.md ✅ updated
	.specify/templates/tasks-template.md ✅ updated
	(No commands directory present; cannot update) ⚠ pending
Deferred TODOs: None
-->

# muskul.ai Constitution

## Core Principles

### I. Code Quality Discipline (NON-NEGOTIABLE)
Code MUST meet objective quality gates before merge: (1) Lint passes with zero errors; (2) Static analysis shows no critical or high issues; (3) Formatting enforced via automated tooling (no manual style debates); (4) Cyclomatic complexity per function SHOULD remain ≤ 10 unless justified in the PR (justification required in a "Complexity Tracking" table); (5) No TODO/FIXME comments in production code—convert to tracked tasks; (6) Public interfaces MUST include concise doc comments describing contract (inputs, outputs, error modes).
Rationale: Enforces a consistent, maintainable codebase, reduces review friction, and lowers defect introduction risk.

### II. Testing Standards & Coverage
All new functionality MUST be implemented using fail-first tests: write tests → confirm they fail → implement → pass → refactor. Categories required: unit tests for pure logic, contract tests for public interfaces or external service boundaries, and integration tests for cross-module flows. Minimum coverage thresholds: 80% line coverage overall, 90% for core domain packages (listed in plan.md), and 100% for critical pure functions (deterministic, side-effect free). Performance tests MUST exist for components declaring performance goals. No code may be merged if it causes any previously passing test to become flaky (flaky test MUST be quarantined and ticketed within same PR).
Rationale: Guarantees reliable evolution, prevents regressions, and builds confidence in rapid iteration.

### III. User Experience Consistency & Accessibility
User-facing components MUST use shared design tokens (color, spacing, typography) and follow a single interaction pattern per control type. All interactive elements MUST have accessible labels/ARIA roles and pass automated a11y checks (contrast ratio ≥ 4.5:1 normal text, ≥ 3:1 large text). Any new user flow MUST include a quickstart scenario in the feature spec and an independent acceptance test. UX changes that alter navigation or primary task flows REQUIRE a documented rationale and a migration note in the release entry.
Rationale: Ensures predictable, inclusive experiences, reducing user confusion and support burden.

### IV. Performance & Resource Efficiency
Each feature MUST declare performance budgets in the plan (e.g., p95 latency < 200ms, memory footprint < 100MB, frame rate ≥ 60fps for UI). CI MUST enforce baseline benchmarks—fail if budget exceeded by >10% unless explicitly waived with a ticket reference. Public APIs MUST avoid breaking backward compatible performance guarantees (no added N+1 queries, no unbounded loops). All I/O and network operations MUST have timeouts and clear error handling paths.
Rationale: Sustains responsiveness and scalability, preventing silent degradation and protecting user trust.

## Non-Functional Standards

Security: Secrets MUST NOT be committed; dependency updates flagged with known CVEs MUST be patched before release. Input validation MUST be centralized. Logging: Structured logging (JSON) with correlation IDs for request/trace level. Observability: Critical path operations MUST emit latency metrics; errors MUST include contextual identifiers. Versioning: Semantic versioning for user-facing contracts; breaking changes require MAJOR increment and migration guide. Internationalization: Text strings extracted for localization—no hard-coded user-visible text in logic files.

## Development Workflow & Quality Gates

Phases: Research → Design (data-model & contracts) → Test Authoring → Implementation → Benchmark → Review → Merge. Quality Gates: (1) Constitution Check (automated script) passes; (2) All required test categories present; (3) Coverage & performance budgets satisfied; (4) Accessibility audit passes for UI changes; (5) Complexity justifications present if thresholds exceeded; (6) Documentation artifacts updated (spec, plan, tasks) before merge. Reviews MUST focus first on principle compliance; non-compliant PRs are rejected without style discussion.

## Governance

Authority: This constitution supersedes informal practices. Amendments: Proposal PR MUST include diff summary, rationale, impact analysis on existing templates, and version bump type (MAJOR/MINOR/PATCH). Approval requires at least two maintainers and zero outstanding impact TODOs. Versioning Policy: MAJOR for principle removals/redefinitions; MINOR for new principles/sections; PATCH for clarifications only. Compliance Review: Monthly automated scans (lint, coverage, benchmark drift) + quarterly manual audit of complexity justifications and a11y baseline. Violations MUST be ticketed within 24h; unresolved critical violations block releases.

**Version**: 1.0.0 | **Ratified**: 2025-11-15 | **Last Amended**: 2025-11-15
