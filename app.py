import streamlit as st
import pandas as pd
from datetime import datetime
from expense_manager import Expense, ExpenseManager

st.set_page_config(page_title="Expense Tracker", layout="wide")
if 'manager' not in st.session_state:
    st.session_state.manager = ExpenseManager()
manager = st.session_state.manager

# --- Sidebar Form ---33
st.sidebar.header("Add New Expense")
with st.sidebar.form("expense_form"):
    amount = st.text_input("Amount (e.g 123.45)")
    category = st.selectbox(
        "Category", ["Food", "Transport", "Utilities", "Other"])
    date_input = st.date_input("Date", value=datetime.today())
    note = st.text_input("Note")
    submitted = st.form_submit_button("Add Expense")

    if submitted:
        try:
            amount_value = float(amount)
            if amount_value <= 0:
                raise ValueError("Amount must be positive.")
            new_expense = Expense(amount_value, category, date_input, note)
            manager.add_expense(new_expense)
            st.sidebar.success("Expense added!")
        except ValueError:
            st.sidebar.error(
                "Please enter a valid positive number for amount.")
        except Exception as e:
            st.sidebar.error(f"Error: {str(e)}")

st.title("Personal Expense Tracker")
# --- Editable/Deletable Table ---
st.subheader("Manage Expenses")

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=None)
with col2:
    end_date = st.date_input("End Date", value=None)

filter_category = st.selectbox(
    "Category", ["All", "Food", "Transport", "Utilities", "Other"])

# --- Apply Filter ---
filtered = manager.filter_expenses(
    category=filter_category if filter_category != "All" else None,
    start_date=start_date,
    end_date=end_date
)


df_filtered = pd.DataFrame([vars(e) for e in filtered])

if not df_filtered.empty:
    df_filtered['date'] = pd.to_datetime(
        df_filtered['date'], errors='coerce').dt.date

    st.subheader("Filtered Expense Editable")
    st.dataframe(df_filtered.sort_values(
        by="date", ascending=False), use_container_width=True)

    # Create selection for rows
    for idx, row in df_filtered.iterrows():
        with st.expander(f"{pd.to_datetime(row['date']).date()} - {row['category']} -  {int(row['amount']) if row['amount'].is_integer() else row['amount']}"):
            col1, col2, col3 = st.columns(3)

            with col1:
                new_amount = st.text_input(
                    f"Amount {idx}", value=str(row['amount']))
            with col2:
                new_category = st.selectbox(f"Category {idx}", ["Food", "Transport", "Utilities", "Other"], index=[
                                            "Food", "Transport", "Utilities", "Other"].index(row['category']))
            with col3:
                new_note = st.text_input(f"Note {idx}", value=row['note'])

            new_date = st.date_input(
                f"Date {idx}", value=pd.to_datetime(row['date']).date())

            col4, col5 = st.columns(2)
            with col4:
                if st.button(f"Update {idx}"):
                    try:
                        updated_expense = Expense(
                            float(new_amount), new_category, new_date, new_note)
                        manager.edit_expense(idx, updated_expense)
                        st.success("Expense updated. Please reload.")
                        st.rerun()

                    except Exception as e:
                        st.error(f"Update failed: {str(e)}")
            with col5:
                if st.button(f"Delete {idx}"):
                    manager.remove_expense(idx)
                    st.warning("Expense deleted. Please reload.")
                    st.rerun()

    st.subheader("Total Spent by Category")
    summary_df = df_filtered.groupby("category")["amount"].sum().reset_index()
    st.dataframe(summary_df)

    st.subheader("Bar Chart of Expenses")
    st.bar_chart(summary_df.set_index("category"))

    csv_data = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Filtered CSV",
        data=csv_data,
        file_name="filtered_expenses.csv",
        mime="text/csv"
    )
else:
    st.info("No expenses found for the selected filters.")
