# scripts/migrar_feedback.py   (VERSIÓN CORREGIDA sin no_cursor_timeout)
import os
from pymongo import MongoClient, errors
from dotenv import load_dotenv

load_dotenv()  # carga variables desde .env si existen

# ---- Configuración (se leen desde .env si están) ----
SOURCE_URI = os.getenv("MONGO_URI")  # tu Atlas (REQUIRED)
SOURCE_DB = os.getenv("MONGO_DB", "ami")
SOURCE_COLLECTION = os.getenv("FEEDBACK_COLLECTION", "feedback_chatbot")

DEST_URI = os.getenv("DEST_MONGO_URI", "mongodb://admindbmongo:MngrMng!2024@192.168.7.43:27017")
DEST_DB = os.getenv("DEST_DB", "parqueos")
DEST_COLLECTION = os.getenv("DEST_COLLECTION", SOURCE_COLLECTION)

BATCH_SIZE = int(os.getenv("MIGRATE_BATCH_SIZE", "500"))

def migrate():
    if not SOURCE_URI:
        print("ERROR: No se ha configurado SOURCE_URI (MONGO_URI). Añádelo al .env.")
        return

    print("Conectando a origen (Atlas)...")
    src_client = MongoClient(SOURCE_URI)
    print("Conectando a destino (empresa)...")
    dst_client = MongoClient(DEST_URI)

    try:
        src_col = src_client[SOURCE_DB][SOURCE_COLLECTION]
        dst_col = dst_client[DEST_DB][DEST_COLLECTION]

        total = src_col.count_documents({})
        print(f"Documentos encontrados en origen: {total}")

        if total == 0:
            print("No hay documentos para migrar. Saliendo.")
            return

        migrated = 0
        print("Iniciando migración por paginación (skip/limit)...")
        for skip in range(0, total, BATCH_SIZE):
            docs = list(src_col.find({}).skip(skip).limit(BATCH_SIZE))
            if not docs:
                break

            for d in docs:
                d.pop("_id", None)

            try:
                dst_col.insert_many(docs, ordered=False)
                migrated += len(docs)
                print(f"  -> Migrados: {migrated}/{total}")
            except errors.BulkWriteError as bwe:
                print("  -> BulkWriteError (se ignoraron duplicados/u otros errores):", str(bwe.details or bwe))
                migrated += len(docs)
                print(f"  -> Aproximado migrados: {migrated}/{total}")

        print("Migración completada ✅")
        print(f"Total aproximado migrado: {migrated} (origen tenía {total})")

    except Exception as e:
        print("ERROR durante la migración:", str(e))
    finally:
        src_client.close()
        dst_client.close()

if __name__ == "__main__":
    migrate()
