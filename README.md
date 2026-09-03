# Code Server Deployment

Self-hosted VS Code in the browser with Claude Code CLI pre-installed, deployed on a dedicated Digital Ocean droplet.

## Architecture

- **Droplet**: $6/month (1GB RAM, 25GB SSD)
- **Code Server**: Browser-based VS Code
- **Caddy**: Automatic HTTPS with Let's Encrypt
- **Pulumi**: Infrastructure as Code for droplet provisioning

## Quick Start

### Prerequisites

1. Digital Ocean API token
2. DNS access to configure `code.graphwright.io`
3. Pulumi CLI installed
4. Python 3.12+

### Deploy

```bash
# Install dependencies
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Set Digital Ocean token
export DIGITALOCEAN_TOKEN=your_token_here
export CODE_SERVER_PASSWORD=your_password_here
export ANTHROPIC_API_KEY=your_anthropic_key_here

# Deploy infrastructure
cd pulumi
pulumi stack init prod
pulumi config set digitalocean:token $DIGITALOCEAN_TOKEN --secret
pulumi config set codeServerPassword $CODE_SERVER_PASSWORD --secret
pulumi config set anthropicApiKey $ANTHROPIC_API_KEY --secret
pulumi up

# Get the droplet IP
pulumi stack output droplet_ip
```

### Deploying via GitHub Actions

Pushing a tag matching `vX.Y.Z` (e.g. `v1.2.3`) triggers the
`.github/workflows/pulumi-refresh.yml` workflow, which runs `pulumi up`
against the `prod` stack to freshen the droplet with any infrastructure or
config changes.

This requires the following secrets to be configured in the GitHub repo
settings (Settings → Secrets and variables → Actions):

- `PULUMI_ACCESS_TOKEN` — Pulumi Cloud access token
- `PULUMI_CONFIG_PASSPHRASE` — passphrase used to decrypt stack secrets
- `DIGITALOCEAN_TOKEN` — Digital Ocean API token
- `PULUMI_BACKEND_URL` — Pulumi backend URL, if not using the default Pulumi Cloud backend

To deploy a new version:

```bash
git tag v1.2.3
git push origin v1.2.3
```

### Configure DNS

Point `code.graphwright.io` A record to the droplet IP from the output above.

### Access

Navigate to https://code.graphwright.io and enter your password.

## What's Included

- **VS Code**: Full VS Code experience in browser
- **Claude Code CLI**: Pre-installed and configured
- **Python 3.12**: With uv package manager
- **Node.js**: Latest LTS
- **Docker**: For running containers
- **Git**: Pre-configured
- **Persistent Storage**: `/workspace` directory

## Repository Structure

```
codeserver/
├── pulumi/                 # Infrastructure as Code
│   ├── __main__.py        # Pulumi program
│   └── Pulumi.yaml        # Pulumi project config
├── docker/                 # Docker configurations
│   ├── docker-compose.yml # Code Server + Caddy
│   └── Caddyfile          # Caddy reverse proxy config
├── scripts/                # Setup and maintenance scripts
│   └── setup-droplet.sh   # Initial droplet configuration
└── README.md              # This file
```

## Maintenance

### Update Code Server

```bash
ssh root@code.graphwright.io
cd /opt/codeserver
docker compose pull
docker compose up -d
```

### Backup Workspace

```bash
ssh root@code.graphwright.io
tar czf workspace-backup-$(date +%Y%m%d).tar.gz /workspace
```

### Destroy Infrastructure

```bash
cd pulumi
pulumi destroy
```

## Cost

- **Droplet**: $6/month
- **Bandwidth**: 1TB included (plenty for personal use)
- **Total**: ~$6/month

## Security

- Password-protected access
- HTTPS with automatic certificate renewal
- Isolated from other infrastructure
- Regular Docker image updates from ghcr.io/graphwright/kgraph-code-server

## Support

Issues: https://github.com/graphwright/codeserver/issues
