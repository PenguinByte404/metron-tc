import math
from modules.math_engine import MetronMath

def execute(db, exe_dir):
    scale_name = db.get('active_scale_name', 'ITS-90')
    print("\n" + "="*50)
    print(f"   MODULE: OPEN WIRE / SPOOL CALIBRATION ({scale_name})  ")
    print("="*50)

    tc_type = input("\nEnter Thermocouple Type (K/J/T/etc.): ").strip().upper()
    
    if tc_type not in db['active']:
        print(f"[!] Standard for Type {tc_type} not found in {scale_name} database.")
        print("[i] Returning to Main Menu...")
        return

    dut_id = input("Enter Spool/Wire Asset ID: ").strip()
    nist_ref = db['active'].get("references", f"{scale_name} Database")
    tc_data = db['active'][tc_type]

    while True:
        print(f"\n--- NEW TEST POINT : {dut_id} ---")
        try:
            sprt_hot = float(input("Enter SPRT Target Temperature (°C): "))
            dut_mv = float(input("Enter DUT Reading (mV): "))
        except ValueError:
            print("[!] Input error. Please enter valid numeric values.")
            continue

        audit_log =  "==================================================\n"
        audit_log += "          METRON TC : CALIBRATION AUDIT           \n"
        audit_log += "==================================================\n"
        audit_log += f"Spool/Wire ID   : {dut_id}\n"
        audit_log += f"Thermocouple    : Type {tc_type}\n"
        audit_log += f"Reference Scale : {scale_name}\n"
        audit_log += f"Primary Ref     : {nist_ref}\n"
        audit_log += "--------------------------------------------------\n"

        audit_log += f"STEP 1: Calculate Expected Theoretical Voltage at Target Temp\n"
        audit_log += f"SPRT True Hot Temp (T_true): {sprt_hot} °C\n"
        
        # --- PIECEWISE UPDATE ---
        try:
            std_block = MetronMath.get_piecewise_data(sprt_hot, tc_data["Standard"], is_inverse=False)
        except ValueError as e:
            print(f"\n[!] Range Error: {e}")
            break
            
        std_coeffs = std_block["coefficients"]
        # Tell the engine we are using raw NIST standard arrays (outputs µV -> mV)
        expected_mv = MetronMath.calc_poly(sprt_hot, std_coeffs, poly_type="standard_nist")
        proof = MetronMath.generate_proof_string("V_expected", sprt_hot, std_coeffs)
        
        # Handle Type K anomaly
        if tc_type == 'K' and "exponential" in std_block:
            exp = std_block["exponential"]
            # Calculate the raw µV exponential output
            exp_val_uv = exp["a0"] * math.exp(exp["a1"] * ((sprt_hot - exp["a2"]) ** 2))
            # Divide by 1000 to convert to mV before adding
            expected_mv += (exp_val_uv / 1000.0)
            proof += f" + [{exp['a0']:.6e} * e^({exp['a1']:.6e} * ({sprt_hot} - {exp['a2']})^2)]"
            
        audit_log += proof + "\n"
        audit_log += f">> Result V_expected: {expected_mv:.6f} mV\n\n"

        audit_log += f"STEP 2: Calculate EMF Voltage Error\n"
        audit_log += f"Actual DUT Reading: {dut_mv:.6f} mV\n"
        mv_error = dut_mv - expected_mv
        audit_log += f"Formula: EMF Error = DUT_mV - V_expected\n"
        audit_log += f">> Final EMF Error: {mv_error:.6f} mV\n"
        audit_log += "==================================================\n"

        print("\n" + audit_log)

        save_opt = input("Save this math proof to a .txt file? (y/n): ").strip().lower()
        if save_opt == 'y':
            saved_path = MetronMath.export_proof(
                proof_text=audit_log,
                exe_dir=exe_dir,
                tc_type=tc_type,
                scale=scale_name,
                test_name="OpenWire",
                dut_id=dut_id
            )
            print(f"[i] Proof successfully saved to: {saved_path}")

        again = input("\nRun another test point for this spool? (y/n): ").strip().lower()
        if again != 'y':
            print("\n[i] Exiting Open Wire Module. Returning to Main Menu...")
            break