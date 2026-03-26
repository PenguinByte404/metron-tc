import math
from modules.math_engine import MetronMath

def execute(db, exe_dir):
    scale_name = db.get('active_scale_name', 'ITS-90')
    print("\n" + "="*50)
    print(f"   MODULE: HOMOGENEITY & PARASITIC EMF SCAN ({scale_name})   ")
    print("="*50)

    tc_type = input("\nEnter Thermocouple Type (K/J/T/etc.): ").strip().upper()
    
    if tc_type not in db['active']:
        print(f"[!] Standard for Type {tc_type} not found in {scale_name} database.")
        print("[i] Returning to Main Menu...")
        return

    dut_id = input("Enter Spool/Wire Asset ID: ").strip()
    tc_data = db['active'][tc_type]

    while True:
        print(f"\n--- NEW SCAN TEST : {dut_id} ---")
        print("[i] Connect both ends of the wire to the DMM.")
        print("[i] Pass the heat source along the wire and record the highest and lowest mV spikes.")
        
        try:
            heat_temp = float(input("\nEnter approximate heat source temp (°C): "))
            max_mv = float(input("Enter Maximum observed parasitic EMF (mV): "))
            min_mv = float(input("Enter Minimum observed parasitic EMF (mV): "))
        except ValueError:
            print("[!] Input error. Please enter valid numeric values.")
            continue

        audit_log =  "==================================================\n"
        audit_log += "          METRON TC : HOMOGENEITY SCAN            \n"
        audit_log += "==================================================\n"
        audit_log += f"Spool/Wire ID   : {dut_id}\n"
        audit_log += f"Thermocouple    : Type {tc_type}\n"
        audit_log += f"Test Temp       : ~{heat_temp} °C\n"
        audit_log += "--------------------------------------------------\n"

        audit_log += f"STEP 1: Calculate Peak-to-Peak (P-P) Parasitic EMF\n"
        audit_log += f"Max Observation : {max_mv:+.6f} mV\n"
        audit_log += f"Min Observation : {min_mv:+.6f} mV\n"
        
        pp_mv = max_mv - min_mv
        
        audit_log += f"Formula: EMF_PP = Max - Min\n"
        audit_log += f">> Result EMF_PP: {pp_mv:.6f} mV\n\n"

        audit_log += f"STEP 2: Calculate Equivalent Temperature Uncertainty (ΔT)\n"
        
        # --- PIECEWISE UPDATE: Get Expected Voltage ---
        try:
            std_block = MetronMath.get_piecewise_data(heat_temp, tc_data["Standard"], is_inverse=False)
        except ValueError as e:
            print(f"\n[!] Range Error: {e}")
            break
            
        std_coeffs = std_block["coefficients"]
        
        # 1. Use standard_nist flag to evaluate °C and convert µV output to mV
        v_expected = MetronMath.calc_poly(heat_temp, std_coeffs, poly_type="standard_nist")
        
        # Handle Type K anomaly
        if tc_type == 'K' and "exponential" in std_block:
            exp = std_block["exponential"]
            exp_val_uv = exp["a0"] * math.exp(exp["a1"] * ((heat_temp - exp["a2"]) ** 2))
            v_expected += (exp_val_uv / 1000.0)
            
        v_parasitic = v_expected + pp_mv
        
        # --- PIECEWISE UPDATE: Convert back to Temperature ---
        try:
            inv_block = MetronMath.get_piecewise_data(v_parasitic, tc_data["Inverse"], is_inverse=True)
        except ValueError as e:
            print(f"\n[!] Range Error: {e}")
            break
            
        inv_coeffs = inv_block["coefficients"]
        
        # 2. Use inverse_nist flag to convert mV input to µV before evaluating
        t_parasitic = MetronMath.calc_poly(v_parasitic, inv_coeffs, poly_type="inverse_nist")
        
        delta_t = t_parasitic - heat_temp
        
        audit_log += f"Expected Voltage at {heat_temp} °C: {v_expected:.6f} mV\n"
        audit_log += f"Voltage w/ Parasitic Error : {v_parasitic:.6f} mV\n"
        audit_log += f"Formula: ΔT = T_parasitic - T_expected\n"
        audit_log += f">> Max Equivalent ΔT Error : ±{abs(delta_t):.4f} °C\n"
        audit_log += "==================================================\n"

        print("\n" + audit_log)

        save_opt = input("Save this scan report to a .txt file? (y/n): ").strip().lower()
        if save_opt == 'y':
            saved_path = MetronMath.export_proof(
                proof_text=audit_log,
                exe_dir=exe_dir,
                tc_type=tc_type,
                scale=scale_name,
                test_name="Homogeneity",
                dut_id=dut_id
            )
            print(f"[i] Report successfully saved to: {saved_path}")

        again = input("\nRun another scan for this spool? (y/n): ").strip().lower()
        if again != 'y':
            print("\n[i] Exiting Homogeneity Scan. Returning to Main Menu...")
            break