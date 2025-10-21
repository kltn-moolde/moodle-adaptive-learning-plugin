"""
Key Management Service
Generates and persists an RSA key pair (JWK) for the Tool and exposes JWKS.

This is required so the LTI Platform (Moodle) can fetch the Tool's public keys
via the TOOL_PUBLIC_JWK_URL during registration/validation flows.
"""

from jwcrypto import jwk
from loguru import logger
import os
import json
import uuid


class KeyService:
    def __init__(self, base_dir: str = "data/keys"):
        self.base_dir = base_dir
        self.private_path = os.path.join(self.base_dir, "tool_private_jwk.json")
        self.public_path = os.path.join(self.base_dir, "tool_public_jwk.json")
        self.kid_path = os.path.join(self.base_dir, "kid.txt")
        self._ensure_keys()

    def _ensure_keys(self):
        os.makedirs(self.base_dir, exist_ok=True)

        if not (os.path.exists(self.private_path) and os.path.exists(self.public_path) and os.path.exists(self.kid_path)):
            logger.info("Generating new RSA key pair for Tool (JWKS)")
            key = jwk.JWK.generate(kty='RSA', size=2048)

            # Derive a key id (kid)
            kid = str(uuid.uuid4())
            key.update(kid=kid)

            # Export keys
            private_jwk = json.loads(key.export(private_key=True))
            public_jwk = json.loads(key.export(private_key=False))

            # Add recommended fields for LTI
            public_jwk["alg"] = "RS256"
            public_jwk["use"] = "sig"
            private_jwk["alg"] = "RS256"
            private_jwk["use"] = "sig"

            with open(self.private_path, "w") as f:
                json.dump(private_jwk, f)
            with open(self.public_path, "w") as f:
                json.dump(public_jwk, f)
            with open(self.kid_path, "w") as f:
                f.write(kid)

            logger.info(f"Tool keys generated with kid={kid}")
        else:
            logger.info("Existing Tool keys found; reusing persisted JWKS")

    def get_public_jwk(self) -> dict:
        with open(self.public_path, "r") as f:
            return json.load(f)

    def get_jwks(self) -> dict:
        return {"keys": [self.get_public_jwk()]}


# Global instance
key_service = KeyService()
