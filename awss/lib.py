import concurrent.futures
from time import perf_counter
from logging import info, debug

def get_regions(session, service):
    info("getting regions...")
    return session.get_available_regions(service)

def list_rds_instances(session, workers, print_lock):
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

            with print_lock:
                if len(db_names) > 0:
                    info(
                        f"region: {region}\n\tfound {len(db_names)} databases:\n\t\t"
                        + "\n\t\t".join(db_names)
                    )
                else:
                    info(f"no databases found in {region}")
        except Exception as e:
            with print_lock:
                debug(f"in {region}: {e}")

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
