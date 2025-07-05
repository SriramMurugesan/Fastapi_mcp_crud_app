from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
import uvicorn
from fastapi_mcp import AuthConfig, FastApiMCP
from . import models, schemas, crud, auth
from .database import engine, get_db
from .config import settings

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FastAPI CRUD App with JWT Authentication",
    description="A simple CRUD application with JWT authentication",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the FastAPI CRUD App with JWT Authentication",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Token endpoint
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# User endpoints
@app.post("/users/", response_model=schemas.User,operation_id="create_user")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/me/", response_model=schemas.User,operation_id="read_users_me")
async def read_users_me(current_user: schemas.User = Depends(auth.get_current_active_user)):
    return current_user

# Item endpoints
@app.post("/items/", response_model=schemas.Item,operation_id="create_item")
def create_item(
    item: schemas.ItemCreate,
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=current_user.id)

@app.get("/items/", response_model=list[schemas.Item],operation_id="read_items")
def read_items(
    skip: int = 0, 
    limit: int = 100, 
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

@app.get("/items/{item_id}", response_model=schemas.Item,operation_id="read_item_id")
def read_item(
    item_id: int,
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    db_item = crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.put("/items/{item_id}", response_model=schemas.Item,operation_id="update_item")
def update_item(
    item_id: int,
    item: schemas.ItemCreate,
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    db_item = crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    if db_item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud.update_item(db=db, item_id=item_id, item=item)

@app.delete("/items/{item_id}",operation_id="delete_item")
def delete_item(
    item_id: int,
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    db_item = crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    if db_item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    crud.delete_item(db=db, item_id=item_id)
    return {"ok": True}

mcp = FastApiMCP(app,include_operations=[
    "create_user",
    "read_users_me",
    "create_item",
    "read_items",
    "read_item_id",
    "update_item",
    "delete_item"
],
auth_config=AuthConfig(
        dependencies=[Depends(auth.get_current_active_user)],
    )
)

mcp.mount()
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


