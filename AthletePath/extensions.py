"""Shared MongoDB connection for API modules."""
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)
db = client["AthletePath"]
