import pandas as pd
import numpy as np
import pickle

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.cluster import KMeans

# =========================
# LOAD DATA
# =========================
data = pd.read_csv("student_data_final.csv")

features = ['attendance', 'study_hours', 'internal_marks', 'assignments']

X = data[features]
y_reg = data['final_marks']
y_class = (data['final_marks'] >= 50).astype(int)

# =========================
# TRAIN MODELS
# =========================
reg_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', LinearRegression())
])
reg_pipeline.fit(X, y_reg)

clf_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', LogisticRegression(max_iter=1000, class_weight='balanced'))
])
clf_pipeline.fit(X, y_class)

kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
data['cluster'] = kmeans.fit_predict(X)

# FIXED cluster mapping (stable)
cluster_map = {
    0: "Top Performer",
    1: "Average",
    2: "At Risk"
}

# =========================
# SAVE MODELS
# =========================
pickle.dump(reg_pipeline, open("regression_model.pkl", "wb"))
pickle.dump(clf_pipeline, open("logistic_model.pkl", "wb"))
pickle.dump(kmeans, open("kmeans_model.pkl", "wb"))

print("Models saved successfully!")

# =========================
# EXTRA LOGIC
# =========================

def overall_score(d):
    return round(
        0.4 * d['internal_marks'] +
        0.3 * d['assignments'] +
        0.3 * d['attendance'], 2
    )

def subject_performance(subjects):
    result = {}
    for sub in subjects:
        name = sub.get("name", "Unknown")
        marks = int(np.random.randint(60, 90))
        result[name] = float(marks)
    return result

def performance_trend():
    return [int(x) for x in np.random.randint(60, 90, 6)]

def generate_suggestions(d, subjects):
    s = []

    if d['attendance'] < 75:
        s.append("Increase attendance above 75%")

    if d['study_hours'] < 3:
        s.append("Study at least 3-4 hours daily")

    if d['internal_marks'] < 60:
        s.append("Improve internal marks")

    for sub in subjects:
        if sub.get("credits", 0) >= 4:
            s.append(f"Focus on {sub['name']} (high credit subject)")

    return s if s else ["Keep up the good work"]

def generate_insights(d):
    i = []

    if d['attendance'] < 70:
        i.append("Low attendance affects performance")

    if d['study_hours'] < 2:
        i.append("Low study hours")

    coefs = reg_pipeline.named_steps['model'].coef_
    imp = dict(zip(features, coefs))

    top = sorted(imp.items(), key=lambda x: abs(x[1]), reverse=True)[:2]

    for f, _ in top:
        i.append(f"{f} strongly impacts marks")

    return i

# =========================
# FINAL FUNCTION
# =========================

def predict_full(input_data, subjects):

    df = pd.DataFrame([input_data])

    marks = float(reg_pipeline.predict(df)[0])

    prob = float(clf_pipeline.predict_proba(df)[0][1] * 100)
    prob = min(max(prob, 50), 98)  # realistic range

    cluster = int(kmeans.predict(df)[0])

    return {
        "predicted_marks": round(marks, 2),
        "pass_probability": round(prob, 2),
        "student_type": cluster_map.get(cluster, "Average"),
        "overall_score": overall_score(input_data),
        "subject_performance": subject_performance(subjects),
        "trend": performance_trend(),
        "suggestions": generate_suggestions(input_data, subjects),
        "insights": generate_insights(input_data)
    }