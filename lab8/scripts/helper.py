import base64
import json
import subprocess
import sys
import os
import boto3 as bt
import docker
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
def create_database(db_name, db_instance_identifier, db_instance_class, engine, engine_version, user_name, password, security_groups_id, db_subnet_group_name, availability_zone, allocated_storage=20):

    rds = bt.client('rds')

    try:

        try:
            rds.describe_db_instances(DBInstanceIdentifier=db_instance_identifier)[
                'DBInstances']
            print(f'database {db_name} instance already exists!')
        except:
            response = rds.create_db_instance(
                DBName=db_name,
                DBInstanceIdentifier=db_instance_identifier,
                DBInstanceClass=db_instance_class,
                Engine=engine,
                EngineVersion=engine_version,
                MasterUsername=user_name,
                MasterUserPassword=password,
                VpcSecurityGroupIds=security_groups_id,
                DBSubnetGroupName=db_subnet_group_name,
                AvailabilityZone=availability_zone,
                AllocatedStorage=allocated_storage,
                Port=3306,
                PubliclyAccessible=False
            )

            print(f'created RDS {db_instance_class} instance successfully!')

        step = 1

        while True:
            print(f'trying to get hostname of database ({step})...')
            instance = rds.describe_db_instances(
                DBInstanceIdentifier=db_instance_identifier)['DBInstances'][0]

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

    instances = ec2.instances.filter(InstanceIds=[instance_id])

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


#  This function creates a launch template.
def create_launch_template(template_name, version, image_id, instance_type, iam_arn, security_group_ids, ssh_key, cluster_name):

    ec2 = bt.client('ec2')
    LAUNCH_TEMPLATE_ID = None

    script= f'''
            #!/bin/bash 
            echo ECS_CLUSTER={cluster_name} >> /etc/ecs/ecs.config;
        '''.encode('ascii')
    script = base64.b64encode(script)
    script = script.decode('ascii')

    try:
        response = ec2.create_launch_template(
            LaunchTemplateName=template_name,
            VersionDescription=version,
            LaunchTemplateData={
                'ImageId': image_id,
                'InstanceType': instance_type,
                'IamInstanceProfile': {
                    'Arn': iam_arn
                },
                'SecurityGroupIds': security_group_ids,
                'KeyName': ssh_key,
                'UserData': script
            }
        )

        LAUNCH_TEMPLATE_ID = response['LaunchTemplate']['LaunchTemplateId']
    except ClientError as err:
        print("error creating launch template!")
        print(err)

    return LAUNCH_TEMPLATE_ID

#  This function creates an auto scaling group.


def create_autoscaling_group(group_name, launch_template_id, launch_template_version, target_groups, availability_zones, min_size=1, max_size=1, desired_capacity=1, cooldown=300):
    scaler = bt.client('autoscaling')

    try:
        response = scaler.create_auto_scaling_group(
            AutoScalingGroupName=group_name,
            LaunchTemplate={
                'LaunchTemplateId': launch_template_id,
                'Version': launch_template_version
            },
            DesiredCapacityType='units',
            MinSize=min_size,
            MaxSize=max_size,
            DesiredCapacity=desired_capacity,
            DefaultCooldown=cooldown,
            TargetGroupARNs=target_groups,
            VPCZoneIdentifier=availability_zones
        )
        print(f'created autoscaling group {group_name} successfully!')
        return True
    except ClientError as err:
        print("error creating auto scaling group!")
        print(err)

    return False


#  This function creates an ECR.
def create_ECR(repository_name):
    ecr_client = bt.client('ecr')

    # Create the ECR repository (if it doesn't exist)
    try:
        ecr_client.create_repository(
            repositoryName=repository_name,
            imageScanningConfiguration={
                'scanOnPush': True
            },
        )
        print(f'ECR repository "{repository_name}" created successfully.')
    except ecr_client.exceptions.RepositoryAlreadyExistsException:
        print(f'ECR repository "{repository_name}" already exists.')
    except:
        print('Something bad happened.')


