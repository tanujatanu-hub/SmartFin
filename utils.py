import sqlite3
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score


DB_NAME = "users.db"


def get_connection():

    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


# =================================================
# LOAD TRANSACTIONS FROM SQLITE
# =================================================

def load_data():

    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT
            id,
            date AS Date,
            category AS Category,
            amount AS Amount,
            type AS Type,
            user_id AS User_ID
        FROM transactions
        """,
        conn
    )

    conn.close()

    if df.empty:

        return pd.DataFrame(
            columns=[
                "Date",
                "Category",
                "Amount",
                "Type",
                "User_ID"
            ]
        )


    df["Date"] = pd.to_datetime(
        df["Date"],
        format="mixed"
    )

    df["Amount"] = pd.to_numeric(
        df["Amount"],
        errors="coerce"
    ).fillna(0)

    df["User_ID"] = pd.to_numeric(
        df["User_ID"],
        errors="coerce"
    ).fillna(0).astype(int)


    # Use transaction ID as dataframe index.
    # This allows Edit/Delete to work correctly.
    df.index = df["id"]

    return df


# =================================================
# GET CURRENT USER DATA
# =================================================

def get_user_data(df, user_id):

    if df.empty:
        return df.copy()

    return df[
        df["User_ID"] == int(user_id)
    ].copy()


# =================================================
# ADD TRANSACTION
# =================================================

def add_transaction(
    date,
    category,
    amount,
    t_type,
    user_id
):

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO transactions
        (
            user_id,
            date,
            category,
            amount,
            type
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            int(user_id),
            pd.to_datetime(date).strftime(
                "%Y-%m-%d"
            ),
            category,
            float(amount),
            t_type
        )
    )

    conn.commit()
    conn.close()


# =================================================
# SUMMARY
# =================================================

def get_summary(df):

    total_income = df[
        df["Type"] == "Income"
    ]["Amount"].sum()

    total_expenses = df[
        df["Type"] == "Expense"
    ]["Amount"].sum()

    savings = (
        total_income
        - total_expenses
    )

    return (
        total_income,
        total_expenses,
        savings
    )


# =================================================
# CATEGORY EXPENSE
# =================================================

def category_expense(df):

    return (
        df[
            df["Type"] == "Expense"
        ]
        .groupby("Category")["Amount"]
        .sum()
    )


# =================================================
# MONTHLY DATA
# =================================================

def prepare_monthly_data(df):

    df = df.copy()

    if df.empty:

        return pd.DataFrame(
            columns=[
                "Month",
                "Income",
                "Expense",
                "Savings",
                "Prev_Expense"
            ]
        )

    df["Month"] = (
        df["Date"]
        .dt.to_period("M")
    )

    monthly = (
        df.groupby(
            ["Month", "Type"]
        )["Amount"]
        .sum()
        .unstack()
        .fillna(0)
    )

    if "Income" not in monthly.columns:
        monthly["Income"] = 0

    if "Expense" not in monthly.columns:
        monthly["Expense"] = 0

    monthly["Savings"] = (
        monthly["Income"]
        - monthly["Expense"]
    )

    monthly["Prev_Expense"] = (
        monthly["Expense"]
        .shift(1)
    )

    monthly["Prev_Expense"] = (
        monthly["Prev_Expense"]
        .fillna(0)
    )

    monthly.reset_index(
        inplace=True
    )

    return monthly


# =================================================
# RANDOM FOREST MODEL
# =================================================

def train_model(monthly_df):

    X = monthly_df[
        ["Income", "Prev_Expense"]
    ]

    y = monthly_df["Expense"]

    model = RandomForestRegressor(
        random_state=42
    )

    model.fit(X, y)

    y_pred = model.predict(X)

    mae = mean_absolute_error(
        y,
        y_pred
    )

    r2 = r2_score(
        y,
        y_pred
    )

    return model, mae, r2


def predict_next(
    monthly_df,
    model
):

    last_row = monthly_df.iloc[-1]

    input_data = [[
        last_row["Income"],
        last_row["Prev_Expense"]
    ]]

    prediction = model.predict(
        input_data
    )

    return round(
        prediction[0],
        2
    )


# =================================================
# FINANCIAL HEALTH SCORE
# =================================================

def calculate_health_score(
    monthly_df
):

    if monthly_df.empty:
        return 0

    latest = monthly_df.iloc[-1]

    income = latest.get(
        "Income",
        0
    )

    expense = latest.get(
        "Expense",
        0
    )

    savings = latest.get(
        "Savings",
        0
    )

    if income == 0:
        return 0

    savings_ratio = (
        savings / income
    )

    score = 0

    score += min(
        max(
            savings_ratio * 100,
            0
        ),
        50
    )

    if expense < income * 0.7:

        score += 30

    elif expense < income:

        score += 15

    if len(monthly_df) > 1:

        prev = (
            monthly_df.iloc[-2]["Expense"]
        )

        change = (
            abs(expense - prev) / prev
            if prev != 0
            else 0
        )

        if change < 0.1:

            score += 20

        elif change < 0.3:

            score += 10

    return round(
        score,
        2
    )


# =================================================
# RECOMMENDATIONS
# =================================================

def generate_recommendations(
    monthly_df,
    monthly_salary,
    existing_savings,
    existing_debt,
    financial_goal,
    risk_appetite
):

    recs = []

    if monthly_df.empty:

        recs.append(
            "📝 Add income and expense "
            "transactions so the system "
            "can analyze your financial pattern."
        )

        return recs

    latest = monthly_df.iloc[-1]

    income = latest.get(
        "Income",
        0
    )

    expense = latest.get(
        "Expense",
        0
    )

    savings = latest.get(
        "Savings",
        0
    )

    if income > 0:

        expense_ratio = (
            expense / income
        )

        if expense_ratio > 0.80:

            recs.append(
                "⚠️ Your recorded expenses are "
                "relatively high compared with "
                "your recorded income."
            )

        elif expense_ratio > 0.60:

            recs.append(
                "💡 Your recorded expenses take "
                "a moderate portion of your "
                "recorded income."
            )

        else:

            recs.append(
                "✅ Your recorded expenses are "
                "below 60% of your recorded income."
            )

    if monthly_salary > 0:

        savings_ratio = (
            savings / monthly_salary
        )

        if savings_ratio < 0.20:

            recs.append(
                "💰 The current recorded savings "
                "are relatively low compared "
                "with the monthly salary."
            )

        else:

            recs.append(
                "✅ The current transaction data "
                "shows positive savings."
            )

    if existing_savings > 0:

        recs.append(
            f"🏦 Existing savings of approximately "
            f"₹{existing_savings:,.0f} are included "
            "in the financial profile."
        )

    else:

        recs.append(
            "💡 No existing savings were entered "
            "in the financial profile."
        )

    if existing_debt > 0:

        recs.append(
            f"⚠️ Existing debt of approximately "
            f"₹{existing_debt:,.0f} is considered "
            "in the analysis."
        )

    else:

        recs.append(
            "✅ No existing debt was entered "
            "in the financial profile."
        )

    recs.append(
        f"🎯 Financial goal selected: "
        f"**{financial_goal}**."
    )

    if risk_appetite == "Low":

        recs.append(
            "🛡️ Low risk appetite selected. "
            "The illustrative planning logic "
            "gives greater emphasis to emergency "
            "savings and lower-risk categories."
        )

    elif risk_appetite == "Medium":

        recs.append(
            "⚖️ Medium risk appetite selected. "
            "The illustrative planning logic "
            "uses a balanced allocation."
        )

    else:

        recs.append(
            "📈 High risk appetite selected. "
            "The illustrative planning logic "
            "allows a larger proportion for "
            "higher-risk categories."
        )

    if len(monthly_df) > 1:

        previous_expense = (
            monthly_df.iloc[-2]["Expense"]
        )

        if expense > previous_expense:

            recs.append(
                "📉 Expenses increased compared "
                "with the previous month."
            )

        elif expense < previous_expense:

            recs.append(
                "📈 Expenses decreased compared "
                "with the previous month."
            )

        else:

            recs.append(
                "➡️ Expenses remained approximately "
                "the same as the previous month."
            )

    return recs


# =================================================
# ILLUSTRATIVE INVESTMENT PLAN
# =================================================

def generate_investment_plan(
    monthly_savings,
    risk_appetite
):

    if monthly_savings <= 0:
        return {}

    if risk_appetite == "Low":

        allocation = {
            "Emergency Fund": 40,
            "Savings": 25,
            "Gold": 15,
            "Insurance / Protection": 10,
            "Equity / Stocks": 10
        }

    elif risk_appetite == "Medium":

        allocation = {
            "Emergency Fund": 25,
            "Savings": 15,
            "Gold": 15,
            "Insurance / Protection": 10,
            "Equity / Stocks": 35
        }

    else:

        allocation = {
            "Emergency Fund": 15,
            "Savings": 10,
            "Gold": 15,
            "Insurance / Protection": 10,
            "Equity / Stocks": 50
        }

    plan = {}

    for category, percentage in allocation.items():

        amount = (
            monthly_savings
            * percentage
            / 100
        )

        plan[category] = {
            "percentage": percentage,
            "amount": round(
                amount,
                2
            )
        }

    return plan


# =================================================
# XAI
# =================================================

def generate_xai_explanation(
    income,
    expense,
    savings,
    monthly_salary,
    existing_savings,
    existing_debt,
    financial_goal,
    risk_appetite,
    investment_plan
):

    expense_ratio = (
        expense / income * 100
        if income > 0
        else 0
    )

    explanation = {

        "Income":
            f"₹{income:,.0f}",

        "Recorded Expenses":
            f"₹{expense:,.0f}",

        "Recorded Savings":
            f"₹{savings:,.0f}",

        "Expense Ratio":
            f"{expense_ratio:.1f}%",

        "Existing Savings":
            f"₹{existing_savings:,.0f}",

        "Existing Debt":
            f"₹{existing_debt:,.0f}",

        "Financial Goal":
            financial_goal,

        "Risk Appetite":
            risk_appetite
    }

    if risk_appetite == "Low":

        rule_reason = (
            "The selected Low-risk rule assigns larger "
            "shares to Emergency Fund and Savings and "
            "smaller shares to Equity / Stocks."
        )

    elif risk_appetite == "Medium":

        rule_reason = (
            "The selected Medium-risk rule uses a more "
            "balanced distribution across the categories."
        )

    else:

        rule_reason = (
            "The selected High-risk rule assigns a larger "
            "share to Equity / Stocks in this academic "
            "prototype."
        )

    return explanation, rule_reason


# =================================================
# UPDATE TRANSACTION
# =================================================

def update_transaction(
    row_index,
    date,
    category,
    amount,
    t_type,
    user_id
):

    conn = get_connection()

    cursor = conn.execute(
        """
        UPDATE transactions

        SET
            date = ?,
            category = ?,
            amount = ?,
            type = ?

        WHERE
            id = ?
            AND user_id = ?
        """,
        (
            pd.to_datetime(date).strftime(
                "%Y-%m-%d"
            ),
            category,
            float(amount),
            t_type,
            int(row_index),
            int(user_id)
        )
    )

    conn.commit()

    success = cursor.rowcount > 0

    conn.close()

    return success


# =================================================
# DELETE TRANSACTION
# =================================================

def delete_transaction(
    row_index,
    user_id
):

    conn = get_connection()

    cursor = conn.execute(
        """
        DELETE FROM transactions

        WHERE
            id = ?
            AND user_id = ?
        """,
        (
            int(row_index),
            int(user_id)
        )
    )

    conn.commit()

    success = cursor.rowcount > 0

    conn.close()

    return success