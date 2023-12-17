from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models
from .database import engine, SessionLocal
from .schemas import Blog, User, ShowUser, ShowBlog, TokenData, Token
from passlib.context import CryptContext
from typing import List, Annotated
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

models.Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:

        yield db
    finally: 
        db.close()


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == token_data.username).first()
    
    # user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


@app.post("/blog", status_code=201, tags=["Blogs"], response_model=ShowBlog)
def create(req : Blog, db: Session = Depends(get_db),current_user: User= Depends(get_current_user )):
    new_blog = models.Blog(title=req.title, body=req.body, user_id = req.userId)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


@app.get("/blog", tags=["Blogs"], response_model=List[ShowBlog])
def all(db: Session = Depends(get_db),current_user: User= Depends(get_current_user )):
    blogs = db.query(models.Blog).all()
    return blogs

@app.get("/blog/{id}", tags=["Blogs"], response_model=ShowBlog)
def single(id,db: Session = Depends(get_db),current_user: User= Depends(get_current_user )):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(404, detail=f"Blog with id={id} not found")
    
    return blog

@app.delete("/blog/{id}", status_code=204, tags=["Blogs"])
def delete(id,db: Session = Depends(get_db),current_user: User= Depends(get_current_user )):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    print(blog)
    if not blog:
        raise HTTPException(404, detail=f"Blog with id={id} not found")
    
    db.query(models.Blog).filter(models.Blog.id == id).delete(synchronize_session=False)
    db.commit()
    return 

@app.patch("/blog/{id}", status_code=200, tags=["Blogs"])
def update(id,req: Blog,db: Session = Depends(get_db),current_user: User= Depends(get_current_user )):
    blog = db.query(models.Blog).filter(models.Blog.id == id)

    if not blog.first():
        raise HTTPException(404, detail=f"Blog with id={id} not found")
    
    db.query(models.Blog).filter(models.Blog.id == id).update(req.dict(exclude_unset=True), synchronize_session=False)
    
    db.commit()
    # db.refresh(blog)
    return blog

@app.post("/user", status_code=201, response_model=ShowUser, tags=["Users"])
def create(req: User,db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == req.username).first()

    print(user)
    if user:
        raise HTTPException(400, detail="Username already used")
    hashed_password = pwd_context.hash(req.password)
    new_user = models.User(username=req.username, password = hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/user/{id}", response_model=ShowUser, tags=["Users"])
def showUser(id,db: Session = Depends(get_db),current_user: User= Depends(get_current_user )):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(404, detail="User not found")

    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/login", tags=["Authentication"])
def login(req: User, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == req.username).first()
    if not user:
        raise HTTPException(400, detail="Invalid credentials")
    
    if not pwd_context.verify(req.password, user.password):
        raise HTTPException(400, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": user.username})
    return {"token": access_token}
    

 
