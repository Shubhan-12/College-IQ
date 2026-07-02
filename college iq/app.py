from flask import Flask, request, jsonify
import pickle
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import re
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 🔥 OPENAI
from openai import OpenAI

# ⚠️ IMPORTANT: set this in terminal instead of hardcoding
# export OPENAI_API_KEY="your_key_here"
from openai import OpenAI

client = OpenAI(api_key="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")
app = Flask(__name__)

# =========================
# LOAD ML MODELS
# =========================
reg_model = pickle.load(open("regression_model.pkl", "rb"))
log_model = pickle.load(open("logistic_model.pkl", "rb"))
kmeans_model = pickle.load(open("kmeans_model.pkl", "rb"))

features = ['attendance', 'study_hours', 'internal_marks', 'assignments']

cluster_map = {
    0: "Top Performer",
    1: "Average",
    2: "At Risk"
}

# =========================
# HELPERS
# =========================
def clean(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, list):
        return [clean(i) for i in obj]
    if isinstance(obj, dict):
        return {k: clean(v) for k, v in obj.items()}
    return obj

def validate_input(data):
    try:
        for f in features:
            if f not in data:
                return False, f"Missing field: {f}"
            float(data[f])
        return True, None
    except:
        return False, "Invalid input values"

def performance_trend():
    return [int(x) for x in np.random.randint(60, 90, 6)]

# =========================
# ROUTES
# =========================

@app.route("/")
def home():
    return "College IQ API Running"

# ---------- DASHBOARD ----------
@app.route("/dashboard", methods=["POST"])
def dashboard():

    data = request.json

    valid, error = validate_input(data)
    if not valid:
        return jsonify({"error": error})

    df = pd.DataFrame([[data[f] for f in features]], columns=features)

    marks = float(reg_model.predict(df)[0])
    prob = float(log_model.predict_proba(df)[0][1] * 100)
    cluster = int(kmeans_model.predict(df)[0])

    return jsonify(clean({
        "predicted_marks": round(marks, 2),
        "pass_probability": round(prob, 2),
        "student_type": cluster_map[cluster],
        "trend": performance_trend(),
        "suggestions": [
            "Study consistently",
            "Improve weak areas",
            "Focus on high weight topics"
        ],
        "insights": [
            "Study hours strongly impact performance",
            "Internal marks matter a lot"
        ]
    }))

# ---------- GOAL ----------
@app.route("/goal", methods=["POST"])
def goal():

    data = request.json

    try:
        target = float(data.get("target_marks", 0))
        attendance = float(data.get("attendance", 0))
        study_hours = float(data.get("study_hours", 0))
        internal = float(data.get("internal_marks", 0))
        assignments = float(data.get("assignments", 0))

        # 📊 ML Prediction
        df = pd.DataFrame([[attendance, study_hours, internal, assignments]], columns=features)
        current_marks = float(reg_model.predict(df)[0])

        expected_marks = current_marks + (study_hours * 1.5)
        gap = target - expected_marks

        plan = []

        # 🎯 1. ATTENDANCE ANALYSIS
        if attendance < 75:
            plan.append("⚠️ Attendance is low → attend classes regularly (minimum 75%)")
        elif attendance < 85:
            plan.append("📌 Try to improve attendance to 85% for internal boost")
        else:
            plan.append("✅ Good attendance maintained")

        # 📘 2. INTERNAL MARKS ANALYSIS
        if internal < 60:
            plan.append("📘 Focus on internals → revise class notes + unit tests")
        elif internal < 75:
            plan.append("📘 Improve internals by practicing important questions")
        else:
            plan.append("✅ Strong internal performance")

        # 📚 3. STUDY HOURS ANALYSIS
        if study_hours < 2:
            plan.append("⏱ Increase study time to at least 3–4 hrs daily")
        elif study_hours < 4:
            plan.append("⏱ Slightly increase study hours for better results")
        else:
            plan.append("✅ Study effort is good")

        # 📝 4. ASSIGNMENTS ANALYSIS
        if assignments < 60:
            plan.append("📝 Complete assignments seriously—they carry marks")
        else:
            plan.append("✅ Assignments performance is fine")

        # 🎯 5. GAP-BASED STRATEGY
        if gap > 20:
            plan.append("🔥 Target is far → aggressive preparation required")
        elif gap > 10:
            plan.append("⚡ Moderate gap → consistent study can achieve target")
        elif gap > 0:
            plan.append("🎯 Very close → focus on revision + accuracy")
        else:
            plan.append("🏆 You are already on track!")

        return jsonify({
            "current_marks": round(current_marks, 2),
            "expected_marks": round(expected_marks, 2),
            "target_marks": target,
            "gap": round(gap, 2),
            "student_profile": {
                "attendance": attendance,
                "study_hours": study_hours,
                "internal_marks": internal,
                "assignments": assignments
            },
            "personalized_plan": plan
        })

    except Exception as e:
        return jsonify({"error": str(e)})
