import boto3
from threading import Lock
from logging import basicConfig, INFO, DEBUG, info
from click import option, group, pass_context  # , Choice
from .rds import list_rds_instances
from .ec2 import find_instances_by_ami_owner
from .sts import check_credentials
from .acm import list_all_acm
from .lib import get_all_regions

print_lock = Lock()


@group()
@option("--profile", "-p", help="AWS profile to use")
@option("--workers", "-w", type=int, default=4, help="Number of workers")
@option("--debug", "-d", is_flag=True, help="Enable debug logging")
@pass_context
def cli(ctx, profile, workers, debug):
    ctx.obj = {}

    if profile:
        ctx.obj["session"] = boto3.Session(profile_name=profile)
    else:
        ctx.obj["session"] = boto3.Session()

    ctx.obj["workers"] = workers

    basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=DEBUG if debug else INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    id_arn = ctx.obj["session"].client("sts").get_caller_identity()["Arn"]
    info(f"using profile {ctx.obj['session'].profile_name} ({id_arn})")
    ctx.obj["regions"] = get_all_regions(ctx.obj["session"])


@cli.command("show-regions", help="Show all available regions")
@pass_context
def regions(ctx):
    info(ctx.obj["regions"])


# RDS COMMANDS


@cli.group(help="RDS commands")
@pass_context
def rds(ctx):
    pass


@rds.command("list", help="List all RDS instance and cluster names")
@pass_context
def list_instances(ctx):
    list_rds_instances(
        ctx.obj["session"], ctx.obj["workers"], ctx.obj["regions"], print_lock
    )


# Certificate Manager COMMANDS


@cli.group(help="Certificate Manager commands")
@pass_context
def acm(ctx):
    pass


@acm.command("list", help="List all ACM certificates and their names")
@option(
    "--filter",
    "-f",
    help="Filter certificates by name regex, enclose argument in single quotes",
)
@pass_context
def list_certificates(ctx, filter):
    list_all_acm(
        ctx.obj["session"], ctx.obj["workers"], ctx.obj["regions"], filter, print_lock
    )


# EC2 COMMANDS


@cli.group(help="EC2 commands")
@pass_context
def ec2(ctx):
    pass


@ec2.command(
    "ami-instances",
    help="Find ec2 instances running an ami owned by the specified owner ID where the ami name matches the specified filter",
)
@pass_context
# defaults find ubuntu 18.04 instances
@option("--owner-id", "-o", help="AMI owner ID, example: '099720109477' (Canonical)")
@option(
    "--ami-name-filter",
    "-n",
    help="AMI name filter, to supply wildcards enclose the argument in single quotes, example: '*18.04*'",
)
def ami_instances(ctx, owner_id, ami_name_filter):
    find_instances_by_ami_owner(
        ctx.obj["session"],
        ctx.obj["workers"],
        ctx.obj["regions"],
        print_lock,
        owner_id,
        ami_name_filter,
    )


# ECR COMMANDS


@cli.command()
@pass_context
def ecr(ctx):
    raise NotImplementedError


# STS COMMANDS


@cli.group(help="STS commands")
@pass_context
def sts(ctx):
    pass


@sts.command("check", help="Check if the current session is valid in all regions")
@pass_context
def check(ctx):
    check_credentials(
        ctx.obj["session"], ctx.obj["workers"], ctx.obj["regions"], print_lock
    )


if __name__ == "__main__":
    cli()
