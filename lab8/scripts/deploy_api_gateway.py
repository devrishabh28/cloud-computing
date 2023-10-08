from constants import *
from helper import create_api_gateway, create_api_resource, create_api_endpoint, deploy_api, get_api_target_uri

if __name__ == '__main__':
    #  Create the API gateway.
    api_id, root_resource_id = create_api_gateway(API_NAME, API_DESCRIPTION)

    #  Create resources for each microservice.
    skill_api = create_api_resource(api_id, root_resource_id, SKILL_PATH_PART)
    education_api = create_api_resource(api_id, root_resource_id, EDUCATION_PATH_PART)    
    comments_api = create_api_resource(api_id, root_resource_id, COMMENTS_PATH_PART)

    # #  Create end points for each API.
    create_api_endpoint(api_id, skill_api, HTTP_GET, SKILL_URI)
    create_api_endpoint(api_id, education_api, HTTP_GET, EDUCATION_URI)  
    create_api_endpoint(api_id, comments_api, HTTP_GET, COMMENTS_URI)  
    create_api_endpoint(api_id, comments_api, HTTP_POST, COMMENTS_URI)

    # #  Deploy the API.
    deploy_api(api_id, STAGE_NAME)

    #  Return the target URI of deployed API.
    api_uri = get_api_target_uri(api_id, STAGE_NAME, AWS_REGION)
    print(api_uri)