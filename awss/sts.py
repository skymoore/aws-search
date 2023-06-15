from logging import info, warning
from .lib import perf_time, multithreaded


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
def check_credentials(session, workers, regions, print_lock):
    info(
        f"checking credentials in {len(regions)} aws regions with {workers} {'worker' if workers == 1 else 'workers'}..."
    )
    success = []
    failure = []
    inputs = [(session, region, print_lock, success, failure) for region in regions]

    check_creds(inputs, workers)

    len_success = len(success)
    len_failure = len(failure)
    info(
        f"credentials ok in {len_success} {'region' if len_success == 1 else 'regions'}: {success}"
    )
    info(
        f"credentials failure in {len_failure} {'region' if len_failure == 1 else 'regions'}: {failure}"
    )
