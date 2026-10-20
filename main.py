"""
========================================================================================
AGRISTRESS ANALYTICS — LOCAL EXECUTION ENTRYPOINT
========================================================================================

Executes the complete local econometric analysis and forecasting pipeline:
    python main.py

Optional flags:
    python main.py --generate-data
    python main.py --state Maharashtra --commodity Onion --horizon 21
    python main.py --kcc data/my_kcc.csv --commodity-file data/my_mandi.csv --fuel data/my_fuel.csv --replace
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from run_pipeline import main

if __name__ == "__main__":
    main()
