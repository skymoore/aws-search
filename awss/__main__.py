import boto3
from threading import Lock
from logging import basicConfig, INFO, DEBUG, info
from click import option, group, pass_context #, Choice
from .rds import list_rds_instances
from .ec2 import find_instances_by_ami_owner

print_lock = Lock()

@group()
@option('--profile', '-p', default="dev-adm", help='AWS profile to use')
@option("--workers", "-w", type=int, default=4, help="Number of workers")
@option("--debug", "-d", is_flag=True, help="Enable debug logging")
@pass_context
def cli(ctx, profile, workers, debug):
    ctx.obj = {}
    ctx.obj["session"] = boto3.Session(profile_name=profile)
    ctx.obj["workers"] = workers

    basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=DEBUG if debug else INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    id_arn = ctx.obj["session"].client('sts').get_caller_identity()["Arn"]
    info(f"using profile {ctx.obj['session'].profile_name} ({id_arn})")


@cli.group(help="RDS commands")
@pass_context
def rds(ctx):
    pass

@rds.command("list", help="List all RDS instance and cluster names")
@pass_context
def list_instances(ctx):
    list_rds_instances(ctx.obj["session"], ctx.obj["workers"], print_lock)

@cli.group(help="EC2 commands")
@pass_context
def ec2(ctx):
    pass

@ec2.command("ami-instances", help="Find ec2 instances running an ami owned by the specified owner ID where the ami name matches the specified filter")
@pass_context
# defaults find ubuntu 18.04 instances
@option("--owner-id", "-o", help="AMI owner ID, example: '099720109477' (Canonical)")
@option("--ami-name-filter", "-n", help="AMI name filter, to supply wildcards enclose the argument in single quotes, example: '*18.04*'")
def ami_instances(ctx, owner_id, ami_name_filter):
    find_instances_by_ami_owner(
        ctx.obj["session"],
        ctx.obj["workers"],
        owner_id,
        ami_name_filter,
        print_lock
    )


@cli.command()
@pass_context
def ecr(ctx):
    raise NotImplementedError

    
