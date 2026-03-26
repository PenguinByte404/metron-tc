from modules.math_engine import MetronMath

def execute(db, exe_dir):
    """Execution logic for Mode 7: Heat Source Characterization (Spatial Gradients)."""
    print("\n" + "="*50)
    print("   MODULE: HEAT SOURCE CHARACTERIZATION   ")
    print("="*50)

    dut_id = input("\nEnter Heat Source / Bath Asset ID: ").strip()
    
    try:
        target_temp = float(input("Enter Target Setpoint Temp (°C): "))
    except ValueError:
        print("[!] Input error. Please enter valid numeric values.")
        return

    # --- 1. RADIAL (TRANSVERSE) UNIFORMITY ---
    print("\n[--- RADIAL (HOLE-TO-HOLE) GRADIENT ---]")
    print("[i] Measure the reference hole vs peripheral holes at the exact same depth.")
    print("[i] Enter data as: [Reference_Temp] [Peripheral_Temp]")
    print("[i] Example: 100.01 99.98. Type 'done' when finished.")
    
    radial_data = []
    while True:
        entry = input(f"  [Radial {len(radial_data)+1}] Enter temps or 'done': ").strip()
        if entry.lower() == 'done':
            break
        try:
            t_ref, t_periph = map(float, entry.replace(',', ' ').split())
            radial_data.append((t_ref, t_periph))
        except ValueError:
            print("  [!] Invalid format. Enter two numeric values separated by a space.")

    # --- 2. AXIAL (DEPTH) UNIFORMITY ---
    print("\n[--- AXIAL (DEPTH) GRADIENT ---]")
    print("[i] Measure the bottom of the well vs elevated positions in the SAME hole.")
    print("[i] Enter data as: [Bottom_Temp] [Elevated_Temp]")
    print("[i] Example: 100.02 99.95. Type 'done' when finished.")
    
    axial_data = []
    while True:
        entry = input(f"  [Axial {len(axial_data)+1}] Enter temps or 'done': ").strip()
        if entry.lower() == 'done':
            break
        try:
            t_bot, t_elev = map(float, entry.replace(',', ' ').split())
            axial_data.append((t_bot, t_elev))
        except ValueError:
            print("  [!] Invalid format. Enter two numeric values separated by a space.")

    if not radial_data and not axial_data:
        print("\n[!] No data entered. Exiting module...")
        return

    # --- MATH & AUDIT TRAIL ---
    audit_log =  "==================================================\n"
    audit_log += "       METRON TC : HEAT SOURCE CHARACTERIZATION   \n"
    audit_log += "==================================================\n"
    audit_log += f"Asset ID        : {dut_id}\n"
    audit_log += f"Target Setpoint : {target_temp:.4f} °C\n"
    audit_log += "--------------------------------------------------\n"

    # Radial Math
    audit_log += "RADIAL (TRANSVERSE) UNIFORMITY:\n"
    max_radial_diff = 0.0
    if radial_data:
        for idx, (ref, periph) in enumerate(radial_data):
            diff = periph - ref
            audit_log += f"  Hole {idx+1} : Ref [{ref:.4f}] vs Periph [{periph:.4f}] -> Δ {diff:+.4f} °C\n"
            if abs(diff) > abs(max_radial_diff):
                max_radial_diff = diff
        audit_log += f">> Max Radial Gradient : {abs(max_radial_diff):.4f} °C\n"
    else:
        audit_log += "  [ No Radial Data Entered ]\n"
        
    audit_log += "--------------------------------------------------\n"

    # Axial Math
    audit_log += "AXIAL (DEPTH) UNIFORMITY:\n"
    max_axial_diff = 0.0
    if axial_data:
        for idx, (bot, elev) in enumerate(axial_data):
            diff = elev - bot
            audit_log += f"  Zone {idx+1} : Bottom [{bot:.4f}] vs Elev [{elev:.4f}] -> Δ {diff:+.4f} °C\n"
            if abs(diff) > abs(max_axial_diff):
                max_axial_diff = diff
        audit_log += f">> Max Axial Gradient  : {abs(max_axial_diff):.4f} °C\n"
    else:
        audit_log += "  [ No Axial Data Entered ]\n"

    audit_log += "==================================================\n"
    
    # Calculate Total Spatial Uncertainty (Root Sum Square of max gradients)
    # This is a standard metrological practice for combining uncorrelated spatial errors
    if radial_data and axial_data:
        rss_spatial = ((max_radial_diff ** 2) + (max_axial_diff ** 2)) ** 0.5
        audit_log += f"COMBINED SPATIAL UNCERTAINTY (RSS): ± {rss_spatial:.4f} °C\n"
        audit_log += "==================================================\n"

    # --- OUTPUT & EXPORT ---
    print("\n" + audit_log)

    save_opt = input("Save this characterization to a .txt file? (y/n): ").strip().lower()
    if save_opt == 'y':
        saved_path = MetronMath.export_proof(
            proof_text=audit_log,
            exe_dir=exe_dir,
            tc_type="None", 
            scale="ITS-90",
            test_name="HeatSourceChar",
            dut_id=dut_id
        )
        print(f"[i] Profile successfully saved to: {saved_path}")

# When calculating spatial error, taking the absolute maximum observed difference is standard ISO practice. But I also added a "Combined Spatial Uncertainty" calculation at the very bottom using the Root Sum Square (RSS) method: $\sqrt{\Delta T_{radial}^2 + \Delta T_{axial}^2}$.