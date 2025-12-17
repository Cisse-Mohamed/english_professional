import sys
print(f"Python Executable: {sys.executable}")
print(f"Path: {sys.path}")
try:
    import daphne
    print("Daphne imported successfully")
except ImportError as e:
    print(f"Error importing daphne: {e}")

try:
    import channels
    print("Channels imported successfully")
except ImportError as e:
    print(f"Error importing channels: {e}")
