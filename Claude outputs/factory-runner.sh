#!/usr/bin/env bash
# One-off: self-hosted GitHub Actions runner for the factory repos, in an
# OrbStack Linux VM on this Mac. Run BEFORE factory-land.sh:
#   bash ~/repos/dotclaude/"Claude outputs"/factory-runner.sh
# Why a VM: jobs run as root-capable Linux (apt, docker, Playwright deps) and
# their Postgres ports (e.g. frontq :55433) never collide with your local ones.
set -euo pipefail
OWNER=dopiotrek; VM=gh-runner
REPOS=(frontq dronelist swissCRM piotrek-cc compass tma)
ask(){ read -r -p "$1 [y/N] " a; [[ ${a:-n} == y* ]]; }
command -v orb >/dev/null || { echo "OrbStack CLI 'orb' not found"; exit 1; }
gh auth status >/dev/null

if ! orb list | grep -qw "$VM"; then
  ask "Create OrbStack VM '$VM' (Ubuntu 24.04)?" || exit 0
  orb create ubuntu:noble "$VM"
fi

echo "== Installing build tools and Docker in the VM"
orb -m "$VM" -u root bash -c '
  set -e; export DEBIAN_FRONTEND=noninteractive
  apt-get update -qq
  apt-get install -y -qq git curl jq unzip zip build-essential python3 postgresql-client docker.io docker-compose-v2 >/dev/null
  systemctl enable --now docker'
orb -m "$VM" -u root usermod -aG docker "$(orb -m "$VM" whoami)"

VER=$(gh api repos/actions/runner/releases/latest -q .tag_name | sed 's/^v//')
ARCH=$(orb -m "$VM" uname -m); [ "$ARCH" = aarch64 ] && ARCH=arm64 || ARCH=x64
echo "== actions/runner $VER linux-$ARCH"

for dir in "${REPOS[@]}"; do
  # GitHub name can differ from the folder (tma -> that-money-app)
  repo=$(git -C ~/repos/apps/$dir remote get-url origin | sed -E 's#.*/([^/]+)(\.git)?$#\1#; s#\.git$##')
  vis=$(gh repo view "$OWNER/$repo" --json visibility -q .visibility)
  if [ "$vis" != PRIVATE ]; then
    echo "!! $repo is $vis — skipped. A self-hosted runner on a public repo lets any fork PR run code on this Mac."
    continue
  fi
  if orb -m "$VM" bash -c "test -f ~/runners/$dir/.runner"; then echo "-- $dir: already registered"; continue; fi
  ask "Register runner for $dir ($OWNER/$repo)?" || continue
  TOKEN=$(gh api -X POST "repos/$OWNER/$repo/actions/runners/registration-token" -q .token)
  orb -m "$VM" bash -c "
    set -e; mkdir -p ~/runners/$dir && cd ~/runners/$dir
    curl -sSL -o r.tgz https://github.com/actions/runner/releases/download/v$VER/actions-runner-linux-$ARCH-$VER.tar.gz
    tar xzf r.tgz && rm r.tgz
    ./config.sh --unattended --replace --url https://github.com/$OWNER/$repo --token $TOKEN \
      --name macmini-$dir --labels self-hosted,linux --work _work
    sudo ./svc.sh install \$(whoami) && sudo ./svc.sh start"
  echo "-- $dir: runner online"
done
echo
echo "Done. Check: GitHub → repo → Settings → Actions → Runners shows 'macmini-<repo>' Idle."
echo "The VM starts with OrbStack; keep OrbStack running (login item) or jobs wait in the queue."
