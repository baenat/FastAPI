from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

app = FastAPI()

oauth2 = OAuth2PasswordBearer(tokenUrl='login')

#openssl rand -hex 32
SECRET_KEY = "dd9ee7644d3e5cd84d4b1b1cab2eeca96204e7c70365b947a3820bb78dd2716e"
ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 1

crypt = CryptContext(schemes=['bcrypt'])

class User(BaseModel):
  username: str
  full_name: str
  email: str
  disabled: bool
  
class UserDB(User):
  password: str
  
users_db = {
  "julianbaena": {
    "username": "julianbaena",
    "full_name": "Julian Baena",
    "email": "julian@gmail.com",
    "disabled": False,
    "password": "$2a$12$1N49FkJGVytfJuvDZtPTBeQ8Jx.s0QEkpvZyqTlwp.DwDTvZq1oKy"
  },
  "johndoe": {
    "username": "johndoe",
    "full_name": "John Doe",
    "email": "johndoe@example.com",
    "disabled": True,
    "password": "$2a$12$iqxsT2xdmoSrj82BkIj3hOHpW.0R7duWMTQakIIONLBPojN46LB7u"
  }
}

def search_user_db(username: str):
  
  if username in users_db:
    return UserDB(**users_db[username])
  

def search_user(username: str):
  
  if username in users_db:
    return User(**users_db[username])


def auth_user(token: str = Depends(oauth2)):
  
  exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Could not validate credentials',
    headers={'www-authenticate': 'Bearer'}
  )
  
  try:
    
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get('sub')
    
    if username is None:
      raise exception
    
  except JWTError as e:
    print(e.args[0], 'ERROR')
    raise exception
  
  return search_user(username)


async def current_user(user: User = Depends(auth_user)):
  
  if user.disabled:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail='Inactive user',
      headers={'www-authenticate': 'Bearer'}
    )
    
  return user


@app.post('/login')
async def login(form: OAuth2PasswordRequestForm = Depends()):
  
  user_db = users_db.get(form.username)
  if not user_db:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail='User does not correct'
    )
  
  user = search_user_db(form.username)
  if not crypt.verify(form.password, user.password):
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail='Password is not correct'
    )
    
  expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_DURATION)
  
  ACCESS_TOKEN = {
    'sub': form.username,
    'exp': expire
  }
  token_user = jwt.encode(
    ACCESS_TOKEN,
    SECRET_KEY,
    ALGORITHM
  )
  
  return { 'access_token': {token_user}, 'token_type': 'bearer' }


@app.get('/users/auth')
async def user_auth(user: User = Depends(current_user)):
  return user

