import sys
import traceback

try:
    from backend.api.main import app
    print("✅ Import successful!")
except Exception as e:
    print("❌ Import failed!")
    print(f"Error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
