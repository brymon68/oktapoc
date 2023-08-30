from typing import List
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from starlette.config import Config
import httpx
from fastapi.middleware.cors import CORSMiddleware


# Load environment variables
config = Config(".env")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_credentials=True,
    allow_methods=["*"],
)

# Define the auth scheme and access token URL


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def validate_remotely(token, issuer, clientId, clientSecret):
    print("bruh1")
    headers = {
        "accept": "application/json",
        "cache-control": "no-cache",
        "content-type": "application/x-www-form-urlencoded",
    }
    data = {
        "client_id": clientId,
        "client_secret": clientSecret,
        "token": token,
    }
    url = issuer + "/v1/introspect"

    response = httpx.post(url, headers=headers, data=data)
    print(headers)
    print(data)
    print(response)

    return response.status_code == httpx.codes.OK and response.json()["active"]


def validate(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=400, detail="No worky - no token")

    res = validate_remotely(
        token,
        config("OKTA_ISSUER"),
        config("OKTA_CLIENT_ID"),
        config("OKTA_CLIENT_SECRET"),
    )

    if res:
        return True
    else:
        raise HTTPException(status_code=400)


# Hello World route
@app.get("/")
def read_root():
    return {"Hello": "World"}


# Call the Okta API to get an access token
# Data model
class Item(BaseModel):
    id: int
    name: str


# Protected, get items route
@app.get("/items", response_model=List[Item])
def read_items(
    request: Request,
    valid: bool = Depends(validate),
):
    print("REQUEST headers")
    for header, value in request.headers.items():
        print(f"{header}: {value}")

    print("hello")
    return [
        Item.model_validate({"id": 1, "name": "red ball"}),
        Item.model_validate({"id": 2, "name": "blue square"}),
        Item.model_validate({"id": 3, "name": "purple ellipse"}),
    ]
