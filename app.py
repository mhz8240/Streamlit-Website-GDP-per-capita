import math
from datetime import datetime

import pandas as pd
import streamlit as st

from utils.db import fetch_filtered_data, get_filter_metadata

st.set_page_config(
    page_title="GDP per Capita Explorer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

YEARS = list(range(2000, 2031))
PAGE_SIZE = 100

DISPLAY_TO_DB_COLUMN = {
    "Country": "country_name",
    "Continent": "continent_name",
    **{str(year): f"gdp_{year}" for year in YEARS},
}

DB_TO_DISPLAY_COLUMN = {
    "country_name": "Country",
    "continent_name": "Continent",
    **{f"gdp_{year}": str(year) for year in YEARS},
}


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #eaf3ff 0%, #f2e8ff 100%);
        }

        .block-container {
            padding-top: 0.05rem;
            padding-bottom: 0.55rem;
            max-width: 98%;
        }

        header[data-testid="stHeader"] { background: transparent; }

        h1 {
            font-size: 1.75rem !important;
            margin-top: 0 !important;
            margin-bottom: 0.15rem !important;
            color: #25364d;
        }

        h2, h3 {
            color: #25364d;
            margin-top: 0 !important;
            margin-bottom: 0.35rem !important;
        }

        .tight-label {
            font-size: 0.88rem;
            font-weight: 700;
            color: #2f3e55;
            margin-top: 0.18rem;
            margin-bottom: 0.08rem;
        }

        .small-note {
            color: #5b6474;
            font-size: 0.85rem;
            line-height: 1.28;
            margin-top: 0.3rem;
        }

        .results-banner {
            padding: 0.45rem 0.65rem;
            border-radius: 10px;
            background: #f7fbff;
            border: 1px solid #d7e6ff;
            margin-bottom: 0.45rem;
            color: #30445f;
            font-size: 0.95rem;
            line-height: 1.25;
        }

        .sort-rule-label {
            color: #667287;
            font-size: 0.66rem;
            margin-bottom: 0.12rem;
        }

        .sort-popover-wrap {
            width: 100%;
        }

        .sort-popover-wrap [data-testid="stPopover"] {
            width: 100%;
        }

        .sort-popover-wrap [data-testid="stPopoverButton"] {
            width: 100%;
        }

        .sort-popover-wrap [data-testid="stPopoverButton"] > button {
            width: 100%;
            min-height: 2.55rem;
            border-radius: 10px;
            border: 1px solid #dde6f2;
            background: #fbfcfe;
            color: #25364d;
            font-weight: 600;
            justify-content: space-between;
            padding: 0.45rem 0.75rem;
        }

        .sort-popover-panel {
            width: 560px;
            min-width: 560px;
            max-width: 560px;
        }

        .sort-popover-panel .stCaption {
            white-space: normal !important;
            line-height: 1.3 !important;
        }

        .sort-popover-panel .stButton > button {
            white-space: nowrap !important;
            width: 100% !important;
        }

        .sort-popover-panel .stSelectbox label,
        .sort-popover-panel .stCaption,
        .sort-popover-panel p,
        .sort-popover-panel span,
        .sort-popover-panel div {
            font-size: 0.79rem;
        }

        div[data-testid="stPopoverContent"]:has(.sort-popover-panel) {
            width: 560px !important;
            min-width: 560px !important;
            max-width: 560px !important;
            z-index: 99990 !important;
        }

        div[data-testid="stPopoverContent"]:has(.sort-popover-panel) > div {
            transform: translateY(calc(-100% - 10px)) !important;
        }

        div[data-baseweb="popover"]:has(ul[role="listbox"]) {
            z-index: 99999 !important;
        }

        div[data-baseweb="popover"]:has(ul[role="listbox"]) > div {
            transform: translateY(42px) !important;
        }

        div[data-baseweb="popover"]:has(ul[role="listbox"]) ul[role="listbox"] {
            margin-top: 0 !important;
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.16) !important;
            border-radius: 10px !important;
        }

        .filter-help {
            color: #667287;
            font-size: 1rem;
            margin-top: 0.12rem;
            margin-bottom: 0.12rem;
        }

        .popover-header {
            font-size: 0.76rem;
            color: #657287;
            margin-bottom: 0.18rem;
        }

        .row-limit-help {
            color: #b42318;
            font-size: 0.72rem;
            margin-top: 0.12rem;
        }

        div[data-testid="stVerticalBlock"] > div {
            gap: 0.22rem !important;
        }

        div[data-testid="stMetric"] {
            background: transparent;
            border: none;
            padding: 0;
        }

        .stButton > button {
            border-radius: 9px;
            width: 100%;
        }

        .stDownloadButton > button {
            border-radius: 9px;
            width: 100%;
        }

        [data-testid="stTextInput"] input,
        [data-testid="stSelectbox"] > div,
        [data-testid="stPopoverButton"] > button {
            font-size: 0.83rem !important;
        }

        .search-clear-wrap,
        .row-limit-clear-wrap {
            width: 100%;
        }

        .search-clear-wrap .stButton,
        .row-limit-clear-wrap .stButton {
            width: 100%;
        }

        .search-clear-wrap .stButton > button,
        .row-limit-clear-wrap .stButton > button {
            width: 100% !important;
            height: 2.5rem !important;
            min-height: 2.5rem !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        .search-clear-wrap .stButton > button > div,
        .row-limit-clear-wrap .stButton > button > div {
            width: 100% !important;
            height: 100% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        .search-clear-wrap .stButton > button p,
        .row-limit-clear-wrap .stButton > button p {
            margin: 0 !important;
            line-height: 1 !important;
            text-align: center !important;
            width: 100% !important;
            font-size: 1.08rem !important;
        }

        .scroll-table-wrap {
            max-height: 560px;
            overflow-y: auto;
            overflow-x: auto;
            border: 1px solid #d7e6ff;
            border-radius: 10px;
            background: white;
        }

        .scroll-table {
            border-collapse: collapse;
            width: max-content;
            min-width: 100%;
            font-size: 0.82rem;
        }

        .scroll-table thead th {
            position: sticky;
            top: 0;
            background: #f7fbff;
            z-index: 2;
            border-bottom: 1px solid #d7e6ff;
        }

        .scroll-table th,
        .scroll-table td {
            padding: 0.45rem 0.65rem;
            text-align: left;
            white-space: nowrap;
            border-bottom: 1px solid #eef2f7;
        }

        .scroll-table tbody tr:nth-child(even) {
            background: #fbfdff;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_default_sort_rules():
    return []


def init_session_state(total_rows: int) -> None:
    defaults = {
        "country_filter": [],
        "continent_filter": [],
        "start_year": 2000,
        "end_year": 2030,
        "row_limit_input": "",
        "current_page": 1,
        "sort_rules_ui": get_default_sort_rules(),
        "sort_rule_next_id": 1,
        "sort_expanded": False,
        "sort_add_nonce": 0,
        "country_search_text": "",
        "continent_search_text": "",
        "country_checkbox_nonce": 0,
        "continent_checkbox_nonce": 0,
        "reset_requested": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if "submitted_query" not in st.session_state:
        st.session_state.submitted_query = build_submitted_query(total_rows)


def reset_controls(total_rows: int, countries: list[str], continents: list[str]) -> None:
    st.session_state.country_filter = []
    st.session_state.continent_filter = []
    st.session_state.start_year = 2000
    st.session_state.end_year = 2030
    st.session_state.row_limit_input = ""
    st.session_state.current_page = 1
    st.session_state.sort_rules_ui = get_default_sort_rules()
    st.session_state.sort_rule_next_id = 1
    st.session_state.sort_expanded = False
    st.session_state.sort_add_nonce = 0
    st.session_state.country_search_text = ""
    st.session_state.continent_search_text = ""
    st.session_state.country_checkbox_nonce += 1
    st.session_state.continent_checkbox_nonce += 1


def request_reset() -> None:
    st.session_state.reset_requested = True


def clear_search_text(search_key: str) -> None:
    st.session_state[search_key] = ""


def select_all_options(selected_key: str, options: list[str], nonce_key: str) -> None:
    st.session_state[selected_key] = options.copy()
    st.session_state[nonce_key] += 1


def clear_all_options(selected_key: str, nonce_key: str) -> None:
    st.session_state[selected_key] = []
    st.session_state[nonce_key] += 1


def toggle_option_from_checkbox(
    selected_key: str,
    checkbox_key: str,
    option: str,
) -> None:
    selected_set = set(st.session_state.get(selected_key, []))
    is_checked = bool(st.session_state.get(checkbox_key, False))

    if is_checked:
        selected_set.add(option)
    else:
        selected_set.discard(option)

    st.session_state[selected_key] = sorted(selected_set)


def get_sort_rule_options(start_year: int, end_year: int) -> list[str]:
    return ["Country", "Continent", *[str(y) for y in range(start_year, end_year + 1)]]


def update_sort_rule_column(rule_id: int) -> None:
    widget_key = f"sort_col_{rule_id}"
    selected_value = st.session_state.get(widget_key)

    for rule in st.session_state.sort_rules_ui:
        if rule["id"] == rule_id:
            rule["column"] = selected_value
            break


def update_sort_rule_direction(rule_id: int) -> None:
    widget_key = f"sort_dir_{rule_id}"
    selected_value = st.session_state.get(widget_key)

    for rule in st.session_state.sort_rules_ui:
        if rule["id"] == rule_id:
            rule["ascending"] = (selected_value == "Ascending")
            break


def validate_sort_rules(start_year: int, end_year: int) -> None:
    valid_options = set(get_sort_rule_options(start_year, end_year))
    cleaned_rules = []
    used_columns = set()

    for rule in st.session_state.sort_rules_ui:
        if rule["column"] not in valid_options:
            continue
        if rule["column"] in used_columns:
            continue

        cleaned_rules.append(rule)
        used_columns.add(rule["column"])

    st.session_state.sort_rules_ui = cleaned_rules


def add_sort_rule(column_name: str) -> None:
    if not column_name:
        return

    existing = {rule["column"] for rule in st.session_state.sort_rules_ui}
    if column_name in existing:
        return

    rule_id = st.session_state.sort_rule_next_id
    st.session_state.sort_rule_next_id += 1

    st.session_state.sort_rules_ui.append(
        {
            "id": rule_id,
            "column": column_name,
            "ascending": True,
        }
    )

    st.session_state[f"sort_col_{rule_id}"] = column_name
    st.session_state[f"sort_dir_{rule_id}"] = "Ascending"
    st.session_state.sort_expanded = True


def remove_sort_rule(rule_id: int) -> None:
    st.session_state.sort_rules_ui = [
        rule for rule in st.session_state.sort_rules_ui if rule["id"] != rule_id
    ]
    st.session_state.sort_expanded = True


def parse_row_limit_input(total_rows: int):
    raw = str(st.session_state.get("row_limit_input", "")).strip()

    if raw == "":
        return None, None

    if not raw.isdigit():
        return None, "Top X Rows must be a positive whole number or blank."

    value = int(raw)

    if value < 1:
        return None, "Top X Rows must be at least 1."

    if value > total_rows:
        return None, f"Top X Rows cannot exceed {total_rows:,}."

    return value, None


def build_submitted_query(total_rows: int) -> dict:
    sort_rules = []
    used_columns = set()

    for rule in st.session_state.sort_rules_ui:
        db_col = DISPLAY_TO_DB_COLUMN.get(rule["column"])
        if db_col and db_col not in used_columns:
            sort_rules.append((db_col, bool(rule["ascending"])))
            used_columns.add(db_col)

    row_limit_value, _ = parse_row_limit_input(total_rows)

    return {
        "countries": sorted(st.session_state.country_filter),
        "continents": sorted(st.session_state.continent_filter),
        "start_year": int(st.session_state.start_year),
        "end_year": int(st.session_state.end_year),
        "sort_rules": tuple(sort_rules),
        "row_limit": row_limit_value,
    }


def render_sort_controls(start_year: int, end_year: int) -> None:
    validate_sort_rules(start_year, end_year)

    rule_count = len(st.session_state.sort_rules_ui)
    sort_header = (
        "Default sorting"
        if rule_count == 0
        else f"Sorted by {rule_count} rule{'s' if rule_count != 1 else ''}"
    )

    st.markdown('<div class="sort-popover-wrap">', unsafe_allow_html=True)

    with st.popover(sort_header):
        st.markdown('<div class="sort-popover-panel">', unsafe_allow_html=True)

        available_options = get_sort_rule_options(start_year, end_year)

        if rule_count == 0:
            st.caption(
                "No custom sorting applied. Results default to Country and then Continent in ascending order."
            )

        for idx, rule in enumerate(st.session_state.sort_rules_ui):
            rule_id = rule["id"]

            other_selected = {
                r["column"] for r in st.session_state.sort_rules_ui if r["id"] != rule_id
            }
            row_options = [opt for opt in available_options if opt not in other_selected]

            if rule["column"] not in row_options:
                row_options = [rule["column"]] + row_options

            col_key = f"sort_col_{rule_id}"
            dir_key = f"sort_dir_{rule_id}"

            st.session_state[col_key] = rule["column"]
            st.session_state[dir_key] = "Ascending" if rule["ascending"] else "Descending"

            st.markdown(
                f'<div class="sort-rule-label">Sort rule {idx + 1}</div>',
                unsafe_allow_html=True,
            )

            rule_col, dir_col, remove_col = st.columns([1.65, 1.85, 0.3])

            with rule_col:
                st.selectbox(
                    f"Sort column {idx + 1}",
                    options=row_options,
                    key=col_key,
                    label_visibility="collapsed",
                    on_change=update_sort_rule_column,
                    args=(rule_id,),
                )

            with dir_col:
                st.selectbox(
                    f"Direction {idx + 1}",
                    options=["Ascending", "Descending"],
                    key=dir_key,
                    label_visibility="collapsed",
                    on_change=update_sort_rule_direction,
                    args=(rule_id,),
                )

            with remove_col:
                if st.button("×", key=f"remove_sort_{rule_id}"):
                    remove_sort_rule(rule_id)
                    st.rerun()

        validate_sort_rules(start_year, end_year)

        selected_columns = {rule["column"] for rule in st.session_state.sort_rules_ui}
        addable_columns = [opt for opt in available_options if opt not in selected_columns]

        add_col1, add_col2 = st.columns([2.35, 1.05])

        add_widget_key = f"sort_add_column_display_{st.session_state.sort_add_nonce}"
        placeholder_options = ["Pick a column"] + addable_columns

        if add_widget_key not in st.session_state:
            st.session_state[add_widget_key] = "Pick a column"

        with add_col1:
            st.selectbox(
                "Add sort column",
                options=placeholder_options,
                key=add_widget_key,
                label_visibility="collapsed",
            )

        with add_col2:
            add_clicked = st.button("Add rule")

        if add_clicked:
            selected_to_add = st.session_state.get(add_widget_key, "Pick a column")
            if selected_to_add != "Pick a column":
                add_sort_rule(selected_to_add)
                st.session_state.sort_add_nonce += 1
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_checkbox_dropdown(
    label: str,
    options: list[str],
    selected_key: str,
    search_key: str,
    checkbox_prefix: str,
    empty_summary_text: str,
    placeholder_text: str,
    nonce_key: str,
) -> None:
    selected = sorted(st.session_state.get(selected_key, []))

    button_label = (
        f"{label}: {empty_summary_text}"
        if len(selected) == 0
        else f"{label}: {len(selected)} selected"
    )

    with st.popover(button_label):
        st.markdown(
            f'<div class="popover-header">{placeholder_text}</div>',
            unsafe_allow_html=True,
        )

        search_col, clear_col = st.columns([5.6, 1.2], gap="small", vertical_alignment="center")

        with search_col:
            st.text_input(
                f"Search {label}",
                key=search_key,
                placeholder="Search...",
                label_visibility="collapsed",
            )

        with clear_col:
            st.markdown('<div class="search-clear-wrap">', unsafe_allow_html=True)
            st.button(
                "×",
                key=f"{search_key}_clear_button",
                on_click=clear_search_text,
                args=(search_key,),
                help=f"Clear {label.lower()} search",
                use_container_width=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        search_text = st.session_state.get(search_key, "").strip().lower()

        if search_text == "":
            top_left, top_right = st.columns(2)
            with top_left:
                st.button(
                    "Select All",
                    key=f"{selected_key}_select_all",
                    on_click=select_all_options,
                    args=(selected_key, options, nonce_key),
                )

            with top_right:
                st.button(
                    "Clear All",
                    key=f"{selected_key}_clear_all",
                    on_click=clear_all_options,
                    args=(selected_key, nonce_key),
                )

        filtered_options = (
            [option for option in options if search_text in option.lower()]
            if search_text
            else options
        )

        if not filtered_options:
            st.caption("No matches found.")
            return

        nonce = st.session_state[nonce_key]
        selected_set = set(st.session_state.get(selected_key, []))

        for option in filtered_options:
            checkbox_key = f"{checkbox_prefix}_{nonce}_{option}"
            st.session_state[checkbox_key] = option in selected_set

            st.checkbox(
                option,
                key=checkbox_key,
                on_change=toggle_option_from_checkbox,
                args=(selected_key, checkbox_key, option),
            )


def clear_row_limit() -> None:
    st.session_state.row_limit_input = ""


def render_row_limit_controls() -> None:
    input_col, clear_col = st.columns([4.15, 0.95], gap="small", vertical_alignment="center")

    with input_col:
        st.text_input(
            "Top X Rows",
            key="row_limit_input",
            placeholder="Blank = all rows",
            label_visibility="collapsed",
        )

    with clear_col:
        st.markdown('<div class="row-limit-clear-wrap">', unsafe_allow_html=True)
        st.button(
            "×",
            key="row_limit_clear",
            on_click=clear_row_limit,
            use_container_width=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)


def format_results_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    display_df = df.rename(columns=DB_TO_DISPLAY_COLUMN).copy()

    for col in display_df.columns:
        if col not in {"Country", "Continent"}:
            numeric_col = pd.to_numeric(display_df[col], errors="coerce")
            display_df[col] = numeric_col.astype("float64").round(2)

    return display_df


def format_table_for_display(df: pd.DataFrame) -> pd.DataFrame:
    table_df = df.copy()

    for col in table_df.columns:
        if col not in {"Country", "Continent"}:
            table_df[col] = pd.to_numeric(table_df[col], errors="coerce").map(
                lambda x: "" if pd.isna(x) else f"{x:.2f}"
            )

    return table_df


def render_scrollable_table(df: pd.DataFrame) -> None:
    html_table = df.to_html(index=False, escape=False, classes="scroll-table")
    st.markdown(
        f'<div class="scroll-table-wrap">{html_table}</div>',
        unsafe_allow_html=True,
    )


inject_css()

countries, continents, total_rows = get_filter_metadata()
countries = sorted(countries)
continents = sorted(continents)
init_session_state(total_rows)

if st.session_state.reset_requested:
    reset_controls(total_rows, countries, continents)
    st.session_state.submitted_query = build_submitted_query(total_rows)
    st.session_state.reset_requested = False

st.title("GDP per Capita Explorer")
st.markdown(
    """
    <div style="font-size: 1rem; color: #5b6474; margin-top: -0.15rem; margin-bottom: 0.45rem;">
        A web application that displays GDP per capita (PPP, 2021 international $) predictions and historical values.
    </div>
    """,
    unsafe_allow_html=True,
)

left_col, right_col = st.columns([1.0, 2.9], gap="medium")

with left_col:
    with st.container(border=True):
        st.subheader("Query Form")

        st.markdown('<div class="tight-label">Country</div>', unsafe_allow_html=True)
        render_checkbox_dropdown(
            label="Country",
            options=countries,
            selected_key="country_filter",
            search_key="country_search_text",
            checkbox_prefix="country_option",
            empty_summary_text="none selected",
            placeholder_text="Select one or more countries",
            nonce_key="country_checkbox_nonce",
        )
        st.markdown(
            '<div class="filter-help">At least one country must be selected before querying.</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="tight-label">Continent</div>', unsafe_allow_html=True)
        render_checkbox_dropdown(
            label="Continent",
            options=continents,
            selected_key="continent_filter",
            search_key="continent_search_text",
            checkbox_prefix="continent_option",
            empty_summary_text="no filter",
            placeholder_text="No continent filter by default",
            nonce_key="continent_checkbox_nonce",
        )

        st.markdown('<div class="tight-label">Year Range (Start and End)</div>', unsafe_allow_html=True)
        y1, y2 = st.columns(2)
        with y1:
            st.selectbox("Start year", YEARS, key="start_year", label_visibility="collapsed")
        with y2:
            st.selectbox("End year", YEARS, key="end_year", label_visibility="collapsed")

        st.markdown('<div class="tight-label">Sorting</div>', unsafe_allow_html=True)
        render_sort_controls(
            int(st.session_state.start_year),
            int(st.session_state.end_year),
        )

        st.markdown(
            '<div class="tight-label" style="margin-top: -0.25rem;">Top X Rows</div>',
            unsafe_allow_html=True,
        )
        render_row_limit_controls()

        row_limit_value, row_limit_error = parse_row_limit_input(total_rows)
        if row_limit_error:
            st.markdown(
                f'<div class="row-limit-help">{row_limit_error}</div>',
                unsafe_allow_html=True,
            )

        year_range_error = int(st.session_state.start_year) > int(st.session_state.end_year)
        query_disabled = (
            (len(st.session_state.country_filter) == 0)
            or (row_limit_error is not None)
            or year_range_error
        )

        if year_range_error:
            st.error("Start year cannot be greater than end year.")

        q1, q2 = st.columns(2)
        with q1:
            query_clicked = st.button(
                "Query",
                type="primary",
                disabled=query_disabled,
            )
        with q2:
            st.button("Reset", on_click=request_reset)

        st.markdown(
            """
            <div class="small-note">
                2000-2024 = actual World Bank values<br>
                2025-2030 = model predictions
            </div>
            """,
            unsafe_allow_html=True,
        )

    if query_clicked:
        validate_sort_rules(
            int(st.session_state.start_year),
            int(st.session_state.end_year),
        )
        st.session_state.submitted_query = build_submitted_query(total_rows)
        st.session_state.current_page = 1
        st.rerun()

with right_col:
    with st.container(border=True):
        st.subheader("Query Results")

        banner_col, export_col = st.columns([6.0, 1.35])

        with banner_col:
            st.markdown(
                """
                <div class="results-banner" style="line-height: 1.55;">
                    2000-2024 are actual historical values. 2025-2030 are model predictions.<br>
                    All values are <strong>inflation-adjusted</strong> and in terms of PPP (constant 2021 international $).
                </div>
                """,
                unsafe_allow_html=True,
            )

        query = st.session_state.submitted_query

        if len(query["countries"]) == 0:
            st.info("Select at least one country on the left to enable querying.")
        else:
            with st.spinner("Running query..."):
                raw_df, matching_row_count = fetch_filtered_data(
                    countries=tuple(query["countries"]),
                    continents=tuple(query["continents"]),
                    start_year=query["start_year"],
                    end_year=query["end_year"],
                    sort_rules=tuple(query["sort_rules"]),
                    row_limit=query["row_limit"],
                )

            display_df = format_results_dataframe(raw_df)

            if len(display_df) == 0:
                st.warning("No rows matched your query.")
            else:
                with export_col:
                    csv_bytes = display_df.to_csv(index=False).encode("utf-8")
                    file_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    st.download_button(
                        label="Export CSV",
                        data=csv_bytes,
                        file_name=f"gdp_per_capita_query_{file_stamp}.csv",
                        mime="text/csv",
                    )

                total_pages = max(1, math.ceil(len(display_df) / PAGE_SIZE))

                current_page = int(st.session_state.current_page)
                if current_page < 1:
                    current_page = 1
                if current_page > total_pages:
                    current_page = total_pages
                st.session_state.current_page = current_page

                pager_left, pager_mid, pager_right, pager_text = st.columns([1, 1.2, 1, 3])

                with pager_left:
                    if st.button("◀ Prev Page", disabled=current_page <= 1):
                        st.session_state.current_page = current_page - 1
                        st.rerun()

                with pager_mid:
                    page_input = st.number_input(
                        "Page",
                        min_value=1,
                        max_value=total_pages,
                        step=1,
                        value=current_page,
                        label_visibility="collapsed",
                    )

                with pager_right:
                    if st.button("Next Page ▶", disabled=current_page >= total_pages):
                        st.session_state.current_page = current_page + 1
                        st.rerun()

                if int(page_input) != current_page:
                    st.session_state.current_page = int(page_input)
                    st.rerun()

                start_idx = (st.session_state.current_page - 1) * PAGE_SIZE
                end_idx = start_idx + PAGE_SIZE
                page_df = display_df.iloc[start_idx:end_idx].reset_index(drop=True)

                with pager_text:
                    st.markdown(
                        f'<div style="font-size: 0.93rem; color: #667287; padding-top: 0.35rem;">'
                        f'Showing {start_idx + 1:,}-{min(end_idx, len(display_df)):,} of {len(display_df):,}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                static_table_df = format_table_for_display(page_df)
                render_scrollable_table(static_table_df)