#  This function creates ECR and uploads docker image to it.
def upload_docker_image(repository_name, aws_region, docker_path, docker_image_tag):

    #  Initialize AWS and ECR clients
    session = bt.Session()

    #  Get ECR login and password
    registry_url = f'{session.client("sts").get_caller_identity()["Account"]}.dkr.ecr.{aws_region}.amazonaws.com'
    password = subprocess.run(
        'aws ecr get-login-password --region ap-south-1'.split(), capture_output=True)

    #  Authenticate docker into AWS ECR
    auth_command = f'docker login --username AWS -p {password.stdout.decode().strip()} {registry_url}'
    subprocess.run(auth_command.split())

    # Build the Docker image
    subprocess.run(['docker', 'build', '-t', repository_name, docker_path])

    # Tag the Docker image
    repository_uri = f'{session.client("sts").get_caller_identity()["Account"]}.dkr.ecr.{aws_region}.amazonaws.com/{repository_name}'
    subprocess.run(['docker', 'tag', repository_name, repository_uri])

    # Push the Docker image to ECR
    subprocess.run(['docker', 'push', repository_uri])

    print(
        f'Docker image pushed to ECR repository: {repository_uri}:{docker_image_tag}')
    
    return f'{repository_uri}:{docker_image_tag}'


#  This function creates and ECS cluster and
#  starts task to run docker container.
def create_and_run_ecs_task(cluster_name, task_family, api_name, image_uri, port, auto_scaling_group_name, capacity_provider_name, desired_count = 1):

    ecs_client = bt.client('ecs')

    # Describe the Auto Scaling group to retrieve its ARN
    autoscaling_client = bt.client('autoscaling')
    response = autoscaling_client.describe_auto_scaling_groups(
        AutoScalingGroupNames=[auto_scaling_group_name]
    )

    # Extract the ARN from the response
    auto_scaling_group_arn = response['AutoScalingGroups'][0]['AutoScalingGroupARN']

    ecs_client.create_capacity_provider(
        name=capacity_provider_name,
        autoScalingGroupProvider={
            'autoScalingGroupArn': f'{auto_scaling_group_arn}',
            'managedScaling': {
                'status': 'ENABLED',
                'targetCapacity': 1,
                'minimumScalingStepSize': 1,
                'maximumScalingStepSize': 1,
            },
            'managedTerminationProtection': 'DISABLED',
        }
    )

    try:
        response = ecs_client.create_cluster(
            clusterName=cluster_name,
            capacityProviders=[capacity_provider_name],
            defaultCapacityProviderStrategy=[
                {
                    'capacityProvider': capacity_provider_name,
                    'weight': 1,
                },
            ],
        )
        print(f'ECS Cluster {cluster_name} created.')
    except ecs_client.exceptions.ClusterAlreadyExistsException:
        print(f'ECS Cluster {cluster_name} already exists.')
    except:
        print('something bad happened.')

    step = 1

    while True:
        print(f'waiting for {cluster_name} container instance to register ({step})...')
        instance = ecs_client.describe_clusters(clusters=[cluster_name],)['clusters'][0]
    
        if instance['registeredContainerInstancesCount'] <= 0:
            step += 1
            sleep(5)
            continue

        print(f'{cluster_name} container instance has been registered...')
        break

    

    # Define the task definition for the API using the ECR image URI
    task_definition = {
        "family": task_family,
        "containerDefinitions": [
            {
                "name": api_name,
                "image": image_uri,
                "cpu": 0,
                "portMappings": [
                    {
                        "containerPort": port,
                        "hostPort": 80,
                        "protocol": "tcp"
                    }
                ],
                "essential": True,
                "entryPoint": [],
                "command": [],
                "environment": [
                    {
                        "name": "PORT",
                        "value": f"{port}"
                    }
                ],
                "mountPoints": [],
                "volumesFrom": []
            }
        ],
        "taskRoleArn": "arn:aws:iam::202783468510:role/ecsTaskExecutionRole",
        "executionRoleArn": "arn:aws:iam::202783468510:role/ecsTaskExecutionRole",
        "requiresCompatibilities": [
            "EC2"
        ],
        "cpu": "1024",
        "memory": "128"
    }

    # Register the task definition
    response = ecs_client.register_task_definition(**task_definition)

    task_definition_arn = response['taskDefinition']['taskDefinitionArn']
    print(f"task definition created with ARN: {task_definition_arn}")

    # Run the ECS task with default network configuration (bridge mode)
    try:
        response = ecs_client.run_task(
            cluster=cluster_name,
            taskDefinition=task_definition_arn,
            count=desired_count,
            launchType='EC2',  # Change to 'FARGATE' if using Fargate
        )

        print(f"successfully started {desired_count} task(s) with default network configuration.")
    except:
        # Check for errors in the response
        print(f"failed to run task {task_family}...")

