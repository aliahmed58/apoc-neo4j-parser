# list of constants for services and the possible list of labels they might have

S3_LABELS = ['S3Bucket', 'S3PolicyStatement', 'S3Acl']
DYNAMODB_LABELS = ['DynamoDBTable', 'DynamoDBGlobalSecondaryIndex']

LABELS = {
    's3': {
        'S3Bucket', 'S3PolicyStatement', 'S3Acl'
    },
    'dynamodb': {
        'DynamoDBTable', 'DynamoDBGlobalSecondaryIndex'
    },
    'aws': {
        'AWSAccount', 'AWSPrincipal', 'AWSPolicy', 'AWSRole'
    }
}
