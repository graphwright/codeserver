"""Pulumi program to provision a Digital Ocean droplet for Code Server.

NOTE: The docker-compose.yml embedded in user_data below only runs once,
at initial droplet boot via cloud-init. It is NOT the source of truth for
the running configuration -- the droplet's live copy at
/opt/codeserver/docker-compose.yml has since diverged (see ../docker/ for
a copy matching what's actually deployed). Changing user_data and running
`pulumi up` will NOT update an existing droplet's compose file; it forces
a full droplet replacement instead.
"""

import pulumi
import pulumi_digitalocean as digitalocean

# Configuration
config = pulumi.Config()
code_server_password = config.require_secret("codeServerPassword")
anthropic_api_key = config.require_secret("anthropicApiKey")
droplet_size = config.get("dropletSize") or "s-1vcpu-1gb"  # $6/month
region = config.get("region") or "nyc3"

# Create SSH key for droplet access (optional - you can use existing key)
ssh_key = digitalocean.SshKey(
    "code-server-key",
    name="code-server-deploy-key",
    public_key=config.require("sshPublicKey"),  # You'll need to set this
)

# Cloud-init script to set up the droplet
user_data = pulumi.Output.all(code_server_password, anthropic_api_key).apply(
    lambda args: f"""#!/bin/bash
set -e

# Install Docker
curl -fsSL https://get.docker.com | sh

# Create directory for code server
mkdir -p /opt/codeserver
cd /opt/codeserver

# Download docker-compose.yml and Caddyfile from repo
# (We'll set this up after initial creation)
cat > docker-compose.yml <<'EOF'
version: '3.8'

services:
  code-server:
    image: ghcr.io/graphwright/kgraph-code-server:latest
    environment:
      PASSWORD: {args[0]}
      ANTHROPIC_API_KEY: {args[1]}
    volumes:
      - /workspace:/workspace
      - /var/run/docker.sock:/var/run/docker.sock:ro
    restart: unless-stopped
    networks:
      - codeserver

  caddy:
    image: caddy:2-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config
    restart: unless-stopped
    networks:
      - codeserver
    depends_on:
      - code-server

networks:
  codeserver:
    driver: bridge

volumes:
  caddy_data:
  caddy_config:
EOF

cat > Caddyfile <<'EOF'
code.graphwright.io {{
    reverse_proxy code-server:8080
}}
EOF

# Start services
docker compose up -d

echo "Code Server setup complete!"
"""
)

# Create the droplet
droplet = digitalocean.Droplet(
    "code-server-droplet",
    name="code-server",
    size=droplet_size,
    image="ubuntu-22-04-x64",
    region=region,
    ssh_keys=[ssh_key.id],
    user_data=user_data,
    tags=["code-server", "development"],
)

# Export the droplet's IP address
pulumi.export("droplet_ip", droplet.ipv4_address)
pulumi.export("droplet_id", droplet.id)
pulumi.export("access_url", "https://code.graphwright.io")
