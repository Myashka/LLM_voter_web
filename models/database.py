from sqlalchemy import create_engine, MetaData

DATABASE_URL = "sqlite:///./databases/questions_answers.db"

engine = create_engine(DATABASE_URL)
metadata = MetaData()