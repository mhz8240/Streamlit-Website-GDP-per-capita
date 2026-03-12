# GDP per Capita Explorer

A Streamlit web app for querying a Supabase Postgres table named `gdp_per_capita_wide`.

## Features

- Left-side query form
- Searchable country filter
- Searchable continent filter
- Start year and end year controls
- Multi-column sorting
- Row limit
- Paginated results
- CSV export
- Clean column names in the displayed table

## Data note

- Years 2000–2024 are actual historical values
- Years 2025–2030 are model predictions

## Project structure

```text
gdp-streamlit-app/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.example
├── utils/
│   └── db.py
└── sql/
    └── 01_optional_indexes.sql