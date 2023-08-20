from models.database import engine, metadata
from models.questions import questions_answers, generated_answers

metadata.create_all(bind=engine)
print("Tables created successfully!")
