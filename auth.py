import os
import re
import sqlite3
from pathlib import Path

import streamlit as st
from pwdlib import PasswordHash


BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "data"
DB_DIR.mkdir(exist_ok=True)

AUTH_DB = DB_DIR / "users.db"

password_hasher = PasswordHash.recommended()


def get_connection():
    connection = sqlite3.connect(AUTH_DB)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_auth_db():
    """Create the local user accounts table."""

    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


def validate_email(email):
    email = email.strip().lower()

    if len(email) > 254:
        return None

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return None

    return email


def signup(email, password):
    """Register a user with a securely hashed password."""

    email = validate_email(email)

    if not email:
        return False, "Please enter a valid email address."

    if len(password) < 12:
        return False, "Password must contain at least 12 characters."

    if len(password) > 1024:
        return False, "Password is too long."

    password_hash = password_hasher.hash(password)

    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO users (email, password_hash)
                VALUES (?, ?)
                """,
                (email, password_hash),
            )

        return True, "Account created successfully. Please log in."

    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."


def authenticate(email, password):
    """Verify the email and password."""

    email = validate_email(email)

    if not email or not password or len(password) > 1024:
        return None

    with get_connection() as connection:
        user = connection.execute(
            """
            SELECT id, email, password_hash
            FROM users
            WHERE email = ?
            """,
            (email,),
        ).fetchone()

    if user is None:
        return None

    try:
        password_matches = password_hasher.verify(
            password,
            user["password_hash"],
        )
    except Exception:
        return None

    if not password_matches:
        return None

    return {
        "id": user["id"],
        "email": user["email"],
    }


def render_auth():
    """Display signup and login forms."""

    initialize_auth_db()

    if "user" not in st.session_state:
        st.session_state["user"] = None

    if st.session_state["user"] is not None:
        return True

    st.title("🔐 SecureBank Account")
    st.write("Sign in to access your financial analytics dashboard.")

    login_tab, signup_tab = st.tabs(["Login", "Create Account"])

    with login_tab:
        with st.form("login_form"):
            login_email = st.text_input(
                "Email address",
                key="login_email",
            )
            login_password = st.text_input(
                "Password",
                type="password",
                key="login_password",
            )
            login_submitted = st.form_submit_button(
                "Login",
                type="primary",
                width="stretch",
            )

        if login_submitted:
            user = authenticate(login_email, login_password)

            if user:
                st.session_state["user"] = user
                st.rerun()
            else:
                st.error("Invalid email or password.")

    with signup_tab:
        with st.form("signup_form"):
            signup_email = st.text_input(
                "Email address",
                key="signup_email",
            )
            signup_password = st.text_input(
                "Password (minimum 12 characters)",
                type="password",
                key="signup_password",
            )
            confirm_password = st.text_input(
                "Confirm password",
                type="password",
                key="confirm_password",
            )
            signup_submitted = st.form_submit_button(
                "Create Account",
                width="stretch",
            )

        if signup_submitted:
            if signup_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                success, message = signup(
                    signup_email,
                    signup_password,
                )

                if success:
                    st.success(message)
                else:
                    st.error(message)

    return False


def render_logout():
    """Clear user session data and log out safely."""

    user = st.session_state.get("user")

    if user:
        st.sidebar.caption(f"Logged in as: {user['email']}")

        if st.sidebar.button("Logout", width="stretch"):
            # Clear application session state.
            # Keep Streamlit's internal widget keys intact.
            keys_to_clear = [
                key
                for key in st.session_state.keys()
                if key not in {"user"}
            ]

            for key in keys_to_clear:
                del st.session_state[key]

            # Remove the authenticated user last.
            st.session_state["user"] = None

            st.rerun()