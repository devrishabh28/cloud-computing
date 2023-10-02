import base64
import boto3 as bt
from botocore.exceptions import ClientError

#  This function creates a launch template.
def create_launch_template(template_name, version, image_id, instance_type, iam_arn, security_group_ids, ssh_key, script_path):
    
    ec2 = bt.client('ec2')
    LAUNCH_TEMPLATE_ID = None
    
    try:
        with open(script_path, 'r') as f:
            script = '\n'.join(f).encode('ascii')
            script = base64.b64encode(script)
            script = script.decode('ascii')
            response = ec2.create_launch_template(
                LaunchTemplateName=template_name,
                VersionDescription=version,
                LaunchTemplateData = {
                    'ImageId':image_id,
                    'InstanceType':instance_type,
                    'IamInstanceProfile':{
                        'Arn': iam_arn
                    },
                    'SecurityGroupIds':security_group_ids,
                    'KeyName':ssh_key,
                    'UserData':script
                }
            )

        LAUNCH_TEMPLATE_ID = response['LaunchTemplate']['LaunchTemplateId']
    except ClientError as err:
        print("error creating launch template!")
        print(err)
        
    return LAUNCH_TEMPLATE_ID

#  This function creates an auto scaling group.
def create_autoscaling_group(group_name, launch_template_id, launch_template_version, target_groups, availability_zones, min_size = 1, max_size = 3, desired_capacity = 2, cooldown = 300):
    scaler = bt.client('autoscaling')
    
    try:
        response = scaler.create_auto_scaling_group(
                AutoScalingGroupName = group_name,
                LaunchTemplate = {
                        'LaunchTemplateId': launch_template_id,
                        'Version': launch_template_version
                    },
                DesiredCapacityType='units',
                MinSize = min_size,
                MaxSize = max_size,
                DesiredCapacity = desired_capacity,
                DefaultCooldown = cooldown,
                TargetGroupARNs = target_groups,
                VPCZoneIdentifier = availability_zones
            )
        print(f'created autoscaling group {group_name} successfully!')
        return True
    except ClientError as err:
        print("error creating auto scaling group!")
        print(err)
    
    return False

#  This function creates a target tracking scaling policy.
def create_target_scaling_policy(autoscaling_group_name, policy_name, adjustment_type, cooldown, metric, target_value):
    scaler = bt.client('autoscaling')
    try:
        response = scaler.put_scaling_policy(
            AutoScalingGroupName = autoscaling_group_name,
            PolicyName = policy_name,
            PolicyType = 'TargetTrackingScaling',
            AdjustmentType = adjustment_type,
            Cooldown = cooldown,
            TargetTrackingConfiguration={
                'PredefinedMetricSpecification': {
                    'PredefinedMetricType': metric, 
                },
                'TargetValue': target_value,
            },
        )
        return response
    except ClientError as err:
        print("error creating scaling policy!")
        print(err)
    return False

#  This function creates a step scaling policy.
def create_step_scaling_policy(autoscaling_group_name, policy_name, policy_type, adjustment_type, cooldown, scale_value):
    
    scaler = bt.client('autoscaling')
    try:
        response_lower = scaler.put_scaling_policy(
            AutoScalingGroupName = autoscaling_group_name,
            PolicyName = policy_name + ' Scale Down',
            PolicyType = policy_type,
            AdjustmentType = adjustment_type,
            Cooldown = cooldown,
            StepAdjustments = [
                {
                    'MetricIntervalUpperBound': 0,
                    'ScalingAdjustment': -scale_value,
                }
            ],
        )

        response_upper = scaler.put_scaling_policy(
            AutoScalingGroupName = autoscaling_group_name,
            PolicyName = policy_name + 'Scale Up',
            PolicyType = policy_type,
            AdjustmentType = adjustment_type,
            Cooldown = cooldown,
            StepAdjustments = [
                {
                    'MetricIntervalLowerBound': 0,
                    'ScalingAdjustment': scale_value,
                }
            ],
        )

        return response_lower['PolicyARN'], response_upper['PolicyARN']
    except ClientError as err:
        print("error creating scaling policy!")
        print(err)
    return False

#  This function creates a cloudwatch alarm
#  and attaches the appropriate action for the policy.
def create_cloudwatch_alarm(autoscaling_group_name, alarm_name, comparison_operator, evaluation_periods, metric_name, namespace, period, threshold, statistic, alarm_description, scaling_policy, sns):
    cloudwatch = bt.client('cloudwatch')
    try:
        cloudwatch.put_metric_alarm(
            AlarmName = alarm_name,
            ComparisonOperator = comparison_operator,
            EvaluationPeriods = evaluation_periods,
            MetricName = metric_name,
            Namespace = namespace,
            Period = period,
            Threshold = threshold,
            Statistic = statistic,
            Dimensions = [
                {
                    'Name': 'AutoScalingGroupName',
                    'Value': autoscaling_group_name
                }
            ],
            AlarmDescription = alarm_description,
            AlarmActions = [scaling_policy, sns],
        )
        return True
    except ClientError as err:
        print("error creating cloudwatch alarm!")
        print(err)
    
    return False

