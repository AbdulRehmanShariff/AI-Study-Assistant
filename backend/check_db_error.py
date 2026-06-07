from config.database import Database

Database.connect()
col = Database.get_collection('documents')

docs = col.find({'status': 'error'})
for d in docs:
    print("ID:", d['_id'])
    print("Error:", d.get('processing_error'))
    print("---")
