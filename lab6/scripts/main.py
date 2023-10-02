from constants import *
from helper import upload, create_database, updateConnection, create_beanstalk_app, create_beanstalk_environment, create_cloudfront_distribution

if __name__ == '__main__':

    create_cloudfront_distribution(TARGET_ID, CALLER_REFERENCE, CF_DESCRIPTION, DOMAIN_NAME, CACHE_POLICY_ID, VIEWER_PROTOCOL)
    
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

    updateConnection(hostname, DB_USERNAME, DB_PASSWORD, DB_NAME)

    if not upload(BUCKET_NAME):
        exit(1)

    
    create_beanstalk_app(APP_NAME, APP_DESCRIPTION, BUCKET_NAME, S3_KEY, APP_VERSION)

    create_beanstalk_environment(APP_NAME, CNAME, ENVIRONMENT_NAME, SOLUTION_STACK, APP_VERSION, ENVIRONMENT_SETTINGS)
