from logging import info, warning
from .lib import get_regions, perf_time, multithreaded


@multithreaded
def check_creds(session, region, print_lock, success, failure):
    try:
        sts = session.client("sts", region_name=region)
        sts.get_caller_identity()
        success.append(region)
        with print_lock:
            info(f"credentials ok in {region}")
    except Exception as e:
        failure.append(region)
        with print_lock:
            warning(f"credentials failure in {region}: {e}")


@perf_time
def check_credentials(session, workers, print_lock):
    regions = get_regions(session, "sts")
    info(
        f"checking credentials in {len(regions)} aws regions with {workers} workers..."
    )
    success = []
    failure = []
    inputs = [(session, region, print_lock, success, failure) for region in regions]

    check_creds(inputs, workers)

    info(f"credentials ok in {len(success)} regions: {success}")
    info(f"credentials failure in {len(failure)} regions: {failure}")
