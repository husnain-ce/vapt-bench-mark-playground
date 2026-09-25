import base64
import io
import time
import paramiko


def connect(host, private_key_text, username="ubuntu", timeout=600, interval=10):
    key = paramiko.Ed25519Key.from_private_key(io.StringIO(private_key_text))
    deadline = time.time() + timeout
    attempt = 0
    last = None

    while time.time() < deadline:
        attempt += 1
        print(f"[SSH] attempt {attempt}: connecting to {username}@{host}:22 ...", flush=True)

        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=host,
                username=username,
                pkey=key,
                timeout=10,
                banner_timeout=20,
                auth_timeout=20,
            )
            print("[SSH] connected successfully.", flush=True)
            return client

        except Exception as e:
            last = e
            print(f"[SSH] not ready yet: {type(e).__name__}: {e}", flush=True)
            time.sleep(interval)

    raise RuntimeError(f"SSH did not become ready: {last}")


def run(client, command, sudo=False, timeout=1200, label=None):
    """
    Execute a potentially multiline shell script safely.

    The old implementation used:
        sudo bash -lc '<script>'

    That breaks when <script> itself contains single quotes, awk programs,
    command substitutions, heredocs, etc.

    This version base64-encodes the entire script locally, then decodes it
    remotely into bash stdin. No script contents are interpolated into shell
    quotes.
    """
    if label:
        print(f"[REMOTE] {label}...", flush=True)

    payload = base64.b64encode(command.encode()).decode()

    if sudo:
        remote_command = f"printf '%s' '{payload}' | base64 -d | sudo -n bash"
    else:
        remote_command = f"printf '%s' '{payload}' | base64 -d | bash"

    transport = client.get_transport()
    if not transport or not transport.is_active():
        raise RuntimeError("SSH transport is not active.")

    channel = transport.open_session(timeout=15)
    # Allocate a PTY so apt/curl/systemctl produce live, line-buffered output.
    channel.get_pty(term="xterm", width=120, height=40)
    channel.settimeout(1.0)
    channel.exec_command(remote_command)

    started = time.time()
    last_output = started
    last_heartbeat = started
    stdout_parts = []
    stderr_parts = []

    while True:
        if time.time() - started > timeout:
            channel.close()
            raise TimeoutError(
                f"Remote command timed out after {timeout} seconds"
                + (f" during: {label}" if label else "")
            )

        got_data = False

        if channel.recv_ready():
            data = channel.recv(4096).decode(errors="replace")
            stdout_parts.append(data)
            print(data, end="", flush=True)
            last_output = time.time()
            got_data = True

        if channel.recv_stderr_ready():
            data = channel.recv_stderr(4096).decode(errors="replace")
            stderr_parts.append(data)
            print(data, end="", flush=True)
            last_output = time.time()
            got_data = True

        if channel.exit_status_ready():
            while channel.recv_ready():
                data = channel.recv(4096).decode(errors="replace")
                stdout_parts.append(data)
                print(data, end="", flush=True)

            while channel.recv_stderr_ready():
                data = channel.recv_stderr(4096).decode(errors="replace")
                stderr_parts.append(data)
                print(data, end="", flush=True)

            break

        now = time.time()
        if not got_data and now - last_heartbeat >= 10:
            elapsed = int(now - started)
            silent = int(now - last_output)
            print(
                f"[REMOTE] still running... elapsed={elapsed}s, "
                f"no new output for {silent}s",
                flush=True,
            )
            last_heartbeat = now

        if not got_data:
            time.sleep(0.1)

    code = channel.recv_exit_status()
    out = "".join(stdout_parts)
    err = "".join(stderr_parts)

    if code != 0:
        raise RuntimeError(
            f"Remote command failed with exit code {code}.\n"
            f"STDERR:\n{err}"
        )

    if label:
        print(f"[REMOTE] {label}: done.", flush=True)

    return out


def occupied_ports(client):
    command = r"""
set -o pipefail
timeout 10s ss -H -lntu |
awk '
{
    proto=tolower($1)
    addr=$5
    n=split(addr, a, ":")
    port=a[n]

    if (port ~ /^[0-9]+$/)
        print proto, port
}
'
"""

    out = run(
        client,
        command,
        timeout=20,
        label="Detecting occupied host ports",
    )

    result = set()

    for line in out.splitlines():
        parts = line.split()
        if len(parts) != 2:
            continue

        proto = parts[0].lower()
        port_text = parts[1]

        if proto not in {"tcp", "udp"}:
            continue

        if not port_text.isdigit():
            continue

        result.add((proto, int(port_text)))

    result.add(("tcp", 22))

    print(
        "[PORTS] occupied: "
        + ", ".join(
            f"{proto}/{port}"
            for proto, port in sorted(result, key=lambda x: (x[1], x[0]))
        ),
        flush=True,
    )

    return result
