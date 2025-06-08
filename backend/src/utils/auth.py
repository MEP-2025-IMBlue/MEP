from fastapi import Request, HTTPException, Depends
from pydantic import BaseModel
from jose import jwt

PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
...BURAYA KENDİ KEYİNİ KOY...
-----END PUBLIC KEY-----
"""

class User(BaseModel):
    id: str
    role: str

def get_current_user(request: Request) -> User:
    """Extrahiert User-ID und Rolle aus dem JWT-Token im Authorization Header."""
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Kein gültiger Auth-Token.")
    token = auth_header.split(" ")[1]
    # JWT-Token mit dem Keycloak Public Key verifizieren und dekodieren
    decoded = jwt.decode(token, "PUBLIC_KEY", algorithms=["RS256"], options={"verify_aud": False})
    user_id = decoded["sub"]
    # Hier wird die erste Rolle des Benutzers übernommen (bei Bedarf anpassen)
    role = decoded["realm_access"]["roles"][0]
    return User(
        id=decoded["sub"],
        role=decoded["realm_access"]["roles"][0]  # [0]Bei mehreren Rollen ggf. verbessern!
    )
#current_user: User = Depends(get_current_user)