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
def upload(bucket_name):
    s3 = bt.client('s3')
    try:
        print(f'generating compressed zip file...')
        os.system('cd ../portfolio && zip -r portfolio.zip .')
        print(f'generated compressed zip file successfully...')
        
        print(f'performing upload files to bucket {bucket_name}...')
        s3.upload_file('../portfolio/portfolio.zip', bucket_name, 'portfolio.zip')
        print(f'successfully uploaded files to bucket {bucket_name}...')
        
        return True
    except ClientError as err:
        print(f'failed to upload file to S3!')
        print(err)
        return False

#  This function creates a beanstalk application.
def create_beanstalk_app(application_name, description, bucket_name, s3_key, version_label):
    ebs = bt.client('elasticbeanstalk')

    try: 
        ebs.create_application_version(
            ApplicationName = application_name,
            AutoCreateApplication = True,
            Description = description,
            SourceBundle = {
                'S3Bucket': bucket_name,
                'S3Key': s3_key
            },
            VersionLabel = version_label
        )

        step = 1

        while True:
            response = ebs.describe_application_versions(
                ApplicationName = application_name,
                VersionLabels = [version_label],
                MaxRecords = 1
            )

            if response['ApplicationVersions'][0]['Status'] != 'PROCESSED':
                print(f'waiting for application to be processed ({step})...')
                step += 1
                sleep(5)
                break
        
        print('application has been processed...')

    except ClientError as err:
        print('error creating beanstalk app!')
        print(err)


#  This function creates a beanstalk environment.
def create_beanstalk_environment(application_name, cname_prefix, environment_name, solution_stack, version_label, environment_settings):
    ebs = bt.client('elasticbeanstalk')

    try:
        response = ebs.create_environment(
            ApplicationName = application_name,
            CNAMEPrefix = cname_prefix,
            EnvironmentName = environment_name,
            SolutionStackName = solution_stack,
            VersionLabel = version_label,
            OptionSettings = environment_settings
        )

        print('created beanstalk environment successfully...')
    except ClientError as err:
        print('error creating beanstalk environment!')
        print(err)

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

#  This function creates cloudfront distribution.
def create_cloudfront_distribution(target_id, caller_reference, cloudfront_description, domain_name, cache_policy_id, viewer_protocol):
    
    cdf = bt.client('cloudfront')

    try:
        response = cdf.create_distribution(
            DistributionConfig = {
                'CallerReference': caller_reference,
                'DefaultRootObject': 'index.html',
                'Comment': cloudfront_description,
                'Enabled': True,
                'Origins': {
                    'Quantity': 1,
                    'Items': [
                        {
                            'Id': target_id,
                            'DomainName': domain_name,
                            'S3OriginConfig': {'OriginAccessIdentity': ''}
                        }
                    ]
                },
                'DefaultCacheBehavior': {
                    'TargetOriginId': target_id,
                    'CachePolicyId': cache_policy_id,
                    'ViewerProtocolPolicy': viewer_protocol,
                    'TrustedSigners': {'Quantity': 0, 'Enabled': False},
                }
            }
        )

        print('created cloudfrony distribution successfully...')

    except ClientError as err:
        print('Error creating cloudfront distribution...')
        print(err)

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