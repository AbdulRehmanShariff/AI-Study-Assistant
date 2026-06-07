import sys
sys.path.insert(0, 'C:\\AI Study Assistant\\backend')
from config.database import Database

Database.connect()
db = Database.get_db()
print(f"Documents: {db.documents.count_documents({})}")
for doc in db.documents.find():
    print(f" - {doc['_id']} : {doc['original_name']} : {doc['status']}")

print(f"Chunks: {db.chunks.count_documents({})}")
