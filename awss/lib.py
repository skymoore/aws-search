import concurrent.futures
from time import perf_counter
from logging import info, debug, error, warning

def get_regions(session, service):
    info("getting regions...")
    return session.get_available_regions(service)

def list_rds_instances(session, workers, info_lock):
    def list_rds(session, region):
        try:
            rds = session.client("rds", region_name=region)
            db_names = list()
            db_names.extend(
                [
                    instance["DBInstanceIdentifier"]
                    for instance in rds.describe_db_instances()["DBInstances"]
                ]
            )
            db_names.extend(
                [
                    cluster["DBClusterIdentifier"]
                    for cluster in rds.describe_db_clusters()["DBClusters"]
                ]
            )

            with info_lock:
                if len(db_names) > 0:
                    info(
                        f"region: {region}\n\tfound {len(db_names)} databases:\n\t\t"
                        + "\n\t\t".join(db_names)
                    )
                else:
                    info(f"no databases found in {region}")
        except Exception as e:
            with info_lock:
                warning(f"in {region}: {e}")

    start = perf_counter()
    regions = get_regions(session, "rds")
    info(
        f"searching {len(regions)} aws regions with {workers} workers for rds clusters or instances..."
    )
    inputs = [(session, region) for region in regions]

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        executor.map(lambda params: list_rds(*params), inputs)
    
    end = perf_counter()
    info(f"list_rds_instances() execution time: {end - start:.2f}s")


def get_ami_ids_by_owner(session, region, owner_id, name_filter):
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

    info(f"{len(ami_ids.keys())} amis owned by {owner_id[0]} in region {region}")
    return ami_ids

def find_instances_by_ami_owner(session, workers, owner_id, name_filter):
    def find_instances(session, region, owner_id, name_filter):
        try:
            ec2_resource = session.resource("ec2", region_name=region)
            instances = ec2_resource.instances.all()
            num_instances = len(list(instances))

            if num_instances == 0:
                info(f"no ec2 instances found in region {region}")
                return

            info(f"{num_instances} ec2 instances in region {region}")
            ami_ids = get_ami_ids_by_owner(session, region, owner_id, name_filter)

            found_instance = False
            matches = []
            for instance in instances:

                try:
                    if instance.image_id in ami_ids:
                        found_instance = True
                        matches.append(instance.id)
                        info(
                            f"matching instance in region {region} with ID: {instance.id}"
                        )
                except Exception as e:
                    error(f"{instance.id}: {e}")
                    continue

            if not found_instance:
                info(f"no matching instances found in region {region}")
            else:
                info(f"{len(matches)} matching instances found in region {region}")

        except Exception as e:
            warning(f"{region}: {e}")
    
    start = perf_counter()
    regions = get_regions(session, "ec2")
    info(
        f"searching {len(regions)} aws regions with {workers} workers for ec2 instances running an ami owned by {owner_id} whose name matches {name_filter}..."
    )
    inputs = [(session, region, owner_id, name_filter) for region in regions]

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        executor.map(lambda params: find_instances(*params), inputs)
    
    end = perf_counter()
    info(f"find_instances_by_ami_owner() execution time: {end - start:.2f}s")