from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Employee(BaseModel):
    employee_id : str
    name : str
    department : str
    salary: float
    joining_date: datetime
    skills: List[str]


class UpdateEmployee(BaseModel):
    name : Optional[str] = None
    department : Optional[str] = None
    salary : Optional[float] = None
    joining_date : Optional[datetime] = None
    skills : Optional[List[str]] = None


