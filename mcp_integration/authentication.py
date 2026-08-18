
import httpx
class MCPAuthentication:
    @staticmethod
    async def get_headers(
        authentication
    ):
        if not authentication:
            return {}
        auth_type = (
            authentication
            .get("type", "")
            .lower()
        )
        # =================================================
        # BEARER TOKEN
        # =================================================
        if auth_type == "bearer":
            token = authentication.get(
                "token"
            )
            if not token:
                raise ValueError(
                    "Bearer token is required."
                )
            return {
                "Authorization":
                    f"Bearer {token}"
            }
        # =================================================
        # OAUTH2
        # =================================================
        if auth_type == "oauth2":
            token_endpoint = (
                authentication.get(
                    "token_endpoint"
                )
            )
            client_id = (
                authentication.get(
                    "client_id"
                )
            )
            client_secret = (
                authentication.get(
                    "client_secret"
                )
            )
            grant_type = (
                authentication.get(
                    "grant_type"
                )
            )
            if not token_endpoint:
                raise ValueError(
                    "token_endpoint is required."
                )
            if not client_id:
                raise ValueError(
                    "client_id is required."
                )
            if not client_secret:
                raise ValueError(
                    "client_secret is required."
                )
            if grant_type != "client_credentials":
                raise ValueError(
                    "Only client_credentials "
                    "OAuth2 is supported."
                )
            async with httpx.AsyncClient(
                timeout=30
            ) as client:
                response = await client.post(
                    token_endpoint,
                    data={
                        "grant_type":
                            "client_credentials",
                        "client_id":
                            client_id,
                        "client_secret":
                            client_secret
                    }
                )
                response.raise_for_status()
                token_data = response.json()
            access_token = (
                token_data.get(
                    "access_token"
                )
            )
            if not access_token:
                raise ValueError(
                    "OAuth2 server did not "
                    "return access_token."
                )
            return {
                "Authorization":
                    f"Bearer {access_token}"
            }
        raise ValueError(
            f"Unsupported authentication type: "
            f"{auth_type}"
        )