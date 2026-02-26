"""
CIACA - Consultas MongoDB demostrativas
"""
from database import get_mongo_db

def consulta_1_top_usuarios():
    """Top 5 usuarios con más chats"""
    db = get_mongo_db()
    resultado = db.chat_logs.aggregate([
        {"$group": {"_id": "$usuario", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}},
        {"$limit": 5}
    ])
    return list(resultado)

def consulta_2_logs_por_fecha():
    """Cantidad de chats agrupados por fecha"""
    db = get_mongo_db()
    resultado = db.chat_logs.aggregate([
        {"$group": {
            "_id": {"$substr": ["$fecha", 0, 10]},
            "total_chats": {"$sum": 1},
            "total_tokens": {"$sum": "$tokens"}
        }},
        {"$sort": {"_id": -1}}
    ])
    return list(resultado)

def consulta_3_latencia_promedio():
    """Latencia promedio por tipo de consulta"""
    db = get_mongo_db()
    resultado = db.chat_logs.aggregate([
        {"$group": {
            "_id": "$tipo",
            "latencia_promedio": {"$avg": "$latencia"},
            "total": {"$sum": 1}
        }}
    ])
    return list(resultado)

if __name__ == "__main__":
    print("📊 Top usuarios:")
    for r in consulta_1_top_usuarios():
        print(f"  {r['_id']}: {r['total']} chats")
    
    print("\n📅 Chats por fecha:")
    for r in consulta_2_logs_por_fecha():
        print(f"  {r['_id']}: {r['total_chats']} chats")
    
    print("\n⏱️ Latencia promedio:")
    for r in consulta_3_latencia_promedio():
        print(f"  {r['_id']}: {r['latencia_promedio']}s")