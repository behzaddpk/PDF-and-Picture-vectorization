import secrets
from datetime import datetime, timedelta
from typing import Dict, Tuple

otp_storage: Dict[str, Tuple[str, datetime]] = {}

def generate_otp(length: int = 4) -> str:
    otp = ''.join([str(secrets.randbelow(10)) for _ in range(length)])
    print(f"Generated OTP: {otp}")
    return otp

def store_otp(email: str, otp: str, duration: int = 10):
    expiry = datetime.now() + timedelta(minutes=duration)
    otp_storage[email] = (otp, expiry)
    print(f"Stored OTP for {email} with expiry {expiry}.")

def verify_otp(email: str, otp: str) -> bool:
    if email in otp_storage:
        stored_otp, expiry = otp_storage[email]
        if datetime.now() < expiry and stored_otp == otp:
            print(f"OTP verification for {email} succeeded.")
            return True
        else:
            print(f"OTP verification for {email} failed.")
    else:
        print(f"OTP verification for {email} failed.")
    return False

def remove_otp(email: str):
    if email in otp_storage:
        del otp_storage[email]
        print(f"Removed OTP for {email}.")
    else:
        print(f"Attempted to remove OTP for {email}, but none was found.")