#  This functions get's the urls of ec2 instances under
#  certain autoscaling groups.
def get_instance_urls(auto_scaling_group_names):
    
    instance_urls = []
    instance_ids = []
    group_names = []

    # Initialize the Boto3 Auto Scaling and EC2 clients
    autoscaling_client = bt.client('autoscaling')
    ec2 = bt.resource('ec2')
    
    # Retrieve information about instances in the specified Auto Scaling group
    response = autoscaling_client.describe_auto_scaling_groups(AutoScalingGroupNames=auto_scaling_group_names)

    # Extract the instance IDs from the Auto Scaling group
    instance_ids = []
    for group in response['AutoScalingGroups']:
        for instance in group['Instances']:
            group_names.append(group['AutoScalingGroupName'])
            instance_ids.append(instance['InstanceId'])

    instances = ec2.instances.filter(InstanceIds=instance_ids)

    for instance in instances:
        instance_urls.append(instance.public_dns_name)

    return dict(zip(group_names, instance_urls))

#  This function creates an API gateway.
def create_api_gateway(api_name, api_description):
    # Initialize the Boto3 API Gateway client
    api_gateway_client = bt.client('apigateway')
    
    # Create the API
    response = api_gateway_client.create_rest_api(
        name=api_name,
        description=api_description,
    )
    
    print(f'created {api_name} api gateway...')
    
    # Get the API ID from the response
    api_id = response['id']


    # Get information about the resources of the API
    response = api_gateway_client.get_resources(
        restApiId=api_id
    )
    
    # Initialize the root resource ID as None
    root_resource_id = None
    
    # Iterate through the resources to find the root resource
    for resource in response['items']:
        if not resource.get('pathPart'):
            root_resource_id = resource['id']
            break
        
    # root_resource_id = response['rootResourceId']

    return api_id, root_resource_id

#  This function creates a resource within an API gateway.
def create_api_resource(api_id, parent_id, resource_path_part):
    # Initialize the Boto3 API Gateway client
    api_gateway_client = bt.client('apigateway')

    # Create the resource
    response = api_gateway_client.create_resource(
        restApiId=api_id,
        parentId=parent_id,
        pathPart=resource_path_part,
    )

    print(f'created {resource_path_part} api resource...')

    resource_id = response['id']

    return resource_id

def create_api_endpoint(api_id, resource_id, http_method, http_uri):
    # Initialize the Boto3 API Gateway client
    api_gateway_client = bt.client('apigateway')

    # Create the GET method for the resource
    response = api_gateway_client.put_method(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod=http_method,
        authorizationType='NONE',  # Change if needed
    )

    # Configure the HTTPS integration with response passthrough
    integration_response = api_gateway_client.put_integration(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod=http_method,
        type='HTTP',
        integrationHttpMethod=http_method,
        uri=http_uri,
        passthroughBehavior='WHEN_NO_MATCH'  # Set to 'WHEN_NO_MATCH' for passthrough
    )

    # Configure method response
    api_gateway_client.put_method_response(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod=http_method,
        statusCode='200',
        responseModels={'application/json': 'Empty'},
    )

    # Configure integration response
    api_gateway_client.put_integration_response(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod=http_method,
        statusCode='200',  # Change as needed
        responseTemplates={'application/json': ''},  # Change as needed
    )

    print(f'created {resource_id} api endpoint({http_method})...')

#  This function deploys the API gateway.
def deploy_api(api_id, stage_name):
    # Initialize the Boto3 API Gateway client
    api_gateway_client = bt.client('apigateway')

    # Deploy the API to make changes live
    api_gateway_client.create_deployment(
        restApiId=api_id,
        stageName=stage_name,
    )

    print(f'successfully deployed api at {stage_name} stage...')

#  This function returns the target URI of deployed API.
def get_api_target_uri(api_id, stage_name, aws_region):
    return f'https://{api_id}.execute-api.{aws_region}.amazonaws.com/{stage_name}/'



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
