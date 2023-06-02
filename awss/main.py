from os import environ
from time import perf_counter
import boto3
import concurrent.futures
from threading import Lock
from logging import basicConfig, info, debug, INFO, DEBUG
from click import option, group, Choice


print_lock = Lock()

basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

@group()
def cli():
    pass


@cli.command()
@option("--workers", "-w", type=int, default=8, help="Number of workers")
def rds(workers):
    session = boto3.Session(profile_name=environ.get("AWS_PROFILE", "dev-adm"))
    list_rds_instances(session, workers)


@cli.command()
@option("--workers", "-w", type=int, default=8, help="Number of workers")
def ec2(workers):
    raise NotImplementedError


@cli.command()
@option("--workers", "-w", type=int, default=8, help="Number of workers")
def ecr(workers):
    raise NotImplementedError


def list_rds_instances(session, workers):
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
    info(f"execution time: {end - start:.2f}s")


def get_regions(session, service):
    info("getting regions...")
    return session.get_available_regions(service)
    
