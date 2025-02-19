import pandas as pd
from pymongo import MongoClient

# Load Excel file
file_path = "output15.xlsx"  # Change to your actual file path
df = pd.read_excel(file_path, sheet_name="Sheet1")  # Adjust sheet name if needed

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Update if using a cloud database
db = client["your_database_name"]  # Create or connect to database
collection = db["your_collection_name"]  # Create or connect to collection

# Convert DataFrame to dictionary and insert into MongoDB
data = df.to_dict(orient="records")  
collection.insert_many(data)

print("Excel data successfully imported into MongoDB!")

