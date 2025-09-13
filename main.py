from fastapi import FastAPI, HTTPException
from database import employees_collection
from models import Employee, UpdateEmployee

app = FastAPI()

# Create Employee data
@app.post("/employees")
async def create_employee(emp : Employee):
    if await employees_collection.find_one({"employee_id": emp.employee_id}):
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    await employees_collection.insert_one(emp.model_dump())
    return {"message": "Employee created successfully"}


# Get Employee by Id
@app.get("/get/employees/{employee_id}")
async def get_employee(employee_id : str):
    emp = await employees_collection.find_one({"employee_id" : employee_id})
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    emp["_id"] = str(emp["_id"])
    return emp


# Update Employees
@app.put("/update/employees/{employee_id}")
async def update_employee(employee_id: str, updates: UpdateEmployee):
    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
    result = await employees_collection.update_one({"employee_id": employee_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee updated successfully"}


# delete Employee
@app.delete("/delete/employees/{employee_id}")
async def delete_employee(employee_id : str):
    result = await employees_collection.delete_one({"employee_id":employee_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}





# Querying and Aggregation

# List Employees by Department sorted by joining_date desc
@app.get("/employees")
async def list_by_department(
    department: str = None,
    skip: int = 0,
    limit: int = 10
):
    query = {"department": department} if department else {}
    cursor = (
        employees_collection.find(query)
        .sort("joining_date", -1)
        .skip(skip)
        .limit(limit)
    )
    employees = await cursor.to_list(length=limit)
    for emp in employees:
        emp["_id"] = str(emp["_id"])
    return {
        "skip": skip,
        "limit": limit,
        "count": len(employees),
        "data": employees
    }


# Average salary by department(Aggregation)
@app.get("/employees/avg_salary")
async def avg_salary():
    pipeline = [
        {"$group": {"_id": "$department", "avg_salary": {"$avg": "$salary"}}},
        {"$project": {"department": "$_id", "avg_salary": 1, "_id": 0}}
        ]
    result = await employees_collection.aggregate(pipeline).to_list(length=100)
    return result

# Search Employees by Skill
@app.get("/employees/search")
async def search_by_skill (skill:str):
    cursor = employees_collection.find({"skills":skill})
    employees = await cursor.to_list(length=100)
    for emp in employees:
        emp["_id"] = str(emp["_id"])
    return employees