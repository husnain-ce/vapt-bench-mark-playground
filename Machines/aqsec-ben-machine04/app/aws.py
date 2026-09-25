import time
import boto3
from botocore.exceptions import ClientError


def make_session(access_key, secret_key, region):
    return boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
    )


def get_latest_ubuntu_ami(ssm):
    param = "/aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id"
    return ssm.get_parameter(Name=param)["Parameter"]["Value"]


def supports_nested_virtualization(ec2, instance_type):
    r = ec2.describe_instance_types(InstanceTypes=[instance_type])
    features = r["InstanceTypes"][0].get("ProcessorInfo", {}).get("SupportedFeatures", [])
    return "nested-virtualization" in features


def default_vpc(ec2):
    vpcs = ec2.describe_vpcs(Filters=[{"Name": "is-default", "Values": ["true"]}])["Vpcs"]
    if not vpcs:
        raise RuntimeError("No default VPC found in this region.")
    return vpcs[0]["VpcId"]


def create_security_group(ec2, vpc_id, name):
    try:
        r = ec2.create_security_group(
            GroupName=name,
            Description="AQSEC generic vulnerable VM lab",
            VpcId=vpc_id,
        )
        return r["GroupId"]
    except ClientError as e:
        if e.response["Error"]["Code"] != "InvalidGroup.Duplicate":
            raise
        groups = ec2.describe_security_groups(
            Filters=[
                {"Name": "group-name", "Values": [name]},
                {"Name": "vpc-id", "Values": [vpc_id]},
            ]
        )["SecurityGroups"]
        return groups[0]["GroupId"]


def authorize_all_from_cidr(ec2, sg_id, cidr, description="AQSEC operator access"):
    try:
        ec2.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[{
                "IpProtocol": "-1",
                "IpRanges": [{"CidrIp": cidr, "Description": description}],
            }],
        )
    except ClientError as e:
        if e.response["Error"]["Code"] != "InvalidPermission.Duplicate":
            raise


def create_key_pair(ec2, name):
    try:
        ec2.delete_key_pair(KeyName=name)
    except Exception:
        pass
    r = ec2.create_key_pair(KeyName=name, KeyType="ed25519")
    return r["KeyMaterial"]


def launch_instance(ec2, ami, instance_type, sg_id, key_name):
    if not supports_nested_virtualization(ec2, instance_type):
        raise RuntimeError(f"{instance_type} does not advertise AWS nested-virtualization support.")

    r = ec2.run_instances(
        ImageId=ami,
        InstanceType=instance_type,
        MinCount=1,
        MaxCount=1,
        KeyName=key_name,
        SecurityGroupIds=[sg_id],
        CpuOptions={"NestedVirtualization": "enabled"},
        BlockDeviceMappings=[{
            "DeviceName": "/dev/sda1",
            "Ebs": {"VolumeSize": 35, "VolumeType": "gp3", "DeleteOnTermination": True},
        }],
        TagSpecifications=[{
            "ResourceType": "instance",
            "Tags": [
                {"Key": "Name", "Value": "aqsec-ben-machine04"},
                {"Key": "AQSEC", "Value": "generic-vulnerable-vm-lab"},
            ],
        }],
    )
    return r["Instances"][0]["InstanceId"]


def get_instance(ec2, instance_id):
    info = ec2.describe_instances(InstanceIds=[instance_id])
    return info["Reservations"][0]["Instances"][0]


def wait_for_instance(ec2, instance_id, timeout=600, interval=10):
    start = time.time()
    last_state = None
    while True:
        if time.time() - start > timeout:
            raise TimeoutError(f"Timed out waiting for instance {instance_id}.")

        inst = get_instance(ec2, instance_id)
        state = inst["State"]["Name"]
        public_ip = inst.get("PublicIpAddress", "-")
        statuses = ec2.describe_instance_status(InstanceIds=[instance_id], IncludeAllInstances=True).get("InstanceStatuses", [])
        system_status = "initializing"
        instance_status = "initializing"
        if statuses:
            system_status = statuses[0]["SystemStatus"]["Status"]
            instance_status = statuses[0]["InstanceStatus"]["Status"]

        snapshot = (state, system_status, instance_status, public_ip)
        if snapshot != last_state:
            print(f"[EC2] state={state} system={system_status} instance={instance_status} public_ip={public_ip}", flush=True)
            last_state = snapshot
        else:
            print("[EC2] still waiting for health checks...", flush=True)

        if state == "running" and system_status == "ok" and instance_status == "ok":
            if not inst.get("PublicIpAddress"):
                raise RuntimeError("Instance is healthy but has no public IPv4 address.")
            return inst["PublicIpAddress"], inst

        if state in {"shutting-down", "terminated", "stopping", "stopped"}:
            raise RuntimeError(f"Instance entered unexpected state: {state}")

        time.sleep(interval)
