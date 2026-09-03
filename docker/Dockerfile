FROM codercom/code-server:latest

USER root

# Install Node.js and other tools
RUN apt-get update && apt-get install -y \
    curl \
    git \
    nodejs \
    npm \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI
RUN npm install -g @anthropic-ai/claude-code

# Create workspace directory
RUN mkdir -p /home/coder/workspace && chown -R coder:coder /home/coder/workspace

USER coder

WORKDIR /home/coder/workspace

# Bake in VS Code extensions so they're available on every container start
RUN code-server --install-extension ms-python.python
