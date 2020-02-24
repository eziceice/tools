import boto3
import docker
import base64
import subprocess
import os


def check_dependencies(names):
    devnull = open(os.devnull, 'wb')
    try:
        for name in names:
            subprocess.call([name], stdout=devnull, stderr=devnull)
    except EnvironmentError:
        print('Missing dependency: {}'.format(name))
        exit(1)


def get_env_variable(name, default):
    try:
        return os.environ[name]
    except KeyError:
        return default


print('Checking the latest git tag...')
target_tag = subprocess.check_output(['git', 'tag', '--sort=committerdate']).decode('utf-8').strip().splitlines()[
    -1].rsplit('-', 1)
image = target_tag[0]
tag = target_tag[1]
service = ''

print('Checking CLI dependencies...')
check_dependencies(['aws', 'docker', 'docker-compose'])
print('All packages are installed...')

if image == 'a':
    service = 'b'
elif image == 'c':
    service = 'd'
print('Processing image: {}:{} - service {} to ECR...'.format(image, tag, service))

region = get_env_variable('AWS_DEFAULT_REGION', 'ap-southeast-2')
docker_client = docker.from_env()
ecr_client = boto3.client('ecr', region_name=region)

token = ecr_client.get_authorization_token()
username, password = base64.b64decode(token['authorizationData'][0]['authorizationToken']).decode().split(':')
registry = token['authorizationData'][0]['proxyEndpoint']

print('Logging in ECR...')
docker_client.login(username, password, registry=registry)
response = ecr_client.describe_repositories(repositoryNames=[image])
repositoryUri = '{}:{}'.format(response['repositories'][0]['repositoryUri'], tag)

subprocess.call(['docker-compose', 'build', service])
print('Tagging image with new name {}'.format(repositoryUri))
subprocess.call(['docker', 'tag', '{}:latest'.format(image), repositoryUri])
subprocess.call(['docker', 'push', repositoryUri])
