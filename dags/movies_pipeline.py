from airflow import DAG
from airflow.decorators import task
from airflow.utils.task_group import TaskGroup
from datetime import datetime
import pandas as pd
import os
import psycopg2


DATA_DIR = '/opt/airflow/data/raw/'
TMP_DIR = '/opt/airflow/data/tmp/'


with DAG('movies_pipeline',
         start_date=datetime(2023, 1, 1),
         schedule="@daily",
         catchup=False) as dag:

    @task
    def ingest_movies():
        movies_path = os.path.join(DATA_DIR, 'movies.csv')
        return movies_path

    @task
    def ingest_ratings():
        ratings_path = os.path.join(DATA_DIR, 'ratings.csv')
        return ratings_path

    @task
    def create_tmp_dir():
        os.makedirs(TMP_DIR, exist_ok=True)

    @task
    def transform_movies(movies_path):
        df = pd.read_csv(movies_path)
        df = df.dropna(subset=['title'])
        outpath = os.path.join(TMP_DIR, 'movies_clean.csv')
        df.to_csv(outpath, index=False)
        return outpath

    @task
    def transform_ratings(ratings_path):
        df = pd.read_csv(ratings_path)
        df = df[df['rating'] > 2.5]
        outpath = os.path.join(TMP_DIR, 'ratings_clean.csv')
        df.to_csv(outpath, index=False)
        return outpath

    @task
    def merge_data(movies_clean, ratings_clean):
        df1 = pd.read_csv(movies_clean)
        df2 = pd.read_csv(ratings_clean)
        df_merged = pd.merge(df2, df1, on='movieId')
        outpath = os.path.join(TMP_DIR, 'merged_data.csv')
        df_merged.to_csv(outpath, index=False)
        return outpath

    @task
    def load_to_postgres(merged_path):
        conn = psycopg2.connect(
            host='postgres',
            dbname='airflow',
            user='airflow',
            password='airflow'
        )
        cur = conn.cursor()
        cur.execute("""
            DROP TABLE IF EXISTS movies_ratings;
            CREATE TABLE movies_ratings (
                userId INT,
                movieId INT,
                rating FLOAT,
                timestamp BIGINT,
                title TEXT,
                genres TEXT
            );
        """)
        df = pd.read_csv(merged_path)
        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO movies_ratings (userId, movieId, rating, timestamp, title, genres)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, tuple(row))
        conn.commit()
        cur.close()
        conn.close()

    @task
    def analysis():
        conn = psycopg2.connect(
            host='postgres',
            dbname='airflow',
            user='airflow',
            password='airflow'
        )
        cur = conn.cursor()
        cur.execute("SELECT title, avg(rating) FROM movies_ratings GROUP BY title ORDER BY avg(rating) DESC LIMIT 5;")
        results = cur.fetchall()
        print("Top 5 Movies by Avg Rating:", results)
        cur.close()
        conn.close()

    @task
    def cleanup():
        for file in ['movies_clean.csv', 'ratings_clean.csv', 'merged_data.csv']:
            try:
                os.remove(os.path.join(TMP_DIR, file))
            except FileNotFoundError:
                pass

    # Define pipeline
    movies = ingest_movies()
    ratings = ingest_ratings()

    tmp_dir_created = create_tmp_dir()

    [movies, ratings] >> tmp_dir_created

    with TaskGroup("transform", tooltip="Transform in parallel") as tg:
        movies_clean = transform_movies(movies)
        ratings_clean = transform_ratings(ratings)

    tmp_dir_created >> tg

    merged = merge_data(movies_clean, ratings_clean)
    load = load_to_postgres(merged)
    analyze = analysis()
    clean = cleanup()

    tg >> merged >> load >> analyze >> clean
