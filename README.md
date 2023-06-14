## Multi-Region Multi-Threaded AWS Search Tool

### Usage Examples:

#### RDS:
list rds instances in every region
```
awss rds list
```

#### EC2:
find any ec2 instances running a specific eks version
```
awss -w 27 -p dev ec2 ami-instances -o 602401143452 -n amazon-eks-node-1.24-v2023030
```
find any ec2 instances running ubuntu 18.04
```
awss -w 27 -p dev-adm ec2 ami-instances -o 099720109477 -n '*18.04*'
```

#### STS:
check which regions aws credentials work in
```
awss -w 27 sts check
```