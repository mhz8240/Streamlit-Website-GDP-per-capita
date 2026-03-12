import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text


def main():
    st.set_page_config(page_title="Supabase Connection Test", layout="centered")
    st.title("Supabase Connection Test")

    try:
        db_url = st.secrets["SUPABASE_DB_URL"]
    except Exception as e:
        st.error("Could not find SUPABASE_DB_URL in Streamlit secrets.")
        st.exception(e)
        return

    st.write("Attempting to connect to Supabase...")

    try:
        engine = create_engine(db_url, pool_pre_ping=True)

        with engine.connect() as conn:
            # 1. Simple connection test
            result = conn.execute(text("SELECT 1 AS connection_test"))
            connection_value = result.scalar()

            # 2. Check whether the table exists
            table_check_sql = text(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                      AND table_name = 'gdp_per_capita_wide'
                ) AS table_exists
                """
            )
            table_exists = conn.execute(table_check_sql).scalar()

            # 3. Retrieve a few rows from the table
            preview_sql = text(
                """
                SELECT *
                FROM public.gdp_per_capita_wide
                LIMIT 5
                """
            )
            preview_df = pd.read_sql_query(preview_sql, conn)

            # 4. Count total rows
            count_sql = text(
                """
                SELECT COUNT(*) AS total_rows
                FROM public.gdp_per_capita_wide
                """
            )
            count_df = pd.read_sql_query(count_sql, conn)
            total_rows = int(count_df.loc[0, "total_rows"])

        st.success("Successfully connected to Supabase.")

        st.subheader("Connection test result")
        st.write(f"`SELECT 1` returned: **{connection_value}**")

        st.subheader("Table existence check")
        st.write(f"`gdp_per_capita_wide` exists: **{table_exists}**")

        st.subheader("Total rows in table")
        st.write(f"**{total_rows:,}** rows found")

        st.subheader("Preview of first 5 rows")
        st.dataframe(preview_df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error("Connection or query failed.")
        st.exception(e)


if __name__ == "__main__":
    main()