import os
import math
from datetime import datetime

class MetronMath:
    """Centralized math and utility engine for Metron TC."""

    @staticmethod
    def calc_poly(val, coeffs, poly_type="raw"):
        """
        Evaluates a polynomial array: E = c_0 + c_1*x + c_2*x^2 ...
        
        Args:
            val (float): The input value (Temp °C or Voltage mV).
            coeffs (list): The array of coefficients.
            poly_type (str): 'standard_nist', 'inverse_nist', or 'raw'.
        """
        result = 0.0

        if poly_type == "inverse_nist":
            # NIST Inverse expects input in µV. Convert app's mV input to µV.
            #val_uv = val * 1000.0
            for i, c in enumerate(coeffs):
                #result += c * (val_uv ** i)
                result += c * (val ** i)
            return result

        elif poly_type == "standard_nist":
            # NIST Standard evaluates °C and natively outputs µV.
            for i, c in enumerate(coeffs):
                result += c * (val ** i)
            # Convert the final µV output back to mV for the app.
            return result / 1000.0
            
        else:
            # 'raw' fallback for custom TRPs (Mode 3) which are already natively in mV
            for i, c in enumerate(coeffs):
                result += c * (val ** i)
            return result

    @staticmethod
    def generate_proof_string(var_name, x_value, coefficients):
        """Generates the string representation of the algebraic polynomial."""
        proof = f"{var_name} = ({coefficients[0]:.6e})"
        for i in range(1, len(coefficients)):
            proof += f" + ({coefficients[i]:.6e} * {x_value}^{i})"
        return proof

    # --- MATRIX SOLVER FOR COEFFICIENT GENERATION ---
    @staticmethod
    def transpose(matrix):
        return [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]

    @staticmethod
    def matmul(A, B):
        result = [[0.0 for _ in range(len(B[0]))] for _ in range(len(A))]
        for i in range(len(A)):
            for j in range(len(B[0])):
                for k in range(len(B)):
                    result[i][j] += A[i][k] * B[k][j]
        return result

    @staticmethod
    def gaussian_elimination(A, b):
        n = len(A)
        M = [A[i] + [b[i][0]] for i in range(n)]

        for i in range(n):
            max_el = abs(M[i][i])
            max_row = i
            for k in range(i + 1, n):
                if abs(M[k][i]) > max_el:
                    max_el = abs(M[k][i])
                    max_row = k

            M[i], M[max_row] = M[max_row], M[i]

            for k in range(i + 1, n):
                if M[i][i] == 0:
                    raise ZeroDivisionError("Matrix is singular.")
                c = -M[k][i] / M[i][i]
                for j in range(i, n + 1):
                    if i == j:
                        M[k][j] = 0
                    else:
                        M[k][j] += c * M[i][j]

        x = [0 for _ in range(n)]
        for i in range(n - 1, -1, -1):
            x[i] = M[i][n] / M[i][i]
            for k in range(i - 1, -1, -1):
                M[k][n] -= M[k][i] * x[i]
        return x

    # --- AUDIT TRAIL EXPORTER ---
    @staticmethod
    def export_proof(proof_text, exe_dir, tc_type, scale, test_name, dut_id):
        """Exports the math proof to an auditable .txt file."""
        import os
        from datetime import datetime

        # Create the Metron_Proofs directory if it doesn't exist
        proof_dir = os.path.join(exe_dir, "Metron_Proofs")
        if not os.path.exists(proof_dir):
            os.makedirs(proof_dir)

        # Generate a timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Clean up the scale string to prevent file path errors (e.g. ITS-90 to ITS90)
        safe_scale = scale.replace("-", "")
        
        filename = f"{timestamp}_Type{tc_type}_{safe_scale}_{test_name}_{dut_id}.txt"
        filepath = os.path.join(proof_dir, filename)

        # Write the file enforcing UTF-8 encoding to support Δ, ±, and ° symbols
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(proof_text)

        return filepath
    
    # --- CAPTURE Scale ---
    @staticmethod
    def get_piecewise_data(value, range_array, is_inverse=False):
        """
        Scans a list of NIST range dictionaries and returns the correct coefficient block.
        'is_inverse' determines if we are checking against mV bounds or °C bounds.
        """
        min_key = "min_mv" if is_inverse else "min_c"
        max_key = "max_mv" if is_inverse else "max_c"
        
        for block in range_array:
            # Allow a tiny bit of floating-point leniency at the exact boundaries
            if block[min_key] - 0.001 <= value <= block[max_key] + 0.001:
                return block
                
        raise ValueError(f"Value {value} falls outside the configured NIST ranges.")