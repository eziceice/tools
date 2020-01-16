import os

credentials_path = os.environ['AWS_CREDENTIALS']
f = open(f'{credentials_path}/credentials')
print(f.read())
