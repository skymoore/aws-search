from logging import info
from .lib import perf_time, multithreaded


def get_ami_ids_by_owner(session, region, owner_id, name_filter, print_lock):
    ec2 = session.client("ec2", region_name=region)
    ami_ids = {}
    filter = [
        {
            "Name": "name",
            "Values": [name_filter],
        }
    ]
    owner_id = owner_id

    response = ec2.describe_images(
        Owners=[owner_id],
        Filters=filter,
    )
    for ami in response["Images"]:
        ami_ids[ami["ImageId"]] = ""

    while "NextToken" in response:
        response = ec2.describe_images(
            Owners=[owner_id],
            Filters=filter,
            NextToken=response["NextToken"],
        )
        for ami in response["Images"]:
            ami_ids[ami["ImageId"]] = ""

    len_ami_ids = len(ami_ids.keys())

    with print_lock:
        info(
            f"{len_ami_ids} {'ami' if len_ami_ids == 1 else 'amis'} owned by {owner_id} in region {region}"
        )
    return ami_ids


@multithreaded
def check_instance_for_match(
    instance, region, instance_ids_by_region, ami_ids, print_lock
):
    if instance.image_id in ami_ids:
        if region not in instance_ids_by_region:
            instance_ids_by_region[region] = [instance.id]
        else:
            instance_ids_by_region[region].append(instance.id)


@multithreaded
def find_instances(
    session, region, print_lock, owner_id, name_filter, instance_ids_by_region
):
    ec2_resource = session.resource("ec2", region_name=region)
    instances = ec2_resource.instances.all()
    num_instances = len(list(instances))

    if num_instances == 0:
        with print_lock:
            info(f"no ec2 instances found in region {region}")
        return
    with print_lock:
        info(f"{num_instances} ec2 instances in region {region}")

    ami_ids = get_ami_ids_by_owner(session, region, owner_id, name_filter, print_lock)

    inputs = [
        (instance, region, instance_ids_by_region, ami_ids, print_lock)
        for instance in instances
    ]

    check_instance_for_match(inputs, 4)
    len_instance_ids = len(instance_ids_by_region[region])
    with print_lock:
        info(
            f"{len_instance_ids} matching {'instance' if len_instance_ids == 1 else 'instances'} found in region {region}"
        )


@perf_time
def find_instances_by_ami_owner(
    session, workers, regions, print_lock, owner_id, name_filter
):
    info(
        f"searching {len(regions)} aws regions with {workers} workers for ec2 instances running an ami owned by {owner_id} whose name matches {name_filter}..."
    )
    instance_ids_by_region = {}
    inputs = [
        (session, region, print_lock, owner_id, name_filter, instance_ids_by_region)
        for region in regions
    ]
    find_instances(inputs, workers)
    len_matched_regions = len(instance_ids_by_region.keys())
    info(
        f"found {len_matched_regions} {'region' if len_matched_regions == 1 else 'regions'} with match: {instance_ids_by_region}"
    )
