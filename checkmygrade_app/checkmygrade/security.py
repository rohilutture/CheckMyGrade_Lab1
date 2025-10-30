import base64, hashlib, secrets

DEFAULT_APP_SECRET = "checkmygrade-lab1-secret-key"

def _derive_key(secret: str) -> bytes:
    return hashlib.sha256(secret.encode("utf-8")).digest()

def encrypt_password(plaintext: str, secret: str = DEFAULT_APP_SECRET) -> str:
    if not isinstance(plaintext, str):
        raise TypeError("plaintext must be str")
    key = _derive_key(secret)
    pt = plaintext.encode("utf-8")
    iv = secrets.token_bytes(16)
    ct = bytes((pt[i] ^ key[i % len(key)] ^ iv[i % len(iv)]) for i in range(len(pt)))
    token = base64.b64encode(iv + ct).decode("ascii")
    return token

def decrypt_password(token: str, secret: str = DEFAULT_APP_SECRET) -> str:
    if not isinstance(token, str):
        raise TypeError("token must be str")
    raw = base64.b64decode(token.encode("ascii"))
    iv, ct = raw[:16], raw[16:]
    key = _derive_key(secret)
    pt = bytes((ct[i] ^ key[i % len(key)] ^ iv[i % len(iv)]) for i in range(len(ct)))
    return pt.decode("utf-8")
