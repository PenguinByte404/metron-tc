# Metron TC - System Architecture & Metrological Operations
**By Metzilla LLC / PenguinByte Open Source Initiative**

## Executive Summary
Metron TC is a zero-dependency, mathematically rigorous thermocouple metrology suite designed for metrology laboratories. Built entirely on the Python standard library, it eliminates the risk of external dependency deprecation and provides an immutable, highly auditable framework for thermocouple calibration, standard realization, and heat source characterization.

## 1. System Architecture (Developer Perspective)
The application utilizes a decoupled, modular architecture to ensure calculation consistency across all testing paradigms.

### Core Components
* **`metron_tc.py` (Master Controller):** The CLI entry point. It loads the static JSON databases into memory on startup to minimize disk I/O, manages reference scale aliasing (ITS-90 vs. IPTS-68), and routes user inputs to the correct sub-modules.
* **`modules/math_engine.py` (The Core Engine):** The centralized mathematical processor. It handles standard polynomial evaluation ($E = \sum_{i=0}^{n} c_i t^i$), custom piecewise array traversing, and the pure-Python Gaussian elimination matrix solver. It also guarantees UTF-8 encoding for all ISO-compliant exported text proofs, ensuring symbols like Δ, ±, and ° render correctly across all operating systems.
* **The Data Layer (`nist_its90.json`, `nist_ipts68.json`):** Immutable dictionaries of standard reference coefficients. Because a single polynomial cannot define a thermocouple curve across its entire physical range, the engine processes these as piecewise arrays, seamlessly jumping between coefficient blocks based on the temperature or voltage threshold.
* **The Asset Layer (`realized_trps.json`):** A dynamic, user-writable database storing custom coefficients for locally characterized Thermodynamic Reference Probes (TRPs).

## 2. Metrological Standards & Compliance
Metron TC is strictly bound to the following international metrology standards:
* **NIST Monograph 175:** Defines the ITS-90 direct and inverse polynomials. *Note: Inverse polynomials inherently carry a curve-fitting approximation error (e.g., ±0.05 °C for Type K at 100 °C). The software faithfully reproduces this mathematical standard.*
* **NBS Monograph 125:** Defines the legacy IPTS-68 reference tables for historical standard matching.
* **ASTM E230 / E230M:** Governs the Standard and Special limits of error (tolerances) for base and noble metal thermocouples.
* **EURAMET cg-13:** Provides the guidelines for the calibration of temperature block calibrators, specifically dictating the measurement of axial and radial temperature uniformity.
* **ISO/IEC 17025:** Supported via the automatic generation of timestamped, immutable `.txt` math proofs for every calculation, ensuring unbroken data traceability.



---

## 3. Module Operations (Technician & Developer Perspectives)

### Mode 1: Joined Probe Calibration
* **Metrological Objective:** Determine the Indicated Temperature ($T_{ind}$) and total Error ($\Delta T$) of a fully assembled thermocouple probe.
* **Physical Lab Setup:** The technician inserts the DUT and a reference SPRT into a stable heat source. The DUT leads are connected to a high-accuracy DMM. The Cold Junction is maintained at 0.0 °C via an ice bath or measured via the DMM's internal thermistor.
* **App Function:** The software calculates the Cold Junction equivalent voltage ($V_{cj}$), adds it to the measured DMM voltage ($V_{dut}$) to find the total absolute voltage ($V_{total}$), and evaluates the piecewise Inverse polynomial to calculate the indicated temperature ($T_{ind}$).

### Mode 2: Open Wire / Spool Calibration
* **Metrological Objective:** Determine the absolute EMF error (in millivolts) of raw thermocouple wire against the theoretical standard before probe manufacturing.
* **Physical Lab Setup:** A sample junction is welded, placed in a furnace alongside an SPRT, and the reference junction is held at 0.0 °C. The DMM reads the direct EMF output.
* **App Function:** Evaluates the Direct polynomial to find the expected theoretical voltage at the SPRT's target temperature, subtracting it from the measured DUT voltage to determine precise EMF deviation.

### Mode 3: Coefficient Generator
* **Metrological Objective:** Characterize a local Thermodynamic Reference Probe (TRP) to establish a highly accurate custom polynomial curve.
* **Physical Lab Setup:** The technician sweeps the TRP through highly stable temperature setpoints, recording true temperature (SPRT) and TRP millivolt output.
* **App Function:** Constructs an Observation (Vandermonde) Matrix from the input coordinates. Applies a native Python Gaussian elimination algorithm to solve the normal equations ($X^T X C = X^T Y$), yielding bespoke least-squares coefficients specifically tailored to that physical probe.

### Mode 4: Homogeneity & Parasitic EMF Scan
* **Metrological Objective:** Detect physical defects, cold-working stress, or metallurgical impurities along the length of a wire.
* **Physical Lab Setup:** Both ends of a single wire are connected to a DMM to form a closed loop. A sharp heat gradient (e.g., heat gun) is passed along the wire. The technician records the maximum and minimum voltage spikes.
* **App Function:** Calculates the Peak-to-Peak parasitic EMF. Evaluates the inverse polynomial of the standard voltage plus the parasitic voltage to translate the electrical anomaly into a true physical temperature uncertainty ($\Delta T$).

### Mode 5: ASTM E230 Tolerance Evaluator
* **Metrological Objective:** Automate compliance validation against industry standards.
* **Physical Lab Setup:** Post-test data review step.
* **App Function:** Dynamically calculates whether the fixed degree limit or the percentage-based limit applies to the specific target temperature via `max(fixed_limit, temp * percentage_limit)`, instantly outputting a PASS/FAIL boolean for Standard and Special classes.

### Mode 6: Drift & Stability Profiling (Temporal)
* **Metrological Objective:** Prove calibration heat source stability over time prior to testing.
* **Physical Lab Setup:** Temperature readings are logged sequentially from an SPRT inside the block over a set time window.
* **App Function:** Utilizes statistical arrays to calculate peak-to-peak spread, total drift, mean ($\mu$), and sample standard deviation ($N-1$). Outputs strict $1\sigma$ (68.2%) and $2\sigma$ (95.4%) uncertainty boundaries.

### Mode 7: Heat Source Characterization (Spatial)
* **Metrological Objective:** Map the physical temperature gradients of a dry-well calibrator or fluid bath per EURAMET cg-13 guidelines.
* **Physical Lab Setup:** Technicians record temperature deltas between the reference hole and peripheral holes (Radial), and between the bottom of the well and elevated positions (Axial).
* **App Function:** Identifies the maximum absolute deviation across all inputted zones. Mathematically combines these uncorrelated errors using the Root Sum Square method ($\sqrt{\Delta T_{radial}^2 + \Delta T_{axial}^2}$) to output a single, non-inflated Spatial Uncertainty figure for the lab's formal budget.

---