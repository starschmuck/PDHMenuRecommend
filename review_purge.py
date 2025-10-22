import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

# Initialize Firebase
cred = credentials.Certificate("tasteful-panthers-firebase-adminsdk-fbsvc-e6f97e55eb.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def delete_seeded_reviews():
    # Use FieldFilter for modern Firestore SDK
    reviews = db.collection("reviews").where(filter=FieldFilter("test", "==", True)).stream()

    count = 0
    for r in reviews:
        r.reference.delete()
        count += 1

    print(f"✅ Deleted {count} seeded reviews")

if __name__ == "__main__":
    delete_seeded_reviews()