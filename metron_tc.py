import json
import sys
import os

# Import the core Metrology Suite modules
import modules.joined_probe as joined_probe
import modules.open_wire as open_wire
import modules.coeff_generator as coeff_generator
import modules.homogeneity_scan as homogeneity_scan
import modules.astm_tolerance as astm_tolerance
import modules.stability_profile as stability_profile
import modules.heat_source_char as heat_source_char

class MetronTC:
    """
    Metron TC: Master Controller
    Routes technicians to specific metrology test modules and manages database state.
    """
    def __init__(self):
        # Handle PyInstaller pathing for bundled JSONs
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS 
            self.exe_dir = os.path.dirname(sys.executable) 
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.exe_dir = base_dir

        its90_path = os.path.join(base_dir, "nist_its90.json")
        ipts68_path = os.path.join(base_dir, "nist_ipts68.json")
        trp_path = os.path.join(self.exe_dir, "realized_trps.json")

        self.db = {}

        try:
            with open(its90_path, 'r') as f:
                self.db['its90'] = json.load(f)
            
            with open(ipts68_path, 'r') as f:
                self.db['ipts68'] = json.load(f)
            
            if not os.path.exists(trp_path):
                print("[!] realized_trps.json missing. Please run db_seeder.py first.")
                sys.exit(1)
                
            with open(trp_path, 'r') as f:
                self.db['trps'] = json.load(f)
                
        except FileNotFoundError as e:
            print(f"\n[!] Critical Error: Missing database file. {e}")
            print("[i] Ensure you have run 'python db_seeder.py' to generate the NIST databases.")
            sys.exit(1)

    def display_header(self):
        print("\n" + r"  __  __      _                     _____ ____  ")
        print(r" |  \/  | ___| |_ _ __ ___  _ __   |_   _/ ___| ")
        print(r" | |\/| |/ _ \ __| '__/ _ \| '_ \    | || |     ")
        print(r" | |  | |  __/ |_| | | (_) | | | |   | || |___  ")
        print(r" |_|  |_|\___|\__|_|  \___/|_| |_|   |_| \____| ")
        print(" Thermocouple Metrology Suite v2.0")
        print("------------------------------------------------")

    def select_scale(self):
        """Allows the technician to toggle between 1990 and 1968 reference scales."""
        print("\n[ Select Reference Scale ]")
        print("1. ITS-90 (Standard)")
        print("2. IPTS-68 (Legacy)")
        
        choice = input("Choice (1 or 2): ").strip()
        if choice == '2':
            # Alias the active database so the modules don't have to rewrite their logic
            self.db['active'] = self.db['ipts68']
            self.db['active_scale_name'] = "IPTS-68"
            return True
        else:
            self.db['active'] = self.db['its90']
            self.db['active_scale_name'] = "ITS-90"
            return True

    def run(self):
        self.display_header()
        
        while True:
            print("\n=== METRON TC : MAIN MENU ===")
            print("1. Joined Probe Calibration (Indicated Error °C)")
            print("2. Open Wire / Spool Calibration (EMF Error mV)")
            print("3. Generate Custom TRP Coefficients (Least-Squares)")
            print("4. Homogeneity & Parasitic EMF Scan")
            print("5. ASTM E230 Tolerance Evaluator")
            print("6. Drift & Stability Profiling")
            print("7. Heat Source Characterization (Spatial Gradients)")
            print("0. Exit Metron TC")
            
            selection = input("\nSelect Metrology Module: ").strip()
            
            if selection == '0':
                print("Shutting down Metron TC. Goodbye.")
                sys.exit(0)

            # Route to appropriate module
            if selection in ['1', '2', '4', '5']:
                if not self.select_scale():
                    continue
                
            if selection == '1':
                print(f"\n[i] Routing to Joined Probe Module ({self.db['active_scale_name']})...")
                joined_probe.execute(self.db, self.exe_dir)
            elif selection == '2':
                print(f"\n[i] Routing to Open Wire Module ({self.db['active_scale_name']})...")
                open_wire.execute(self.db, self.exe_dir)
            elif selection == '3':
                print("\n[i] Routing to Coefficient Generator...")
                coeff_generator.execute(self.db, self.exe_dir)
            elif selection == '4':
                print(f"\n[i] Routing to Homogeneity Scan ({self.db['active_scale_name']})...")
                homogeneity_scan.execute(self.db, self.exe_dir)
            elif selection == '5':
                print("\n[i] Routing to ASTM Evaluator...")
                astm_tolerance.execute(self.db, self.exe_dir)
            elif selection == '6':
                print("\n[i] Routing to Stability Profiler...")
                stability_profile.execute(self.db, self.exe_dir)
            elif selection == '7':
                print("\n[i] Routing to Heat Source Characterizer...")
                heat_source_char.execute(self.db, self.exe_dir)
            else:
                print("[!] Invalid selection. Please choose a valid module.\n")

if __name__ == "__main__":
    app = MetronTC()
    app.run()
