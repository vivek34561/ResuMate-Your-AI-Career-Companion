import os
import streamlit as st
from database import (
    init_mysql_db,
    authenticate_user,
    create_user,
    get_user_settings,
    get_user_by_username,
)


def login_view() -> bool:
    """
    Simple username/password login view (Google OAuth removed).
    """
    st.header("🔐 Welcome to ResuMate")
    st.markdown("### Sign in to continue")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        with st.form("login_form"):
            u = st.text_input("Username", key="login_user")
            p = st.text_input("Password", type="password", key="login_pass")
            submit = st.form_submit_button("Login", type="primary")

        if submit:
            if not u or not p:
                st.error("Please enter both username and password.")
            else:
                user = authenticate_user(u, p)
                if user:
                    st.session_state.user = user
                    st.session_state.user_settings = get_user_settings(user['id']) or {}
                    st.success(f"Welcome back, {user['username']}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    with tab2:
        with st.form("register_form"):
            new_u = st.text_input("Choose Username", key="reg_user")
            new_p = st.text_input("Choose Password", type="password", key="reg_pass")
            new_p2 = st.text_input("Confirm Password", type="password", key="reg_pass2")
            reg_submit = st.form_submit_button("Register")

        if reg_submit:
            if not new_u or not new_p:
                st.error("Please fill in all fields.")
            elif new_p != new_p2:
                st.error("Passwords do not match.")
            else:
                existing = get_user_by_username(new_u)
                if existing:
                    st.error("Username already taken.")
                else:
                    uid = create_user(new_u, new_p)
                    if uid:
                        st.success("Account created! Please log in.")
                    else:
                        st.error("Failed to create account.")

    return bool(st.session_state.user)


def ensure_logged_in() -> bool:
    try:
        init_mysql_db()
    except Exception as e:
        st.warning(f"Database init warning: {e}")
    if not st.session_state.user:
        return login_view()
    return True
