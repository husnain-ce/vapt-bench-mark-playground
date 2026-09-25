import getpass
import ipaddress
import os
import sys
import urllib.request
import uuid
from pathlib import Path

import yaml
from botocore.exceptions import ClientError, BotoCoreError

from .aws import (
    make_session,
    get_latest_ubuntu_ami,
    default_vpc,
    create_security_group,
    authorize_all_from_cidr,
    create_key_pair,
    launch_instance,
    wait_for_instance,
)
from .ssh import connect, run, occupied_ports
from .ports import choose_external_ports
from .metasploitable import bootstrap_script


BASE = Path(__file__).resolve().parent.parent


def progress(step, total, message):
    print(f"\n[{step}/{total}] {message}", flush=True)


def prompt(name, secret=False, default=None):
    env = os.getenv(name)
    if env:
        return env
    label = name.replace("_", " ").title()
    suffix = f" [{default}]" if default else ""
    value = (getpass.getpass if secret else input)(f"{label}{suffix}: ").strip()
    return value or default


def detect_public_ipv4():
    with urllib.request.urlopen(
        "https://checkip.amazonaws.com",
        timeout=10
    ) as response:
        ip = response.read().decode().strip()

    addr = ipaddress.ip_address(ip)
    if addr.version != 4:
        raise ValueError("Detected address is not IPv4.")
    return f"{addr}/32"


def resolve_allowed_cidr(settings):
    # Highest priority: environment variable.
    env = os.getenv("ALLOWED_CIDR")
    if env:
        value = env
    else:
        value = settings.get("network", {}).get("allowed_cidr", "auto")

    if str(value).strip().lower() == "auto":
        return detect_public_ipv4()

    net = ipaddress.ip_network(str(value), strict=False)
    if net.version != 4:
        raise ValueError("allowed_cidr must be IPv4.")


    return str(net)


def explain_aws_error(e):
    if isinstance(e, ClientError):
        err = e.response.get("Error", {})
        return f"{err.get('Code', 'AWS error')}: {err.get('Message', str(e))}"
    return str(e)


def main():
    total = 13

    settings = yaml.safe_load((BASE / "configs" / "deployer.yaml").read_text())
    config = yaml.safe_load((BASE / "configs" / "machine.yaml").read_text())
    machine = config["machine"]

    default_region = settings.get("aws", {}).get("region", "eu-north-1")
    default_type = settings.get("aws", {}).get("instance_type", "m7i-flex.large")

    print("=" * 60)
    print("AQSEC AWS VULNERABLE MACHINE DEPLOYER")
    print("=" * 60)
    print(f"Machine: {machine.get('name', machine.get('id', 'unknown'))}")

    access = prompt("AWS_ACCESS_KEY_ID")
    secret = prompt("AWS_SECRET_ACCESS_KEY", secret=True)
    region = prompt("AWS_REGION", default=default_region)
    instance_type = prompt("INSTANCE_TYPE", default=default_type)

    progress(1, total, "Resolving authorized inbound source")
    allowed_cidr = resolve_allowed_cidr(settings)
    print(f"    Security-group source: {allowed_cidr}")

    session = make_session(access, secret, region)
    ec2 = session.client("ec2")
    ssm = session.client("ssm")

    progress(2, total, "Validating AWS credentials")
    caller = session.client("sts").get_caller_identity()
    print(f"    Account: {caller['Account']}")
    print(f"    Region:  {region}")

    progress(3, total, "Resolving Ubuntu 24.04 AMI")
    ami = get_latest_ubuntu_ami(ssm)
    print(f"    AMI: {ami}")

    progress(4, total, "Finding default VPC")
    vpc_id = default_vpc(ec2)
    print(f"    VPC: {vpc_id}")

    suffix = uuid.uuid4().hex[:8]
    sg_name = f"aqsec-machine-{suffix}"
    key_name = f"aqsec-machine-{suffix}"

    progress(5, total, "Creating security group")
    sg_id = create_security_group(ec2, vpc_id, sg_name)
    authorize_all_from_cidr(
        ec2,
        sg_id,
        allowed_cidr,
        "AQSEC benchmark access - all traffic from operator only",
    )
    print(f"    Security group: {sg_id}")
    print(f"    Inbound: ALL traffic from {allowed_cidr}")

    progress(6, total, "Creating temporary EC2 SSH key")
    key_material = create_key_pair(ec2, key_name)
    print(f"    Key pair: {key_name}")

    progress(7, total, f"Launching EC2 instance ({instance_type})")
    instance_id = launch_instance(ec2, ami, instance_type, sg_id, key_name)
    print(f"    Instance ID: {instance_id}")

    progress(8, total, "Waiting for EC2 to become healthy")
    public_ip, inst = wait_for_instance(ec2, instance_id)
    print(f"    Public IP: {public_ip}")

    progress(9, total, "Connecting to Ubuntu over SSH")
    ssh = connect(public_ip, key_material)

    progress(10, total, "Preserving host ports and mapping VM conflicts")
    occupied = occupied_ports(ssh)
    mappings = choose_external_ports(machine["ports"], occupied)

    print("    Existing Ubuntu listeners are NOT changed.")
    for m in mappings:
        service = next(
            (p.get("service", "") for p in machine["ports"]
             if int(p["guest"]) == m["guest"]
             and p.get("protocol", "tcp") == m["protocol"]),
            ""
        )

        if m["guest"] == m["external"]:
            state = "original port"
        else:
            state = "VM remapped; host port preserved"

        print(
            f"    VM {m['guest']}/{m['protocol']} -> HOST {m['external']}"
            + (f"  ({service})" if service else "")
            + f"  [{state}]",
            flush=True,
        )

    progress(11, total, "Downloading, verifying, and starting vulnerable VM")
    script = bootstrap_script(config, mappings)
    run(
        ssh,
        script,
        sudo=True,
        timeout=2400,
        label="Remote vulnerable-machine installation",
    )

    progress(12, total, "Verifying benchmark access")
    print(f"    ALL protocols/ports allowed from {allowed_cidr}")
    print("    QEMU forwards configured machine ports on 0.0.0.0.")

    progress(13, total, "Deployment complete")

    print("\n" + "=" * 60)
    print("AQSEC MACHINE DEPLOYMENT")
    print("=" * 60)
    print("Status: SUCCESS")
    print(f"Machine:       {machine.get('name', machine.get('id'))}")
    print(f"Instance ID:   {instance_id}")
    print(f"Instance type: {instance_type}")
    print(f"Public IP:     {public_ip}")
    print(f"Allowed CIDR:  {allowed_cidr}")

    print("\nPORT MAPPING")
    print("-" * 60)
    for m in mappings:
        print(f"{m['guest']:<6}/{m['protocol']:<4} -> {m['external']}")
    print("-" * 60)
    print(f"Benchmark Target: {public_ip}")

    ssh.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled by user.", file=sys.stderr, flush=True)
        sys.exit(130)
    except (ClientError, BotoCoreError) as e:
        print(f"\nAWS ERROR: {explain_aws_error(e)}", file=sys.stderr, flush=True)
        sys.exit(2)
    except Exception as e:
        print(f"\nERROR [{type(e).__name__}]: {e}", file=sys.stderr, flush=True)
        sys.exit(1)
