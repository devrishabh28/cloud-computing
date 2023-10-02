import sys
from time import sleep
import boto3 as bt
from botocore.exceptions import ClientError
import helpers as hp

def create_instance(image_id, instance_type, security_groups_ids, security_groups, key_name, script=""):
    ec2 = bt.client('ec2')
    try:
        response = ec2.run_instances(
            ImageId=image_id,
            InstanceType=instance_type,
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

    print(f'created ec2 {instance_type} instance successfully!')
    INSTANCE_ID = response['Instances'][0]['InstanceId']

    return INSTANCE_ID

if __name__ == '__main__':

    commands = {
                'create':create_instance,
                'list': hp.list_running_instances,
                'health': hp.health_checkup,
                'stop': hp.stop_running_instances,
                'terminate': hp.terminate_running_instances
                }
    
    command = sys.argv[1]

    

    if len(sys.argv) < 1 or sys.argv[1] not in commands:
        print('invalid command! usage: python helpers.py <create | list | health | stop | terminate>')
        exit()

    if command == 'create':
        AMI_AML = 'ami-0ded8326293d3201b'
        AMI_UBT = 'ami-0f5ee92e2d63afc18'
        SCRIPT_PATH = 'sync.sh'
        INSTANCE_MICRO = 't2.micro'
        INSTANCE_NANO = 't2.nano'
        SECURITY_GROUP_IDS = ['sg-0016c71b27fedaa68']
        SECURITY_GROUPS = ['launch-wizard-2']
        INSTANCE_PROFILE_ARN = 'arn:aws:iam::202783468510:instance-profile/EC2_S3'
        INSTANCE_PROFILE_NAME = 'EC2_S3'
        SSH_KEY = 'arch-key'

        script = ''

        INSTANCE_IDS = []

        with open('sync.sh') as f:
            script = '\n'.join(f)
            INSTANCE_IDS.append(create_instance(AMI_AML, INSTANCE_MICRO, SECURITY_GROUP_IDS, SECURITY_GROUPS, SSH_KEY, script))

        INSTANCE_IDS.append(create_instance(AMI_UBT, INSTANCE_NANO, SECURITY_GROUP_IDS, SECURITY_GROUPS, SSH_KEY))
        INSTANCE_IDS.append(create_instance(AMI_UBT, INSTANCE_NANO, SECURITY_GROUP_IDS, SECURITY_GROUPS, SSH_KEY))

        ec2 = bt.client('ec2')
        ec2_resource = bt.resource('ec2')

        running = False

        while not running:
            print('waiting for instances to run')
            running = True
            for instance_id in INSTANCE_IDS:
                if ec2_resource.Instance(instance_id).state['Name'] != 'running':
                    running = False
            sleep(2)

        print()
        print('---------------------------------------------------------------------------------')
        for INSTANCE_ID in INSTANCE_IDS:
            print(f'ec2 instance {INSTANCE_ID} running!')
        print('---------------------------------------------------------------------------------')

        hp.list_running_instances()       
    
    else:
        commands[command]()
