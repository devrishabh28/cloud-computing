from constants import *
from helper import create_autoscaling_group, create_launch_template, get_instance_urls, create_database, create_ECR, upload_docker_image, create_and_run_ecs_task


def deploy_microservice(ecr_replository_name, aws_region, microservice_directory, launch_template_name, version_description, ami_id, instance_type, instance_profile_arn, security_group_ids, ssh_key, auto_scaling_group_name, launch_version, target_group, availability_zones, ecs_cluster_name, ecs_task_family, api_name, container_port, capacity_provider_name):
    create_ECR(ecr_replository_name)
    IMAGE_URI = upload_docker_image(ecr_replository_name, aws_region, microservice_directory, 'latest')

    LAUNCH_TEMPLATE_ID = create_launch_template(
            launch_template_name,
            version_description,
            ami_id, instance_type,
            instance_profile_arn,
            security_group_ids,
            ssh_key,
            ecs_cluster_name
        )
    
    if LAUNCH_TEMPLATE_ID is not None:
        print(f'created launch template {launch_template_name} ({LAUNCH_TEMPLATE_ID}) successfully!')
    else:
        exit(1)

    if not create_autoscaling_group(
            auto_scaling_group_name,
            LAUNCH_TEMPLATE_ID,
            launch_version,
            target_group,
            availability_zones
            ):
        exit(1)

    create_and_run_ecs_task(ecs_cluster_name, ecs_task_family, api_name, IMAGE_URI, container_port, auto_scaling_group_name, capacity_provider_name)


if __name__ == '__main__':

    #  Deploying microservice skills.
    deploy_microservice(
                    SKILLS_REPOSITORY_NAME,
                    AWS_REGION,
                    SKILLS_DIRECTORY,
                    SKILLS_LAUNCH_TEMPLATE_NAME,
                    SKILLS_VERSION_DESCRIPTION,
                    AMI_ID,
                    INSTANCE_MICRO,
                    INSTANCE_PROFILE_ARN,
                    SECURITY_GROUP_IDS,
                    SSH_KEY,
                    SKILLS_AUTOSCALING_GROUP_NAME,
                    SKILLS_LAUNCH_VERSION,
                    TARGET_GROUPS,
                    AUTOSCALING_AVAILABILITY_ZONE,
                    SKILLS_CLUSTER_NAME,
                    SKILLS_TASK_FAMILY,
                    SKILLS_API_NAME,
                    SKILLS_CONTAINER_PORT,
                    SKILLS_PROVIDER_NAME
    )

    #  Deploying microservice education.
    deploy_microservice(
                    EDUCATION_REPOSITORY_NAME,
                    AWS_REGION,
                    EDUCATION_DIRECTORY,
                    EDUCATION_LAUNCH_TEMPLATE_NAME,
                    EDUCATION_VERSION_DESCRIPTION,
                    AMI_ID,
                    INSTANCE_MICRO,
                    INSTANCE_PROFILE_ARN,
                    SECURITY_GROUP_IDS,
                    SSH_KEY,
                    EDUCATION_AUTOSCALING_GROUP_NAME,
                    EDUCATION_LAUNCH_VERSION,
                    TARGET_GROUPS,
                    AUTOSCALING_AVAILABILITY_ZONE,
                    EDUCATION_CLUSTER_NAME,
                    EDUCATION_TASK_FAMILY,
                    EDUCATION_API_NAME,
                    EDUCATION_CONTAINER_PORT,
                    EDUCATION_PROVIDER_NAME
    )

    #  Create database.
    hostname = create_database(
                            DB_NAME,
                            DB_INSTANCE_IDENTIFIER,
                            DB_INSTANCE_CLASS,
                            DB_ENGINE,
                            DB_ENGINE_VERSION,
                            DB_USERNAME,
                            DB_PASSWORD,
                            SECURITY_GROUP_IDS,
                            DB_SUBNET_ZONE,
                            AVAILABILITY_ZONE
                        )
    
    #  Deploying microservice comments.
    deploy_microservice(
                    COMMENTS_REPOSITORY_NAME,
                    AWS_REGION,
                    COMMENTS_DIRECTORY,
                    COMMENTS_LAUNCH_TEMPLATE_NAME,
                    COMMENTS_VERSION_DESCRIPTION,
                    AMI_ID,
                    INSTANCE_MICRO,
                    INSTANCE_PROFILE_ARN,
                    SECURITY_GROUP_IDS,
                    SSH_KEY,
                    COMMENTS_AUTOSCALING_GROUP_NAME,
                    COMMENTS_LAUNCH_VERSION,
                    TARGET_GROUPS,
                    AUTOSCALING_AVAILABILITY_ZONE,
                    COMMENTS_CLUSTER_NAME,
                    COMMENTS_TASK_FAMILY,
                    COMMENTS_API_NAME,
                    COMMENTS_CONTAINER_PORT,
                    COMMENTS_PROVIDER_NAME
    )

    print(get_instance_urls(
        auto_scaling_group_names=[
                SKILLS_AUTOSCALING_GROUP_NAME,
                EDUCATION_AUTOSCALING_GROUP_NAME,
                COMMENTS_AUTOSCALING_GROUP_NAME
            ]
        )
    )
