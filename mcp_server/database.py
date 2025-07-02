from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from .config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():
    """Generator to provide a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_schema(session):
    """Function to get the database schema as a string."""
    query = """
    SELECT table_name, column_name, data_type
    FROM information_schema.columns
    WHERE table_schema = 'public'
    ORDER BY table_name, ordinal_position;
    """
    try:
        result = session.execute(text(query))
        schema_str = ""
        current_table = ""
        for row in result:
            table_name, column_name, data_type = row
            if table_name != current_table:
                if current_table:
                    schema_str += "\n"
                schema_str += f"Table: {table_name}\n"
                current_table = table_name
            schema_str += f"  - {column_name}: {data_type}\n"
        return schema_str
    except SQLAlchemyError as e:
        print(f"Error fetching schema: {e}")
        return "Error: Could not retrieve database schema."

def execute_sql_query(session, sql_query: str):
    """Executes a SQL query and returns the result."""
    try:
        result = session.execute(text(sql_query))
        if result.returns_rows:
            rows = result.fetchall()
            return "\n".join([str(row) for row in rows])
        else:
            session.commit()
            return "Query executed successfully."
    except SQLAlchemyError as e:
        session.rollback()
        return f"Error executing query: {e}" 