import re
import sqlite3
from pathlib import Path

import streamlit as st
from pwdlib import PasswordHash
import pyotp


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
            SELECT id, email, password_hash, totp_secret
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
        "totp_secret": user["totp_secret"],
    }


def save_totp_secret(email, secret):
    """Persist an authenticator-app secret after the user verifies a code."""
    with get_connection() as connection:
        connection.execute(
            "UPDATE users SET totp_secret = ? WHERE email = ?",
            (secret, email),
        )


def render_auth():
    """Display signup and login forms."""
    initialize_auth_db()
    if "user" not in st.session_state:
        st.session_state["user"] = None
    if st.session_state.get("demo_mode", False) or st.session_state.get("guest_mode", False):
        return True
    if st.session_state["user"] is not None:
        return True

    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:0.5rem;">
          <svg width="48" height="48" viewBox="0 0 64 64" role="img"
               aria-label="SecureBank logo" xmlns="http://www.w3.org/2000/svg">
            <rect x="5" y="5" width="54" height="54" rx="14" fill="#123B5D"/>
            <path d="M12 24 L32 13 L52 24 Z" fill="#FFFFFF"/>
            <path d="M15 26 H49 V30 H15 Z" fill="#5CC8B2"/>
            <rect x="17" y="32" width="5" height="13" rx="1" fill="#FFFFFF"/>
            <rect x="29.5" y="32" width="5" height="13" rx="1" fill="#FFFFFF"/>
            <rect x="42" y="32" width="5" height="13" rx="1" fill="#FFFFFF"/>
            <path d="M12 47 H52 V51 H12 Z" fill="#5CC8B2"/>
          </svg>
          <span style="font-size:2rem;font-weight:700;">SecureBank Account</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("Sign in to access your financial analytics dashboard.")

    with st.expander("How your CSV data is processed", expanded=True):
        st.markdown(
            """
            - **Parsing and analysis:** CSV files are uploaded to the Streamlit app server, then parsed and analyzed there (not in your browser).
            - **Storage:** Uploaded CSVs are processed in memory and are not automatically saved to the app's MySQL database. Avoid uploading sensitive real customer data.
            - **Review the code:** [GitHub repository](https://github.com/Sheran2004/securebank-financial-analytics)
            """
        )

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
            login_otp = st.text_input(
                "Authenticator code (if 2FA is enabled)",
                max_chars=6,
                key="login_otp",
                help="Enter the 6-digit code from your authenticator app if you have already enabled 2FA.",
            )
            login_submitted = st.form_submit_button(
                "Login",
                type="primary",
                width="stretch",
            )
        if login_submitted:
            user = authenticate(login_email, login_password)
            if user:
                if user["totp_secret"]:
                    if pyotp.TOTP(user["totp_secret"]).verify(
                        login_otp.strip(), valid_window=1
                    ):
                        st.session_state["user"] = user
                        st.rerun()
                    else:
                        st.error("Enter a valid 6-digit authenticator code to finish signing in.")
                else:
                    st.session_state["pending_2fa_email"] = user["email"]
                    st.session_state["pending_2fa_secret"] = pyotp.random_base32()
                    st.info("Secure your account by setting up authenticator-app two-factor authentication below.")
            else:
                st.error("Invalid email or password.")

        st.markdown("[Terms of Service](https://github.com/Sheran2004/securebank-financial-analytics/blob/main/terms_of_service.md) · [GitHub repository](https://github.com/Sheran2004/securebank-financial-analytics)")

        # Enroll accounts that do not yet have 2FA, then require a code on later logins.
        pending_email = st.session_state.get("pending_2fa_email")
        pending_secret = st.session_state.get("pending_2fa_secret")
        if pending_email and pending_secret:
            st.markdown("#### Set up two-factor authentication (2FA)")
            st.write("In your authenticator app (for example, Google Authenticator or Microsoft Authenticator), add an account using this secret:")
            st.code(pending_secret, language=None)
            st.caption("Keep this secret private. Enter the current 6-digit code from the app to confirm setup.")
            with st.form("confirm_2fa_setup_form"):
                setup_code = st.text_input("6-digit verification code", max_chars=6, key="setup_2fa_code")
                setup_submitted = st.form_submit_button("Verify and enable 2FA", type="primary", width="stretch")
            if setup_submitted:
                if pyotp.TOTP(pending_secret).verify(setup_code.strip(), valid_window=1):
                    save_totp_secret(pending_email, pending_secret)
                    st.session_state["user"] = {
                        "email": pending_email,
                        "totp_secret": pending_secret,
                    }
                    del st.session_state["pending_2fa_email"]
                    del st.session_state["pending_2fa_secret"]
                    st.success("Two-factor authentication enabled.")
                    st.rerun()
                else:
                    st.error("That code is not valid. Check your authenticator app and try again.")

        st.caption("Want to try the analytics without creating an account?")
        if st.button(
            "🧪 Continue as Guest",
            key="continue_as_guest",
            width="stretch",
        ):
            st.session_state["guest_mode"] = True
            st.rerun()

        if st.button(
            "👁️ View Live Demo",
            key="view_live_demo",
            width="stretch",
        ):
            st.session_state["demo_mode"] = True
            st.rerun()

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
    """Display account details and logout button at the top."""
    user = st.session_state.get("user")
    if user:
        left, right = st.columns([5, 1])
        with left:
            st.caption(f"👤 Logged in as: {user['email']}")
        with right:
            if st.button(
                "🚪 Logout",
                key="top_logout_button",
                type="secondary",
                width="stretch",
            ):
                keys_to_clear = [
                    key
                    for key in st.session_state.keys()
                    if key != "user"
                ]
                for key in keys_to_clear:
                    del st.session_state[key]
                st.session_state["user"] = None
                st.rerun()