import math
from modules.math_engine import MetronMath

def select_trp(trp_db, target_tc_type):
    """Local helper to filter and select a realized TRP standard."""
    valid_trps = {
        asset_id: data for asset_id, data in trp_db.items() 
        if data['tc_type'].upper() == target_tc_type.upper()
    }
    
    if not valid_trps:
        return None, None

    print(f"\n[ AVAILABLE REALIZED TRPs - TYPE {target_tc_type.upper()} ]")
    for asset_id in valid_trps.keys():
        print(f" - {asset_id}")
        
    while True:
        selection = input("\nSelect TRP Asset ID (or type 'NIST' for standard): ").strip()
        if selection.upper() == 'NIST':
            return "NIST Standard", None
        if selection in valid_trps:
            return selection, valid_trps[selection]["Standard_CJC_coeffs"]
        print("[!] Invalid selection. Please choose a valid asset or 'NIST'.")

def execute(db, exe_dir):
    """Execution logic for Mode 1: Joined Probe Calibration."""
    scale_name = db.get('active_scale_name', 'ITS-90')
    
    print("\n" + "="*50)
    print(f"   MODULE: JOINED PROBE CALIBRATION ({scale_name})   ")
    print("="*50)

    tc_type = input("\nEnter Thermocouple Type (K/J/T/etc.): ").strip().upper()
    
    # Validate TC Type against the active database
    if tc_type not in db['active']:
        print(f"[!] Standard for Type {tc_type} not found in {scale_name} database.")
        print("[i] Returning to Main Menu...")
        return

    dut_id = input("Enter DUT Asset ID / Serial Number: ").strip()

    # Select TRP Standard
    trp_name, custom_cjc = select_trp(db['trps'], tc_type)
    if not trp_name:
        print(f"[i] No custom TRPs found. Defaulting to standard curves.")
        trp_name = f"{scale_name} Standard"
        custom_cjc = None

    nist_ref = db['active'].get("references", f"{scale_name} Database")
    tc_data = db['active'][tc_type]

    # Enter the continuous testing loop
    while True:
        print(f"\n--- NEW TEST POINT : {dut_id} ---")
        try:
            sprt_cj = float(input("Enter SPRT Cold Junction Temp (°C): "))
            sprt_hot = float(input("Enter SPRT Target Temperature (°C): "))
            dut_mv = float(input("Enter DUT Reading (mV): "))
        except ValueError:
            print("[!] Input error. Please enter valid numeric values.")
            continue

        # --- BUILD THE AUDIT TRAIL AND DO THE MATH ---
        audit_log =  "==================================================\n"
        audit_log += "          METRON TC : CALIBRATION AUDIT           \n"
        audit_log += "==================================================\n"
        audit_log += f"DUT Asset ID    : {dut_id}\n"
        audit_log += f"Thermocouple    : Type {tc_type}\n"
        audit_log += f"Reference Scale : {scale_name}\n"
        audit_log += f"Primary Ref     : {nist_ref}\n"
        audit_log += "--------------------------------------------------\n"

        # 1. Cold Junction Calculation
        audit_log += f"STEP 1: Calculate Cold Junction Voltage (V_cj)\n"
        audit_log += f"Measured CJ Temp (T_cj): {sprt_cj} °C\n"
        
        if custom_cjc:
            audit_log += f"Reference: Realized TRP Asset [{trp_name}]\n"
            # Mode 3 custom TRPs are natively in mV, so use poly_type="raw"
            v_cj = MetronMath.calc_poly(sprt_cj, custom_cjc, poly_type="raw")
            audit_log += MetronMath.generate_proof_string("V_cj", sprt_cj, custom_cjc) + "\n"
        else:
            audit_log += f"Reference: {nist_ref}\n"
            
            # --- PIECEWISE UPDATE ---
            try:
                std_block = MetronMath.get_piecewise_data(sprt_cj, tc_data["Standard"], is_inverse=False)
            except ValueError as e:
                print(f"\n[!] Range Error: {e}")
                break
                
            std_coeffs = std_block["coefficients"]
            # Tell the engine we are using raw NIST standard arrays (outputs µV -> mV)
            v_cj = MetronMath.calc_poly(sprt_cj, std_coeffs, poly_type="standard_nist")
            proof = MetronMath.generate_proof_string("V_cj", sprt_cj, std_coeffs)
            
            # Handle exponential anomaly if it exists in this specific piecewise block
            if tc_type == 'K' and "exponential" in std_block:
                exp = std_block["exponential"]
                # Calculate the raw µV exponential output
                exp_val_uv = exp["a0"] * math.exp(exp["a1"] * ((sprt_cj - exp["a2"]) ** 2))
                # Divide by 1000 to convert to mV before adding to v_cj
                v_cj += (exp_val_uv / 1000.0)
                proof += f" + [{exp['a0']:.6e} * e^({exp['a1']:.6e} * ({sprt_cj} - {exp['a2']})^2)]"
            
            audit_log += proof + "\n"
            
        audit_log += f">> Result V_cj: {v_cj:.6f} mV\n\n"

        # 2. Total Voltage Calculation
        audit_log += f"STEP 2: Calculate Total Absolute Voltage (V_total)\n"
        v_total = dut_mv + v_cj
        audit_log += f"Formula: V_total = DUT_mV + V_cj\n"
        audit_log += f">> Result V_total = {dut_mv:.6f} + {v_cj:.6f} = {v_total:.6f} mV\n\n"

        # 3. Indicated Temp Calculation
        audit_log += f"STEP 3: Calculate Indicated Temp (T_ind) via Inverse Polynomial\n"
        audit_log += f"Reference: {nist_ref}\n"
        
        # --- PIECEWISE UPDATE ---
        try:
            inv_block = MetronMath.get_piecewise_data(v_total, tc_data["Inverse"], is_inverse=True)
        except ValueError as e:
            print(f"\n[!] Range Error: {e}")
            break
            
        inv_coeffs = inv_block["coefficients"]
        # Tell the engine we are using raw NIST inverse arrays (input mV -> µV)
        t_ind = MetronMath.calc_poly(v_total, inv_coeffs, poly_type="inverse_nist")
        audit_log += MetronMath.generate_proof_string("T_ind", round(v_total, 6), inv_coeffs) + "\n"
        audit_log += f">> Result T_ind: {t_ind:.4f} °C\n\n"

        # 4. Error Calculation
        audit_log += f"STEP 4: Calculate DUT Error\n"
        audit_log += f"SPRT True Hot Temp (T_true): {sprt_hot} °C\n"
        error = t_ind - sprt_hot
        audit_log += f"Formula: Error = T_ind - T_true\n"
        audit_log += f">> Final Error: {error:.4f} °C\n"
        audit_log += "==================================================\n"

        # --- OUTPUT & EXPORT PROMPT ---
        print("\n" + audit_log)

        save_opt = input("Save this math proof to a .txt file? (y/n): ").strip().lower()
        if save_opt == 'y':
            saved_path = MetronMath.export_proof(
                proof_text=audit_log,
                exe_dir=exe_dir,
                tc_type=tc_type,
                scale=scale_name,
                test_name="JoinedProbe",
                dut_id=dut_id
            )
            print(f"[i] Proof successfully saved to: {saved_path}")

        # --- LOOP OR EXIT ---
        again = input("\nRun another test point for this DUT? (y/n): ").strip().lower()
        if again != 'y':
            print("\n[i] Exiting Joined Probe Module. Returning to Main Menu...")
            break