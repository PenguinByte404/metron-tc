
# 🌡️ Metron TC
**By Metzilla LLC / PenguinByte Open Source Initiative**

> 💡 **TL;DR:** Metron TC is a zero-dependency, mathematically rigorous thermocouple metrology suite designed for ISO/IEC 17025 accredited laboratories. Built entirely on the Python standard library, it eliminates external dependency risks and provides an immutable, highly auditable framework for thermocouple calibration, standard realization, and heat source characterization.

---

## 🏗️ 1. System Architecture (Developer Perspective)
The application utilizes a decoupled, modular architecture to ensure calculation consistency across all testing paradigms.

| Component | Role | Description |
| :--- | :--- | :--- |
| 💻 **`metron_tc.py`** | **Master Controller** | The CLI entry point. Loads static JSON databases into memory on startup, manages reference scale aliasing (ITS-90 vs. IPTS-68), and routes user inputs. |
| 🧠 **`math_engine.py`** | **The Core Engine** | Centralized math processor handling polynomial evaluation ($E = \sum_{i=0}^{n} c_i t^i$), piecewise array traversing, and matrix solving. Guarantees UTF-8 encoding for math proofs (Δ, ±, °). |
| 📚 **Data Layer** | **Standard Refs** | `nist_its90.json` & `nist_ipts68.json`. Immutable dictionaries of standard reference coefficients processed as piecewise arrays. |
| 💾 **Asset Layer** | **Custom Probes** | `realized_trps.json`. A dynamic, user-writable database storing custom coefficients for locally characterized Thermodynamic Reference Probes (TRPs). |

---

## 📜 2. Metrological Standards & Compliance
Metron TC is strictly bound to the following international metrology standards:

| Standard | Application in Metron TC |
| :--- | :--- |
| **NIST Monograph 175** | Defines the ITS-90 direct and inverse polynomials. *(Note: Faithfully reproduces curve-fitting approximation errors, e.g., ±0.05 °C for Type K at 100 °C).* |
| **NBS Monograph 125** | Defines the legacy IPTS-68 reference tables for historical standard matching. |
| **ASTM E230 / E230M** | Governs the Standard and Special limits of error (tolerances) for base and noble metal thermocouples. |
| **EURAMET cg-13** | Provides guidelines for calibrating temperature block calibrators (measuring axial/radial uniformity). |
| **ISO/IEC 17025** | Supported via automatic generation of timestamped, immutable `.txt` math proofs for unbroken data traceability. |

---

## ⚙️ 3. Module Operations (Technician & Developer Perspectives)

| 🔢 Mode | 🎯 Metrological Objective | 🔬 Physical Lab Setup | 🖥️ App Function |
| :--- | :--- | :--- | :--- |
| **1. Joined Probe** | Determine Indicated Temp ($T_{ind}$) & total Error ($\Delta T$) of an assembled probe. | DUT & SPRT in stable heat source. CJC at 0.0 °C (or DMM thermistor). | Calculates $V_{cj}$, adds to $V_{dut}$ to find $V_{total}$, evaluates inverse polynomial for $T_{ind}$. |
| **2. Open Wire** | Determine absolute EMF error (mV) of raw wire against theoretical standard. | Sample junction in furnace with SPRT, CJC at 0.0 °C. DMM reads direct EMF. | Evaluates Direct polynomial for expected mV at target temp, subtracts from DUT mV. |
| **3. Coeff. Generator** | Characterize local TRP to establish a custom polynomial curve. | Sweep TRP through stable setpoints, record true temp (SPRT) & TRP mV. | Builds Vandermonde Matrix, applies Gaussian elimination ($X^T X C = X^T Y$) for least-squares coefficients. |
| **4. Homogeneity** | Detect physical defects, cold-working stress, or metallurgical impurities. | Both wire ends to DMM. Pass sharp heat gradient along wire; record mV spikes. | Calculates P-P parasitic EMF. Evaluates inverse polynomial to find true $\Delta T$ uncertainty. |
| **5. ASTM E230** | Automate compliance validation against industry standards. | Post-test data review step. | Dynamically executes `max(fixed_limit, temp * percentage_limit)` for PASS/FAIL booleans. |
| **6. Drift & Stability** | Prove heat source stability (Temporal) prior to testing. | Log sequential SPRT readings inside the block over a set time window. | Calculates P-P spread, total drift, mean ($\mu$), and sample standard deviation ($N-1$). |
| **7. Heat Source** | Map physical temp gradients (Spatial) per EURAMET cg-13. | Record deltas between reference hole/peripheral holes and well bottom/elevated depths. | Identifies max absolute deviation. Combines uncorrelated errors via Root Sum Square ($\sqrt{\Delta T_{rad}^2 + \Delta T_{ax}^2}$). |

---

## 🛠️ 4. Quick Setup & Deployment

### 🔍 Step 1: Validate Coefficients
Only `Type K`, `Type J`, and `Type T` standard & inverse coefficients are fully populated by default. Validate all coefficients against the [Official NIST Monograph 175 Reference](https://nvlpubs.nist.gov/nistpubs/Legacy/MONO/nistmonograph175.pdf).
* **To add new types (e.g., S, R, N):** Update `db_seeder.py` (generates the local JSONs) **OR** directly update `nist_its90.json` and `nist_ipts68.json`.

### 🏗️ Step 2: Run the DB Seeder
Generates your fresh standard JSON databases and TRP templates.
```bash
python db_seeder.py
```

### 🚀 Step 3: Run Metrology Suite
Boot up the master controller for terminal use.
```bash
python metron_tc.py
```

### 🧪 Step 4: Validate the App Functionality
We rigorously validated the functionality in `METRON_TESTING_CRITERIA.md` during each phase of the SSDLC. However, it is highly recommended to run a known test point through Mode 1 to validate local execution.

### 📦 Step 5: Compile the Application
Bundle the suite into a single, portable Windows executable (Zero Python installation required on lab workstations!).
```bash
pyinstaller --onefile --add-data "nist_its90.json;." --add-data "nist_ipts68.json;." metron_tc.py
```

### ✅ Finished! 
Distribute the `dist/metron_tc.exe` alongside your `realized_trps.json` file to the lab floor.


---

## ⚖️ License & Copyright

**Copyright © 2026 Metzilla LLC. > This repository is licensed under the MIT License.**

* **Permission:** You are free to use, copy, modify, merge, and distribute this software for any purpose.
* **Condition:** The above copyright notice and this permission notice must be included in all copies or substantial portions of the software.

### ⚠️ Disclaimer

**THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND. > In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use of the scripts provided herein. Always test in a sandbox environment before production use.**

---
