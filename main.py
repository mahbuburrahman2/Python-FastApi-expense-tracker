from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, Field
from typing import Annotated, Optional
import json

app = FastAPI()


class Expense(BaseModel):
    id: Annotated[
        str,
        Field(..., description="ID of the expense", example="E001")
    ]
    name: Annotated[
        str,
        Field(..., description="Name of the expense", example="Lunch")
    ]
    amount: Annotated[
        int,
        Field(..., description="Amount of the expense", example=500)
    ]
    category: Annotated[
        str,
        Field(..., description="Category of the expense", example="Food")
    ]
    date: Annotated[
        str,
        Field(..., description="Date of the expense", example="2026-08-01")
    ]
    description: Annotated[
        str,
        Field(..., description="Description of the expense", example="Lunch at restaurant")
    ]


class ExpenseUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    amount: Annotated[Optional[int], Field(default=None)]
    category: Annotated[Optional[str], Field(default=None)]
    date: Annotated[Optional[str], Field(default=None)]
    description: Annotated[Optional[str], Field(default=None)]


def load_data():
    with open("expenses.json", "r") as f:
        data = json.load(f)
    return data


def save_data(data):
    with open("expenses.json", "w") as f:
        json.dump(data, f, indent=4)


@app.get("/hello")
def hello():
    return "Hi"


@app.get("/about")
def about():
    return "This is the about page."


@app.get("/view")
def view_expenses():
    data = load_data()
    return data


@app.get("/view/{expense_id}")
def view_specific_expense(
    expense_id: str = Path(
        ...,
        description="The ID of the expense",
        example="E001"
    )
):
    data = load_data()

    if expense_id in data:
        return data[expense_id]
    else:
        raise HTTPException(
            status_code=404,
            detail="Expense not found."
        )


@app.get("/sort")
def view_sorted_expenses(sorted_by: str, order: str):
    data = load_data()

    if sorted_by not in ["name", "amount", "category", "date", "description"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid sorting field."
        )

    sorted_data = list(data.values())

    def get_value(expense):
        return expense[sorted_by]

    if order == "asc":
        sorted_data.sort(key=get_value)
    elif order == "desc":
        sorted_data.sort(key=get_value, reverse=True)
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid order. Use asc or desc."
        )

    return sorted_data


@app.post("/create")
def create_expense(expense: Expense):
    data = load_data()

    if expense.id in data:
        raise HTTPException(
            status_code=400,
            detail="Expense already exists"
        )

    data[expense.id] = expense.model_dump(exclude=["id"])

    save_data(data)

    return {
        "message": "Expense created successfully",
        "expense": expense
    }


@app.put("/edit/{expense_id}")
def update_expense(
    expense_id: str,
    expense: ExpenseUpdate
):
    data = load_data()

    if expense_id not in data:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    update_data = expense.model_dump(exclude_unset=True)

    data[expense_id].update(update_data)

    save_data(data)

    return {
        "message": "Expense updated successfully",
        "expense": data[expense_id]
    }


@app.delete("/delete/{expense_id}")
def delete_expense(expense_id: str):
    data = load_data()

    if expense_id not in data:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    del data[expense_id]

    save_data(data)

    return {
        "message": "Expense deleted successfully"
    }