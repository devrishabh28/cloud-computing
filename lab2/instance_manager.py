import sys
import boto3 as bt
from botocore.exceptions import ClientError

if __name__ == '__main__':

    AMI_ID = 'ami-0ded8326293d3201b'
    SCRIPT_PATH = 'sync.sh'
    INSTANCE_TYPE = 't2.micro'
    SECURITY_GROUP_IDS = ['sg-0016c71b27fedaa68']
    SECURITY_GROUPS = ['launch-wizard-2']
    INSTANCE_PROFILE_ARN = 'arn:aws:iam::202783468510:instance-profile/EC2_S3'
    INSTANCE_PROFILE_NAME = 'EC2_S3'
    SSH_KEY = 'arch-key'

    ec2 = bt.client('ec2')

    try:
        with open(SCRIPT_PATH, 'r') as f:
            script = '\n'.join(f)
            response = ec2.run_instances(
                ImageId=AMI_ID,
                InstanceType=INSTANCE_TYPE,
                MinCount=1,
                MaxCount=1,
                IamInstanceProfile={
                    'Arn': INSTANCE_PROFILE_ARN
                },
                SecurityGroupIds=SECURITY_GROUP_IDS,
                SecurityGroups=SECURITY_GROUPS,
                KeyName=SSH_KEY,
                UserData=script
            )
    except ClientError as err:
        print("error creating ec2 instance!")
        print(err)

print('created ec2 instance successfully!')
INSTANCE_ID = response['Instances'][0]['InstanceId']

ec2_resource = bt.resource('ec2')

while ec2_resource.Instance(INSTANCE_ID).state['Name'] != 'running':
    pass

print(f'ec2 instance {INSTANCE_ID} running!')
print(
    f"Public DNS: {ec2.describe_instances(InstanceIds=[INSTANCE_ID])['Reservations'][0]['Instances'][0]['PublicDnsName']}")