# ---------- 🔥 AI PLAN TASK ----------
@app.route("/plan-task", methods=["POST"])
def plan_task():

    data = request.json

    task = data.get("task_name", "Study")
    difficulty = data.get("difficulty", "medium")
    due_date = data.get("due_date")

    start = datetime.today()
    due = datetime.strptime(due_date, "%Y-%m-%d")
    days = (due - start).days + 1

    if days <= 0:
        return jsonify({"error": "Invalid due date"})

    # -----------------------------
    # 🔥 TRY AI FIRST
    # -----------------------------
    plan = None

    try:
        prompt = f"""
        Create a {days}-day study plan for: {task}
        Difficulty: {difficulty}

        Rules:
        - Use REAL topics (not generic like basics/revision)
        - Return ONLY JSON

        Format:
        [
          {{"day": 1, "topic": "Arrays"}},
          {{"day": 2, "topic": "Recursion"}}
        ]
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        text = response.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "")

        plan = json.loads(text)

        print("AI PLAN SUCCESS")

    except Exception as e:
        print("AI FAILED:", str(e))

    # -----------------------------
    # 🔁 FALLBACK IF AI FAILS
    # -----------------------------
    if not plan:

        def get_topics(task):
            t = task.lower()

            if "dsa" in t:
                return [
                    "Arrays", "Strings", "Linked List", "Stack", "Queue",
                    "Trees", "BST", "Graphs", "DFS & BFS",
                    "Recursion", "Backtracking", "Dynamic Programming"
                ]

            elif "java" in t:
                return [
                    "OOP Concepts", "Classes", "Inheritance",
                    "Polymorphism", "Collections", "Exception Handling",
                    "Multithreading"
                ]

            elif "math" in t:
                return [
                    "Algebra", "Trigonometry",
                    "Probability", "Statistics",
                    "Calculus"
                ]

            else:
                return ["Concepts", "Practice", "Revision"]

        topics = get_topics(task)

        plan = [{"day": i+1, "topic": topics[i % len(topics)]} for i in range(days)]

        print("USING FALLBACK PLAN")

    # -----------------------------
    # 🔥 BUILD FINAL RESPONSE
    # -----------------------------
    schedule = []

    for i in range(days):
        d = start + timedelta(days=i)

        topic = plan[i]["topic"] if i < len(plan) else "Study"

        hours = 2 if difficulty == "medium" else (1 if difficulty == "easy" else 3)

        schedule.append({
            "date": d.strftime("%Y-%m-%d"),
            "task": topic,
            "hours": hours,
            "status": "pending"
        })

    return jsonify({
        "task": task,
        "days": days,
        "schedule": schedule,
        "today": schedule[0]
    })
from chatbot import get_reply
import requests

# ---------------- CHATBOT ----------------
@app.route("/chat", methods=["POST"])
def chat():

    data = request.json

    message = data.get("message", "")

    reply = get_reply(message)

    return jsonify({
        "user": message,
        "reply": reply
    })


# ---------------- QUIZ ----------------
@app.route("/generate-quiz", methods=["POST"])
def generate_quiz():

    data = request.json

    topic = data.get("topic", "")

    prompt = f"""
Generate EXACTLY 5 multiple choice quiz questions about {topic}.

STRICT RULES:
- EXACTLY 5 questions
- EXACTLY 4 options per question
- ONLY ONE correct answer
- ALWAYS include Answer:
- NO markdown
- NO emojis
- NO explanations

FORMAT:

1. Question here
A) Option
B) Option
C) Option
D) Option
Answer: Correct Option

Generate all 5 completely.
"""

    try:

        response = requests.post(

            "http://localhost:11434/api/generate",

            json={
                "model": "phi3",
                "prompt": prompt,
                "stream": False
            },

            timeout=120
        )

        data = response.json()

        if "response" not in data:
            return jsonify([])

        text = data["response"]

        print("Quiz generated successfully")

        questions = []

        current_question = None
        options = []
        correct_answer = ""

        for line in text.splitlines():

            line = line.strip()

            if not line:
                continue

            # -----------------------------
            # Detect Question
            # -----------------------------
            if re.match(
                r"^(Q?\d+[\.\):]|Question\s*\d+:)",
                line,
                re.IGNORECASE
            ):

                # Save previous question
                if (
                    current_question and
                    len(options) == 4 and
                    correct_answer
                ):

                    questions.append({
                        "question": current_question,
                        "options": options,
                        "answer": correct_answer
                    })

                # Clean numbering
                current_question = re.sub(
                    r"^(Q?\d+[\.\):]\s*|Question\s*\d+:\s*)",
                    "",
                    line,
                    flags=re.IGNORECASE
                )

                options = []
                correct_answer = ""

            # -----------------------------
            # Detect Options
            # -----------------------------
            elif re.match(r"^[A-Da-d][\).]", line):

                option = re.sub(
                    r"^[A-Da-d][\).]\s*",
                    "",
                    line
                ).strip()

                options.append(option)

            # -----------------------------
            # Detect Correct Answer
            # -----------------------------
            elif line.lower().startswith("answer:"):

                correct_answer = (
                    line.split(":", 1)[1]
                    .replace("A)", "")
                    .replace("B)", "")
                    .replace("C)", "")
                    .replace("D)", "")
                    .replace("a)", "")
                    .replace("b)", "")
                    .replace("c)", "")
                    .replace("d)", "")
                    .strip()
                )

        # -----------------------------
        # Save Last Question
        # -----------------------------
        if (
            current_question and
            len(options) == 4 and
            correct_answer
        ):

            questions.append({
                "question": current_question,
                "options": options,
                "answer": correct_answer
            })

        # -----------------------------
        # Fallback Questions
        # -----------------------------
        while len(questions) < 5:

            num = len(questions) + 1

            questions.append({
                "question": f"Sample Question {num} on {topic}",
                "options": [
                    "Option A",
                    "Option B",
                    "Option C",
                    "Option D"
                ],
                "answer": "Option A"
            })

        print("FINAL QUESTIONS:")
        print(questions)

        return jsonify(questions[:5])

    except Exception as e:

        print("QUIZ ERROR:", str(e))

        return jsonify([
            {
                "question": "Quiz generation failed",
                "options": [
                    "Retry",
                    "Restart Flask",
                    "Check Ollama",
                    "Check Internet"
                ],
                "answer": "Retry"
            }
        ])
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )