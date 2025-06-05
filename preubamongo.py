from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime

def test_conexion_mongodb():
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI")
    
    try:
        # Intentar conexión
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Verificar conexión
        client.admin.command('ping')
        print("✅ Conexión exitosa a MongoDB")
        
        # Probar operaciones CRUD
        db = client["diagnosticos"]
        coleccion = db["resultados"]
        
        # Crear documento de prueba
        doc_prueba = {
            "empresa": "Empresa de prueba",
            "fecha": datetime.now().isoformat(),
            "test": True
        }
        
        # Insertar documento
        resultado = coleccion.insert_one(doc_prueba)
        print(f"✅ Documento insertado con ID: {resultado.inserted_id}")
        
        # Leer documento
        doc_leido = coleccion.find({})
        
        print(f"✅ Documento leído: {doc_leido[0]}")
        print(f"✅ Total de documentos en la colección: {coleccion.count_documents({})}")
       
        
        # Eliminar documento de prueba
        coleccion.delete_one({"_id": resultado.inserted_id})
        print("✅ Documento de prueba eliminado")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_conexion_mongodb()