from datasets import load_dataset
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    confusion_matrix
)
from collections import Counter
import joblib
import os

# -----------------------------------
# 1. DISASTER DATASETS
# -----------------------------------

disasters = [
    "hurricane_florence_2018",
    "kaikoura_earthquake_2016",
    "kerala_floods_2018",
    "hurricane_harvey_2017",
    "hurricane_maria_2017",
    "midwestern_us_floods_2019",
    "puebla_mexico_earthquake_2017",
    "maryland_floods_2018",
    "hurricane_irma_2017",
    "ecuador_earthquake_2016",
    "cyclone_idai_2019",
    "canada_wildfires_2016",
    "italy_earthquake_aug_2016",
    "greece_wildfires_2018",
    "hurricane_dorian_2019",
    "california_wildfires_2018",
    "pakistan_earthquake_2019",
    "srilanka_floods_2017"
]

train_text, train_labels = [], []
dev_text, dev_labels = [], []
test_text, test_labels = [], []

print("Loading HumAID disaster datasets...")

# -----------------------------------
# 2. LOAD DATA
# -----------------------------------

for disaster in disasters:
    try:
        print(f"\nLoading: {disaster}")

        data = load_dataset("QCRI/HumAID-events", disaster)

        for row in data["train"]:
            train_text.append(row["tweet_text"])
            train_labels.append(row["class_label"])

        for row in data["dev"]:
            dev_text.append(row["tweet_text"])
            dev_labels.append(row["class_label"])

        for row in data["test"]:
            test_text.append(row["tweet_text"])
            test_labels.append(row["class_label"])

        print("Loaded successfully")

    except Exception as error:
        print(f"Could not load {disaster}: {error}")

# -----------------------------------
# 3. CHECK DATA
# -----------------------------------

if not train_text or not dev_text or not test_text:
    raise ValueError(
        "Dataset loading failed. Check the errors above."
    )

print("\n" + "=" * 50)
print("DATASET SUMMARY")
print("=" * 50)

print("Training reports:", len(train_text))
print("Validation reports:", len(dev_text))
print("Testing reports:", len(test_text))

print("Training categories:", len(set(train_labels)))
print("Validation categories:", len(set(dev_labels)))
print("Testing categories:", len(set(test_labels)))

print("\nTRAINING CATEGORY DISTRIBUTION")

for category, count in Counter(train_labels).most_common():
    print(f"{category}: {count}")

print("\nVALIDATION CATEGORY DISTRIBUTION")

for category, count in Counter(dev_labels).most_common():
    print(f"{category}: {count}")

# -----------------------------------
# 4. CHECK LABEL CONSISTENCY
# -----------------------------------

train_categories = set(train_labels)
dev_categories = set(dev_labels)
test_categories = set(test_labels)

print("\nCATEGORY CONSISTENCY CHECK")

print(
    "Categories missing from validation:",
    train_categories - dev_categories
)

print(
    "Categories missing from testing:",
    train_categories - test_categories
)

# -----------------------------------
# 5. DEFINE MODELS - EXPERIMENT 4
# -----------------------------------

custom_weights = {
    "caution_and_advice": 1.0,
    "displaced_people_and_evacuations": 1.0,
    "infrastructure_and_utility_damage": 1.0,
    "injured_or_dead_people": 1.0,
    "missing_or_found_people": 1.0,
    "not_humanitarian": 1.3,
    "other_relevant_information": 1.3,
    "requests_or_urgent_needs": 1.5,
    "rescue_volunteering_or_donation_effort": 1.0,
    "sympathy_and_support": 1.0
}

classifiers = {
    "Logistic Regression C=1.0 Custom Weights":
        LogisticRegression(
            C=1.0,
            max_iter=3000,
            class_weight=custom_weights,
            random_state=42
        ),

    "Logistic Regression C=2.0 Custom Weights":
        LogisticRegression(
            C=2.0,
            max_iter=3000,
            class_weight=custom_weights,
            random_state=42
        ),

    "Logistic Regression C=1.0 Balanced":
        LogisticRegression(
            C=1.0,
            max_iter=3000,
            class_weight="balanced",
            random_state=42
        )
}

