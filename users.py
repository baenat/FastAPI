from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Iniciar servidor: uvicorn users:app --reload

# Entidad User
class User(BaseModel):
  id: int
  name: str
  surname: str
  age: int
  url: str

# Data fake BD
users_fake = [
  User(id=1, name='Julian', surname='Bae', age=20, url='https://github/baeant'),
  User(id=2, name='Stiven', surname='Jules', age=20, url='https://github/jule'),
]

# Method GET
@app.get('/users', status_code=200)
async def users_all():
  return users_fake

@app.get('/users/{id}', status_code=200)
async def user_by_id(id: int):
  user = search_user(id)
  if not type(user) == User:
    raise HTTPException(status_code=404, detail=user)

  return { 'detail': user }

# Method POST
@app.post('/users', status_code=201)
async def user(user: User):
  if type(search_user(user.id)) == User:
    raise HTTPException(status_code=409, detail='User already exists')
  
  users_fake.append(user)
  return { 'detail': 'User has been registered' }
  
# Method PUT
@app.put('/users/{id}', status_code=200)
async def user(id: int, user: User):
  found = False
  for index, saved_user in enumerate(users_fake):
    if saved_user.id == id:
      users_fake[index] = user
      found = True
  
  if not found:
    raise HTTPException(status_code=404, detail='User already exists')
    
  return user

# Method DELETE
@app.delete('/users/{id}', status_code=200)
async def user(id: int):
  found = False
  
  for index, saved_user in enumerate(users_fake):
    if saved_user.id == id:
      del users_fake[index]
      found = True
  
  if not found:
    raise HTTPException(status_code=404, detail='User has not been deleted')
  
  return {'detail': 'User has been deleted'}
    

def search_user(id: int):
  users = filter(lambda user: user.id == id, users_fake)
  try:
    return list(users)[0]
  except:
    return 'User not found'
