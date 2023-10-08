AWS_REGION = 'ap-south-1'
AMI_AML = 'ami-0ded8326293d3201b'
SCRIPT_PATH = 'script.sh'
INSTANCE_MICRO = 't2.micro'
SUBNET_IDS = ['subnet-02b11a18a3a7dfd0e', 'subnet-0bf1c768c5554388e']
SECURITY_GROUP_IDS = ['sg-0016c71b27fedaa68']
SECURITY_GROUPS = ['launch-wizard-2']
INSTANCE_PROFILE_ARN = 'arn:aws:iam::202783468510:instance-profile/ecsInstanceRole'
INSTANCE_PROFILE_NAME = 'ecsInstanceRole'
SSH_KEY = 'arch-key'

BUCKET_NAME = 'thedarksoul'

DB_NAME = 'abyss'
DB_INSTANCE_IDENTIFIER = 'abyss'
DB_INSTANCE_CLASS = 'db.t3.micro'
DB_ENGINE = 'mariadb'
DB_ENGINE_VERSION = '10.11.4'
DB_USERNAME = 'abysswalker'
DB_PASSWORD = 'Qwerty123'
DB_SUBNET_ZONE = 'default-vpc-0ecc7c41a0b92665d'
AVAILABILITY_ZONE = 'ap-south-1a'



AMI_ID = 'ami-01fc890789da0c85a' 
INSTANCE_TYPE = INSTANCE_MICRO
TARGET_GROUPS = ['arn:aws:elasticloadbalancing:ap-south-1:202783468510:targetgroup/entropy/763a603b5418676a']
AUTOSCALING_AVAILABILITY_ZONE = 'subnet-02b11a18a3a7dfd0e'

SKILLS_REPOSITORY_NAME = 'portfolio/skills'
SKILLS_DIRECTORY = '/home/abysswalker/sem-5/it-workshop/lab8/application/skills/'
SKILLS_CLUSTER_NAME = 'skills-cluster'
SKILLS_TASK_FAMILY = 'skills-task-family'
SKILLS_API_NAME = 'skills'
SKILLS_PROVIDER_NAME = 'skills-provider'
SKILLS_CONTAINER_PORT = 8080
SKILLS_LAUNCH_TEMPLATE_NAME = 'skills-template'
SKILLS_VERSION_DESCRIPTION = 'V1'
SKILLS_AUTOSCALING_GROUP_NAME = 'skills-autoscale'
SKILLS_LAUNCH_VERSION = '$Latest'

EDUCATION_REPOSITORY_NAME = 'portfolio/education'
EDUCATION_DIRECTORY = '/home/abysswalker/sem-5/it-workshop/lab8/application/education/'
EDUCATION_CLUSTER_NAME = 'education-cluster'
EDUCATION_TASK_FAMILY = 'education-task-family'
EDUCATION_API_NAME = 'education'
EDUCATION_PROVIDER_NAME = 'education-provider'
EDUCATION_CONTAINER_PORT = 8080
EDUCATION_LAUNCH_TEMPLATE_NAME = 'education-template'
EDUCATION_VERSION_DESCRIPTION = 'V1'
EDUCATION_AUTOSCALING_GROUP_NAME = 'education-autoscale'
EDUCATION_LAUNCH_VERSION = '$Latest'

COMMENTS_REPOSITORY_NAME = 'portfolio/comments'
COMMENTS_DIRECTORY = '/home/abysswalker/sem-5/it-workshop/lab8/application/comments/'
COMMENTS_CLUSTER_NAME = 'comments-cluster'
COMMENTS_TASK_FAMILY = 'comments-task-family'
COMMENTS_API_NAME = 'comments'
COMMENTS_PROVIDER_NAME = 'comments-provider'
COMMENTS_CONTAINER_PORT = 8080
COMMENTS_LAUNCH_TEMPLATE_NAME = 'comments-template'
COMMENTS_VERSION_DESCRIPTION = 'V1'
COMMENTS_AUTOSCALING_GROUP_NAME = 'comments-autoscale'
COMMENTS_LAUNCH_VERSION = '$Latest'

PORTFOLIO_REPOSITORY_NAME = 'portfolio'
PORTFOLIO_DIRECTORY = '/home/abysswalker/sem-5/it-workshop/lab8/application/portfolio/'
PORTFOLIO_CLUSTER_NAME = 'portfolio-cluster'
PORTFOLIO_TASK_FAMILY = 'portfolio-task-family'
PORTFOLIO_API_NAME = 'portfolio'
PORTFOLIO_PROVIDER_NAME = 'portfolio-provider'
PORTFOLIO_CONTAINER_PORT = 8080
PORTFOLIO_LAUNCH_TEMPLATE_NAME = 'portfolio-template'
PORTFOLIO_VERSION_DESCRIPTION = 'V1'
PORTFOLIO_AUTOSCALING_GROUP_NAME = 'portfolio-autoscale'
PORTFOLIO_LAUNCH_VERSION = '$Latest'


API_NAME = 'eclipse'
API_DESCRIPTION = 'An API for portfolio microservices'
STAGE_NAME = 'prod'

HTTP_GET= 'GET'
HTTP_POST = 'POST'

SKILL_PATH_PART = 'skills'
SKILL_URI = 'http://ec2-13-232-3-243.ap-south-1.compute.amazonaws.com/'

EDUCATION_PATH_PART = 'education'
EDUCATION_URI = 'http://ec2-13-127-105-226.ap-south-1.compute.amazonaws.com/'

COMMENTS_PATH_PART = 'comments'
COMMENTS_URI = 'http://ec2-43-205-236-121.ap-south-1.compute.amazonaws.com/'