from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


def create_mcp_client(settings) -> Client:
    transport = StreamableHttpTransport(
        url=settings.mcp_url,
        headers={
            "vyzno-cookie": settings.vyzno_cookie,
            "vyzno-csrf-token": settings.vyzno_csrf_token,
            "vyzno-mailbox-id": settings.vyzno_mailbox_id,
        },
    )

    return Client(
        auth=settings.mcp_token,
        transport=transport,
    )
