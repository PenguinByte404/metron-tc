import json
import os
from datetime import datetime, timedelta

def build_its90():
    """Compiles the raw NIST ITS-90 Database into a JSON file."""
    its90_data = {
        "references": "NIST Monograph 175, ITS-90 Thermocouple Database",
        "K": {
            "Standard": [
                {
                    "min_c": -270.0,
                    "max_c": 0.0,
                    "coefficients": [
                        0.000000000000e+00, 3.945012802500e+01, 2.362237359800e-02, 
                        -3.285890678400e-04, -4.990482877700e-06, -6.750905917300e-08, 
                        -5.741032742800e-10, -3.108887289400e-12, -1.045160936500e-14, 
                        -1.988926687800e-17, -1.632269748600e-20
                    ]
                },
                {
                    "min_c": 0.0,
                    "max_c": 1372.0,
                    "coefficients": [
                        -1.76004136860e+01, 3.89212049750e+01, 1.85587700320e-02, 
                        -9.94575928740e-05, 3.18409457190e-07, -5.60728448890e-10, 
                        5.60750590590e-13, -3.20207200030e-16, 9.71511471520e-20, 
                        -1.21047212750e-23
                    ],
                    "exponential": {
                        "a0": 1.18597600000e+02, 
                        "a1": -1.18343200000e-04, 
                        "a2": 1.26968600000e+02
                    }
                }
            ],
            "Inverse": [
                {
                    "min_mv": -5.891,
                    "max_mv": 0.0,
                    "coefficients": [
                        0.0, 2.5173462e+01, -1.1662878e+00, -1.0833638e+00, -8.9773540e-01, 
                        -3.7342377e-01, -8.6632643e-02, -1.0450598e-02, -5.1920577e-04
                    ]
                },
                {
                    "min_mv": 0.0,
                    "max_mv": 20.644,
                    "coefficients": [
                        0.0, 2.508355e+01, 7.860106e-02, -2.503131e-01, 8.315270e-02, 
                        -1.228034e-02, 9.804036e-04, -4.413030e-05, 1.057734e-06, -1.052755e-08
                    ]
                },
                {
                    "min_mv": 20.644,
                    "max_mv": 54.886,
                    "coefficients": [
                        -1.318058e+02, 4.830222e+01, -1.646031e+00, 5.464731e-02, -9.650715e-04, 
                        8.802193e-06, -3.110810e-08
                    ]
                }
            ]
        },
        "J": {
            "Standard": [
                {
                    "min_c": -210.0,
                    "max_c": 760.0,
                    "coefficients": [
                        0.0, 5.0381187815e+01, 3.0475836930e-02, -8.5681065720e-05, 
                        1.3228195295e-07, -1.7052958337e-10, 2.0948090697e-13, 
                        -1.2538395336e-16, 1.5631725697e-20
                    ]
                },
                {
                    "min_c": 760.0,
                    "max_c": 1200.0,
                    "coefficients": [
                        2.9645625681e+05, -1.4976127786e+03, 3.1787103924e+00, 
                        -3.1847331440e-03, 1.5720819004e-06, -3.0691369056e-10
                    ]
                }
            ],
            "Inverse": [
                {
                    "min_mv": -8.095,
                    "max_mv": 0.0,
                    "coefficients": [
                        0.0, 1.9528268e+01, -1.2286185e+00, -1.0752178e+00, -5.9086933e-01, 
                        -1.7256713e-01, -2.8131513e-02, -2.3963370e-03, -8.3823321e-05
                    ]
                },
                {
                    "min_mv": 0.0,
                    "max_mv": 42.919,
                    "coefficients": [
                        0.0, 1.978425e+01, -2.001204e-01, 1.036969e-02, -2.549687e-04, 
                        3.585153e-06, -5.344285e-08, 5.099890e-10
                    ]
                },
                {
                    "min_mv": 42.919,
                    "max_mv": 69.553,
                    "coefficients": [
                        -3.11358187e+03, 3.00543684e+02, -9.94773230e+00, 1.70276630e-01, 
                        -1.43033468e-03, 4.73886084e-06
                    ]
                }
            ]
        },
        "T": {
            "Standard": [
                {
                    "min_c": -270.0,
                    "max_c": 0.0,
                    "coefficients": [
                        0.0, 3.8748106364e+01, 4.4194434347e-02, 1.1844323105e-04, 
                        2.0032973554e-05, 9.0138019559e-07, 2.2651156593e-08, 
                        3.6071154205e-10, 3.8493939883e-12, 2.8213521925e-14, 
                        1.4251594779e-16, 4.8768662286e-19, 1.0795539270e-21, 
                        1.3945027062e-24, 7.9795153927e-28
                    ]
                },
                {
                    "min_c": 0.0,
                    "max_c": 400.0,
                    "coefficients": [
                        0.0, 3.8748106364e+01, 3.3292227880e-02, 2.0618243404e-04, 
                        -2.1882256846e-06, 1.0996880928e-08, -3.0815758772e-11, 
                        4.5479135290e-14, -2.7512901673e-17
                    ]
                }
            ],
            "Inverse": [
                {
                    "min_mv": -5.603,
                    "max_mv": 0.0,
                    "coefficients": [
                        0.0, 2.5949192e+01, -2.1316967e-01, 7.9018692e-01, 4.2527777e-01, 
                        1.3304473e-01, 2.0241446e-02, 1.1526022e-03
                    ]
                },
                {
                    "min_mv": 0.0,
                    "max_mv": 20.869,
                    "coefficients": [
                        0.0, 2.592800e+01, -7.602961e-01, 4.637791e-02, -2.165394e-03, 
                        6.048144e-05, -7.293422e-07
                    ]
                }
            ]
        }
    }

    with open('nist_its90.json', 'w') as f:
        json.dump(its90_data, f, indent=4)
    print("[+] Successfully compiled raw nist_its90.json")

