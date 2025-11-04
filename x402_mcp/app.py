#!/usr/bin/env python3
"""
MCP Server using fastmcp framework
"""

from fastmcp import FastMCP
from x402.facilitator import FacilitatorClient
from cdp.x402 import create_facilitator_config
from x402.types import ListDiscoveryResourcesRequest, ListDiscoveryResourcesResponse
from x402.clients.httpx import x402HttpxClient
from x402.clients.base import decode_x_payment_response, x402Client
from eth_account import Account
from httpx._config import Timeout
import logging
import os

logger = logging.getLogger(__name__)

# Create the MCP application
app = FastMCP()

httpx_default_timeout = os.getenv("HTTPX_DEFAULT_TIMEOUT", "30")

@app.tool(
    name="discovery_resource",
    description="List discoverable x402 resources from the Bazaar.",
)
async def discovery_resource(
    type: str = None,
    limit: int = 100,
    offset: int = 0,
    asset: str = None,
    max_price: int = None,
) -> ListDiscoveryResourcesResponse:
    """List discoverable x402 resources from the Bazaar.

    Args:
        type (str, optional): Filter by resource type (e.g., “http”). Defaults to None.
        limit (int, optional): Maximum number of results to return (1-100). Defaults to 100.
        offset (int, optional): Number of results to skip for pagination. Defaults to 0.
        asset (str, optional): Filter by ERC-20 token contract address for payment. Defaults to USDC token address on basechain.
        max_price (int, optional): Maximum price to filter services, inclusive. 1000000 equals to 1 usdc. Defaults to None.

    Returns:
        _type_: dict
    """
    facilitator_config = create_facilitator_config()
    facilitator = FacilitatorClient(facilitator_config)

    # Fetch all available services
    services = await facilitator.list(
        ListDiscoveryResourcesRequest(type=type, limit=limit, offset=offset)
    )

    result_services = []
    for item in services.items:
        if asset is None and max_price is None:
            result_services.append(item)
            continue

        if any(
            (asset is None or payment_req.asset == asset)
            and (max_price is None or int(payment_req.max_amount_required) <= max_price)
            for payment_req in item.accepts
        ):
            result_services.append(item)

    services.items = result_services
    return services


@app.tool(name="call_service", description="Call x402 service")
async def call_service(
    private_key: str,
    resource: str,
    method: str,
    input_data: dict,
    custom_network_filter: str = None,
) -> dict:
    """Call x402 service

    Args:
        private_key (str): User's private key to sign payments
        resource (str): The resource URL to call
        method (str): HTTP method ("get" or "post")
        input_data (dict): Input data for the request
        custom_network_filter (str, optional): Custom network filter for payment requirements. Defaults to None.

    Returns:
        dict: Response from the x402 service
    """
    account = Account.from_key(private_key)
    logger.info(f"Initialized account: {account.address}")
    # check resource
    if not resource.startswith("http"):
        raise ValueError("Resource must be a valid URL starting with http or https")
    
    resource = resource.split("/")
    if len(resource) < 4:
        raise ValueError("Resource URL is not valid")
    
    endpoint_path = "/" + "/".join(resource[3:])
    base_url = "/".join(resource[0:3])

    def custom_payment_selector(
        accepts, network_filter=None, scheme_filter=None, max_value=None
    ):
        """Custom payment selector that filters by network."""

        # NOTE: In a real application, you'd want to dynamically choose the most
        # appropriate payment requirement based on user preferences, available funds,
        # network conditions, or other business logic rather than hardcoding a network.

        if custom_network_filter:
            network_filter = custom_network_filter

        return x402Client.default_payment_requirements_selector(
            accepts,
            network_filter=network_filter,
            scheme_filter=scheme_filter,
            max_value=max_value,
        )

    async with x402HttpxClient(
        account=account,
        base_url=base_url,
        payment_requirements_selector=custom_payment_selector,
        timeout=Timeout(int(httpx_default_timeout))
    ) as client:
        # Make request - payment handling is automatic
        try:
            assert endpoint_path is not None  # we already guard against None above
            logger.info(f"Making request to {endpoint_path}")
            if method.lower() == "post":
                response = await client.post(endpoint_path, json=input_data)
            elif method.lower() == "get":
                response = await client.get(endpoint_path, params=input_data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Read the response content
            content = await response.aread()
            logger.debug(f"Response: {content.decode()}")

            # Check for payment response header
            payment_response = None
            if "X-Payment-Response" in response.headers:
                payment_response = decode_x_payment_response(
                    response.headers["X-Payment-Response"]
                )
                logger.info(
                    f"Payment response transaction hash: {payment_response['transaction']}"
                )
            else:
                logger.warning("No payment response header found")

            return {
                "result": content.decode(),
                "hash": payment_response["transaction"] if payment_response else None,
            }
            
        except Exception as e:
            logger.exception(e)

    return {"error": "Request failed"}


def main():
    """Main function to run the MCP server"""
    logger.info("Starting MCP Server...")
    # Run with stdio transport (default)
    app.run(transport="stdio")

if __name__ == "__main__":
    main()
