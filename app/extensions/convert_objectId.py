from bson import ObjectId

# Função auxiliar para converter ObjectId para string
def convert_objectid(data):
    if isinstance(data, list):
        for item in data:
            convert_objectid(item)
    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, ObjectId):
                data[key] = str(value)
            elif isinstance(value, (dict, list)):
                convert_objectid(value)