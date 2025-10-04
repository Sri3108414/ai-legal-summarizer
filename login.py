import streamlit as st
import sqlite3
import hashlib

# ---------------- Database Setup ----------------
conn = sqlite3.connect("users.db")
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    password TEXT
)
''')
conn.commit()

# ---------------- Helper Functions ----------------
def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hash(password, hashed):
    return make_hash(password) == hashed

def add_user(username, password):
    c.execute("INSERT INTO users(username, password) VALUES (?,?)",
              (username, make_hash(password)))
    conn.commit()

def login_user(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, make_hash(password)))
    return c.fetchone()

# ---------------- Streamlit Pages ----------------
def signup_page():
    st.subheader("Create New Account")
    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")

    if st.button("Signup"):
        try:
            add_user(new_user, new_pass)
            st.success("Account created successfully!")
            st.info("Go to Login page to continue.")
        except:
            st.error("Username already exists. Try another.")

def login_page():
    st.subheader("Login to your account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        result = login_user(username, password)
        if result:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success(f"Welcome {username}!")
        else:
            st.error("Invalid Username or Password")

def dashboard_page():
    st.subheader("Main Dashboard")
    st.write(f"Hello, **{st.session_state['username']}** 👋")
    
    uploaded_file = st.file_uploader("Upload a file", type=["pdf", "docx", "txt"])
    if uploaded_file:
        st.success(f"File `{uploaded_file.name}` uploaded successfully!")
        # (Optional) Save file
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())

# ---------------- Main App ----------------
def main():
    st.title("Secure Login System")

    menu = ["Login", "Signup"]
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        dashboard_page()
    else:
        choice = st.sidebar.selectbox("Menu", menu)
        if choice == "Login":
            login_page()
        elif choice == "Signup":
            signup_page()

if __name__ == "__main__":
    main()
