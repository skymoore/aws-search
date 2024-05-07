from logging import info
from .lib import perf_time, multithreaded
from pprint import PrettyPrinter


@multithreaded
def list_acm_certificates(session, region, filter, print_lock, pp):
    client = session.client("acm", region_name=region)
    paginator = client.get_paginator("list_certificates")

    certificate_list = []
    for response in paginator.paginate():
        for certificate in response["CertificateSummaryList"]:
            domain_name = certificate["DomainName"]
            altnames = (
                [name for name in certificate["SubjectAlternativeNameSummaries"]]
                if "SubjectAlternativeNameSummaries" in certificate
                else []
            )
            domain_names = [domain_name] + altnames
            if filter and any([True for name in domain_names if filter in name]):
                certificate_list.append(
                    {
                        "DomainNames": domain_names,
                        "CertificateArn": certificate["CertificateArn"],
                    }
                )
            elif filter:
                continue
            else:
                certificate_list.append(
                    {
                        "DomainNames": domain_names,
                        "CertificateArn": certificate["CertificateArn"],
                    }
                )

    len_certificate_list = len(certificate_list)
    if len_certificate_list > 0:
        with print_lock:
            info(
                f"found {len_certificate_list} {'certificate' if len_certificate_list == 1 else 'certificates'} in {region}{':' if len_certificate_list > 0 else ''}"
            )
            pp.pprint(certificate_list)


@perf_time
def list_all_acm(session, workers, regions, filter, print_lock):
    info(
        f"listing all ACM certificates in {len(regions)} aws regions with {workers} {'worker' if workers == 1 else 'workers'}..."
    )

    pp = PrettyPrinter(indent=4)
    inputs = [(session, region, filter, print_lock, pp) for region in regions]

    list_acm_certificates(inputs, workers)
