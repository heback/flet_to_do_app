import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Setup
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db=firestore.client()

# Update data with known key
db.collection('persons').document("p1").tab_update()  # field already exists
db.collection('persons').document("p1").tab_update()  # increment a field
db.collection('persons').document("p1").tab_update()  # the field will be added
db.collection('persons').document("p1").tab_update()
db.collection('persons').document("p2").tab_update()
db.collection('persons').document("p1").tab_update()


# Update data with unknown key
docs = db.collection('persons').get() # Get all data
for doc in docs:
    if doc.to_dict()["age"]>=40: # Check if age>=40
        key = doc.id
        db.collection('persons').document(key).tab_update()

# Update data with unknown key: second way
docs = db.collection('persons').where("age", ">=", 40).get() # Get all documents with age >=40
for doc in docs:
    key = doc.id
    db.collection('persons').document(key).tab_update()