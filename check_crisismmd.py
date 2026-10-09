from datasets import load_dataset

print("Loading CrisisMMD humanitarian dataset...")

ds = load_dataset("QCRI/CrisisMMD", "humanitarian")

print("\nDATASET LOADED SUCCESSFULLY")
print(ds)

for split in ds:
    print(f"\n--- {split.upper()} ---")
    print("Columns:", ds[split].column_names)
    print("First example:", ds[split][0])