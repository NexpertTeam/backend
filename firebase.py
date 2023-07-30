import firebase_admin
from firebase_admin import credentials, firestore


class Firebase:
    def __init__(self):
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()
    
    def read_from_collection(self, collection_name: str):
        collections = self.db.collection(collection_name)
        docs = collections.get()
        for doc in docs:
            print(doc.to_dict())
        
    def write_data_to_collection(self, collection_name: str, document_id: str, data):
        collection_ref = self.db.collection(collection_name)
        doc_ref = collection_ref.document(document_id).set(data)
        print(f"Document added: {doc_ref}")

    def delete_data_from_collection(self, collection_name, document_id):
        try:
            doc_ref = self.db.collection(collection_name).document(document_id)
            doc_ref.delete()
            print(f"Document {document_id} successfully deleted from {collection_name} collection.")
        except Exception as e:
            print(f"An error occurred: {e}")

firestore_client = Firebase()

def get_firestore_client():
    return firestore_client