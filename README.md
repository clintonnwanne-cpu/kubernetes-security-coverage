# Kubernetes Security Coverage Checker

Compare declared node inventory with sensor-health observations before reporting coverage.

**Status:** independent local prototype, developed with AI assistance, using original code and synthetic fixtures. No production integration or employer implementation is included. Python 3.10+; standard library only.

## Two-minute demo

From this repository directory:

```sh
python3 coverage_check.py examples/inventory.json --now 2026-10-08T12:00:00Z
python3 -m unittest discover -v
```

The sample deliberately has incomplete inventory. It reports 25% coverage of four known nodes while fleet coverage stays null. Unsupported nodes remain in the denominator. Missing, unhealthy, stale, contradictory and future observations cannot count as healthy coverage.

See `examples/report.json` for the recorded local output and `test-results.txt` for the local test run. There are 12 focused regression tests. A GitHub workflow is included but has not run remotely before publication.

## Design

Declared inventory → timestamp and identity checks → per-node state → explicit denominators.

The code is intentionally small enough to inspect. CLI inputs are local JSON files, and stdout is a JSON report. Only the ticket simulator writes a database explicitly chosen by the caller. No tool connects to employer systems or makes a network call.

## Verification boundaries

This initial version evaluates node observations only. It does not query Kubernetes, inspect workloads or admission controls, attest inventory completeness, validate vendor agents, or prove enforcement. Caller-declared completeness can be wrong. No exceptions or exclusions are silently removed from the denominator.

This is a bounded control-validation demonstration, not a production security product. Tests exercise the included synthetic cases; passing tests do not establish comprehensive correctness or production readiness. Malformed top-level schemas may reject the input; they must never be treated as an all-clear report.

## Operational walkthrough

1. Run the checked-in fixture and inspect the report.
2. Change one synthetic input to trigger a failure; run the tests to see the expected behavior.
3. Review any proposed resolution manually. For real adoption, independently validate schema, identity, ownership, freshness and API semantics before developing a separately reviewed adapter.

No deployment takes place, so there is no production rollback. Keep the original input for comparison. For a disposable simulator run, choose a new temporary database path rather than overwriting an existing run. Do not put credentials, employer exports or sensitive identifiers in fixtures or reports.

## Contributing

Add a minimal synthetic failing fixture and a regression test with each behavior change. Keep evidence states explicit and avoid claims stronger than the input supports. See SECURITY.md for safe issue reporting.

## Provenance and license

Inspired by general security-engineering patterns from Kubernetes sensor validation, event-driven workflow automation and edge-control review. This is independent demonstration code, not code used by or endorsed by any employer. No historical workplace metric is presented as a measurement of this demo. AI assisted implementation and documentation; local tests and sample outputs are retained for inspection.

MIT license. Copyright 2026 Clinton Nwanne.
