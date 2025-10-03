import streamlit as st
import sqlite3
import hashlib

# ----------------- DB Functions -----------------
def create_usertable():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users(username TEXT UNIQUE, password TEXT)')
    conn.commit()
    conn.close()

def add_userdata(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT INTO users(username,password) VALUES (?,?)', (username, password))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    data = c.fetchone()
    conn.close()
    return data

# ----------------- Hashing -----------------
def make_hashes(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# ----------------- Dashboard Page -----------------
def dashboard_page():
    st.title("📂 Legal Document Summarization Dashboard")

    st.sidebar.subheader("📤 Upload Documents")
    uploaded_file = st.sidebar.file_uploader(
        "Choose a legal document", 
        type=["pdf", "docx", "txt"]
    )

    if uploaded_file:
        st.success(f"✅ File '{uploaded_file.name}' uploaded successfully!")

    st.sidebar.subheader("⚙️ Controls")
    if st.sidebar.button("Clear All Documents"):
        st.info("🗑️ All documents cleared.")

    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["user"] = None
        st.success("🔓 Logged out successfully!")

# ----------------- Streamlit App -----------------
def main():
    st.set_page_config(page_title="Login & Signup with Dashboard", page_icon="🔑", layout="centered")
    create_usertable()

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["user"] = None

    if st.session_state["logged_in"]:
        dashboard_page()
    else:
        menu = ["Login", "Signup"]
        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "Signup":
            st.subheader("Create New Account")
            new_user = st.text_input("Username")
            new_pass = st.text_input("Password", type="password")
            if st.button("Signup"):
                if new_user and new_pass:
                    try:
                        add_userdata(new_user, make_hashes(new_pass))
                        st.success("✅ Account created successfully!")
                        st.info("Go to Login menu to login")
                    except:
                        st.error("⚠️ Username already exists")
                else:
                    st.warning("⚠️ Please enter both username and password")

        elif choice == "Login":
            st.subheader("Login to Your Account")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            if st.button("Login"):
                if username and password:
                    hashed_pass = make_hashes(password)
                    result = login_user(username, hashed_pass)
                    if result:
                        st.session_state["logged_in"] = True
                        st.session_state["user"] = username
                        st.success(f"Welcome back, {username}! 🎉")
                        st.experimental_rerun()
                    else:
                        st.error("❌ Invalid Username or Password")
                else:
                    st.warning("⚠️ Please fill in both fields")

if __name__ == '__main__':
    main()
