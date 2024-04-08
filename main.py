from fastapi import FastAPI
from routers import users

app = FastAPI()

# Path
path = '/api/v1/'

# Routers
app.include_router(users.router, prefix=path + 'users')
# app.include_router(products.router, prefix=path + 'products')

@app.get('/') 
def read_root():
  return { 
    'paths': [
      path+'users',
    ]
  }