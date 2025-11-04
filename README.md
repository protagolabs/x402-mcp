# MCP Server

A simple MCP server implementation using the fastmcp framework.

## Features

- Health check tool
- Echo tool
- Easy to extend
- Justfile for automation

## Installation

```bash
pip install -r requirements.txt
```

## Running the Server

```bash
python app.py
```

Or install and run:

```bash
pip install -e .
mcp-server
```

## Using Justfile

This project includes a [Justfile](https://github.com/casey/just) for easy automation:

```bash
just install    # Install dependencies
just develop    # Install in development mode
just run        # Run the server
just test       # Test the server
just help       # Show available commands
```

## Tools

- `discovery_resource` - List discoverable x402 resources from the Bazaar.
- `call_service` - Call x402 service

## License

MIT
