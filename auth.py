import sqlite3
import hashlib
import os


DB_NAME = "users.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# -------------------------------------------------
# INITIALIZE DATABASE
# -------------------------------------------------

def init_db():

    conn = get_connection()

    # Users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    # Financial profile table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS financial_profiles (
            user_id INTEGER PRIMARY KEY,
            monthly_salary REAL DEFAULT 0,
            existing_savings REAL DEFAULT 0,
            existing_debt REAL DEFAULT 0,
            financial_goal TEXT DEFAULT 'Wealth Creation',
            risk_appetite TEXT DEFAULT 'Low',

            FOREIGN KEY (user_id)
            REFERENCES users(id)
            ON DELETE CASCADE
        )
    """)

    # Transactions table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL,

            FOREIGN KEY (user_id)
            REFERENCES users(id)
            ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# -------------------------------------------------
# PASSWORD SECURITY
# -------------------------------------------------

def hash_password(password):

    salt = os.urandom(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        100000
    )

    return salt.hex() + ":" + password_hash.hex()


def verify_password(password, stored_password):

    try:

        salt_hex, password_hash_hex = (
            stored_password.split(":")
        )

        salt = bytes.fromhex(salt_hex)

        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt,
            100000
        )

        return (
            password_hash.hex()
            == password_hash_hex
        )

    except Exception:

        return False


# -------------------------------------------------
# REGISTER
# -------------------------------------------------

def register_user(name, email, password):

    conn = get_connection()

    try:

        password_hash = hash_password(password)

        cursor = conn.execute(
            """
            INSERT INTO users
            (name, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (
                name,
                email,
                password_hash
            )
        )

        user_id = cursor.lastrowid

        # Create empty financial profile
        conn.execute(
            """
            INSERT INTO financial_profiles
            (user_id)
            VALUES (?)
            """,
            (user_id,)
        )

        conn.commit()

        return True, "Registration successful!"

    except sqlite3.IntegrityError:

        return False, "Email already registered."

    finally:

        conn.close()


# -------------------------------------------------
# LOGIN
# -------------------------------------------------

def login_user(email, password):

    conn = get_connection()

    cursor = conn.execute(
        """
        SELECT
            id,
            name,
            email,
            password_hash
        FROM users
        WHERE email = ?
        """,
        (email,)
    )

    user = cursor.fetchone()

    conn.close()

    if user and verify_password(
        password,
        user[3]
    ):

        return {
            "id": user[0],
            "name": user[1],
            "email": user[2]
        }

    return None


# -------------------------------------------------
# GET FINANCIAL PROFILE
# -------------------------------------------------

def get_financial_profile(user_id):

    conn = get_connection()

    cursor = conn.execute(
        """
        SELECT
            monthly_salary,
            existing_savings,
            existing_debt,
            financial_goal,
            risk_appetite
        FROM financial_profiles
        WHERE user_id = ?
        """,
        (user_id,)
    )

    profile = cursor.fetchone()

    conn.close()

    if profile:

        return {
            "monthly_salary": profile[0],
            "existing_savings": profile[1],
            "existing_debt": profile[2],
            "financial_goal": profile[3],
            "risk_appetite": profile[4]
        }

    return {
        "monthly_salary": 0,
        "existing_savings": 0,
        "existing_debt": 0,
        "financial_goal": "Wealth Creation",
        "risk_appetite": "Low"
    }


# -------------------------------------------------
# SAVE FINANCIAL PROFILE
# -------------------------------------------------

def save_financial_profile(
    user_id,
    monthly_salary,
    existing_savings,
    existing_debt,
    financial_goal,
    risk_appetite
):

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO financial_profiles
        (
            user_id,
            monthly_salary,
            existing_savings,
            existing_debt,
            financial_goal,
            risk_appetite
        )
        VALUES (?, ?, ?, ?, ?, ?)

        ON CONFLICT(user_id)
        DO UPDATE SET
            monthly_salary =
                excluded.monthly_salary,

            existing_savings =
                excluded.existing_savings,

            existing_debt =
                excluded.existing_debt,

            financial_goal =
                excluded.financial_goal,

            risk_appetite =
                excluded.risk_appetite
        """,
        (
            user_id,
            monthly_salary,
            existing_savings,
            existing_debt,
            financial_goal,
            risk_appetite
        )
    )

    conn.commit()
    conn.close()