if __name__ == '__main__':
    
    LAUNCH_TEMPLATE_NAME = 'alpha'
    VERSION_DESCRIPTION = 'V1'
    AMI_ID = 'ami-0ded8326293d3201b'
    SCRIPT_PATH = 'sync.sh'
    INSTANCE_TYPE = 't2.micro'
    SECURITY_GROUP_IDS = ['sg-0016c71b27fedaa68']
    SECURITY_GROUPS = ['launch-wizard-2']
    INSTANCE_PROFILE_ARN = 'arn:aws:iam::202783468510:instance-profile/EC2_S3'
    INSTANCE_PROFILE_NAME = 'EC2_S3'
    SSH_KEY = 'arch-key'

    AUTOSCALING_GROUP_NAME = 'cosmos'
    LAUNCH_VERSION = '$Latest'
    TARGET_GROUPS = ['arn:aws:elasticloadbalancing:ap-south-1:202783468510:targetgroup/entropy/763a603b5418676a']
    AVAILABILITY_ZONE = 'subnet-02b11a18a3a7dfd0e'

    POLICY_NAME = 'AutoScalingPolicy'
    POLICY_TYPE = 'StepScaling'
    ADJUSTMENT_TYPE = 'ChangeInCapacity'
    SCALE_VALUE = 1
    COOLDOWN = 300

    METRIC_NAME = 'CPUUtilization'
    NAMESPACE = 'AWS/EC2'
    STATISTIC = 'Average'
    EVALUATION_PERIOD = 1
    PERIOD = 60
    SNS_ARN = 'arn:aws:sns:ap-south-1:202783468510:Default_CloudWatch_Alarms_Topic'

    HEAVY_USAGE = 'Heavy Usage'
    HEAVY_USE_COMPARATOR = 'GreaterThanOrEqualToThreshold'
    HEAVY_USE_THRESHOLD = 80
    HEAVY_USE_DESCRIPTION = 'Alerts when CPU utilization exceeds 80%'

    LOW_USAGE = 'Low Usage'
    LOW_USE_COMPARATOR = 'LessThanOrEqualToThreshold'
    LOW_USE_THRESHOLD = 20
    LOW_USE_DESCRIPTION = 'Alerts when CPU utilization falls below 20%'

    ec2 = bt.client('ec2')
    scaler = bt.client('autoscaling')
    cloudwatch = bt.client('cloudwatch')

    
    LAUNCH_TEMPLATE_ID = create_launch_template(
            LAUNCH_TEMPLATE_NAME,
            VERSION_DESCRIPTION,
            AMI_ID, INSTANCE_TYPE,
            INSTANCE_PROFILE_ARN,
            SECURITY_GROUP_IDS,
            SSH_KEY,
            SCRIPT_PATH
        )
    
    if LAUNCH_TEMPLATE_ID is not None:
        print(f'created launch template {LAUNCH_TEMPLATE_NAME} ({LAUNCH_TEMPLATE_ID}) successfully!')
    else:
        exit(1)

    if not create_autoscaling_group(
            AUTOSCALING_GROUP_NAME,
            LAUNCH_TEMPLATE_ID,
            LAUNCH_VERSION,
            TARGET_GROUPS,
            AVAILABILITY_ZONE
            ):
        exit(1)

    scaling_policy_lower, scaling_policy_upper = create_step_scaling_policy(AUTOSCALING_GROUP_NAME, POLICY_NAME, POLICY_TYPE, ADJUSTMENT_TYPE, COOLDOWN, SCALE_VALUE)
    if scaling_policy_lower and scaling_policy_upper:
        print('created scaling policies successfully!')
    else:
        exit(1)
    
    heavy_use_alarm = create_cloudwatch_alarm(AUTOSCALING_GROUP_NAME, HEAVY_USAGE, HEAVY_USE_COMPARATOR, EVALUATION_PERIOD, METRIC_NAME, NAMESPACE, PERIOD, HEAVY_USE_THRESHOLD, STATISTIC, HEAVY_USE_DESCRIPTION, scaling_policy_upper, SNS_ARN)
    low_use_alarm = create_cloudwatch_alarm(AUTOSCALING_GROUP_NAME, LOW_USAGE, LOW_USE_COMPARATOR, EVALUATION_PERIOD, METRIC_NAME, NAMESPACE, PERIOD, LOW_USE_THRESHOLD, STATISTIC, LOW_USE_DESCRIPTION, scaling_policy_lower, SNS_ARN)
    print('created cloudwatch alarms successfully!')
