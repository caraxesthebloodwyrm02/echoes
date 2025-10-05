#!/bin/bash

# Individual Docker Security Scripts
# These are modular scripts for specific security tasks

# 1. Secrets Management Script
cat > ./scripts/create-secrets.sh << 'EOF'
#!/bin/bash
SECRETS_DIR="../secrets"
mkdir -p "$SECRETS_DIR"
chmod 700 "$SECRETS_DIR"

# Generate secure passwords
openssl rand -base64 32 > "$SECRETS_DIR/db_password.txt"
openssl rand -base64 32 > "$SECRETS_DIR/redis_password.txt"
openssl rand -base64 32 > "$SECRETS_DIR/pgadmin_password.txt"
chmod 600 "$SECRETS_DIR"/*.txt

echo "Secrets created successfully"
EOF

# 2. Docker Daemon Configuration Script
cat > ./scripts/update-docker-daemon.sh << 'EOF'
#!/bin/bash
DAEMON_CONFIG="/etc/docker/daemon.json"

if [[ $EUID -eq 0 ]]; then
    cat > "$DAEMON_CONFIG" <<EOL
{
  "userns-remap": "default",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOL
    systemctl restart docker
    echo "Docker daemon updated"
else
    echo "Root access required"
fi
EOF

# 3. Image Scanning Script
cat > ./scripts/scan-images.sh << 'EOF'
#!/bin/bash
IMAGES=$(docker images --format "{{.Repository}}:{{.Tag}}")

for image in $IMAGES; do
    echo "Scanning $image..."
    docker scan "$image" || echo "Failed to scan $image"
done
EOF

# 4. Resource Cleanup Script
cat > ./scripts/cleanup.sh << 'EOF'
#!/bin/bash
echo "Cleaning up Docker resources..."
docker system prune -f
docker volume prune -f
echo "Cleanup completed"
EOF

# 5. Security Testing Script
cat > ./scripts/security-test.sh << 'EOF'
#!/bin/bash
docker run --rm -it --net host --pid host --cap-add audit_control \
    -e DOCKER_CONTENT_TRUST=1 \
    -v /var/lib:/var/lib \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --label docker_bench_security \
    docker/docker-bench-security
EOF

# Make scripts executable
chmod +x ./scripts/*.sh

echo "Individual security scripts created"
