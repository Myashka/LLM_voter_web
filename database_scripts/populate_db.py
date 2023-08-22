import argparse
import pandas as pd
from sqlalchemy import insert
from models.database import engine
from models.questions import questions_answers, generated_answers
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO)


def get_csv_id_from_filename(filename):
    """Извлекает идентификатор CSV из имени файла."""
    try:
        return int(filename.split("_")[-1].split(".")[0])
    except (IndexError, ValueError):
        logging.error(f"Unable to extract CSV ID from filename: {filename}")
        return None


def populate_database(csv_path):
    df = pd.read_csv(csv_path, lineterminator="\n")
    csv_id = get_csv_id_from_filename(csv_path.split("/")[-1])

    if not csv_id:
        logging.error("Failed to process the file due to invalid filename format.")
        return

    if df.empty:
        logging.info("CSV file is empty. Exiting...")
        return

    processed_q_ids = {}

    logging.info(f"Starting to populate the database with {len(df)} rows from the CSV.")

    with engine.begin() as connection:
        for index, row in df.iterrows():
            q_id = int(row["Q_Id"])

            # Если этот Q_Id еще не был обработан
            if q_id not in processed_q_ids or csv_id not in processed_q_ids[q_id]:
                # Добавляем запись в таблицу questions_answers
                stmt = insert(questions_answers).values(
                    q_id=row["Q_Id"],
                    title=row["Title"],
                    question=row["Question"],
                    answer=row["Answer"],
                    csv_id=csv_id,
                )
                try:
                    result = connection.execute(stmt)
                except Exception as e:
                    logging.error(f"Error while inserting data: {e}")
                qa_id = result.inserted_primary_key[0]
                if q_id not in processed_q_ids:
                    processed_q_ids[q_id] = [csv_id]
                else:
                    processed_q_ids[q_id].append(csv_id)

                logging.info(
                    f"Added question with Q_Id {q_id} and Title '{row['Title'][:20]}...' to the database."
                )
            else:
                # Получаем qa_id для текущего Q_Id
                s = questions_answers.select().where(
                    (questions_answers.c.q_id == q_id)
                    & (questions_answers.c.csv_id == csv_id)
                )
                qa_id = connection.execute(s).fetchone()[0]

            # Добавляем сгенерированный ответ в таблицу generated_answers
            stmt = insert(generated_answers).values(
                qa_id=qa_id,
                generated_answer=row["Generated Answer"],
                csv_gen_id=row["Gen_Q_Id"],  # обновляем название поля на csv_gen_id
            )
            connection.execute(stmt)
            logging.info(f"Added generated answer for Q_Id {q_id}.")

    logging.info("Finished populating DB")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Populate the database with data from a CSV file."
    )
    parser.add_argument("csv_path", type=str, help="Path to the CSV file.")
    args = parser.parse_args()
    populate_database(args.csv_path)
