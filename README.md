# de_airflow_windows

## Overview

This repository contains an Apache Airflow project that implements an ETL pipeline to ingest, transform, and load movie data into a PostgreSQL database. It processes raw movie and ratings CSV files, merges the data, loads it into the database, and runs analysis queries.

## Disclaimer

**NOTE: This is a Windows setup.**  
This project and its Docker Compose configuration are tailored to run Airflow and related services on a Windows environment, utilizing Docker Desktop with Windows-specific considerations.

## Repository Structure

- `dags/`: Contains Airflow DAGs including the main `movies_pipeline.py`.
- `data/raw/`: Raw CSV files (`movies.csv` and `ratings.csv`).
- `config/`: Airflow configuration files — **do not commit sensitive files here**.
- Docker and other setup files for running Airflow and PostgreSQL in containers.

## Features

- Ingests and transforms movie and rating data.
- Merges datasets on movie ID.
- Loads merged data into PostgreSQL table.
- Runs analysis to find top-rated movies.
- Orchestrated with Airflow tasks.
- Uses Docker Compose for environment setup.

## Getting Started

### Prerequisites

- Install Docker and Docker Compose.
- Python 3.8+ (optional, for local scripts).

### Setup

1. Clone the repository:

    git clone https://github.com/sejal-jagtap/de_airflow_windows.git
    cd de_airflow_windows


2. Ensure that `data/raw/` contains the input CSV files (`movies.csv` and `ratings.csv`).

3. Build and start containers:

        docker compose build
        docker compose up


4. Access Airflow UI via [http://localhost:8082](http://localhost:8082).

5. Trigger the `movies_pipeline` DAG manually to run the pipeline.

## Important Notes

- Avoid committing sensitive information like the Fernet key in `config/airflow.cfg`.
- Use `.gitignore` to exclude the `config/` directory.
- If secrets were pushed accidentally, rotate keys and clean git history.
- Make sure data folders are properly mounted for containers.

## Usage

- Customize or add new DAGs in `dags/`.
- Place additional raw data files in `data/raw/`.
- Manage configurations in `config/` (locally only).
- Monitor Airflow tasks and logs via the Web UI.

## License

This project is licensed under the MIT License.

---

