""" ---------------------------- EC2 Settings ---------------------------- """
AMI_AML = 'ami-0ded8326293d3201b'
SCRIPT_PATH = 'script.sh'
INSTANCE_MICRO = 't2.micro'
SECURITY_GROUP_IDS = ['sg-0016c71b27fedaa68']
SECURITY_GROUPS = ['launch-wizard-2']
INSTANCE_PROFILE_ARN = 'arn:aws:iam::202783468510:instance-profile/EC2_S3'
INSTANCE_PROFILE_NAME = 'EC2_S3'
SSH_KEY = 'arch-key'
VPC = 'vpc-0ecc7c41a0b92665d'
SUBNET = 'subnet-02b11a18a3a7dfd0e'
""" ---------------------------- EC2 Settings ---------------------------- """

BUCKET_NAME = 'thedarksoul'

""" ---------------------------- Database Settings ---------------------------- """
DB_NAME = 'abyss'
DB_INSTANCE_IDENTIFIER = 'abyssDB'
DB_INSTANCE_CLASS = 'db.t3.micro'
DB_ENGINE = 'mariadb'
DB_ENGINE_VERSION = '10.11.4'
DB_USERNAME = 'abysswalker'
DB_PASSWORD = 'Qwerty123'
DB_SUBNET_ZONE = 'default-vpc-0ecc7c41a0b92665d'
AVAILABILITY_ZONE = 'ap-south-1a'
""" ---------------------------- Database Settings ---------------------------- """

""" ---------------------------- CloudFront Settings ---------------------------- """
TARGET_ID = 'portfolio-cdn'
CALLER_REFERENCE = 'excalibur'
CF_DESCRIPTION = 'CDN for portfolio'
DOMAIN_NAME = 'thedarksoul.s3.ap-south-1.amazonaws.com'
CACHE_POLICY_ID = '658327ea-f89d-4fab-a63d-7e88639e58f6'
VIEWER_PROTOCOL = 'allow-all'
""" ---------------------------- CloudFront Settings ---------------------------- """

""" ---------------------------- Beanstalk Settings ---------------------------- """
APP_NAME = 'portfolio'
APP_DESCRIPTION = 'My portfolio website app.'
APP_VERSION = 'V1'
S3_KEY = 'portfolio.zip'

BREACH_DURATION = '1'
STATISTIC = 'Average'
UNIT = 'Percent'
EVALUATION_PERIOD = '1'
PERIOD = '1'
MEASURE_NAME = 'CPUUtilization'
LOWER_THRESHOLD = '20'
UPPER_THRESHOLD = '80'

CNAME = 'devrishabh28-portfolio'
ENVIRONMENT_NAME = 'lordran'
ENVIRONMENT_ROLE = 'arn:aws:iam::202783468510:role/EC2_S3'
SOLUTION_STACK = '64bit Amazon Linux 2023 v6.0.0 running Node.js 18'
AVAILABILITY_ZONES = 'Any 2'
MIN_SIZE = '1'
MAX_SIZE = '3'
ENVIRONMENT_SETTINGS = [
    {
        'Namespace': 'aws:autoscaling:launchconfiguration',
        'OptionName': 'IamInstanceProfile',
        'Value': INSTANCE_PROFILE_NAME
    },
    {
        'Namespace': 'aws:autoscaling:launchconfiguration',
        'OptionName': 'InstanceType',
        'Value': INSTANCE_MICRO
    },
    {
        'Namespace': 'aws:autoscaling:launchconfiguration',
        'OptionName': 'EC2KeyName',
        'Value': SSH_KEY 
    },
    {
        'Namespace': 'aws:autoscaling:launchconfiguration',
        'OptionName': 'ImageId',
        'Value': AMI_AML
    },
    {
        'Namespace': 'aws:autoscaling:launchconfiguration',
        'OptionName': 'SecurityGroups',
        'Value': 'sg-0016c71b27fedaa68'
    },
    {
        'Namespace': 'aws:ec2:vpc',
        'OptionName': 'VPCId',
        'Value': VPC
    },
    {
        'Namespace': 'aws:ec2:vpc',
        'OptionName': 'Subnets',
        'Value': SUBNET
    },
    {
        'Namespace': 'aws:elasticbeanstalk:environment',
        'OptionName': 'ServiceRole',
        'Value': ENVIRONMENT_ROLE
    },


    {
        'Namespace': 'aws:autoscaling:trigger',
        'OptionName': 'BreachDuration',
        'Value': BREACH_DURATION 
    }, 
    {
        'Namespace': 'aws:autoscaling:trigger',
        'OptionName': 'Statistic',
        'Value': STATISTIC
    },
    {
        'Namespace': 'aws:autoscaling:trigger',
        'OptionName': 'Unit',
        'Value': UNIT 
    },
    {
        'Namespace': 'aws:autoscaling:trigger',
        'OptionName': 'EvaluationPeriods',
        'Value': EVALUATION_PERIOD 
    },
    {
        'Namespace': 'aws:autoscaling:trigger',
        'OptionName': 'Period',
        'Value': PERIOD 
    },
    {
        'Namespace': 'aws:autoscaling:trigger',
        'OptionName': 'MeasureName',
        'Value': MEASURE_NAME
    },
    {
        'Namespace': 'aws:autoscaling:trigger',
        'OptionName': 'LowerThreshold',
        'Value': LOWER_THRESHOLD 
    },
    {
        'Namespace': 'aws:autoscaling:trigger',
        'OptionName': 'LowerBreachScaleIncrement',
        'Value': '-1'
    },
    {
        'Namespace': 'aws:autoscaling:trigger',
        'OptionName': 'UpperThreshold',
        'Value': UPPER_THRESHOLD 
    },
    {
        'Namespace': 'aws:autoscaling:trigger',
        'OptionName': 'UpperBreachScaleIncrement',
        'Value': '1'
    },
    {
        'Namespace': 'aws:autoscaling:asg',
        'OptionName': 'Availability Zones',
        'Value': AVAILABILITY_ZONES
    },
    {
        "Namespace": "aws:autoscaling:asg",
        "OptionName": "MinSize",
        "Value": MIN_SIZE,
    },
    {
        "Namespace": "aws:autoscaling:asg",
        "OptionName": "MaxSize",
        "Value": MAX_SIZE,
    },

]
""" ---------------------------- Beanstalk Settings ---------------------------- """