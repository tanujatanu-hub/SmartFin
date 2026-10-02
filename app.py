import streamlit as st
import pandas as pd

from auth import (
    init_db,
    register_user,
    login_user,
    get_financial_profile,
    save_financial_profile
)

from utils import (
    load_data,
    get_user_data,
    add_transaction,
    get_summary,
    category_expense,
    prepare_monthly_data,
    train_model,
    predict_next,
    calculate_health_score,
    generate_recommendations,
    generate_investment_plan,
    generate_xai_explanation,
    update_transaction,
    delete_transaction
)


# =================================================
# PAGE SETTINGS
# =================================================

st.set_page_config(
    page_title="SmartFin",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =================================================
# CUSTOM CSS
# =================================================

st.markdown("""
<style>

/* ================================================
   SMARTFIN GLOBAL
   ================================================ */

.stApp {
    background-color: #f5f7f9;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}


/* ================================================
   SIDEBAR
   ================================================ */

[data-testid="stSidebar"] {
    background: #123c35;
    border-right: 1px solid #0f302b;
}

[data-testid="stSidebar"] * {
    color: #ffffff;
}

/* Sidebar input text */
[data-testid="stSidebar"] input {
    color: #ffffff !important;
    background-color: #194c43 !important;
}

/* Sidebar selectbox */
[data-testid="stSidebar"] div[data-baseweb="select"] {
    background-color: #194c43 !important;
    color: #ffffff !important;
}

[data-testid="stSidebar"] div[data-baseweb="select"] * {
    color: #ffffff !important;
}

/* Selectbox dropdown options */
[data-baseweb="popover"] {
    color: #17201e !important;
}

[data-baseweb="menu"] {
    color: #17201e !important;
}

[data-baseweb="option"] {
    color: #17201e !important;
    background-color: white !important;
}

/* Date input */
[data-testid="stSidebar"] input[type="text"] {
    color: #ffffff !important;
}

/* Number input buttons */
[data-testid="stSidebar"] button {
    color: #ffffff !important;
    border-radius: 8px;
}

[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stNumberInput input {
    background-color: #194c43;
    color: white;
    border: 1px solid #36766b;
    border-radius: 8px;
}

[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
    background-color: #194c43;
    color: white;
}

[data-testid="stSidebar"] button {
    border-radius: 8px;
}


/* ================================================
   SMARTFIN HEADER
   ================================================ */

.smartfin-header {
    background: linear-gradient(
        135deg,
        #0f2925,
        #155c4d
    );

    padding: 32px 38px;
    border-radius: 20px;
    margin-bottom: 28px;

    box-shadow:
        0 10px 30px rgba(15, 41, 37, 0.15);
}

.smartfin-title {
    font-size: 40px;
    font-weight: 800;
    color: white;
    margin-bottom: 4px;
}

.smartfin-subtitle {
    font-size: 17px;
    color: #d1fae5;
    font-weight: 600;
}

.smartfin-description {
    font-size: 14px;
    color: #cbd5e1;
    margin-top: 14px;
    max-width: 850px;
    line-height: 1.6;
}


/* ================================================
   SECTION HEADINGS
   ================================================ */

.section-heading {
    font-size: 24px;
    font-weight: 750;
    color: #17201e;
    margin-top: 12px;
    margin-bottom: 6px;
}

.section-description {
    color: #64748b;
    font-size: 14px;
    margin-bottom: 18px;
}


/* ================================================
   METRIC CARDS
   ================================================ */

.metric-card {
    background: white;
    border-radius: 16px;
    padding: 22px;
    border: 1px solid #e5e7eb;

    box-shadow:
        0 5px 18px rgba(15, 23, 42, 0.06);

    min-height: 125px;
}

.metric-title {
    font-size: 12px;
    color: #64748b;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin-bottom: 9px;
}

.metric-value {
    font-size: 29px;
    font-weight: 800;
    color: #17201e;
}

.metric-subtitle {
    font-size: 12px;
    color: #94a3b8;
    margin-top: 5px;
}


/* ================================================
   DASHBOARD CARDS
   ================================================ */

.dashboard-card {
    background: white;
    border-radius: 16px;
    padding: 22px;
    border: 1px solid #e5e7eb;

    box-shadow:
        0 5px 18px rgba(15, 23, 42, 0.05);

    margin-bottom: 20px;
}


/* ================================================
   SMART INSIGHT
   ================================================ */

.insight-card {
    background: #ecfdf5;
    border-left: 5px solid #10b981;
    padding: 20px;
    border-radius: 12px;
    margin-top: 10px;
    margin-bottom: 20px;
}

.insight-title {
    font-size: 15px;
    font-weight: 700;
    color: #065f46;
}

.insight-text {
    font-size: 14px;
    color: #047857;
    margin-top: 6px;
}


/* ================================================
   HEALTH SCORE
   ================================================ */

.health-card {
    background: white;
    border-radius: 16px;
    padding: 25px;
    border: 1px solid #e5e7eb;

    box-shadow:
        0 5px 18px rgba(15, 23, 42, 0.05);

    text-align: center;
}

.health-score {
    font-size: 46px;
    font-weight: 850;
    color: #059669;
}


/* ================================================
   FINANCIAL PLAN
   ================================================ */

.plan-card {
    background: white;
    border-radius: 18px;
    padding: 25px;
    border: 1px solid #e5e7eb;

    box-shadow:
        0 5px 18px rgba(15, 23, 42, 0.06);

    margin-bottom: 20px;
}

.plan-title {
    font-size: 20px;
    font-weight: 750;
    color: #17201e;
}

.plan-caption {
    font-size: 13px;
    color: #64748b;
    margin-top: 5px;
}


/* ================================================
   XAI
   ================================================ */

.xai-card {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 16px;
    padding: 24px;
    margin-top: 20px;
}

.xai-title {
    font-size: 20px;
    font-weight: 750;
    color: #334155;
}


/* ================================================
   TABS
   ================================================ */

button[data-baseweb="tab"] {
    font-size: 15px;
    font-weight: 650;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #059669;
}


/* ================================================
   TABLE
   ================================================ */

[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}


/* ================================================
   BUTTONS
   ================================================ */

/* BUTTONS */

.stButton > button {
    border-radius: 9px;
    font-weight: 600;
}

/* SIDEBAR BUTTONS */

[data-testid="stSidebar"] .stButton > button {
    background-color: #194c43 !important;
    color: #ffffff !important;
    border: 1px solid #36766b !important;
    border-radius: 9px !important;
    font-weight: 700 !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #246356 !important;
    color: #ffffff !important;
    border-color: #6aa99d !important;
}
/* Date input visibility */
[data-testid="stDateInput"] input {
    color: #1f2937 !important;
    background-color: #ffffff !important;
    -webkit-text-fill-color: #1f2937 !important;
}

[data-testid="stDateInput"] input::placeholder {
    color: #6b7280 !important;
    opacity: 1 !important;
}

[data-testid="stDateInput"] button {
    color: #1f2937 !important;
}


/* ================================================
   HEADINGS
   ================================================ */

h1, h2, h3 {
    color: #17201e;
}

</style>
""", unsafe_allow_html=True)


# =================================================
# DATABASE
# =================================================

init_db()


# =================================================
# SESSION
# =================================================

if "user" not in st.session_state:
    st.session_state.user = None


# =================================================
# LOGIN / REGISTER
# =================================================

if st.session_state.user is None:

    st.markdown("""
    <style>
        .auth-page {
            max-width: 1200px;
            margin: 20px auto;
        }

        .auth-left {
            background: linear-gradient(145deg, #0b3029, #155c4d);
            border-radius: 24px;
            padding: 48px 42px;
            min-height: 600px;
            box-shadow: 0 14px 35px rgba(15,41,37,0.16);
            color: white;
        }

        .auth-left-title {
            font-size: 42px;
            font-weight: 800;
            margin-bottom: 10px;
        }

        .auth-left-title span {
            color: #79e0b3;
        }

        .auth-left-subtitle {
            color: #d8fff2;
            font-size: 18px;
            font-weight: 600;
            line-height: 1.5;
            margin-bottom: 22px;
        }

        .auth-left-text {
            color: #c9e8df;
            font-size: 14px;
            line-height: 1.7;
            margin-bottom: 35px;
        }

        .auth-feature {
            display: flex;
            align-items: flex-start;
            gap: 14px;
            margin: 22px 0;
        }

        .auth-feature-icon {
            font-size: 24px;
            min-width: 35px;
        }

        .auth-feature-title {
            color: white;
            font-size: 15px;
            font-weight: 700;
            margin-bottom: 4px;
        }

        .auth-feature-text {
            color: #b9ddd3;
            font-size: 13px;
            line-height: 1.5;
        }

        .auth-tagline {
            color: #79e0b3;
            font-size: 17px;
            font-weight: 700;
            margin-top: 40px;
        }

        .auth-logo {
            text-align: center;
            font-size: 27px;
            font-weight: 800;
            color: #123c35;
            margin-bottom: 28px;
        }

        .auth-logo span {
            color: #10b981;
        }

        .auth-card-title {
            font-size: 30px;
            font-weight: 800;
            color: #123c35;
            text-align: center;
            margin-bottom: 5px;
        }

        .auth-card-subtitle {
            color: #64748b;
            font-size: 14px;
            text-align: center;
            margin-bottom: 25px;
        }

        .auth-page [data-testid="stTextInput"] input {
            border-radius: 10px !important;
            border: 1px solid #d9e2e7 !important;
            background: white !important;
            color: #17201e !important;
            -webkit-text-fill-color: #17201e !important;
            padding: 12px 14px !important;
        }

        .auth-page [data-testid="stTextInput"] input:focus {
            border-color: #159a76 !important;
            box-shadow: 0 0 0 2px rgba(21,154,118,0.12) !important;
        }

        .auth-page .stButton > button {
            width: 100% !important;
            min-height: 46px !important;
            background: #116b58 !important;
            color: white !important;
            border: 1px solid #116b58 !important;
            border-radius: 10px !important;
            font-size: 15px !important;
            font-weight: 700 !important;
        }

        .auth-page .stButton > button:hover {
            background: #0d594a !important;
            border-color: #0d594a !important;
            color: white !important;
        }

        .auth-page [data-testid="stRadio"] > div {
            justify-content: center;
        }

        .auth-page [data-testid="stRadio"] label {
            font-weight: 650 !important;
        }

        .auth-note {
            text-align: center;
            color: #94a3b8;
            font-size: 12px;
            margin-top: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

    # =================================================
    # COLUMNS
    # =================================================

    left_col, right_col = st.columns(
        [1.05, 0.95],
        gap="large"
    )

    # =================================================
    # LEFT SIDE
    # =================================================

    with left_col:

        st.markdown("""
<div class="auth-left">

<div class="auth-left-title">
Smart<span>Fin</span>
</div>

<div class="auth-left-subtitle">
Personal Financial Planning &amp;<br>
Analysis System
</div>

<div class="auth-left-text">
Track your finances, understand spending patterns,
analyze financial health, and explore an illustrative
financial plan.
</div>

<div class="auth-feature">
<div class="auth-feature-icon">📊</div>
<div>
<div class="auth-feature-title">Track Your Finances</div>
<div class="auth-feature-text">
Keep a clear record of your income and expenses.
</div>
</div>
</div>

<div class="auth-feature">
<div class="auth-feature-icon">🤖</div>
<div>
<div class="auth-feature-title">Analyze Spending with ML</div>
<div class="auth-feature-text">
Analyze historical spending patterns using machine learning.
</div>
</div>
</div>

<div class="auth-feature">
<div class="auth-feature-icon">💡</div>
<div>
<div class="auth-feature-title">Understand Your Financial Plan</div>
<div class="auth-feature-text">
Explore an illustrative plan with transparent XAI explanations.
</div>
</div>
</div>

<div class="auth-tagline">
Better Decisions, Brighter Financial Future
</div>

<div style="
margin-top:35px;
text-align:right;
font-size:60px;
line-height:1;
">
🪙 📈 🌱
</div>

</div>
""", unsafe_allow_html=True)

    # =================================================
    # RIGHT SIDE
    # =================================================

    with right_col:

        auth_card = st.container(border=True)

        with auth_card:

            st.markdown(
                '<div class="auth-logo">💰 Smart<span>Fin</span></div>',
                unsafe_allow_html=True
            )

            mode = st.radio(
                "",
                ["Login", "Register"],
                horizontal=True,
                key="auth_mode"
            )

            # =================================================
            # LOGIN
            # =================================================

            if mode == "Login":

                st.markdown(
                    '<div class="auth-card-title">Welcome back 👋</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    '<div class="auth-card-subtitle">'
                    'Login to continue to SmartFin'
                    '</div>',
                    unsafe_allow_html=True
                )

                email = st.text_input(
                    "Email",
                    placeholder="Enter your email",
                    key="login_email"
                )

                password = st.text_input(
                    "Password",
                    placeholder="Enter your password",
                    type="password",
                    key="login_password"
                )

                if st.button(
                    "↪  Login",
                    key="login_button"
                ):

                    user = login_user(
                        email,
                        password
                    )

                    if user:
                        st.session_state.user = user
                        st.rerun()

                    else:
                        st.error(
                            "Invalid email or password."
                        )

                st.markdown(
                    '<div class="auth-note">'
                    'Secure account access'
                    '</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    '<div class="auth-note">'
                    'Don\'t have an account? Select '
                    '<b>Register</b> above.'
                    '</div>',
                    unsafe_allow_html=True
                )

            # =================================================
            # REGISTER
            # =================================================

            else:

                st.markdown(
                    '<div class="auth-card-title">'
                    'Create your account ✨'
                    '</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    '<div class="auth-card-subtitle">'
                    'Start using SmartFin today'
                    '</div>',
                    unsafe_allow_html=True
                )

                name = st.text_input(
                    "Full Name",
                    placeholder="Enter your full name",
                    key="register_name"
                )

                email = st.text_input(
                    "Email",
                    placeholder="Enter your email",
                    key="register_email"
                )

                password = st.text_input(
                    "Password",
                    placeholder="Create a password",
                    type="password",
                    key="register_password"
                )

                if st.button(
                    "Create Account →",
                    key="register_button"
                ):

                    if not name or not email or not password:

                        st.warning(
                            "Please fill in all fields."
                        )

                    else:

                        success, message = register_user(
                            name,
                            email,
                            password
                        )

                        if success:

                            st.success(message)

                            st.info(
                                "Select Login above to continue."
                            )

                        else:

                            st.error(message)

                st.markdown(
                    '<div class="auth-note">'
                    'Already have an account? Select '
                    '<b>Login</b> above.'
                    '</div>',
                    unsafe_allow_html=True
                )

    # VERY IMPORTANT:
    # This is INSIDE the if block.
    st.stop()
# =================================================
# CURRENT USER
# =================================================

user = st.session_state.user

user_id = user["id"]
user_name = user["name"]
user_email = user["email"]


# =================================================
# LOAD DATA
# =================================================

df = load_data()

filtered_user_df = get_user_data(
    df,
    user_id
)


# =================================================
# SIDEBAR
# =================================================

st.sidebar.markdown(
    """
<div style="
    text-align:center;
    padding:10px 0 22px 0;
">
<div style="
    font-size:30px;
    font-weight:800;
    color:white;
">
💰 SmartFin
</div>

<div style="
    font-size:12px;
    color:#a7d8ce;
    margin-top:4px;
">
Financial Planning &amp; Analysis
</div>
</div>
""",
    unsafe_allow_html=True
)


# =================================================
# USER CARD
# =================================================

st.sidebar.markdown(
    """
<div style="
    background:#194c43;
    padding:16px;
    border-radius:12px;
    margin-bottom:22px;
    border:1px solid #36766b;
">

<div style="
    font-size:11px;
    color:#a7d8ce;
    margin-bottom:5px;
    letter-spacing:0.8px;
    font-weight:700;
">
LOGGED IN AS
</div>

<div style="
    font-size:17px;
    font-weight:700;
    color:white;
">
👋 {}
</div>

<div style="
    font-size:12px;
    color:#cbd5e1;
    margin-top:4px;
    word-break:break-word;
">
{}
</div>

</div>
""".format(
        user_name,
        user_email
    ),
    unsafe_allow_html=True
)


# =================================================
# SIDEBAR FILTER LABEL
# =================================================

st.sidebar.markdown(
    """
<div style="
    font-size:11px;
    font-weight:700;
    letter-spacing:1px;
    color:#8fcfc2;
    margin:8px 0 10px 2px;
">
FILTERS
</div>
""",
    unsafe_allow_html=True
)


# =================================================
# FILTERS
# =================================================

st.sidebar.header(
    "📅 Filters"
)

if not filtered_user_df.empty:

    filtered_user_df = filtered_user_df.copy()

    filtered_user_df["Month"] = (
        filtered_user_df["Date"]
        .dt.to_period("M")
    )

    months = (
        filtered_user_df["Month"]
        .astype(str)
        .unique()
    )

    selected_month = st.sidebar.selectbox(
        "Select Month",
        months,
        key="filter_month"
    )

    selected_df = filtered_user_df[
        filtered_user_df["Month"].astype(str)
        == selected_month
    ]

else:

    selected_df = filtered_user_df


# =================================================
# ADD TRANSACTION
# =================================================

st.sidebar.header(
    "➕ Add Transaction"
)

date = st.sidebar.date_input(
    "Date",
    key="transaction_date"
)

category = st.sidebar.text_input(
    "Category",
    key="transaction_category"
)

amount = st.sidebar.number_input(
    "Amount",
    min_value=0.0,
    step=100.0,
    key="transaction_amount"
)

t_type = st.sidebar.selectbox(
    "Type",
    ["Expense", "Income"],
    key="transaction_type"
)

if st.sidebar.button(
    "Add Transaction",
    key="add_transaction_button"
):

    if amount <= 0:

        st.sidebar.warning(
            "Enter an amount greater than zero."
        )

    elif not category:

        st.sidebar.warning(
            "Enter a category."
        )

    else:

        add_transaction(
            date,
            category,
            amount,
            t_type,
            user_id
        )

        st.sidebar.success(
            "Transaction added!"
        )

        st.rerun()


# =================================================
# FINANCIAL PROFILE
# =================================================

st.sidebar.divider()

st.sidebar.header(
    "💼 Financial Profile"
)

profile = get_financial_profile(
    user_id
)

monthly_salary = st.sidebar.number_input(
    "Monthly Salary (₹)",
    min_value=0.0,
    value=float(
        profile["monthly_salary"]
    ),
    step=1000.0,
    key=f"profile_salary_{user_id}"
)

existing_savings = st.sidebar.number_input(
    "Existing Savings (₹)",
    min_value=0.0,
    value=float(
        profile["existing_savings"]
    ),
    step=5000.0,
    key=f"profile_savings_{user_id}"
)

debt = st.sidebar.number_input(
    "Existing Debt (₹)",
    min_value=0.0,
    value=float(
        profile["existing_debt"]
    ),
    step=5000.0,
    key=f"profile_debt_{user_id}"
)

financial_goals = [
    "Wealth Creation",
    "Emergency Fund",
    "Buying a House",
    "Education",
    "Retirement"
]

saved_goal = profile["financial_goal"]

if saved_goal not in financial_goals:
    saved_goal = "Wealth Creation"

financial_goal = st.sidebar.selectbox(
    "Financial Goal",
    financial_goals,
    index=financial_goals.index(
        saved_goal
    ),
    key=f"profile_goal_{user_id}"
)

risk_options = [
    "Low",
    "Medium",
    "High"
]

saved_risk = profile["risk_appetite"]

if saved_risk not in risk_options:
    saved_risk = "Low"

risk_appetite = st.sidebar.selectbox(
    "Risk Appetite",
    risk_options,
    index=risk_options.index(
        saved_risk
    ),
    key=f"profile_risk_{user_id}"
)

if st.sidebar.button(
    "💾 Save Financial Profile",
    key=f"profile_save_{user_id}"
):

    save_financial_profile(
        user_id,
        monthly_salary,
        existing_savings,
        debt,
        financial_goal,
        risk_appetite
    )

    st.sidebar.success(
        "Financial profile saved successfully!"
    )


# =================================================
# LOGOUT
# =================================================

if st.sidebar.button(
    "Logout",
    key="logout_button"
):

    for key in [
        f"profile_salary_{user_id}",
        f"profile_savings_{user_id}",
        f"profile_debt_{user_id}",
        f"profile_goal_{user_id}",
        f"profile_risk_{user_id}",
        "selected_transaction"
    ]:

        st.session_state.pop(
            key,
            None
        )

    st.session_state.user = None

    st.rerun()


# =================================================
# MAIN HEADER
# =================================================

st.markdown(
    """
<div class="smartfin-header">
<div class="smartfin-title">SmartFin</div>
<div class="smartfin-subtitle">Personal Financial Planning &amp; Analysis System</div>
<div class="smartfin-description">
Track your finances, understand spending patterns,
analyze financial health, and explore an
illustrative financial plan.
</div>
</div>
""",
    unsafe_allow_html=True
)


# =================================================
# PREPARE MONTHLY DATA
# =================================================

monthly_df = prepare_monthly_data(
    filtered_user_df
)


# =================================================
# SMARTFIN TABS
# =================================================

tab_overview, tab_transactions, tab_analysis, tab_plan = st.tabs(
    [
        "📊 Overview",
        "💳 Transactions",
        "📈 Analysis & ML",
        "💼 Financial Plan"
    ]
)


# =================================================
# OVERVIEW TAB
# =================================================

with tab_overview:

    st.markdown(
        """
<div class="section-heading">
Financial Overview
</div>

<div class="section-description">
Get a quick view of your recorded financial activity.
</div>
""",
        unsafe_allow_html=True
    )


    # =============================================
    # SUMMARY
    # =============================================

    if not selected_df.empty:

        income, expense, savings = get_summary(
            selected_df
        )

    else:

        income = 0
        expense = 0
        savings = 0


    savings_rate = (
        savings / income * 100
        if income > 0
        else 0
    )


    # =============================================
    # METRIC CARDS
    # =============================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            f"""
<div class="metric-card">
<div class="metric-title">
MONTHLY INCOME
</div>

<div class="metric-value">
₹{income:,.0f}
</div>

<div class="metric-subtitle">
Recorded income
</div>
</div>
""",
            unsafe_allow_html=True
        )


    with col2:

        st.markdown(
            f"""
<div class="metric-card">
<div class="metric-title">
MONTHLY EXPENSES
</div>

<div class="metric-value">
₹{expense:,.0f}
</div>

<div class="metric-subtitle">
Recorded spending
</div>
</div>
""",
            unsafe_allow_html=True
        )


    with col3:

        st.markdown(
            f"""
<div class="metric-card">
<div class="metric-title">
MONTHLY SAVINGS
</div>

<div class="metric-value">
₹{savings:,.0f}
</div>

<div class="metric-subtitle">
Income minus expenses
</div>
</div>
""",
            unsafe_allow_html=True
        )


    with col4:

        st.markdown(
            f"""
<div class="metric-card">
<div class="metric-title">
SAVINGS RATE
</div>

<div class="metric-value">
{savings_rate:.1f}%
</div>

<div class="metric-subtitle">
Savings as % of income
</div>
</div>
""",
            unsafe_allow_html=True
        )


    st.write("")


    # =============================================
    # EXPENSE ANALYSIS
    # =============================================

    st.markdown(
        """
<div class="section-heading">
Expense Analysis
</div>

<div class="section-description">
Understand where your recorded spending is going.
</div>
""",
        unsafe_allow_html=True
    )


    if not selected_df.empty:

        cat_data = category_expense(
            selected_df
        )

        col5, col6 = st.columns(2)


        # =========================================
        # BAR CHART
        # =========================================

        with col5:

            st.markdown(
                """
<div class="dashboard-card">

<div class="plan-title">
Expenses by Category
</div>

<div class="plan-caption">
Recorded expenses across categories
</div>

</div>
""",
                unsafe_allow_html=True
            )

            if not cat_data.empty:

                st.bar_chart(
                    cat_data,
                    use_container_width=True
                )

            else:

                st.info(
                    "No expense data available."
                )


        # =========================================
        # PIE CHART
        # =========================================

        with col6:

            st.markdown(
                """
<div class="dashboard-card">

<div class="plan-title">
Expenses Distribution
</div>

<div class="plan-caption">
Percentage of spending by category
</div>

</div>
""",
                unsafe_allow_html=True
            )

            if not cat_data.empty:

                pie_df = (
                    cat_data
                    .reset_index()
                )

                fig = (
                    pie_df
                    .set_index("Category")
                    .plot.pie(
                        y="Amount",
                        autopct="%1.1f%%",
                        figsize=(5, 5),
                        legend=False
                    )
                    .figure
                )

                st.pyplot(
                    fig,
                    use_container_width=True
                )

            else:

                st.info(
                    "No expense data available."
                )

    else:

        st.info(
            "Add transactions to view expense charts."
        )


    # =============================================
    # SMART INSIGHT
    # =============================================

    st.markdown(
        """
<div class="section-heading">
Smart Insight
</div>

<div class="section-description">
A quick summary of your current spending pattern.
</div>
""",
        unsafe_allow_html=True
    )


    if not selected_df.empty:

        cat_data = category_expense(
            selected_df
        )

        if not cat_data.empty:

            top_category = cat_data.idxmax()
            top_value = cat_data.max()

            st.markdown(
                f"""
<div class="insight-card">

<div class="insight-title">
💡 Spending Pattern Detected
</div>

<div class="insight-text">
Your highest recorded spending category is
<strong>{top_category}</strong>
with an amount of
<strong>₹{top_value:,.0f}</strong>.
</div>

</div>
""",
                unsafe_allow_html=True
            )


            if savings < 0:

                st.error(
                    "⚠️ Expenses are higher than income."
                )

            elif (
                income > 0
                and savings < income * 0.2
            ):

                st.warning(
                    "⚠️ Your current savings level "
                    "is relatively low."
                )

            else:

                st.success(
                    "✅ Your current income and expenses "
                    "show positive savings."
                )

        else:

            st.info(
                "Add expense transactions to generate insights."
            )

    else:

        st.info(
            "Add transactions to generate smart insights."
        )


# =================================================
# TRANSACTIONS TAB
# =================================================

with tab_transactions:

    st.markdown(
        """
<div class="section-heading">
My Transactions
</div>

<div class="section-description">
View, edit, and manage your recorded financial transactions.
</div>
""",
        unsafe_allow_html=True
    )


    if not selected_df.empty:

        display_df = (
            selected_df
            .sort_values(
                by="Date",
                ascending=False
            )
        )


        st.markdown(
            """
<div class="dashboard-card">

<div class="plan-title">
Transaction History
</div>

<div class="plan-caption">
Your recorded income and expenses
</div>

</div>
""",
            unsafe_allow_html=True
        )


        st.dataframe(
            display_df[
                [
                    "Date",
                    "Category",
                    "Amount",
                    "Type"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )


        # =========================================
        # MANAGE TRANSACTIONS
        # =========================================

        st.markdown(
            """
<div class="section-heading">
Manage Transactions
</div>

<div class="section-description">
Select a transaction below to update or delete it.
</div>
""",
            unsafe_allow_html=True
        )


        transaction_options = []


        for index, row in display_df.iterrows():

            label = (
                f"{index} | "
                f"{row['Date'].strftime('%Y-%m-%d')} | "
                f"{row['Category']} | "
                f"₹{row['Amount']:,.2f} | "
                f"{row['Type']}"
            )

            transaction_options.append(
                (index, label)
            )


        selected_transaction = st.selectbox(
            "Select a transaction",
            transaction_options,
            format_func=lambda x: x[1],
            key="selected_transaction"
        )


        selected_index = selected_transaction[0]

        selected_row = display_df.loc[
            selected_index
        ]


        # =========================================
        # EDIT TRANSACTION
        # =========================================

        st.write(
            "#### ✏️ Edit Transaction"
        )


        edit_col1, edit_col2 = st.columns(2)


        with edit_col1:

            edit_date = st.date_input(
                "Date",
                value=selected_row[
                    "Date"
                ].date(),
                key="edit_date"
            )


        with edit_col2:

            edit_category = st.text_input(
                "Category",
                value=str(
                    selected_row[
                        "Category"
                    ]
                ),
                key="edit_category"
            )


        edit_col3, edit_col4 = st.columns(2)


        with edit_col3:

            edit_amount = st.number_input(
                "Amount",
                min_value=0.0,
                value=float(
                    selected_row[
                        "Amount"
                    ]
                ),
                step=100.0,
                key="edit_amount"
            )


        with edit_col4:

            edit_type = st.selectbox(
                "Type",
                ["Expense", "Income"],
                index=(
                    0
                    if selected_row["Type"] == "Expense"
                    else 1
                ),
                key="edit_type"
            )


        save_col, delete_col = st.columns(2)


        # =========================================
        # SAVE
        # =========================================

        with save_col:

            if st.button(
                "💾 Save Changes",
                key="save_transaction"
            ):

                if not edit_category.strip():

                    st.error(
                        "Category cannot be empty."
                    )

                elif edit_amount <= 0:

                    st.error(
                        "Amount must be greater than zero."
                    )

                else:

                    success = update_transaction(
                        selected_index,
                        edit_date,
                        edit_category.strip(),
                        edit_amount,
                        edit_type,
                        user_id
                    )


                    if success:

                        st.success(
                            "Transaction updated successfully!"
                        )

                        st.rerun()

                    else:

                        st.error(
                            "Unable to update this transaction."
                        )


        # =========================================
        # DELETE
        # =========================================

        with delete_col:

            if st.button(
                "🗑️ Delete Transaction",
                key="delete_transaction"
            ):

                success = delete_transaction(
                    selected_index,
                    user_id
                )


                if success:

                    st.success(
                        "Transaction deleted successfully!"
                    )

                    st.rerun()

                else:

                    st.error(
                        "Unable to delete this transaction."
                    )


    else:

        st.info(
            "No transactions found for this user."
        )


# =================================================
# ANALYSIS & MACHINE LEARNING TAB
# =================================================

with tab_analysis:

    st.markdown(
        """
<div class="section-heading">
Analysis & Machine Learning
</div>

<div class="section-description">
Analyze spending patterns, predict expenses,
and review financial health.
</div>
""",
        unsafe_allow_html=True
    )


    # =============================================
    # AI EXPENSE PREDICTION
    # =============================================

    st.markdown(
        """
<div class="dashboard-card">

<div style="
    font-size:12px;
    font-weight:800;
    letter-spacing:1px;
    color:#059669;
    margin-bottom:6px;
">
MACHINE LEARNING MODEL
</div>

<div class="plan-title">
🤖 Random Forest Expense Prediction
</div>

<div class="plan-caption">
The model analyzes historical monthly expense
patterns to estimate the next month's recorded expenses.
</div>

</div>
""",
        unsafe_allow_html=True
    )


    if len(monthly_df) >= 2:

        model, mae, r2 = train_model(
            monthly_df
        )


        prediction = predict_next(
            monthly_df,
            model
        )


        col1, col2, col3 = st.columns(3)


        with col1:

            st.markdown(
                f"""
<div class="metric-card">

<div class="metric-title">
PREDICTED EXPENSE
</div>

<div class="metric-value">
₹{prediction:,.0f}
</div>

<div class="metric-subtitle">
Estimated next month
</div>

</div>
""",
                unsafe_allow_html=True
            )


        with col2:

            st.markdown(
                f"""
<div class="metric-card">

<div class="metric-title">
R² SCORE
</div>

<div class="metric-value">
{r2:.2f}
</div>

<div class="metric-subtitle">
Model performance
</div>

</div>
""",
                unsafe_allow_html=True
            )


        with col3:

            st.markdown(
                f"""
<div class="metric-card">

<div class="metric-title">
MEAN ABSOLUTE ERROR
</div>

<div class="metric-value">
₹{mae:,.0f}
</div>

<div class="metric-subtitle">
Prediction error
</div>

</div>
""",
                unsafe_allow_html=True
            )


        st.markdown(
            """
<div class="insight-card">

<div class="insight-title">
🤖 How the ML component works
</div>

<div class="insight-text">
The Random Forest model learns patterns from
previously recorded monthly expenses and uses
these patterns to estimate the next month's expense.
R² Score and Mean Absolute Error are displayed
to evaluate prediction performance.
</div>

</div>
""",
            unsafe_allow_html=True
        )


    else:

        st.info(
            "Add transactions for at least two months "
            "to enable expense prediction."
        )


    # =============================================
    # FINANCIAL HEALTH SCORE
    # =============================================

    st.markdown(
        """
<div class="section-heading">
Financial Health Score
</div>

<div class="section-description">
A score calculated from your recorded income,
expenses, savings, and financial patterns.
</div>
""",
        unsafe_allow_html=True
    )


    if not monthly_df.empty:

        score = calculate_health_score(
            monthly_df
        )


        st.markdown(
            f"""
<div class="health-card">

<div class="metric-title">
FINANCIAL HEALTH
</div>

<div class="health-score">
{score}/100
</div>

<div class="metric-subtitle">
Based on recorded financial activity
</div>

</div>
""",
            unsafe_allow_html=True
        )


        if score < 40:

            st.warning(
                "Expense control and savings could be improved."
            )

        elif score < 70:

            st.info(
                "Your financial health score is moderate."
            )

        else:

            st.success(
                "Your recorded financial indicators "
                "show a stronger score."
            )

    else:

        st.info(
            "Add transactions to calculate your "
            "financial health score."
        )


    # =============================================
    # SMART RECOMMENDATIONS
    # =============================================

    st.markdown(
        """
<div class="section-heading">
Smart Recommendations
</div>

<div class="section-description">
System-generated observations based on your
recorded financial data.
</div>
""",
        unsafe_allow_html=True
    )


    recs = generate_recommendations(
        monthly_df,
        monthly_salary,
        existing_savings,
        debt,
        financial_goal,
        risk_appetite
    )


    if recs:

        for recommendation in recs:

            st.markdown(
                f"""
<div class="insight-card">

<div class="insight-text">
{recommendation}
</div>

</div>
""",
                unsafe_allow_html=True
            )

    else:

        st.success(
            "No additional recommendations at this time."
        )


# =================================================
# FINANCIAL PLAN TAB
# =================================================

with tab_plan:

    st.markdown(
        """
<div class="section-heading">
Financial Plan
</div>

<div class="section-description">
Explore an illustrative allocation based on
the selected financial profile.
</div>
""",
        unsafe_allow_html=True
    )


    # =============================================
    # INVESTMENT SUPPORT PLAN
    # =============================================

    st.markdown(
        """
<div class="plan-card">

<div class="plan-title">
📊 Investment Support Plan
</div>

<div class="plan-caption">
Illustrative allocation generated using
the selected prototype rule.
</div>

</div>
""",
        unsafe_allow_html=True
    )


    st.caption(
        "Illustrative academic prototype only — "
        "not personalized financial advice."
    )


    # =============================================
    # GOAL + RISK
    # =============================================

    col1, col2 = st.columns(2)


    with col1:

        st.markdown(
            f"""
<div class="dashboard-card">

<div class="metric-title">
FINANCIAL GOAL
</div>

<div class="metric-value"
style="font-size:22px;">
{financial_goal}
</div>

</div>
""",
            unsafe_allow_html=True
        )


    with col2:

        st.markdown(
            f"""
<div class="dashboard-card">

<div class="metric-title">
RISK APPETITE
</div>

<div class="metric-value"
style="font-size:22px;">
{risk_appetite}
</div>

</div>
""",
            unsafe_allow_html=True
        )


    # =============================================
    # INVESTIBLE AMOUNT
    # =============================================

    investible_amount = max(
        savings,
        0
    )


    st.markdown(
        f"""
<div class="insight-card">

<div class="insight-title">
Illustrative Monthly Amount
</div>

<div class="insight-text">
₹{investible_amount:,.2f}
available after the selected month's
recorded expenses.
</div>

</div>
""",
        unsafe_allow_html=True
    )


    # =============================================
    # ALLOCATION
    # =============================================

    if investible_amount > 0:

        investment_plan = generate_investment_plan(
            investible_amount,
            risk_appetite
        )


        plan_data = []


        for category, details in investment_plan.items():

            plan_data.append(
                {
                    "Category": category,
                    "Percentage": f"{details['percentage']}%",
                    "Amount": f"₹{details['amount']:,.2f}"
                }
            )


        plan_df = pd.DataFrame(
            plan_data
        )


        st.markdown(
            """
<div class="section-heading">
Illustrative Allocation
</div>

<div class="section-description">
Distribution generated by the prototype's
selected risk-based rule.
</div>
""",
            unsafe_allow_html=True
        )


        st.dataframe(
            plan_df,
            use_container_width=True,
            hide_index=True
        )


    else:

        investment_plan = {}


        st.warning(
            "No positive amount is available "
            "for the illustrative allocation."
        )


    # =============================================
    # XAI EXPLANATION
    # =============================================

    st.markdown(
        """
<div class="xai-card">

<div class="xai-title">
🔍 Why was this plan generated?
</div>

<div class="plan-caption">
Explainable AI view showing the inputs
and prototype rule used to generate
the illustrative allocation.
</div>

</div>
""",
        unsafe_allow_html=True
    )


    st.caption(
        "Explainable AI view: this section shows "
        "the inputs and prototype rules used to "
        "generate the illustrative allocation. "
        "It is not personalized financial advice."
    )


    if investible_amount > 0:

        xai_data, rule_reason = (
            generate_xai_explanation(
                income,
                expense,
                savings,
                monthly_salary,
                existing_savings,
                debt,
                financial_goal,
                risk_appetite,
                investment_plan
            )
        )


        # =========================================
        # FACTORS
        # =========================================

        st.markdown(
            """
<div class="section-heading">
📌 Factors Considered
</div>
""",
            unsafe_allow_html=True
        )


        factor_col1, factor_col2 = st.columns(2)


        factor_items = list(
            xai_data.items()
        )


        for i, (factor, value) in enumerate(
            factor_items
        ):

            target_col = (
                factor_col1
                if i % 2 == 0
                else factor_col2
            )

            with target_col:

                st.markdown(
                    f"""
<div class="dashboard-card">

<div class="metric-title">
{factor.upper()}
</div>

<div class="metric-value"
style="font-size:20px;">
{value}
</div>

</div>
""",
                    unsafe_allow_html=True
                )


        # =========================================
        # PROTOTYPE REASONING
        # =========================================

        st.markdown(
            """
<div class="section-heading">
🧠 Prototype Reasoning
</div>
""",
            unsafe_allow_html=True
        )


        st.info(
            f"The system recorded "
            f"₹{income:,.0f} of income, "
            f"₹{expense:,.0f} of expenses, "
            f"and ₹{savings:,.0f} of savings "
            f"for the selected month. "
            f"The selected financial goal is "
            f"**{financial_goal}** and the selected "
            f"risk appetite is **{risk_appetite}**. "
            f"{rule_reason}"
        )


        # =========================================
        # ALLOCATION RULE
        # =========================================

        st.markdown(
            """
<div class="section-heading">
📊 Allocation Rule Used
</div>
""",
            unsafe_allow_html=True
        )


        rule_data = []


        for category, details in investment_plan.items():

            rule_data.append(
                {
                    "Category": category,
                    "Allocation": f"{details['percentage']}%",
                    "Amount": f"₹{details['amount']:,.2f}"
                }
            )


        rule_df = pd.DataFrame(
            rule_data
        )


        st.dataframe(
            rule_df,
            use_container_width=True,
            hide_index=True
        )


        st.success(
            "The explanation makes the output traceable "
            "by showing the input factors and the rule "
            "used to produce the displayed allocation."
        )


    else:

        st.info(
            "XAI explanation will appear when there "
            "is a positive recorded savings amount."
        )


# =================================================
# FOOTER
# =================================================

st.markdown(
    """
<div style="
    text-align:center;
    margin-top:45px;
    padding:20px;
    color:#94a3b8;
    font-size:12px;
    border-top:1px solid #e5e7eb;
">
SmartFin · Personal Financial Planning &amp; Analysis System
<br>
Academic Prototype
</div>
""",
    unsafe_allow_html=True
)