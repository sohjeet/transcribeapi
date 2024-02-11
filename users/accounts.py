import time
import secrets
import string

def generate_username(email):
    max_length = 20  
    username = email.split('@')[0] # Extract the portion before the '@' symbol as the username
    username = username[:max_length]  # Trim the username to the specified length
    unique_id = str(int(time.time()))[-4:]  
    username = f"{username}_{unique_id}"
    return username

def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password