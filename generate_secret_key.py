#!/usr/bin/env python3

import secrets
import string

def generate_secret_key(length=32):
    """Generate a secure random secret key"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    secret_key = ''.join(secrets.choice(alphabet) for _ in range(length))
    return secret_key

if __name__ == "__main__":
    print("Generated SECRET_KEY for your .env file:")
    print(f"SECRET_KEY={generate_secret_key()}")
    print()
    print("Copy this line to your Render environment variables!")
    print("Make sure to keep this secret and never commit it to GitHub.")
