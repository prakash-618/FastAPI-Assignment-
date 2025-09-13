from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

Url = "mongodb://localhost:27017"
client  = AsyncIOMotorClient(Url)
db = client.assessment_db
employees_collection = db.employees


# JSON Schema for employees collection
EMPLOYEE_JSON_SCHEMA = {
    "bsonType": "object",
    "required": ["employee_id", "name", "department", "salary", "joining_date", "skills"],
    "properties": {
        "employee_id": {"bsonType": "string"},
        "name": {"bsonType": "string"},
        "department": {"bsonType": "string"},
        "salary": {"bsonType": ["double", "int", "long", "decimal"]},
        "joining_date": {"bsonType": "date"},
        "skills": {
            "bsonType": "array",
            "items": {"bsonType": "string"}
        }
    }
}

async def ensure_collection():
    coll_names = await db.list_collection_names()
    if "employees" not in coll_names:
        await db.create_collection(
            "employees",
            validator={"$jsonSchema": EMPLOYEE_JSON_SCHEMA},
            validationLevel="strict"
        )
    else:
        try:
            await db.command({
                "collMod": "employees",
                "validator": {"$jsonSchema": EMPLOYEE_JSON_SCHEMA},
                "validationLevel": "strict"
            })
        except Exception:
            pass

    # Unique index on employee_id
    await employees_collection.create_index("employee_id", unique=True)

# Run schema setup on import
asyncio.get_event_loop().create_task(ensure_collection())