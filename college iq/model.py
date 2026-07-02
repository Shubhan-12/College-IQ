from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

texts = ["I am tired", "I feel happy"]
labels = ["negative", "positive"]

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(texts)

model = MultinomialNB()
model.fit(X, labels)

def predict_sentiment(text):
    return model.predict(vectorizer.transform([text]))[0]