# Teardown & RAM reclamation

`bin/teardown.sh` stops the range in layers so you can free memory without losing
the (slow-to-pull) images.

## Levels

```bash
./bin/teardown.sh            # stop all compose stacks + the k8s port-forward
                             # (images, volumes, k3s, venv all kept — fast re-up)

./bin/teardown.sh --k8s      # + remove Kubernetes Goat workloads (k3s stays up)
./bin/teardown.sh --k3s      # + uninstall the whole k3s cluster
./bin/teardown.sh --purge    # + remove aqira-range network, localstack volume, venv
./bin/teardown.sh --all      # --k3s + --purge (near-clean; images remain)
```

After any teardown the script prints current free RAM.

## What each level leaves behind

| Level | Containers | k3s | Images | Network/volumes | venv |
|---|---|---|---|---|---|
| (default) | stopped | up | kept | kept | kept |
| `--k8s` | stopped | up (empty) | kept | kept | kept |
| `--k3s` | stopped | removed | kept | kept | kept |
| `--purge` | stopped | up | kept | removed | removed |
| `--all` | stopped | removed | kept | removed | removed |

## Fast re-up after a teardown

```bash
./bin/deploy-all.sh          # re-runs all phases; cached images make it quick
# or a single phase:
./bin/deploy-web.sh
FORCE=1 ./k8s/deploy-k8s.sh
```

## Removing images too (full reclaim)

The kit never force-prunes images (they are expensive to re-pull). To reclaim
that disk yourself:

```bash
docker image rm bkimminich/juice-shop vulnerables/web-dvwa webgoat/webgoat \
  erev0s/vampi:latest vulhub/solr:8.11.0 localstack/localstack:3.8.1 \
  tleemcjr/metasploitable2 aqira/ms3-lite:ub1404 2>/dev/null
docker image prune -f
```

## Host artifacts to clean up manually

- `/etc/hosts` — the `# >>> aqira-range >>>` block (re-run installer removes it, or
  delete by hand).
- `/etc/nginx/conf.d/aqira-range.conf` + `aqira-range-proxy.inc` — remove and
  `systemctl reload nginx` if you want nginx clean.
- `evidence/iac/proof/` under the kit — checkov reports; delete freely.
