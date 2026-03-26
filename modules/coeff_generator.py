from modules.math_engine import MetronMath

def execute(db, exe_dir):
    """Execution logic for Mode 3: Generate Custom TRP Coefficients."""
    print("\n" + "="*50)
    print(" MODULE: COEFFICIENT GENERATOR (LEAST-SQUARES) ")
    print("="*50)

    while True:
        tc_type = input("\nEnter Thermocouple Type being characterized (K/J/T/etc.): ").strip().upper()
        dut_id = input("Enter the Asset ID for this new Standard (e.g., TRP-999): ").strip()

        print("\n[i] Enter calibration data points: SPRT Temp (°C) and DUT Reading (mV).")
        print("[i] Separate values with a space or comma. Type 'done' when finished.")
        
        observations = []
        while True:
            entry = input(f"[{len(observations)+1}] Enter [Temp_C DUT_mV] or 'done': ").strip()
            if entry.lower() == 'done':
                break
            try:
                temp_c, dut_mv = map(float, entry.replace(',', ' ').split())
                observations.append((temp_c, dut_mv))
            except ValueError:
                print("[!] Invalid format. Example: 100.0, 4.096")
                
        if len(observations) < 4:
            print("[!] Error: At least 4 points required for a reliable polynomial fit.")
            print("[i] Restarting data entry...")
            continue

        try:
            degree = int(input("\nEnter desired polynomial degree (Recommended: 2, 3, or 4): "))
        except ValueError:
            print("[!] Invalid input. Defaulting to 3rd degree polynomial.")
            degree = 3
        
        # --- BUILD THE AUDIT TRAIL AND DO THE MATH ---
        audit_log =  "==================================================\n"
        audit_log += "        METRON TC : COEFFICIENT GENERATION        \n"
        audit_log += "==================================================\n"
        audit_log += f"Asset ID        : {dut_id}\n"
        audit_log += f"Thermocouple    : Type {tc_type}\n"
        audit_log += f"Polynomial Deg  : {degree}\n"
        audit_log += f"Data Points     : {len(observations)}\n"
        audit_log += "--------------------------------------------------\n"
        
        audit_log += "OBSERVATION MATRIX:\n"
        for t, v in observations:
            audit_log += f"  Temp: {t:8.3f} °C  |  Voltage: {v:8.3f} mV\n"
        audit_log += "\n"

        # 1. Build Matrices
        X = [[(temp ** p) for p in range(degree + 1)] for temp, _ in observations]
        Y = [[mv] for _, mv in observations]

        # 2. Linear Algebra Operations
        X_T = MetronMath.transpose(X)
        X_T_X = MetronMath.matmul(X_T, X)
        X_T_Y = MetronMath.matmul(X_T, Y)

        # 3. Gaussian Elimination
        try:
            coeffs = MetronMath.gaussian_elimination(X_T_X, X_T_Y)
        except ZeroDivisionError:
            print("[!] Mathematical Error: Matrix is singular. Data points may be too clustered or perfectly linear.")
            continue

        audit_log += "GENERATED COEFFICIENTS (Lowest to Highest Degree):\n"
        for i, c in enumerate(coeffs):
            audit_log += f"  c{i} = {c:e}\n"
        
        audit_log += "\nGENERATED MATH PROOF:\n"
        audit_log += MetronMath.generate_proof_string("E_out", "T", coeffs) + "\n"
        audit_log += "==================================================\n"

        # --- OUTPUT & EXPORT ---
        print("\n" + audit_log)
        
        print("--- COPY THIS TO realized_trps.json ---")
        print(f'"{dut_id}": {{')
        print(f'  "tc_type": "{tc_type}",')
        print(f'  "Standard_CJC_coeffs": [')
        print("    " + ",\n    ".join([f"{c:e}" for c in coeffs]))
        print('  ]')
        print('}')
        print("---------------------------------------\n")

        save_opt = input("Save this generation proof to a .txt file? (y/n): ").strip().lower()
        if save_opt == 'y':
            saved_path = MetronMath.export_proof(
                proof_text=audit_log,
                exe_dir=exe_dir,
                tc_type=tc_type,
                scale="ITS-90",
                test_name="CoeffGen",
                dut_id=dut_id
            )
            print(f"[i] Proof successfully saved to: {saved_path}")

        # --- LOOP OR EXIT ---
        again = input("\nCharacterize another asset? (y/n): ").strip().lower()
        if again != 'y':
            print("\n[i] Exiting Coefficient Generator. Returning to Main Menu...")
            break