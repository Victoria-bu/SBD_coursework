import couchdb
from config import Config
from datetime import datetime

COUCHDB_URL = "http://admin:28102005@localhost:5984/"
DB_NAME = "certificates"

class CouchDBClient:
    def __init__(self):
        self.server = couchdb.Server(Config.COUCHDB_URL)
        if Config.COUCHDB_DB not in self.server:
            self.db = self.server.create(Config.COUCHDB_DB)
        else:
            self.db = self.server[Config.COUCHDB_DB]

    def save_certificate(self, tenant_id, pdf_bytes):

        # 1. Створюємо запис у CouchDB
        doc = {
            "tenant_id": tenant_id,
            "created_at": datetime.now().isoformat(),
            "type": "certificate"
        }

        doc_id, doc_rev = self.db.save(doc)

        # 2. Отримуємо документ з БД
        stored_doc = self.db[doc_id]

        # 3. Додаємо PDF як вкладення
        self.db.put_attachment(
            stored_doc,
            content=pdf_bytes,
            filename=f"certificate_{tenant_id}.pdf",
            content_type="application/pdf"
        )

        return doc_id
