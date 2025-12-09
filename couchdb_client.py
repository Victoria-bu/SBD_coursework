import couchdb
from config import Config
from datetime import datetime

class CouchDBClient:
    def __init__(self):
        self.server = couchdb.Server(Config.COUCHDB_URL)
        if Config.COUCHDB_DB not in self.server:
            self.db = self.server.create(Config.COUCHDB_DB)
        else:
            self.db = self.server[Config.COUCHDB_DB]

    def save_certificate(self, tenant_id, pdf_bytes):

        # Створюємо запис у CouchDB
        doc = {
            "tenant_id": tenant_id,
            "created_at": datetime.now().isoformat(),
            "type": "certificate"
        }

        doc_id, doc_rev = self.db.save(doc)

        # Отримуємо документ з БД
        stored_doc = self.db[doc_id]

        # Додаємо PDF як вкладення
        self.db.put_attachment(
            stored_doc,
            content=pdf_bytes,
            filename=f"certificate_{tenant_id}.pdf",
            content_type="application/pdf"
        )

        return doc_id

    def save_district_report(self, street_id, pdf_bytes):
        doc = {
            "street_id": street_id,
            "created_at": datetime.now().isoformat(),
            "type": "district_report"
        }
    
        doc_id, doc_rev = self.db.save(doc)
    
        stored_doc = self.db[doc_id]
    
        self.db.put_attachment(
            stored_doc,
            content=pdf_bytes,
            filename=f"district_report_{street_id}.pdf",
            content_type="application/pdf"
        )
    
        return doc_id

