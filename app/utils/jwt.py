import os
import jwt
import datetime
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')

if not SECRET_KEY:
    raise ValueError("SECRET_KEY not set in environment")

def encode_auth_token(fin_kod, role, approved):
    try:
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

        payload = {
            'fin_kod': fin_kod,
            'role': role,
            'approved': approved,
            'exp': expiration_time
        }

        auth_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return auth_token

    except Exception as e:
        return str(e)
    

def decode_auth_token(auth_token):
    try:
        payload = jwt.decode(auth_token, SECRET_KEY, algorithms=['HS256'], options={"require": ["exp"]})

        return {
            'fin_kod': payload['fin_kod'],
            'role': payload['role'],
            'approved': payload['approved'],
            'exp': payload['exp']
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error decoding token")

def encode_otp_token(fin_kod, otp):
    try:
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=3)

        payload = {
            'fin_kod': fin_kod,
            'otp': otp,
            'exp': expiration_time
        }

        auth_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return auth_token

    except Exception as e:
        return str(e)
    

def decode_otp_token(otp_token):
    try:
        payload = jwt.decode(otp_token, SECRET_KEY, algorithms=['HS256'], options={"require": ["exp"]})

        return {
            'fin_kod': payload['fin_kod'],
            'otp': payload['otp'],
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error decoding token")