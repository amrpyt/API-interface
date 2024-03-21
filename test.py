import sqlite3
from cryptography.fernet import Fernet
import streamlit as st

# Create a new database or connect to an existing one
conn = sqlite3.connect('credentials.db')
conn.isolation_level = None  # Set isolation level to EXCLUSIVE
c = conn.cursor()

# Create a table to store the credentials if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS credentials (name TEXT PRIMARY KEY, value BLOB)''')

# Read the encryption key from a file
try:
    with open('encryption_key.txt', 'rb') as key_file:
        key = key_file.read()
except FileNotFoundError:
    st.error("Encryption key file not found. Please create 'encryption_key.txt' file.")
    st.stop()

fernet = Fernet(key)

# Streamlit app
def main():
    st.title("Credential Manager")
    menu = ["Store Credential", "Retrieve/Search Credential", "Delete Credential"]
    choice = st.sidebar.selectbox("Select an option", menu)

    if choice == "Store Credential":
        st.subheader("Store Credential")
        name = st.text_input("Enter the credential name:")
        value = st.text_input("Enter the credential value:", type="password")
        if st.button("Store"):
            if name and value:
                encrypted_value = fernet.encrypt(value.encode())
                c.execute("INSERT OR REPLACE INTO credentials (name, value) VALUES (?, ?)", (name, encrypted_value))
                conn.commit()
                st.success(f"Credential '{name}' stored successfully.")
            else:
                st.warning("Please enter both name and value.")

    elif choice == "Retrieve/Search Credential":
        st.subheader("Retrieve/Search Credential")
        name = st.text_input("Enter the credential name or search term:")
        if st.button("Search"):
            if name:
                c.execute("SELECT name, value FROM credentials WHERE name LIKE ?", (f"%{name}%",))
                results = c.fetchall()
                if results:
                    st.write("Search results:")
                    for result in results:
                        credential_name = result[0]
                        encrypted_value = result[1]
                        decrypted_value = fernet.decrypt(encrypted_value).decode()
                        st.write(f"{credential_name}: {decrypted_value}")
                else:
                    st.warning("No matching credentials found.")
            else:
                st.warning("Please enter a credential name or search term.")
        else:
            if name:
                c.execute("SELECT value FROM credentials WHERE name = ?", (name,))
                result = c.fetchone()
                if result:
                    decrypted_value = fernet.decrypt(result[0]).decode()
                    st.text(f"Value for '{name}': {decrypted_value}")
                else:
                    st.warning(f"Credential '{name}' not found.")
            else:
                st.warning("Please enter a credential name.")

    elif choice == "Delete Credential":
        st.subheader("Delete Credential")
        name = st.text_input("Enter the credential name:")
        if st.button("Delete"):
            if name:
                c.execute("DELETE FROM credentials WHERE name = ?", (name,))
                conn.commit()
                if c.rowcount > 0:
                    st.success(f"Credential '{name}' deleted successfully.")
                else:
                    st.warning(f"Credential '{name}' not found.")
            else:
                st.warning("Please enter a credential name.")

if __name__ == "__main__":
    main()

# Close the database connection
conn.close()