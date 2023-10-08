from constants import *
from deploy_microservices import deploy_microservice
from helper import get_instance_urls

if __name__ == '__main__':
    #  Deploying portfolio website.
    deploy_microservice(
                    PORTFOLIO_REPOSITORY_NAME,
                    AWS_REGION,
                    PORTFOLIO_DIRECTORY,
                    PORTFOLIO_LAUNCH_TEMPLATE_NAME,
                    PORTFOLIO_VERSION_DESCRIPTION,
                    AMI_ID,
                    INSTANCE_MICRO,
                    INSTANCE_PROFILE_ARN,
                    SECURITY_GROUP_IDS,
                    SSH_KEY,
                    PORTFOLIO_AUTOSCALING_GROUP_NAME,
                    PORTFOLIO_LAUNCH_VERSION,
                    TARGET_GROUPS,
                    AUTOSCALING_AVAILABILITY_ZONE,
                    PORTFOLIO_CLUSTER_NAME,
                    PORTFOLIO_TASK_FAMILY,
                    PORTFOLIO_API_NAME,
                    PORTFOLIO_CONTAINER_PORT,
                    PORTFOLIO_PROVIDER_NAME
    )

    print(get_instance_urls(
        auto_scaling_group_names=[
                PORTFOLIO_AUTOSCALING_GROUP_NAME
            ]
        )
    )