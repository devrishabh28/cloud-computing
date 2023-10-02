import sys
import os
import boto3 as bt
from botocore.exceptions import ClientError
from time import sleep

#  This function updates connection information in node.js application.
def updateConnection(hostname, user, password, db):

    connectionTemplate = '../portfolio/models/connectionTemplate.js'
    connection = '../portfolio/models/connection.js'

    os.system(f'cat {connectionTemplate} > {connection}')

    os.system(f'sed -i s/HOSTNAME/{hostname}/ {connection}')
    os.system(f'sed -i s/USER/{user}/ {connection}')
    os.system(f'sed -i s/PASSWORD/{password}/ {connection}')
    os.system(f'sed -i s/DB/{db}/ {connection}')

    print('db connection information updated successfully...')

#  This function uplodes the application to S3 bucket.
def upload(bucket_name, verbose=True):
    s3 = bt.client('s3')

    if verbose:
        print('\n-----------------------------------------------------------------------------------')
        print(f'\tperforming upload files to bucket {bucket_name}...')
        print('-----------------------------------------------------------------------------------')
    else:
        print(f'performing upload files to bucket {bucket_name}...')

    for root, dirs, files in os.walk('../portfolio'):

        if 'node_modules' in root:
            continue

        for filename in files:
            
            #  Construct full local path
            local_path = os.path.join(root, filename)

            #  Construct full path
            relative_path = os.path.relpath(local_path, '../portfolio')
            s3_path = os.path.join('portfolio', relative_path)

            if verbose:
                print(f'Searching {s3_path} in {bucket_name}')
            
            try:
                s3.head_object(Bucket=bucket_name, Key=s3_path)
                if verbose:
                    print(f'Path found on S3! overwriting {s3_path}...')
                s3.upload_file(local_path, bucket_name, s3_path)

            except:
                if verbose:
                    print(f'Uploading {s3_path}...')
                s3.upload_file(local_path, bucket_name, s3_path)

    if verbose:
        print('\n-----------------------------------------------------------------------------------')
        print(f'\tsuccessfully uploaded files to bucket {bucket_name}...')
        print('-----------------------------------------------------------------------------------')
    else:
        print(f'successfully uploaded files to bucket {bucket_name}...')

#  This function creates an instance.
def create_instance(image_id, instance_type, iam_profile_arn, security_groups_ids, security_groups, key_name, script=""):
    ec2 = bt.client('ec2')
    try:
        response = ec2.run_instances(
            ImageId=image_id,
            InstanceType=instance_type,
            MinCount=1,
            MaxCount=1,
            IamInstanceProfile={
                'Arn': iam_profile_arn
            },
            SecurityGroupIds=security_groups_ids,
            SecurityGroups=security_groups,
            KeyName=key_name,
            UserData=script
        )
    except ClientError as err:
        print("error creating ec2 instance!")
        print(err)

    print(f'created ec2 {instance_type} instance successfully!')
    INSTANCE_ID = response['Instances'][0]['InstanceId']

    return INSTANCE_ID

#  This function creates an RDS instance.
def create_database(db_name, db_instance_identifier, db_instance_class, engine, engine_version, user_name, password, security_groups_id, db_subnet_group_name, availability_zone, allocated_storage = 20):

    rds = bt.client('rds')
    
    try:

        try: 
            rds.describe_db_instances(DBInstanceIdentifier = db_instance_identifier)['DBInstances']
            print(f'database {db_name} instance already exists!')
        except:
            response = rds.create_db_instance(
                DBName = db_name,
                DBInstanceIdentifier = db_instance_identifier,
                DBInstanceClass = db_instance_class,
                Engine = engine,
                EngineVersion = engine_version,
                MasterUsername = user_name,
                MasterUserPassword = password,
                VpcSecurityGroupIds = security_groups_id,
                DBSubnetGroupName = db_subnet_group_name,
                AvailabilityZone = availability_zone,
                AllocatedStorage = allocated_storage,
                Port=3306,
                PubliclyAccessible=False
            )

            print(f'created RDS {db_instance_class} instance successfully!')

        step = 1

        while True:
            print(f'trying to get hostname of database ({step})...')
            instance = rds.describe_db_instances(DBInstanceIdentifier = db_instance_identifier)['DBInstances'][0]

            if 'Endpoint' not in instance.keys():
                step += 1
                sleep(5)
                continue

            hostname = instance['Endpoint']['Address']
            print('database hostname found...')
            break

        return hostname
    except ClientError as err:
        print("error creating rds instance!")
        print(err)

#  This function displays stats for an instance.
def instance_stats(instance_id):
    ec2 = bt.resource('ec2')

    step = 1
    while ec2.Instance(instance_id).state['Name'] != 'running':
        print(f'waiting for instance to start ({step})...')
        step += 1
        sleep(2)

    instances = ec2.instances.filter(InstanceIds = [instance_id])

    instance_ids = [instance.instance_id for instance in instances] 

    print()
    
    for instance, status in zip(instances, ec2.meta.client.describe_instance_status(InstanceIds=instance_ids)['InstanceStatuses']):
        print('---------------------------------------------------------------------------------')
        print(f'\tInstance ID: {instance.instance_id}')
        print(f'\tInstance Type: {instance.instance_type}')
        print(f'\tInstance Zone: {status["AvailabilityZone"]}')
        print(f'\tInstance State: {instance.state["Name"]}')
        print(f'\tSSH Key: {instance.key_name}')
        
        print()
        
        print(f'\tPublic IP Address: {instance.public_ip_address}')
        print(f'\tPrivate IP Address: {instance.private_ip_address}')
        
        print()
        
        print(f'\tPublic DNS Name: {instance.public_dns_name}')
        print(f'\tPrivate DNS Name: {instance.private_dns_name}')

        print()

        instance_status = status['InstanceStatus']['Status']
        system_status = status['SystemStatus']['Status']

        print(f'\tHealth Checkup: ')
        print(f'\t\tInstance Status: {instance_status}')
        print(f'\t\tSystem Status: {system_status}')
        
        print('---------------------------------------------------------------------------------')
        print()

if __name__ == '__main__':

    if not (len(sys.argv) == 3 or len(sys.argv) == 6):
        print('invalid command! use:')
        print('\tpython helper.py <update> {hostname} {user} {password} {db}')
        print('\tpython helper.py <upload> {bucket}')
        exit(1)

    if len(sys.argv) == 6 and sys.argv[1] == 'update':
        updateConnection(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif sys.argv[1] == 'upload':
        upload(sys.argv[2])