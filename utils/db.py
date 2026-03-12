import pandas as pd
import streamlit as st
from sqlalchemy import bindparam, create_engine, text

TABLE_NAME = "gdp_per_capita_wide"
VALID_SORT_COLUMNS = {
    "country_name",
    "continent_name",
    *[f"gdp_{year}" for year in range(2000, 2031)],
}


@st.cache_resource
def get_engine():
    db_url = st.secrets["SUPABASE_DB_URL"]
    return create_engine(db_url, pool_pre_ping=True)


@st.cache_data(ttl=3600, show_spinner=False)
def get_filter_metadata():
    sql = text(
        f"""
        SELECT country_name, continent_name
        FROM {TABLE_NAME}
        ORDER BY country_name ASC, continent_name ASC
        """
    )

    with get_engine().connect() as conn:
        df = pd.read_sql_query(sql, conn)

    countries = sorted(df["country_name"].dropna().astype(str).unique().tolist())
    continents = sorted(df["continent_name"].dropna().astype(str).unique().tolist())
    total_rows = int(len(df))

    return countries, continents, total_rows


def _sanitize_sort_rules(sort_rules):
    cleaned = []
    seen = set()

    for column, ascending in sort_rules:
        if column not in VALID_SORT_COLUMNS:
            continue
        if column in seen:
            continue

        cleaned.append((column, bool(ascending)))
        seen.add(column)

    if not cleaned:
        cleaned = [("country_name", True), ("continent_name", True)]

    return cleaned


def _build_filter_parts(countries, continents):
    where_clauses = []
    params = {}
    bind_params = []

    if countries:
        where_clauses.append("country_name IN :countries")
        params["countries"] = list(countries)
        bind_params.append(bindparam("countries", expanding=True))

    if continents:
        where_clauses.append("continent_name IN :continents")
        params["continents"] = list(continents)
        bind_params.append(bindparam("continents", expanding=True))

    return where_clauses, params, bind_params


@st.cache_data(ttl=600, show_spinner=False)
def fetch_filtered_data(
    countries,
    continents,
    start_year,
    end_year,
    sort_rules,
    row_limit,
):
    if start_year > end_year:
        raise ValueError("start_year cannot be greater than end_year")

    selected_columns = [
        "country_name",
        "continent_name",
        *[f"gdp_{year}" for year in range(start_year, end_year + 1)],
    ]

    sort_rules = _sanitize_sort_rules(sort_rules)
    where_clauses, params, bind_params = _build_filter_parts(countries, continents)

    where_sql = ""
    if where_clauses:
        where_sql = " WHERE " + " AND ".join(where_clauses)

    order_sql = " ORDER BY " + ", ".join(
        f"{column} {'ASC' if ascending else 'DESC'} NULLS LAST"
        for column, ascending in sort_rules
    )

    limit_sql = ""
    if row_limit is not None:
        params["row_limit"] = int(row_limit)
        limit_sql = " LIMIT :row_limit"

    data_sql = f"""
        SELECT {", ".join(selected_columns)}
        FROM {TABLE_NAME}
        {where_sql}
        {order_sql}
        {limit_sql}
    """

    count_sql = f"""
        SELECT COUNT(*) AS total_rows
        FROM {TABLE_NAME}
        {where_sql}
    """

    data_stmt = text(data_sql)
    count_stmt = text(count_sql)

    if bind_params:
        data_stmt = data_stmt.bindparams(*bind_params)
        count_stmt = count_stmt.bindparams(*bind_params)

    count_params = {key: value for key, value in params.items() if key != "row_limit"}

    with get_engine().connect() as conn:
        data_df = pd.read_sql_query(data_stmt, conn, params=params)
        count_df = pd.read_sql_query(count_stmt, conn, params=count_params)

    total_matching_rows = int(count_df.iloc[0]["total_rows"])
    return data_df, total_matching_rows