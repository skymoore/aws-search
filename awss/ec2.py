from time import perf_counter
from logging import info, error, warning
from .lib import get_regions, perf_time, multithreaded


def get_ami_ids_by_owner(session, region, owner_id, name_filter, print_lock):
    ec2 = session.client("ec2", region_name=region)
    ami_ids = {}
    filter = [
        {
            "Name": "name",
            "Values": [name_filter],
        }
    ]
    owner_id = [owner_id]

    response = ec2.describe_images(
        Owners=owner_id,
        Filters=filter,
    )
    for ami in response["Images"]:
        ami_ids[ami["ImageId"]] = ""

    while "NextToken" in response:
        response = ec2.describe_images(
            Owners=owner_id,
            Filters=filter,
            NextToken=response["NextToken"],
        )
        for ami in response["Images"]:
            ami_ids[ami["ImageId"]] = ""

    with print_lock:
        info(f"{len(ami_ids.keys())} amis owned by {owner_id[0]} in region {region}")
    return ami_ids


@multithreaded
def find_instances(
    session, region, print_lock, owner_id, name_filter, instance_ids_by_region
):
    try:
        ec2_resource = session.resource("ec2", region_name=region)
        instances = ec2_resource.instances.all()
        num_instances = len(list(instances))

        if num_instances == 0:
            with print_lock:
                info(f"no ec2 instances found in region {region}")
            return
        with print_lock:
            info(f"{num_instances} ec2 instances in region {region}")
        ami_ids = get_ami_ids_by_owner(
            session, region, owner_id, name_filter, print_lock
        )

        found_instance = False
        for instance in instances:
            try:
                if instance.image_id in ami_ids:
                    found_instance = True
                    if region not in instance_ids_by_region:
                        instance_ids_by_region[region] = [instance.id]
                    else:
                        instance_ids_by_region[region].append(instance.id)
                    with print_lock:
                        info(
                            f"matching instance in region {region} with ID: {instance.id}"
                        )
            except Exception as e:
                with print_lock:
                    error(f"{instance.id}: {e}")
                continue

        if not found_instance:
            with print_lock:
                info(f"no matching instances found in region {region}")
        else:
            with print_lock:
                info(
                    f"{len(instance_ids_by_region[region])} matching instances found in region {region}"
                )

    except Exception as e:
        with print_lock:
            warning(f"{region}: {e}")


@perf_time
def find_instances_by_ami_owner(session, workers, print_lock, owner_id, name_filter):
    regions = get_regions(session, "ec2")
    info(
        f"searching {len(regions)} aws regions with {workers} workers for ec2 instances running an ami owned by {owner_id} whose name matches {name_filter}..."
    )
    instance_ids_by_region = {}
    inputs = [
        (session, region, print_lock, owner_id, name_filter, instance_ids_by_region)
        for region in regions
    ]
    find_instances(inputs, workers)
    info(
        f"found {len(instance_ids_by_region)} regions with matching instances: {instance_ids_by_region}"
    )
