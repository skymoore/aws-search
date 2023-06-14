from logging import info
from time import perf_counter
import concurrent.futures


def get_all_regions(session):
    info("getting available regions...")
    return [
        region["RegionName"]
        for region in session.client("ec2").describe_regions()["Regions"]
    ]


def multithreaded(func):
    def wrapper(inputs, workers):
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            executor.map(lambda params: func(*params), inputs)

    return wrapper


def perf_time(func):
    def wrapper(*args, **kwargs):
        start_time = perf_counter()
        result = func(*args, **kwargs)
        end_time = perf_counter()
        info(f"{func.__name__} executed in {end_time - start_time:.2f}s")
        return result

    return wrapper
