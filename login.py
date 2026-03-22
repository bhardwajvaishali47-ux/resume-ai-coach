import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def call_register_api(email: str, password: str, full_name: str) -> dict:
    """Calls FastAPI /auth/register endpoint"""
    payload = {
        "email": email,
        "password": password,
        "full_name": full_name
    }
    response = requests.post(
        f"{API_BASE_URL}/auth/register",
        json=payload
    )
    return response


def call_login_api(email: str, password: str) -> dict:
    """Calls FastAPI /auth/login endpoint"""
    payload = {
        "email": email,
        "password": password
    }
    response = requests.post(
        f"{API_BASE_URL}/auth/login",
        json=payload
    )
    return response


def show_login_page():
    """
    Renders the complete login and registration page.
    Handles both login and registration in one page
    using tabs — clean and simple.
    """

    query_params = st.query_params
    google_code = query_params.get("code")

    if google_code:
        with st.spinner("Completing Google login..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/auth/google/callback",
                    params={"code": google_code}
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state["token"] = data["access_token"]
                    st.session_state["user_email"] = data["user_email"]
                    st.session_state["user_name"] = data["user_name"]
                    st.session_state["authenticated"] = True
                    st.query_params.clear()
                    st.rerun()
                else:
                    st.error("Google login failed. Please try again.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        return

    st.markdown("""
        <div style='text-align: center; padding: 2rem 0 1rem 0'>
            <h1>📄 AI Resume Coach</h1>
            <p style='color: grey; font-size: 1.1rem'>
                Your personal AI-powered career coach
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    tab1, tab2 = st.tabs(["Login", "Create Account"])

    with tab1:
        st.subheader("Welcome back")
        st.markdown("Login to access your AI Resume Coach.")

        with st.form("login_form"):
            email = st.text_input(
                "Email address",
                placeholder="you@example.com"
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Your password"
            )
            submit = st.form_submit_button(
                "Login",
                use_container_width=True,
                type="primary"
            )

        if submit:
            if not email or not password:
                st.warning("Please enter both email and password.")
            else:
                with st.spinner("Logging in..."):
                    response = call_login_api(email, password)

                if response.status_code == 200:
                    data = response.json()
                    st.session_state["token"] = data["access_token"]
                    st.session_state["user_email"] = data["user_email"]
                    st.session_state["user_name"] = data["user_name"]
                    st.session_state["authenticated"] = True
                    st.success(f"Welcome back {data['user_name']}!")
                    st.rerun()
                elif response.status_code == 401:
                    st.error("Invalid email or password. Please try again.")
                else:
                    st.error("Something went wrong. Please try again.")

    with tab2:
        st.subheader("Create your account")
        st.markdown("Free to use. No credit card required.")

        with st.form("register_form"):
            full_name = st.text_input(
                "Full name",
                placeholder="Vaishali Bhardwaj"
            )
            email_reg = st.text_input(
                "Email address",
                placeholder="you@example.com"
            )
            password_reg = st.text_input(
                "Password",
                type="password",
                placeholder="Choose a strong password"
            )
            password_confirm = st.text_input(
                "Confirm password",
                type="password",
                placeholder="Repeat your password"
            )
            submit_reg = st.form_submit_button(
                "Create Account",
                use_container_width=True,
                type="primary"
            )

        if submit_reg:
            if not full_name or not email_reg or not password_reg:
                st.warning("Please fill in all fields.")
            elif password_reg != password_confirm:
                st.error("Passwords do not match.")
            elif len(password_reg) < 8:
                st.error("Password must be at least 8 characters.")
            else:
                with st.spinner("Creating your account..."):
                    response = call_register_api(
                        email_reg,
                        password_reg,
                        full_name
                    )

                if response.status_code == 200:
                    data = response.json()
                    st.session_state["token"] = data["access_token"]
                    st.session_state["user_email"] = data["user_email"]
                    st.session_state["user_name"] = data["user_name"]
                    st.session_state["authenticated"] = True
                    st.success(
                        f"Account created successfully. "
                        f"Welcome {data['user_name']}!"
                    )
                    st.rerun()
                elif response.status_code == 400:
                    error_detail = response.json().get("detail", "")
                    st.error(error_detail)
                else:
                    st.error("Something went wrong. Please try again.")

    st.divider()
    st.subheader("Or continue with")

    if st.button("🔵 Login with Google", use_container_width=True):
        try:
            response = requests.get(f"{API_BASE_URL}/auth/google/url")
            google_url = response.json()["url"]
            st.markdown(
                f'<meta http-equiv="refresh" content="0;url={google_url}">',
                unsafe_allow_html=True
            )
            st.info("Redirecting to Google login...")
        except Exception as e:
            st.error(f"Could not connect to Google: {str(e)}")

    st.divider()
    st.markdown("""
        <div style='text-align: center; color: grey; font-size: 0.8rem'>
            Powered by Claude AI and LangChain
        </div>
    """, unsafe_allow_html=True)
