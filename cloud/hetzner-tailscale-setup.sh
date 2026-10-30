#!/bin/bash
# Setup script for the Claude Code cloud environment: lets cloud sessions run
# `ssh hetzner` over Tailscale SSH. Paste into the environment's "Setup script".
# Needs TS_AUTHKEY (ephemeral, tag:agent) in the environment variables and
# Custom network access that allows *.tailscale.com and *.tailscale.io.
set -euo pipefail

TS_VERSION=1.104.2

curl -fsSL "https://pkgs.tailscale.com/stable/tailscale_${TS_VERSION}_amd64.tgz" \
  | tar -xz -C /tmp
install -m 0755 "/tmp/tailscale_${TS_VERSION}_amd64/tailscale" /usr/local/bin/tailscale
install -m 0755 "/tmp/tailscale_${TS_VERSION}_amd64/tailscaled" /usr/local/bin/tailscaled
rm -rf "/tmp/tailscale_${TS_VERSION}_amd64"

# The setup script result is cached as a disk snapshot, so tailscaled can't be
# started here. ssh starts it on first use through this ProxyCommand instead.
cat > /usr/local/bin/ts-ssh-proxy <<'EOF'
#!/bin/bash
set -euo pipefail
SOCK=/run/tailscale/tailscaled.sock
ts() { tailscale --socket="$SOCK" "$@"; }

exec 9>/run/ts-ssh-proxy.lock
flock 9
if ! ts status >/dev/null 2>&1; then
  if [ -z "${TS_AUTHKEY:-}" ]; then
    echo "ts-ssh-proxy: TS_AUTHKEY is not set in the cloud environment" >&2
    exit 1
  fi
  mkdir -p /run/tailscale
  # Userspace mode: the VM has no TUN device. In-memory state makes the node
  # ephemeral, so it leaves the tailnet when the VM goes away.
  nohup tailscaled --tun=userspace-networking --state=mem: --socket="$SOCK" \
    --no-logs-no-support >/tmp/tailscaled.log 2>&1 &
  for _ in $(seq 50); do [ -S "$SOCK" ] && break; sleep 0.2; done
  ts up --authkey="$TS_AUTHKEY" --hostname="claude-cloud" --accept-dns=false \
    --timeout=60s >&2
fi
flock -u 9
exec tailscale --socket="$SOCK" nc "$1" "$2"
EOF
chmod 0755 /usr/local/bin/ts-ssh-proxy

mkdir -p /root/.ssh
chmod 700 /root/.ssh
cat > /root/.ssh/config <<'EOF'
Host hetzner
  HostName 100.95.154.125
  HostKeyAlias 2.28.7.7
  User root
  ProxyCommand /usr/local/bin/ts-ssh-proxy %h %p
  IdentityAgent none
  StrictHostKeyChecking yes
  ControlMaster auto
  ControlPath ~/.ssh/cm-%r@%h:%p
  ControlPersist 30m
EOF
echo '2.28.7.7 ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILyHi5XLYLB3JsX2wa+eQxUQ4tfBhnhkm0G5o2g/KUFC' \
  > /root/.ssh/known_hosts
chmod 600 /root/.ssh/config /root/.ssh/known_hosts
