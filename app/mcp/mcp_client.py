import httpx
from fastapi import HTTPException, status
from typing import Optional, Dict, Any
import json
import os
from ..config import settings

class MCPClient:
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or os.getenv("MCP_BASE_URL", "http://localhost:8001")
        self.api_key = api_key or os.getenv("MCP_API_KEY")
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}" if self.api_key else ""
            },
            timeout=30.0
        )

    async def send_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a request to the MCP server
        """
        try:
            url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
            response = await self.client.request(
                method=method,
                url=url,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"MCP Server Error: {e.response.text}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to communicate with MCP server: {str(e)}"
            )

    async def process_item(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send item data to MCP for additional processing
        """
        return await self.send_request("POST", "process/item", item_data)

    async def get_item_analysis(self, item_id: str) -> Dict[str, Any]:
        """
        Get analysis for a specific item from MCP
        """
        return await self.send_request("GET", f"analysis/item/{item_id}")

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Dependency to get MCP client
async def get_mcp_client():
    client = MCPClient()
    try:
        yield client
    finally:
        await client.close()
