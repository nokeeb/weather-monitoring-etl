# Weather Monitoring ETL

A scheduled Python ETL pipeline that collects current weather data from the Open-Meteo API, stores raw API responses locally, validates and transforms selected fields, and loads the results into PostgreSQL.

The pipeline collects weather snapshots for:

- Mostar, Bosnia and Herzegovina
- Sarajevo, Bosnia and Herzegovina
- Zagreb, Croatia

## Project overview

This project was built to practice a complete local ETL workflow without orchestration tools such as Airflow.

Every pipeline run:

1. Reads configured locations from PostgreSQL.
2. Requests current weather data from the Open-Meteo API.
3. Saves the full raw JSON response locally.
4. Extracts and validates selected weather fields.
5. Loads valid weather observations into PostgreSQL.
6. Records pipeline metadata in an audit table.
7. Writes execution details and errors to a log file.

The pipeline is scheduled through Windows Task Scheduler to run every 12 hours.

## Architecture

```text
PostgreSQL: weather.locations
            |
            v
      Open-Meteo API
            |
            v
     Raw JSON files
   data/raw/*.json
            |
            v
Python transformation
and validation layer
            |
            v
PostgreSQL: weather.observations
            |
            v
PostgreSQL: weather.pipeline_runs
            |
            v
     Logs and SQL analysis
```

## Data model

The PostgreSQL database is named:

```text
weather_etl_db
```

The project uses the `weather` schema.

### `weather.locations`

Stores the locations that the pipeline processes.

| Column | Description |
|---|---|
| `location_id` | Primary key for a location |
| `city_name` | City name |
| `country_code` | Two-letter country code |
| `latitude` | Geographic latitude |
| `longitude` | Geographic longitude |

The initial seed data contains Mostar, Sarajevo, and Zagreb.

### `weather.observations`

Stores transformed weather snapshots returned by the API.

The grain of this table is:

> One row represents one weather observation for one location at one API observation timestamp.

| Column | Description |
|---|---|
| `observation_id` | Primary key |
| `run_id` | Foreign key to the pipeline run that loaded the record |
| `location_id` | Foreign key to `weather.locations` |
| `observed_at` | Timestamp returned by the weather API |
| `extracted_at` | UTC timestamp when the pipeline extracted the data |
| `temperature_c` | Temperature in Celsius |
| `relative_humidity_pct` | Relative humidity percentage |
| `surface_pressure_hpa` | Surface pressure in hPa |
| `wind_speed_kmh` | Wind speed in km/h |
| `weather_code` | Weather condition code returned by the API |
| `raw_file_path` | Path to the raw JSON response used for the record |

The table has a unique constraint on:

```text
(location_id, observed_at)
```

This prevents duplicate observations for the same location and API timestamp.

### `weather.pipeline_runs`

Stores audit information for every pipeline execution.

| Column | Description |
|---|---|
| `run_id` | Unique identifier for one pipeline run |
| `started_at` | UTC timestamp when the pipeline started |
| `finished_at` | UTC timestamp when the pipeline finished |
| `status` | Final pipeline status |
| `records_extracted` | Number of successful raw API responses |
| `records_loaded` | Number of records loaded into PostgreSQL |
| `error_message` | Error details when a run fails |

Possible statuses:

- `SUCCESS`
- `PARTIAL`
- `FAILED`

A run is marked as:

- `SUCCESS` when all locations are extracted, transformed, and loaded successfully.
- `PARTIAL` when at least one location fails but at least one valid record is loaded.
- `FAILED` when no valid records can be loaded or a critical database error occurs.

## Pipeline flow

### Extract

For every location in `weather.locations`, the pipeline sends a request to the Open-Meteo API.

The pipeline requests these current weather variables:

- `temperature_2m`
- `relative_humidity_2m`
- `surface_pressure`
- `wind_speed_10m`
- `weather_code`

The full API response is saved as a raw JSON file:

```text
data/raw/<run_id>_<city_name>.json
```

Raw files are ignored by Git because they are generated every time the pipeline runs.

### Transform

The pipeline extracts only the fields needed for analysis and prepares one normalized observation record per city.

The following checks are applied before loading:

- Temperature must be between -60°C and 60°C.
- Relative humidity must be between 0% and 100%.
- Surface pressure must be between 800 hPa and 1100 hPa.
- Wind speed cannot be negative.
- All required fields must exist in the API response.
- The API timestamp must be valid and stored as UTC.

Invalid records are not loaded into PostgreSQL.

### Load

Valid records are inserted into `weather.observations`.

The load uses an idempotent insert strategy:

```text
ON CONFLICT (location_id, observed_at) DO NOTHING
```

This means that rerunning the pipeline does not create duplicate observations for the same city and timestamp.

Each pipeline execution is tracked in `weather.pipeline_runs`.

### Logging and error handling

Pipeline logs are written to:

```text
logs/weather_etl.log
```

Each run logs:

- Pipeline start and finish.
- The generated `run_id`.
- The city currently being processed.
- Successful raw API responses.
- Validation failures.
- Number of extracted responses.
- Number of valid records.
- Number of loaded records.
- Final run status.
- Errors and traceback information for unexpected failures.

If one city API request fails, the pipeline continues with the remaining locations and can finish with the `PARTIAL` status.

If a database load fails, the transaction is rolled back to prevent partial inserts.

## Technologies

