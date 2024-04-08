from fastapi import FastAPI
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
@app.get('/users')
async def users_all():
  return users_fake

@app.get('/users/{id}')
async def user_by_id(id: int):
  return search_user(id)

# Method POST
@app.post('/users')
async def user(user: User):
  if type(search_user(user.id)) == User:
    return { 'error': 'User already exists' }
  
  users_fake.append(user)
  return { 'message': 'User has been registered' }
  
# Method PUT
@app.put('/users/{id}')
async def user(id: int, user: User):
  found = False
  for index, saved_user in enumerate(users_fake):
    if saved_user.id == id:
      users_fake[index] = user
      found = True
  
  if not found:
    return { 'message': 'User has not been updated' }
  
  return user

# Method DELETE
@app.delete('/users/{id}')
async def user(id: int):
  found = False
  message = ''
  
  for index, saved_user in enumerate(users_fake):
    if saved_user.id == id:
      del users_fake[index]
      found = True
  
  message = 'User has been deleted' if found else 'User has not been deleted'
  return {'message': message}
    

def search_user(id: int):
  users = filter(lambda user: user.id == id, users_fake)
  try:
    return list(users)[0]
  except:
    return { 'error':'User not found' }
