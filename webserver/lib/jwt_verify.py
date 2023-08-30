import asyncio
from okta_jwt_verifier import BaseJWTVerifier


async def okta_verify():
    jwt_verifier = BaseJWTVerifier(issuer="{ISSUER}", audience="api://default")
    await jwt_verifier.verify_access_token("{JWT}")
    print("Token validated successfully.")


loop = asyncio.get_event_loop()
loop.run_until_complete(validate())
