import statistics
from modules.math_engine import MetronMath

def execute(db, exe_dir):
    """Execution logic for Mode 6: Drift & Stability Profiling."""
    print("\n" + "="*50)
    print("   MODULE: DRIFT & STABILITY PROFILING   ")
    print("="*50)

    while True:
        dut_id = input("\nEnter Heat Source / Bath Asset ID: ").strip()
        target_temp = input("Enter Target Setpoint Temp (°C): ").strip()
        
        print("\n[i] Enter SPRT temperature readings sequentially.")
        print("[i] Separate values with a space or comma. Type 'done' when finished.")
        
        readings = []
        while True:
            entry = input(f"[{len(readings)+1}] Enter Temp_C or 'done': ").strip()
            if entry.lower() == 'done':
                break
            try:
                # Handle comma or space separated lists if they paste a block of data
                values = map(float, entry.replace(',', ' ').split())
                readings.extend(values)
            except ValueError:
                print("[!] Invalid format. Enter valid numeric temperatures.")
                
        n = len(readings)
        if n < 2:
            print("[!] Error: At least 2 points required to calculate standard deviation.")
            continue

        # --- STATISTICAL MATH ---
        t_max = max(readings)
        t_min = min(readings)
        t_mean = statistics.mean(readings)
        t_spread = t_max - t_min
        
        # Sample standard deviation (N-1)
        std_dev = statistics.stdev(readings)
        
        # Total drift (First reading vs Last reading)
        drift = readings[-1] - readings[0]

        # --- BUILD THE AUDIT TRAIL ---
        audit_log =  "==================================================\n"
        audit_log += "          METRON TC : STABILITY PROFILE           \n"
        audit_log += "==================================================\n"
        audit_log += f"Heat Source ID  : {dut_id}\n"
        audit_log += f"Target Setpoint : {target_temp} °C\n"
        audit_log += f"Sample Size (N) : {n} readings\n"
        audit_log += "--------------------------------------------------\n"

        audit_log += "RAW OBSERVATIONS (°C):\n"
        # Print in columns of 4 for readability
        for i in range(0, n, 4):
            chunk = readings[i:i+4]
            audit_log += "  " + "  ".join([f"{r:8.4f}" for r in chunk]) + "\n"
        
        audit_log += "\n--------------------------------------------------\n"
        audit_log += "STATISTICAL ANALYSIS:\n"
        audit_log += f"Maximum Temp    : {t_max:.4f} °C\n"
        audit_log += f"Minimum Temp    : {t_min:.4f} °C\n"
        audit_log += f"Mean Temp (μ)   : {t_mean:.4f} °C\n"
        audit_log += f"P-P Spread      : {t_spread:.4f} °C\n"
        audit_log += f"Total Drift     : {drift:+.4f} °C (Last - First)\n\n"
        
        audit_log += "UNCERTAINTY BOUNDS:\n"
        audit_log += f"1-Sigma (1σ)    : ± {std_dev:.4f} °C (68.2% Confidence)\n"
        audit_log += f"2-Sigma (2σ)    : ± {(std_dev * 2):.4f} °C (95.4% Confidence)\n"
        audit_log += "==================================================\n"

        # --- OUTPUT & EXPORT ---
        print("\n" + audit_log)

        save_opt = input("Save this stability profile to a .txt file? (y/n): ").strip().lower()
        if save_opt == 'y':
            saved_path = MetronMath.export_proof(
                proof_text=audit_log,
                exe_dir=exe_dir,
                tc_type="N/A",  # Not applicable for a bath stability test
                scale="ITS-90",
                test_name="Stability",
                dut_id=dut_id
            )
            print(f"[i] Profile successfully saved to: {saved_path}")

        # --- LOOP OR EXIT ---
        again = input("\nRun another stability profile? (y/n): ").strip().lower()
        if again != 'y':
            print("\n[i] Exiting Stability Profiler. Returning to Main Menu...")
            break