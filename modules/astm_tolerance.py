from modules.math_engine import MetronMath

# A lightweight, embedded dictionary of ASTM E230 Limits of Error (above 0 °C)
# Format: { 'TYPE': (Standard_Fixed, Standard_Percent, Special_Fixed, Special_Percent) }
ASTM_LIMITS = {
    'K': (2.2, 0.0075, 1.1, 0.004),
    'J': (2.2, 0.0075, 1.1, 0.004),
    'T': (1.0, 0.0075, 0.5, 0.004),
    'E': (1.7, 0.0050, 1.0, 0.004),
    'N': (2.2, 0.0075, 1.1, 0.004),
    'R': (1.5, 0.0025, 0.6, 0.001),
    'S': (1.5, 0.0025, 0.6, 0.001),
    'B': (0.5, 0.0025, None, None) # Type B generally doesn't have a Special limit defined in the same way
}

def get_astm_tolerance(tc_type, target_temp):
    """Calculates the exact ASTM E230 tolerance bounds for a given temperature."""
    if tc_type not in ASTM_LIMITS:
        return None, None
        
    std_fixed, std_pct, spl_fixed, spl_pct = ASTM_LIMITS[tc_type]
    
    # Standard Limit is the greater of the fixed °C or the percentage of temp
    std_limit = max(std_fixed, target_temp * std_pct)
    
    # Special Limit calculation
    if spl_fixed is not None:
        spl_limit = max(spl_fixed, target_temp * spl_pct)
    else:
        spl_limit = None
        
    return std_limit, spl_limit

def execute(db, exe_dir):
    """Execution logic for Mode 5: ASTM E230 Tolerance Evaluator."""
    print("\n" + "="*50)
    print("   MODULE: ASTM E230 TOLERANCE EVALUATOR   ")
    print("="*50)

    while True:
        tc_type = input("\nEnter Thermocouple Type (K/J/T/etc.): ").strip().upper()
        
        if tc_type not in ASTM_LIMITS:
            print(f"[!] ASTM E230 data for Type {tc_type} not configured in this module.")
            continue

        dut_id = input("Enter DUT Asset ID / Serial Number: ").strip()

        try:
            target_temp = float(input("Enter SPRT Target Temperature (°C): "))
            measured_error = float(input("Enter calculated DUT Error (°C): "))
        except ValueError:
            print("[!] Input error. Please enter valid numeric values.")
            continue

        # --- MATH & AUDIT TRAIL ---
        std_limit, spl_limit = get_astm_tolerance(tc_type, target_temp)
        abs_error = abs(measured_error)

        std_pass = abs_error <= std_limit
        spl_pass = False if spl_limit is None else (abs_error <= spl_limit)

        audit_log =  "==================================================\n"
        audit_log += "          METRON TC : ASTM E230 EVALUATION        \n"
        audit_log += "==================================================\n"
        audit_log += f"DUT Asset ID    : {dut_id}\n"
        audit_log += f"Thermocouple    : Type {tc_type}\n"
        audit_log += f"Test Temp       : {target_temp:.4f} °C\n"
        audit_log += f"Measured Error  : {measured_error:+.4f} °C\n"
        audit_log += "--------------------------------------------------\n"

        audit_log += "ASTM E230 LIMITS OF ERROR:\n"
        audit_log += f"Standard Limit  : ± {std_limit:.4f} °C\n"
        
        if spl_limit:
            audit_log += f"Special Limit   : ± {spl_limit:.4f} °C\n"
        else:
            audit_log += f"Special Limit   : N/A\n"
            
        audit_log += "--------------------------------------------------\n"
        audit_log += "EVALUATION RESULTS:\n"
        
        if std_pass:
            audit_log += f"Standard Class  : PASS\n"
        else:
            audit_log += f"Standard Class  : FAIL (Exceeds by {abs_error - std_limit:.4f} °C)\n"
            
        if spl_limit:
            if spl_pass:
                audit_log += f"Special Class   : PASS\n"
            else:
                audit_log += f"Special Class   : FAIL (Exceeds by {abs_error - spl_limit:.4f} °C)\n"

        audit_log += "==================================================\n"

        # --- OUTPUT & EXPORT ---
        print("\n" + audit_log)

        save_opt = input("Save this evaluation report to a .txt file? (y/n): ").strip().lower()
        if save_opt == 'y':
            saved_path = MetronMath.export_proof(
                proof_text=audit_log,
                exe_dir=exe_dir,
                tc_type=tc_type,
                scale="ITS-90",
                test_name="ASTME230",
                dut_id=dut_id
            )
            print(f"[i] Report successfully saved to: {saved_path}")

        # --- LOOP OR EXIT ---
        again = input("\nEvaluate another point or DUT? (y/n): ").strip().lower()
        if again != 'y':
            print("\n[i] Exiting ASTM Evaluator. Returning to Main Menu...")
            break
