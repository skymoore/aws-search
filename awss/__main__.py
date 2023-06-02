import boto3
from threading import Lock
from logging import basicConfig, INFO, DEBUG, info
from click import option, group, pass_context #, Choice
from .lib import list_rds_instances

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


@cli.command()
@pass_context
def rds(ctx):
    list_rds_instances(ctx.obj["session"], ctx.obj["workers"], print_lock)


@cli.command()
@pass_context
def ec2(ctx):
    raise NotImplementedError


@cli.command()
@pass_context
def ecr(ctx):
    raise NotImplementedError

    