results = {}

# -----------------------------------
# 6. DEFINE TEXT FEATURES
# -----------------------------------

features = FeatureUnion([
    (
        "word_tfidf",
        TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",
            analyzer="word",
            ngram_range=(1, 2),
            max_features=50000,
            min_df=2,
            sublinear_tf=True
        )
    ),
    (
        "char_tfidf",
        TfidfVectorizer(
            lowercase=True,
            analyzer="char",
            ngram_range=(3, 5),
            max_features=30000,
            min_df=2,
            sublinear_tf=True
        )
    )
])

# -----------------------------------
# 7. TRAIN AND COMPARE MODELS
# -----------------------------------

for name, classifier in classifiers.items():

    print("\n" + "=" * 50)
    print("Training:", name)

    model = Pipeline([
        ("features", features),
        ("classifier", classifier)
    ])

    model.fit(train_text, train_labels)

    predictions = model.predict(dev_text)

    accuracy = accuracy_score(
        dev_labels,
        predictions
    )

    macro_f1 = f1_score(
        dev_labels,
        predictions,
        average="macro",
        zero_division=0
    )

    weighted_f1 = f1_score(
        dev_labels,
        predictions,
        average="weighted",
        zero_division=0
    )

    print("\nVALIDATION RESULTS")
    print("Accuracy:", round(accuracy * 100, 2), "%")
    print("Macro F1:", round(macro_f1 * 100, 2), "%")
    print("Weighted F1:", round(weighted_f1 * 100, 2), "%")

    results[name] = {
        "model": model,
        "macro_f1": macro_f1,
        "accuracy": accuracy,
        "weighted_f1": weighted_f1
    }

print("\nALL MODELS TRAINED SUCCESSFULLY!")

# -----------------------------------
# 8. SELECT BEST MODEL
# -----------------------------------

best_name = max(
    results,
    key=lambda name: results[name]["macro_f1"]
)

best_model = results[best_name]["model"]

print("\n" + "=" * 50)
print("BEST MODEL:", best_name)
print("=" * 50)

print(
    "Best validation accuracy:",
    round(results[best_name]["accuracy"] * 100, 2),
    "%"
)

print(
    "Best validation macro F1:",
    round(results[best_name]["macro_f1"] * 100, 2),
    "%"
)

# -----------------------------------
# 9. FINAL TEST EVALUATION
# -----------------------------------

test_predictions = best_model.predict(test_text)

test_accuracy = accuracy_score(
    test_labels,
    test_predictions
)

test_macro_f1 = f1_score(
    test_labels,
    test_predictions,
    average="macro",
    zero_division=0
)

test_weighted_f1 = f1_score(
    test_labels,
    test_predictions,
    average="weighted",
    zero_division=0
)

print("\nFINAL TEST RESULTS")

print("Selected model:", best_name)
print("Test accuracy:", round(test_accuracy * 100, 2), "%")
print("Test macro F1:", round(test_macro_f1 * 100, 2), "%")
print("Test weighted F1:", round(test_weighted_f1 * 100, 2), "%")

print("\nCLASSIFICATION REPORT")

print(
    classification_report(
        test_labels,
        test_predictions,
        zero_division=0
    )
)

print("\nCONFUSION MATRIX")

labels = sorted(set(test_labels))

print("Category order:", labels)

print(
    confusion_matrix(
        test_labels,
        test_predictions,
        labels=labels
    )
)

# -----------------------------------
# 10. SAVE MODEL
# -----------------------------------

os.makedirs("models", exist_ok=True)

model_path = (
    "models/resq_disaster_classifier_experiment4.pkl"
)

joblib.dump(best_model, model_path)

print("\nMODEL SAVED SUCCESSFULLY")
print("Path:", model_path)

# -----------------------------------
# 11. TEST SAMPLE REPORT
# -----------------------------------

sample = (
    "Families are stranded due to severe flooding. "
    "We urgently need boats and food for rescue."
)

sample_prediction = best_model.predict([sample])[0]

print("\nSAMPLE PREDICTION")
print("Report:", sample)
print("Predicted category:", sample_prediction)

print("\nRESQ MODEL TRAINING COMPLETED!")

