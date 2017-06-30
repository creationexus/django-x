'''
Created on 23-06-2014

@author: carriagadad
'''
# schemas.py
json = {
    "name": "Product",
    "properties": {
        "name": {
            "type": "string",
            "required": "true"
        },
        "price": {
            "type": "number",
            "minimum": 0,
            "required": "true"
        },
        "tags": {
            "type": "array",
            "items": {"type": "string"}
        },
        "stock": {
            "type": "object",
            "properties": {
                "warehouse": {"type": "number"},
                "retail": {"type": "number"}
            }
        }
    }
}