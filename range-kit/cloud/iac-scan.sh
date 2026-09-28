#!/usr/bin/env bash
# Static IaC misconfiguration scan for the Aqira Cyber Range (Agent D).
# Runs checkov over TerraGoat (Terraform), CFNGoat (CloudFormation) and the
# Kubernetes Goat manifests, writing machine- and human-readable reports.
set -uo pipefail
# Path-independent: resolve against the kit layout, allow env overrides.
_SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # .../cloud
_ROOT="$(cd "$_SELF_DIR/.." && pwd)"                         # kit root
CKV="${CKV:-$_ROOT/.venv/bin/checkov}"
[ -x "$CKV" ] || CKV="$(command -v checkov || echo checkov)"
CLOUD="${CLOUD:-$_SELF_DIR}"
OUT="${OUT:-$_ROOT/evidence/iac/proof}"
mkdir -p "$OUT"

scan() {
  local name="$1" dir="$2"; shift 2
  echo "=== checkov: $name ($dir) ==="
  "$CKV" -d "$dir" "$@" --compact --quiet -o cli 2>/dev/null | tee "$OUT/checkov_${name}.txt" | tail -3
  "$CKV" -d "$dir" "$@" --quiet -o json 2>/dev/null > "$OUT/checkov_${name}.json"
}

# Kubernetes Goat is fetched by k8s/deploy-k8s.sh into ../k8s/kubernetes-goat.
K8SGOAT="${K8SGOAT:-$_ROOT/k8s/kubernetes-goat/scenarios}"

scan terragoat_aws   "$CLOUD/terragoat/terraform/aws"   --framework terraform
scan terragoat_azure "$CLOUD/terragoat/terraform/azure" --framework terraform
scan terragoat_gcp   "$CLOUD/terragoat/terraform/gcp"   --framework terraform
scan cfngoat         "$CLOUD/cfngoat"                    --framework cloudformation
if [ -d "$K8SGOAT" ]; then
  scan k8sgoat_manifests "$K8SGOAT" --framework kubernetes
else
  echo "SKIP k8sgoat_manifests — $K8SGOAT not present (run k8s/deploy-k8s.sh first)"
fi

echo "=== SCAN COMPLETE ==="
