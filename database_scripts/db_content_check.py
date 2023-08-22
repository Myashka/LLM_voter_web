from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, distinct
from models.database import engine
from models.questions import questions_answers, generated_answers, user_ratings_table
from collections import defaultdict


def get_table_content():
    Session = sessionmaker(bind=engine)
    session = Session()

    # 1. Unique q_id counts for each csv_id
    unique_qid_counts = (
        session.query(
            questions_answers.c.csv_id, func.count(distinct(questions_answers.c.q_id))
        )
        .group_by(questions_answers.c.csv_id)
        .all()
    )

    print("Unique q_id counts for each csv_id:")
    for csv_id, count in unique_qid_counts:
        print(f"csv_id {csv_id}: {count} unique q_id")

    # 2. Rating counts for each csv_id
    rating_counts_per_csv = defaultdict(lambda: defaultdict(int))
    fully_rated_qa_counts = session.query(
        questions_answers.c.csv_id,
        questions_answers.c.qa_id,
        questions_answers.c.rating_count,
    ).all()

    for csv_id, qa_id, rating_count in fully_rated_qa_counts:
        rating_counts_per_csv[csv_id][rating_count] += 1

    print("Rating counts for each csv_id:")
    for csv_id, counts in rating_counts_per_csv.items():
        print(f"csv_id {csv_id}:")
        for rating_count, question_count in counts.items():
            print(f"   {rating_count} ratings: {question_count} questions")

    session.close()


if __name__ == "__main__":
    get_table_content()
