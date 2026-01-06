import os
import glob
import sys
from lint_layout import lint_layout

def lint_all():
    csg_dir = "csg"
    collections = glob.glob(os.path.join(csg_dir, "collection_*.json"))
    
    print(f"Starting Batch Lint of {len(collections)} collections...")
    print("-" * 40)
    
    failed = 0
    clean = 0
    
    for col_path in sorted(collections):
        # We need to capture the print output or modify lint_layout to return a status
        # For now, let's just run it. It prints its own status.
        print(f"CHECKING: {os.path.basename(col_path)}")
        try:
            # Note: lint_layout prints directly to stdout
            # If we wanted to count, we'd need to modify the original script
            lint_layout(col_path)
        except Exception as e:
            print(f"  CRITICAL ERROR: {e}")
            failed += 1
        print("-" * 20)

if __name__ == "__main__":
    # Ensure we can import from the same directory
    sys.path.append(os.path.dirname(__file__))
    lint_all()