def build_ipts68():
    ipts68_data = {
        "references": "NBS Monograph 125, IPTS-68 Reference Tables",
        "K": {
            "Standard": [
                {
                    "min_c": 0.0,
                    "max_c": 1372.0,
                    "coefficients": [],
                    "exponential": {
                        "a0": 0.1185976e0, 
                        "a1": -0.1183432e-3, 
                        "a2": 0.1269686e3
                    }
                }
            ],
            "Inverse": [
                {
                    "min_mv": 0.0,
                    "max_mv": 54.886,
                    "coefficients": []
                }
            ]
        }
    }

    with open('nist_ipts68.json', 'w') as f:
        json.dump(ipts68_data, f, indent=4)
    print("[+] Successfully compiled raw nist_ipts68.json")

def build_realized_trps_template():
    today = datetime.now()
    next_year = today + timedelta(days=365)
    
    template_data = {
        "TRP-TEMPLATE-K": {
            "tc_type": "K",
            "calibration_date": today.strftime("%Y-%m-%d"),
            "due_date": next_year.strftime("%Y-%m-%d"),
            "Standard_CJC_coeffs": [
                -1.760041e-02, 3.892120e-02, 1.855877e-05
            ],
            "notes": "Replace this template block with your actual standard's data."
        }
    }

    with open('realized_trps.json', 'w') as f:
        json.dump(template_data, f, indent=4)
    print("[+] Successfully compiled realized_trps.json template")

if __name__ == "__main__":
    print("=== METRON TC : DATABASE SEEDER ===")
    
    if os.path.exists('nist_its90.json'):
        if input("[!] nist_its90.json already exists. Overwrite? (y/n): ").lower() == 'y':
            build_its90()
    else:
        build_its90()

    if os.path.exists('nist_ipts68.json'):
        if input("[!] nist_ipts68.json already exists. Overwrite? (y/n): ").lower() == 'y':
            build_ipts68()
    else:
        build_ipts68()
        
    if os.path.exists('realized_trps.json'):
        if input("[!] realized_trps.json already exists. Overwrite and lose custom assets? (y/n): ").lower() == 'y':
            build_realized_trps_template()
    else:
        build_realized_trps_template()
        
    print("\n[i] Database seeding complete. Metron TC is ready to run.")