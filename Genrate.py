from cryptography.fernet import Fernet

# Generate a new encryption key
key = Fernet.generate_key()
print(key.decode())