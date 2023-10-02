import sys
import boto3 as bt
from botocore.exceptions import ClientError

#  This function prints health checkup for all running instances.
def health_checkup():
    ec2 = bt.resource('ec2')
    print('\nPerforming Health Cehckup:')
    for status in  ec2.meta.client.describe_instance_status()['InstanceStatuses']:
        
        if status['InstanceState']['Name'] != 'running':
            continue

        print('---------------------------------------------------------------------------------')
        print(f'\tInstance ID: {status["InstanceId"]}')
        print(f'\tInstance Zone: {status["AvailabilityZone"]}')
        instance_status = status['InstanceStatus']['Status']
        system_status = status['SystemStatus']['Status']
        print(f'\tInstance Status: {instance_status}')
        print(f'\tSystem Status: {system_status}')
        print('---------------------------------------------------------------------------------')

#  This function lists all the currently running instances.
def list_running_instances():
    ec2 = bt.resource('ec2')

    instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

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
        # print("\n\n", dir(instance))

#  This function stops all the currently running instances.
def stop_running_instances():
    ec2 = bt.resource('ec2')

    instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

    print()
    for instance in instances:
        instance.stop()
        print(f'Instance {instance.instance_id} has been stopped.')

#  This function terminates all the currently running instances.
def terminate_running_instances():
    ec2 = bt.resource('ec2')

    instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

    print()
    for instance in instances:
        instance.terminate()
        print(f'Instance {instance.instance_id} has been terminated.')
        
if __name__ == '__main__':

    commands = {'list': list_running_instances,
                'health': health_checkup,
                'stop': stop_running_instances,
                'terminate': terminate_running_instances
                }

    if len(sys.argv) < 1 or sys.argv[1] not in commands:
        print('invalid command! usage: python helpers.py <list | health | stop | terminate>')
        exit()

    command = sys.argv[1]

    commands[command]() 
