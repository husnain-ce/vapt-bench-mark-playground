# Cloud labs

The IaC static-analysis labs use two upstream, intentionally-vulnerable repos that
are **fetched at deploy time** rather than vendored here (they ship planted example
AWS keys and carry their own licenses):

- **cfngoat** — https://github.com/bridgecrewio/cfngoat
- **terragoat** — https://github.com/bridgecrewio/terragoat

Clone them into this directory before running `iac-scan.sh`:

```bash
git clone --depth 1 https://github.com/bridgecrewio/cfngoat.git   cfngoat
git clone --depth 1 https://github.com/bridgecrewio/terragoat.git terragoat
```

`kubernetes-goat` is fetched automatically by `../k8s/deploy-k8s.sh`.
`iac-scan.sh` then runs checkov over `cfngoat/`, `terragoat/`, and the k8s-goat scenarios.