- Python 3.10+
- PostgreSQL
- psycopg2
- requests
- python-dotenv
- Open-Meteo API
- Windows Task Scheduler
- Git and GitHub

## Project structure

```text
weather-monitoring-etl/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── data/
│   └── raw/
│       └── .gitkeep
├── images/
│   └── .gitkeep
├── logs/
│   └── .gitkeep
├── schedule/
│   └── run_weather_etl.example.bat
├── scripts/
│   ├── create_database.py
│   └── run_pipeline.py
├── sql/
│   ├── 001_schema.sql
│   ├── 002_seed_locations.sql
│   └── 003_analysis.sql
└── src/
    ├── __init__.py
    ├── config.py
    ├── database.py
    ├── extract.py
    ├── transform.py
    ├── load.py
    └── pipeline.py
```

## Installation

Clone the repository:

```bash
git clone [https://github.com/nokeeb/weather-monitoring-etl.git](https://github.com/nokeeb/weather-monitoring-etl.git)
cd weather-monitoring-etl
```

Create and activate a virtual environment.

### Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Configuration

This repository does not store database credentials in source code.

Copy `.env.example` and create a local `.env` file in the project root.

Example configuration:

```text
PG_HOST=localhost
PG_PORT=5432
PG_ADMIN_DB=postgres
PG_DBNAME=weather_etl_db
PG_USER=postgres
PG_PASSWORD=replace_with_your_password
```

Replace:

```text
replace_with_your_password
```

with your local PostgreSQL password.

The `.env` file is ignored by Git and must not be committed.

The PostgreSQL user must have permission to create the `weather_etl_db` database.

## How to run locally

### 1. Create and initialize the database

Run:

```bash
python scripts/create_database.py
```

This script:

1. Connects to the PostgreSQL administrative database specified by `PG_ADMIN_DB`.
2. Creates `weather_etl_db` if it does not already exist.
3. Creates the `weather` schema and required tables.
4. Seeds the `weather.locations` table with Mostar, Sarajevo, and Zagreb.

You can safely run the script more than once.

### 2. Run the pipeline

Run:

```bash
python scripts/run_pipeline.py
```

The pipeline will:

- Create a new pipeline audit record.
- Request current weather data for all configured locations.
- Save raw JSON responses in `data/raw/`.
- Validate and transform API fields.
- Load valid records into `weather.observations`.
- Update the final run status in `weather.pipeline_runs`.
- Write logs to `logs/weather_etl.log`.

## Scheduling

The pipeline is intended to run every 12 hours through Windows Task Scheduler.

The repository includes:

```text
schedule/run_weather_etl.example.bat
```

Copy it locally as:

```text
schedule/run_weather_etl.bat
```

Update the Windows username and local project path inside the batch file.

Example:

```bat
@echo off
cd /d "C:\Users\YOUR_WINDOWS_USERNAME\Documents\de-projects\weather-monitoring-etl"
"C:\Users\YOUR_WINDOWS_USERNAME\Documents\de-projects\weather-monitoring-etl\.venv\Scripts\python.exe" "scripts\run_pipeline.py" >> "logs\task_scheduler.log" 2>&1
exit /b %ERRORLEVEL%
```

The local `run_weather_etl.bat` file is ignored by Git because it contains a user-specific local path.

In Windows Task Scheduler:

1. Create a task named `Weather Monitoring ETL`.
2. Set a daily trigger.
3. Configure the trigger to repeat every 12 hours indefinitely.
4. Set the action to run `schedule/run_weather_etl.bat`.
5. Test the task manually with **Run** before relying on the schedule.

## Data quality and idempotency

The project includes database constraints and SQL checks to validate loaded data.

Examples of checks:

- Duplicate observations for the same location and timestamp.
- Invalid temperature values.
- Invalid humidity values.
- Invalid pressure values.
- Negative wind speeds.
- Observations without a matching location.
- Observations without a matching pipeline run.

The idempotent load logic prevents duplicate observations through:

```text
UNIQUE (location_id, observed_at)
```

and:

```text
ON CONFLICT (location_id, observed_at) DO NOTHING
```

## Example SQL analysis

The SQL analysis file is located at:

```text
sql/003_analysis.sql
```

### Daily average temperature by city

This analysis calculates the average temperature per city and UTC day.

Example output:

| observation_day_utc | city_name | avg_temperature_c |
|---|---|---:|
| 2026-09-15 | Mostar | 23.40 |
| 2026-09-15 | Sarajevo | 18.75 |
| 2026-09-15 | Zagreb | 20.10 |

### Latest weather observation by city

This analysis returns the most recently collected weather snapshot for each city.

### Pipeline health

This analysis aggregates pipeline runs by status and returns:

- Pipeline status.
- Number of runs per status.
- Average number of loaded records.
- Latest pipeline start time for each status.

This makes it possible to track whether scheduled executions are succeeding, partially succeeding, or failing over time.

## Limitations

- The pipeline runs locally and is not deployed to a cloud environment.
- Windows Task Scheduler only runs the pipeline while the machine is available.
- The initial location list is limited to Mostar, Sarajevo, and Zagreb.
- The project collects current weather snapshots, not a complete historical weather archive.
- The raw JSON files are kept locally and are not stored in the GitHub repository.
- The API data is model-based weather data and should not be treated as a direct measurement from a personal local weather station.

## Data source

Weather data is provided by the [Open-Meteo API](https://open-meteo.com/).

Open-Meteo provides weather data based on numerical weather models and combines data from multiple meteorological providers.
