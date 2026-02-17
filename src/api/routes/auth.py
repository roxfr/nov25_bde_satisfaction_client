# File: src\api\routes\auth.py

"""Module FastAPI pour gérer l'authentification via JWT avec utilisateur admin hashé depuis le .env."""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from loguru import logger


load_dotenv()

router = APIRouter()

# --- Config JWT ---
SECRET_KEY: str = os.getenv("SECRET_KEY")
if SECRET_KEY is None:
    logger.error("La clé secrète (SECRET_KEY) n'est pas définie dans le fichier .env")
    raise ValueError("La clé secrète (SECRET_KEY) n'est pas définie dans le fichier .env")

ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# --- Credentials admin depuis le .env ---
ADMIN_USERNAME: str = os.getenv("USERNAME_ADMIN")
if ADMIN_USERNAME is None:
    logger.error("Le nom d'utilisateur admin (USERNAME_ADMIN) n'est pas défini dans le fichier .env")
    raise ValueError("Le nom d'utilisateur admin (USERNAME_ADMIN) n'est pas défini dans le fichier .env")

ADMIN_PASSWORD_HASH: str = os.getenv("PASSWORD_ADMIN")
if ADMIN_PASSWORD_HASH is None:
    logger.error("Le mot de passe admin (PASSWORD_ADMIN) n'est pas défini dans le fichier .env")
    raise ValueError("Le mot de passe admin (PASSWORD_ADMIN) n'est pas défini dans le fichier .env")

# --- OAuth2 ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# --- Hashing context ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie qu'un mot de passe en clair correspond au hash."""
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str) -> bool:
    """Vérifie que le username correspond à l'admin et que le mot de passe est correct."""
    if username == ADMIN_USERNAME:
        logger.info(f"Tentative d'authentification pour l'utilisateur : {username}")
        is_authenticated = verify_password(password, ADMIN_PASSWORD_HASH)
        if is_authenticated:
            logger.info(f"Authentification réussie pour l'utilisateur : {username}")
        else:
            logger.warning(f"Mot de passe incorrect pour l'utilisateur : {username}")
        return is_authenticated
    else:
        logger.warning(f"Tentative d'authentification avec un nom d'utilisateur inconnu : {username}")
    return False


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Crée un token JWT pour un utilisateur donné avec expiration."""
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """Récupère l'utilisateur courant à partir du token JWT."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username != ADMIN_USERNAME:
            logger.error(f"Utilisateur invalide : {username}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilisateur invalide")
        logger.info(f"Utilisateur authentifié : {username}")
        return username
    except JWTError as e:
        logger.error(f"Token invalide : {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide")


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    """Génère un token JWT après authentification de l'utilisateur admin."""
    if not authenticate_user(form_data.username, form_data.password):
        logger.warning(f"Nom d'utilisateur ou mot de passe incorrect pour l'utilisateur : {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect"
        )
    access_token = create_access_token(
        {"sub": form_data.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    logger.info(f"Token généré pour l'utilisateur : {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}
