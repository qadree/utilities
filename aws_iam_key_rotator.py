import boto3
import os
import re
from sys import argv

if __name__ == "__main__":
    cred_file = os.path.expanduser('~/.aws/credentials')
    profiles = boto3.session.Session().available_profiles
    user = 'qadree.woodland'

    with open(cred_file, 'r') as shared_cred_file:
        creds = shared_cred_file.read()

    for profile in profiles:
        profile_regex = re.compile(
            '(\[{}\])(\n)'.format(profile)+
            '(aws_access_key_id)([ =]+)(.+)(\n)'
            '(aws_secret_access_key)([ =]+)(.+)'
        )

        current_key_id = profile_regex.search(creds).group(5)
        current_key_secret = profile_regex.search(creds).group(9)
        try:
            session = boto3.session.Session(profile_name='iam_rotator')
            iam = session.client('iam')
            #iam = boto3.client('iam')
            iam_key_old = iam.list_access_keys(UserName=user)['AccessKeyMetadata']
            iam_key_new = iam.create_access_key(UserName=user)
            new_key_id = iam_key_new['AccessKey']['AccessKeyId']
            new_key_secret = iam_key_new['AccessKey']['SecretAccessKey']
            creds = creds.replace(current_key_id, new_key_id)
            creds = creds.replace(current_key_secret, new_key_secret)
        except iam.exceptions.ClientError as error:
            print(error)
        else:
            with open(cred_file, 'w') as shared_cred_file:
                shared_cred_file.write(creds)

            iam.delete_access_key(AccessKeyId=current_key_id)

