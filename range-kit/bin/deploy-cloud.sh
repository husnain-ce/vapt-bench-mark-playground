#!/usr/bin/env bash
# Deploy the cloud labs: LocalStack (emulated AWS) + seed misconfigured resources.
# The static IaC scan (TerraGoat/CFNGoat/K8s manifests) is run separately by
# cloud/iac-scan.sh — it needs no runtime and is invoked from deploy-all.sh.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

"$BENCH_ROOT/bin/create-network.sh"

log "up: localstack (127.0.0.1:8107)"
dc -f "$COMPOSE_DIR/cloud-localstack.yml" up -d

log "waiting for LocalStack edge to become healthy..."
for i in $(seq 1 30); do
  if [ "$(probe_http localhost /_localstack/health)" != "000" ] || \
     curl -s http://127.0.0.1:8107/_localstack/health >/dev/null 2>&1; then
    ok "LocalStack edge responding"; break
  fi
  sleep 3
done

# Provision the venv (awslocal) then seed the misconfigured AWS resources.
"$CLOUD_DIR/venv-setup.sh" || warn "venv-setup failed; seeding may fall back to awslocal on PATH"
log "seeding misconfigured AWS resources"
bash "$CLOUD_DIR/localstack-seed.sh" || warn "localstack seed reported errors (see output above)"
ok "cloud lab deployed + seeded"
