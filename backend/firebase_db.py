import firebase_admin
from firebase_admin import credentials, firestore

try:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    FIREBASE_ENABLED = True
except Exception as e:
    print("Firebase disabled:", e)
    FIREBASE_ENABLED = False

def log_question(question, answer):
    if not FIREBASE_ENABLED:
        return
    db.collection("queries").add({
        "question": question,
        "answer": answer
    })
