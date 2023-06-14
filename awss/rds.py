from logging import info, warning
from .lib import perf_time, multithreaded


@multithreaded
def list_rds(session, region, print_lock):
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

        len_db_names = len(db_names)
        with print_lock:
            if len_db_names > 0:
                info(
                    f"region: {region}\n\tfound {len_db_names} {'database' if len_db_names == 1 else 'databases'}:\n\t\t"
                    + "\n\t\t".join(db_names)
                )
            else:
                info(f"no databases found in {region}")
    except Exception as e:
        with print_lock:
            warning(f"in {region}: {e}")


@perf_time
def list_rds_instances(session, workers, regions, print_lock):
    info(
        f"searching {len(regions)} aws regions with {workers} workers for rds clusters or instances..."
    )
    inputs = [(session, region, print_lock) for region in regions]

    list_rds(inputs, workers)
