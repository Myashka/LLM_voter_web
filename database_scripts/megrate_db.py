import argparse
import pandas as pd
from sqlalchemy import select
from models.database import engine
from models.questions import questions_answers, generated_answers, user_ratings_table
import logging

logging.basicConfig(level=logging.INFO)


def update_csv_from_db(csv_path):
    df = pd.read_csv(csv_path)

    if "rank" not in df.columns:
        df["rank"] = None
    if "correct" not in df.columns:
        df["correct"] = None

    # Запрос данных из базы данных
    with engine.connect() as connection:
        query = select(
            questions_answers.c.q_id,
            generated_answers.c.csv_gen_id,
            user_ratings_table.c.rating_value,
            user_ratings_table.c.rights,
        ).select_from(
            questions_answers.join(
                generated_answers,
                questions_answers.c.qa_id == generated_answers.c.qa_id,
            ).join(
                user_ratings_table,
                generated_answers.c.gen_id == user_ratings_table.c.gen_id,
            )
        )
        ratings_data = connection.execute(query).fetchall()

    updated_rows = 0
    for q_id, csv_gen_id, rating_value, rights in ratings_data:
        # Проверка наличия значений rank и correct
        mask = (df["Q_Id"] == q_id) & (df["Gen_Q_Id"] == csv_gen_id)
        if df.loc[mask, "rank"].isna().all() and df.loc[mask, "correct"].isna().all():
            df.loc[mask, "rank"] = rating_value
            df.loc[mask, "correct"] = rights
            updated_rows += 1

    if updated_rows > 0:
        df.to_csv(csv_path, index=False)
        logging.info(f"CSV file {csv_path} has been updated.")
        logging.info(f"Total rows updated: {updated_rows}")
    else:
        logging.info("No rows were updated.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update CSV from the database.")
    parser.add_argument("csv_path", type=str, help="Path to the CSV file.")
    args = parser.parse_args()
    update_csv_from_db(args.csv_path)
