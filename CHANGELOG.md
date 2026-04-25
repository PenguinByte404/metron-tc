# Changelog
All notable changes to the Metron TC project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
*This section holds changes that are currently in work but haven't officially been published.*

## [2.1.0] - 2026-04-25
### Added
- Implemented composite multi-point logging in `joined_probe.py` to allow technicians to record full sweep calibrations into a single `.txt` math proof.
- Added a `test_point_count` tracker to clearly index sequentially tested points in the audit trail.

### Changed
- Moved the `Save to .txt` prompt outside of the continuous test loop in Mode 1.

## [2.0.1] - 2026-03-15
### Fixed
- Corrected a unit conversion bug in `db_seeder.py` where Inverse coefficients were incorrectly scaled. NIST natively expects millivolts (mV) for Inverse operations, so scaling was removed.
- Corrected scientific notation exponents for the Standard polynomials ($10^{-3}$ shift).

## [2.0.0] - 2026-03-10
### Added
- Complete architectural rewrite implementing a modular package structure.
- Introduced `math_engine.py` to centralize all polynomial evaluations and matrix solving.
- Introduced 6 distinct metrology modules (Joined Probe, Open Wire, Coefficient Generator, Homogeneity Scan, ASTM Evaluator, Stability Profiler).
- Added UTF-8 text file generation for ISO/IEC 17025 auditable math proofs.
- Shifted from hardcoded dictionaries to static JSON databases (`nist_its90.json`, `nist_ipts68.json`) for immutable traceability.
- Created `realized_trps.json` for dynamic asset management of locally characterized TRPs.

## [1.0.0] - 2026-02-15
### Added
- Initial stable release for lab floor testing.
- Single-script architecture featuring terminal prompts for SPRT Cold Junction, Target Temperature, and DUT mV readings.
- Hardcoded NIST Monograph 175 dictionaries for Type K thermocouples.
- Explicit handling of the Type K exponential adjustment anomaly.
- Algebraic expansion terminal printouts for math verification.

## [0.1.0] - 2026-01-20
### Added
- Initial proof-of-concept prototype.
- Basic implementation of the fundamental law of intermediate temperatures using NIST standard and inverse polynomial formulas.
