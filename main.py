

from collections import namedtuple
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Request,status, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from hashing import Hash
from jwttoken import create_access_token
from oauth import get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
# const port = Process.env.PORT || 3000 ;
origins = [
    "http://localhost:3000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from pymongo import MongoClient
mongodb_uri = 'mongodb+srv://dbUser:chula123@cluster0.nds32.mongodb.net/myFirstDatabase?ssl=true&ssl_cert_reqs=CERT_NONE'
port = 8000
client = MongoClient(mongodb_uri, port)
db = client["User"]

database = client.User_bloodsugar
collection = database.bloodsugar

class User(BaseModel):
    username: str
    real_name: Optional[str] = None
    surname: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    weight: Optional[int] = None
    height: Optional[int] = None
    tel: Optional[str] = None
    email: Optional[str] = None
    password: str
    confirmpassword: Optional[str] = None

class BloodSugar(BaseModel):
    username: str
    mealtype: str
    time: str
    bloodsugar: int

class Login(BaseModel):
	username: str
	password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    username: Optional[str] = None

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/x", response_model=User)
def read_root(current_user:User = Depends(get_current_user)):
    # print(TokenData(username=username))
    response = db["users"].find_one({'username': current_user.username})
    return response

@app.post('/register')
def create_user(request:User):
	hashed_pass = Hash.bcrypt(request.password)
	user_object = dict(request)
	user_object["password"] = hashed_pass
	user_id = db["users"].insert(user_object)
	# print(user)
	return {"res":"created"}

@app.post('/uploadbloodsugar', response_model=BloodSugar)
async def post_bloodsugar(bloodsugar: BloodSugar):
    user_bloodSugar = dict(bloodsugar)
    response = collection.insert(user_bloodSugar)
    return response

# 
@app.post('/login')
def login(request:OAuth2PasswordRequestForm = Depends()):
	user = db["users"].find_one({"username":request.username})
	if not user:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = f'No user found with this {request.username} username')
	if not Hash.verify(user["password"],request.password):
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = f'Wrong Username or password')
	access_token = create_access_token(data={"sub": user["username"] })
	return {"access_token": access_token, "token_type": "bearer", "username": request.username}