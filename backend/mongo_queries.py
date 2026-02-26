# mongo_queries.py
# Las 3 consultas principales a MongoDB para analizar el uso del sistema
# Para ejecutar directamente: python mongo_queries.py

from database import get_mongo_db  # Importa la función que conecta a MongoDB

# Consulta 1: encuentra los usuarios que más han usado el chat
def consulta_1_top_usuarios():
    db = get_mongo_db()  # Abre conexión a MongoDB
    
    resultado = db.chat_logs.aggregate([
        # $group agrupa todos los documentos por el campo usuario y cuenta cuántos hay
        {"$group": {"_id": "$usuario", "total": {"$sum": 1}}},
        # $sort ordena de mayor a menor según el total de chats
        {"$sort": {"total": -1}},
        # $limit muestra solo los 5 usuarios con más chats
        {"$limit": 5}
    ])
    return list(resultado)

# Consulta 2: muestra cuántos chats y tokens se usaron cada día
def consulta_2_logs_por_fecha():
    db = get_mongo_db()
    
    resultado = db.chat_logs.aggregate([
        {"$group": {
            # Toma solo los primeros 10 caracteres de la fecha para quedarse con YYYY-MM-DD
            "_id": {"$substr": ["$fecha", 0, 10]},
            # Cuenta cuántos chats hubo ese día
            "total_chats": {"$sum": 1},
            # Suma todos los tokens consumidos ese día
            "total_tokens": {"$sum": "$tokens"}
        }},
        # Ordena de más reciente a más antiguo
        {"$sort": {"_id": -1}}
    ])
    return list(resultado)

# Consulta 3: calcula cuánto tarda en promedio cada tipo de consulta
def consulta_3_latencia_promedio():
    db = get_mongo_db()
    
    resultado = db.chat_logs.aggregate([
        {"$group": {
            # Agrupa por tipo de consulta: chat general o RAG
            "_id": "$tipo",
            # Calcula el promedio de latencia para cada tipo
            "latencia_promedio": {"$avg": "$latencia"},
            # Cuenta cuántas consultas hay de cada tipo
            "total": {"$sum": 1}
        }}
    ])
    return list(resultado)

if __name__ == "__main__":
    # Este bloque solo corre si ejecutas directamente: python mongo_queries.py
    
    print("📊 Top usuarios:")
    for r in consulta_1_top_usuarios():
        print(f"  {r['_id']}: {r['total']} chats")
    
    print("\n📅 Chats por fecha:")
    for r in consulta_2_logs_por_fecha():
        print(f"  {r['_id']}: {r['total_chats']} chats")
    
    print("\n⏱️ Latencia promedio:")
    for r in consulta_3_latencia_promedio():
        print(f"  {r['_id']}: {r['latencia_promedio']}s")