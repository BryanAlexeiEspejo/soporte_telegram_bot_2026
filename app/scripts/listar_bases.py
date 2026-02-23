# listar_bases.py
from pymongo import MongoClient

# PONER LA URI DE LA EMPRESA AQUÍ o usar variable de entorno DEST_MONGO_URI
DEST_URI = "mongodb://admindbmongo:MngrMng!2024@192.168.7.43:27017"

def main():
    client = MongoClient(DEST_URI)
    admin = client.admin
    dbs = admin.command("listDatabases")
    print("Bases disponibles en el servidor de la empresa:")
    for db in dbs.get("databases", []):
        print(" -", db.get("name"))
    client.close()

if __name__ == "__main__":
    main()
