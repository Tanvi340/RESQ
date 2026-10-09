from datasets import load_dataset

print("Loading HumAID Kerala floods dataset...")

dataset = load_dataset(
    "QCRI/HumAID-events",
    "kerala_floods_2018"
)

print("\nDataset loaded successfully!")
print(dataset)

for split_name, split_data in dataset.items():
    print(f"\nSplit: {split_name}")
    print("Number of rows:", len(split_data))
    print("Columns:", split_data.column_names)
    print("\nFirst example:")
    print(split_data[0])