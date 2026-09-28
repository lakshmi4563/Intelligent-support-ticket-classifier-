from pathlib import Path
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report, confusion_matrix

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "dataset-tickets-multi-lang3-4k.csv"
MODEL_PATH = ROOT / "backend" / "model" / "ticket_classifier.pkl"

df = pd.read_csv(DATA_PATH)
print("Original shape:", df.shape)
print(df["queue"].value_counts())

df = df[df["language"] == "en"][["subject", "body", "queue"]].copy()
df["text"] = (df["subject"].fillna("") + " " + df["body"].fillna("")).str.strip()
df = df[df["text"] != ""]

category_mapping = {
    "Technical Support": "Technical",
    "IT Support": "Technical",
    "Service Outages and Maintenance": "Technical",
    "Billing and Payments": "Billing",
    "Customer Service": "General Inquiry",
    "Product Support": "General Inquiry",
    "General Inquiry": "General Inquiry",
    "Returns and Exchanges": "General Inquiry",
    "Sales and Pre-Sales": "General Inquiry",
}
df["category"] = df["queue"].map(category_mapping)
df = df.dropna(subset=["category"]).drop_duplicates(subset="text")

print("\nFinal shape:", df.shape)
print(df["category"].value_counts())

X, y = df["text"], df["category"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True,
                              min_df=2, stop_words="english")),
    ("svm", LinearSVC(class_weight="balanced", C=1.0)),
])
pipeline.fit(X_train, y_train)

pred = pipeline.predict(X_test)
print("\nClassification report:")
print(classification_report(y_test, pred, zero_division=0))
print("Confusion matrix:")
print(confusion_matrix(y_test, pred))
print("Accuracy:", accuracy_score(y_test, pred))

cv = cross_val_score(pipeline, X, y, cv=5, scoring="f1_macro")
print(f"\n5-fold CV macro F1: {cv.mean():.3f} (+/- {cv.std():.3f})")

MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(pipeline, MODEL_PATH)
print("Saved:", MODEL_PATH)

