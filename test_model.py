import joblib

model_path = "models/resq_disaster_classifier_multi_disaster.pkl"

model = joblib.load(model_path)

reports = [
    "Families are stranded due to flooding and need food and drinking water.",
    "Several buildings have collapsed following an earthquake.",
    "Volunteers are distributing supplies to affected families.",
    "People have been injured during a cyclone.",
    "Electricity lines and roads are damaged after a severe storm."
]

print("RESQ DISASTER REPORT CLASSIFIER")
print("-" * 40)

for report in reports:
    prediction = model.predict([report])[0]

    print("\nReport:", report)
    print("Predicted category:", prediction)