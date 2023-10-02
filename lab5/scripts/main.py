from constants import *
from helper import create_instance, updateConnection, upload, create_database, instance_stats

import boto3 as bt
from botocore.exceptions import ClientError

if __name__ == '__main__':

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

    upload(BUCKET_NAME)

    print()

    with open(SCRIPT_PATH, 'r') as f:
        script = '\n'.join(f)
        instance_id = create_instance(AMI_AML,
                        INSTANCE_MICRO,
                        INSTANCE_PROFILE_ARN,
                        SECURITY_GROUP_IDS,
                        SECURITY_GROUPS,
                        SSH_KEY,
                        script
                    )
        
        instance_stats(instance_id)