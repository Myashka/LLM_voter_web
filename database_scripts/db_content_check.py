from sqlalchemy.orm import sessionmaker
from models.database import engine
from models.questions import questions_answers


def get_table_content():
    Session = sessionmaker(bind=engine)
    session = Session()

    results = session.query(
        questions_answers.c.q_id, questions_answers.c.title, questions_answers.c.status
    ).all()
    print(f"Number of records retrieved: {len(results)}")

    print("Content of 'questions_answers' table:")
    print("-" * 50)

    for question in session.query(questions_answers).all():
        print(
            f"ID: {question.q_id}, Title: {question.title}, Status: {question.status}"
        )

    session.close()


if __name__ == "__main__":
    get_table_content()
