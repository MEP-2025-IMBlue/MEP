from fastapi import Request, HTTPException, Depends
from pydantic import BaseModel
from jose import jwt
import os

# Lese den Public Key aus der .env-Datei (mit Zeilenumbruch-Ersatz)
PUBLIC_KEY = os.getenv("KEYCLOAK_PUBLIC_KEY", "").replace("\\n", "\n")

class User(BaseModel):
    id: str
    role: str

# Systeminterne Aufrufe wie Prometheus oder Hintergrundtasks
SYSTEM_USER = User(id="system", role="system")

def get_current_user(request: Request) -> User:
    """Extrahiert User-ID und Rolle aus dem JWT-Token im Authorization Header."""
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Kein gültiger Auth-Token.")
    token = auth_header.split(" ")[1]

    try:
        # JWT-Token mit dem Keycloak Public Key verifizieren und dekodieren
        decoded = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"], options={"verify_aud": False})
        roles = decoded.get("realm_access", {}).get("roles", [])

        if not roles:
            raise HTTPException(status_code=403, detail="Keine Rolle im Token gefunden.")

        # Erste Rolle übernehmen (so wie ursprünglich gewünscht)
        return User(
            id=decoded["sub"],
            role=roles[0]
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Ungültiger oder abgelaufener Token.")

# current_user: User = Depends(get_current_user)
