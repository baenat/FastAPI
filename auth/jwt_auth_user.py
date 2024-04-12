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

bcrypt = CryptContext(schemes=['bcrypt'])

class User(BaseModel):
  username: str
  full_name: str
  email: str
  disabled: bool

class UserInDB(User):
  password: str

class Token(BaseModel):
  access_token: str
  token_type: str

class TokenData(BaseModel):
  username: str | None = None

fake_users_db = {
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

def verify_password(plain_password, hashed_password):
  
    return bcrypt.verify(plain_password, hashed_password)


def get_user_db(db, username: str):
  
  if username in db:
    return UserInDB(**fake_users_db[username])
  

def get_user(db, username: str):
  
  if username in db:
    return User(**fake_users_db[username])


def authenticate_user(fake_db, username: str, password: str):
  
    user = get_user_db(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
      
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
  
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta        
        
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        
    to_encode = {
      'sub': data.username,
      'exp': expire
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt
 

def get_current_user(token: str = Depends(oauth2)):
  
  credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Could not validate credentials',
    headers={'www-authenticate': 'Bearer'}
  )
  
  try:
    
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get('sub')
    
    if username is None:
      raise credentials_exception
    
  except JWTError as e:
    # print(e.args[0], 'ERROR')
    raise credentials_exception
  
  user = get_user(fake_users_db, username=username)
  if user is None:
      raise credentials_exception
  
  return user


async def get_current_active_user(user: User = Depends(get_current_user)):
  
  if user.disabled:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail='Inactive user',
      headers={'www-authenticate': 'Bearer'}
    )
    
  return user


@app.post('/login')
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
  
  user = authenticate_user(fake_users_db, form_data.username, form_data.password)
  if not user:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
  access_token_expires = timedelta(minutes=ACCESS_TOKEN_DURATION)
  access_token = create_access_token(
    data=form_data, expires_delta=access_token_expires
  )
  
  return Token(access_token=access_token, token_type="bearer")


@app.get('/users/auth')
async def user_auth(current_user: User = Depends(get_current_active_user)):
  return current_user


@app.get("/users/items")
async def read_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]