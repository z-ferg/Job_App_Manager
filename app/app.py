# app.py
# ------------------------------------------------------------------
# The web page (frontend), built with Streamlit.
# Run it with:  streamlit run app/app.py
#
# KEY IDEA: Streamlit re-runs this WHOLE file from top to bottom every
# time the user clicks a button, types in a box, or changes the menu.
# This file never writes SQL; it calls functions from database.py.
# ------------------------------------------------------------------

import pandas as pd        # turns query results into a neat table
import psycopg2            # imported only to recognise database error types
import streamlit as st     # draws the web page

import database as db      # our own database.py (same folder), used as db.function()

# Must be the first Streamlit command: sets the browser tab title and
# uses the full window width.
st.set_page_config(page_title="Student Database", layout="wide")
st.title("Student Database")


def show(result):
    """Turn (columns, rows) into a nice table."""
    # Every read function returns (column_names, rows). Writing this once
    # saves repeating the same two lines on every page.
    columns, rows = result
    st.dataframe(pd.DataFrame(rows, columns=columns), hide_index=True)


# Sidebar menu. Whatever the user picks is stored in `page`, and the
# if/elif chain below draws only that page: one file acts like a
# multi-page app.
page = st.sidebar.selectbox(
    "Menu",
    ["Home", "View", "Add", "Search", "Update", "Delete", "Reports"],
)

# The whole app is inside one try block so that if the database is down,
# the user sees one clear message instead of a long error (see the bottom).
try:
    if page == "Home":
        st.write("Use the menu on the left to work with the database.")

    elif page == "View":
        # READ: run the SELECT and display the result.
        st.subheader("All Students")
        show(db.get_students())

    elif page == "Add":
        # CREATE. st.form groups the inputs so the page only re-runs when
        # Submit is pressed, not on every keystroke. clear_on_submit=True
        # empties the boxes after a successful add.
        st.subheader("Add Student")
        with st.form("add_form", clear_on_submit=True):
            name = st.text_input("Name")
            email = st.text_input("Email")
            submitted = st.form_submit_button("Add Student")
        if submitted:
            # INPUT VALIDATION: catch bad input here, before it reaches the
            # database. .strip() removes spaces so "   " counts as empty.
            if not name.strip() or not email.strip():
                st.error("Name and email are both required.")
            elif "@" not in email:
                st.error("Please enter a valid email address.")
            else:
                try:
                    db.add_student(name.strip(), email.strip())
                    st.success(f"Added {name}.")
                except psycopg2.errors.UniqueViolation:
                    # The UNIQUE rule on email in init.sql makes PostgreSQL
                    # refuse duplicates. We turn that error into a friendly
                    # message instead of letting the app crash.
                    st.error("That email is already in the database.")

    elif page == "Search":
        st.subheader("Search Students")
        keyword = st.text_input("Name or email contains")
        # st.button returns True only on the re-run caused by the click.
        if st.button("Search"):
            result = db.search_students(keyword.strip())
            # result[1] is the list of rows; an empty list counts as False.
            if result[1]:
                show(result)
            else:
                st.info("No matching students.")

    elif page == "Update":
        # UPDATE. number_input only accepts whole numbers >= 1, so the user
        # cannot type letters or negative IDs (validation by the widget).
        st.subheader("Update Student Email")
        student_id = st.number_input("Student ID", min_value=1, step=1)
        new_email = st.text_input("New Email")
        if st.button("Update"):
            if "@" not in new_email:
                st.error("Please enter a valid email address.")
            else:
                try:
                    count = db.update_student_email(int(student_id), new_email.strip())
                    # Updating a missing ID is not a SQL error; it just
                    # changes 0 rows. Checking the count lets us tell the user.
                    if count == 0:
                        st.warning(f"No student with ID {student_id}.")
                    else:
                        st.success("Email updated.")
                except psycopg2.errors.UniqueViolation:
                    st.error("Another student already uses that email.")

    elif page == "Delete":
        # DELETE. Confirmation uses a CHECKBOX, not a second button:
        # a button inside another button's `if` never works in Streamlit,
        # because the click re-runs the page and the first button is False
        # again. A checkbox remembers its state across re-runs.
        st.subheader("Delete Student")
        student_id = st.number_input("Student ID", min_value=1, step=1)
        confirm = st.checkbox("Yes, I am sure I want to delete this student.")
        if st.button("Delete"):
            if not confirm:
                st.warning("Tick the confirmation box first.")
            else:
                count = db.delete_student(int(student_id))
                if count == 0:
                    st.warning(f"No student with ID {student_id}.")
                else:
                    st.success(f"Student {student_id} deleted.")

    elif page == "Reports":
        # The two required read-only queries: a JOIN and an aggregate.
        st.subheader("Enrollments (JOIN)")
        show(db.get_enrollment_details())
        st.subheader("Students per Course (Aggregate)")
        show(db.get_course_counts())

except psycopg2.OperationalError:
    # OperationalError = Python could not reach PostgreSQL at all
    # (Docker stopped, wrong port, wrong password).
    st.error(
        "Cannot connect to the database. Is Docker running? "
        "Try: docker compose up -d"
    )