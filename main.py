from fastapi import FastAPI, Form, Request
from fastapi import FastAPI, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import List
import csv
import io
import os

print("Current working directory:", os.getcwd())


app = FastAPI()

# SQLite Database Configuration
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define the Users table
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("name", String, index=True),
    Column("age", Integer),
)

# Create the database and tables
metadata.create_all(engine)

# Pydantic model for CSV data
class CSVData(BaseModel):
    content: List[List[str]]

# Jinja2 Templates Configuration
templates = Jinja2Templates(directory="templates")



# Process CSV file and save data to SQLite database
@app.post("/upload")
async def upload_file(request: Request, file: UploadFile = Form(...), name_col: int = Form(...), age_col: int = Form(...)):
    try:
        content = await file.read()
        csv_data = read_csv(content.decode())
        
        # Extract name and age columns
        names = [row[name_col] for row in csv_data]
        ages = [row[age_col] for row in csv_data]

        # Save data to SQLite database
        db = SessionLocal()
        try:
            for name, age in zip(names, ages):
                db.execute(users.insert().values(name=name, age=age))
            db.commit()
        finally:
            db.close()

        return {"message": "Data uploaded successfully"}
    except Exception as e:
        return {"error": str(e)}



# Home route to upload CSV file
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Process CSV file and save data to SQLite database
@app.post("/upload")
async def upload_file(request: Request, file: UploadFile = Form(...), name_col: int = Form(...), age_col: int = Form(...)):
    content = await file.read()
    csv_data = read_csv(content.decode())
    
    # Extract name and age columns
    names = [row[name_col] for row in csv_data]
    ages = [row[age_col] for row in csv_data]

    # Save data to SQLite database
    db = SessionLocal()
    try:
        for name, age in zip(names, ages):
            db.execute(users.insert().values(name=name, age=age))
        db.commit()
    finally:
        db.close()

    return {"message": "Data uploaded successfully"}


# Helper function to read CSV content
def read_csv(csv_content: str):
    csv_file = io.StringIO(csv_content)
    csv_reader = csv.reader(csv_file)
    return list(csv_reader)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
