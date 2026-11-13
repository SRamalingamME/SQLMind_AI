import sys
from pathlib import Path

# Add project root directory to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
import os

# Load .env variables first
load_dotenv()

from sqlalchemy import create_engine, inspect
import json

# Get DATABASE_URL directly from environment
DATABASE_URL = os.getenv("DATABASE_URL")

def reflect_database_schema() -> dict:
    """Connects to PostgreSQL and extracts table definitions, columns, types, and foreign keys."""
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    schema_metadata = {}
    table_names = inspector.get_table_names()
    
    for table_name in table_names:
        table_info = {
            "columns": [],
            "foreign_keys": []
        }
        
        # Extract Column Metadata
        for col in inspector.get_columns(table_name):
            table_info["columns"].append({
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col["nullable"]
            })
            
        # Extract Foreign Key Relationships
        for fk in inspector.get_foreign_keys(table_name):
            table_info["foreign_keys"].append({
                "constrained_columns": fk["constrained_columns"],
                "referred_table": fk["referred_table"],
                "referred_columns": fk["referred_columns"]
            })
            
        schema_metadata[table_name] = table_info
        
    return schema_metadata

def assemble_llm_context(schema_metadata: dict) -> str:
    """Transforms raw schema metadata into a clean Markdown context string for the LLM with explicit guardrails."""
    markdown_context = "# Database Schema Context\n\n"
    markdown_context += "The database contains the following relational tables for an e-commerce platform:\n\n"
    
    for table_name, details in schema_metadata.items():
        markdown_context += f"## Table: `{table_name}`\n"
        
        # Add explicit guardrail instruction for the products table
        if table_name == "products":
            markdown_context += "> **CRITICAL NOTE:** `'category'` is a direct text column inside this products table (containing values like 'Electronics', 'Furniture'). There is **NO** separate `categories` relational table. Do **NOT** attempt to JOIN with a categories table.\n\n"

        markdown_context += "**Columns:**\n"
        for col in details["columns"]:
            null_str = "NULL" if col["nullable"] else "NOT NULL"
            markdown_context += f"- `{col['name']}` ({col['type']}) - {null_str}\n"
            
        if details["foreign_keys"]:
            markdown_context += "\n**Foreign Keys:**\n"
            for fk in details["foreign_keys"]:
                constrained = ", ".join(fk["constrained_columns"])
                referred_cols = ", ".join(fk["referred_columns"])
                markdown_context += f"- `{constrained}` -> `{fk['referred_table']}.{referred_cols}`\n"
                
        markdown_context += "\n---\n\n"
        
    return markdown_context

if __name__ == "__main__":
    print("Reflecting database schema...")
    metadata = reflect_database_schema()
    
    print("\nAssembling LLM Context...")
    llm_context = assemble_llm_context(metadata)
    
    print("\n=== GENERATED LLM CONTEXT ===")
    print(llm_context)
    
    # Save context to file for inspection and RAG usage
    with open("data/schema_context.md", "w", encoding="utf-8") as f:
        f.write(llm_context)
    print("Schema context successfully saved to data/schema_context.md!")