import json
import logging
import os
from typing import Dict, Any, List
import boto3
from botocore.exceptions import ClientError

#################
# Configuration #
#################
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

# Initializing clients outside the handler for connection reuse
S3_CLIENT = boto3.client('s3')
SNS_CLIENT = boto3.client('sns')


####################
# Helper Functions #
####################
def get_s3_object_keys(bucket_name: str) -> List[str]:
    """
    Retrieves a list of object keys (file names) from the specified S3 bucket.
    
    Args:
        bucket_name (str): The name of the S3 bucket.
        
    Returns:
        List[str]: A list of file names found in the bucket.
    """
    try:
        response = S3_CLIENT.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in response:
            return [obj['Key'] for obj in response['Contents']]
        return []
    except ClientError as error:
        LOGGER.error("Failed to list objects in S3 bucket '%s': %s", bucket_name, error)
        raise


def publish_execution_report(topic_arn: str, message: str) -> None:
    """
    Publishes the execution report message to the given SNS topic.
    
    Args:
        topic_arn (str): The ARN of the SNS Topic.
        message (str): The message body to publish.
    """
    try:
        SNS_CLIENT.publish(
            TopicArn=topic_arn,
            Subject='AWS Task - Execution Report',
            Message=message
        )
    except ClientError as error:
        LOGGER.error("Failed to publish message to SNS topic '%s': %s", topic_arn, error)
        raise


#######################
# Main Lambda Handler #
#######################

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main entry point for the AWS Lambda function.
    Coordinates the process of reading from S3 and notifying via SNS.
    Args:
        event (Dict[str, Any]): The event dictionary containing the payload that triggered the Lambda.
        context (Any): An AWS Lambda Context object providing runtime information.
        
    Returns:
        Dict[str, Any]: A dictionary containing a standard HTTP-like response with 'statusCode' and 'body'.
    """
    LOGGER.info("Lambda execution started.")
    
    # Fetch Environment Variables
    bucket_name = os.environ.get('BUCKET_NAME')
    sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')
    
    if not bucket_name or not sns_topic_arn:
        error_msg = "Critical environment variables (BUCKET_NAME, SNS_TOPIC_ARN) are missing."
        LOGGER.error(error_msg)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': error_msg})
        }

    try:
        # Execute Business Logic
        LOGGER.info("Attempting to read from bucket: %s", bucket_name)
        file_names = get_s3_object_keys(bucket_name)
        
        # Format the Notification Message
        if file_names:
            files_str = "\n".join(file_names)
            message_body = (
                f"Lambda execution completed successfully.\n\n"
                f"Found {len(file_names)} files in bucket '{bucket_name}':\n"
                f"{files_str}"
            )
        else:
            message_body = (
                f"Lambda execution completed successfully.\n\n"
                f"The bucket '{bucket_name}' is currently empty."
            )
            
        # Send Notification
        LOGGER.info("Publishing report to SNS.")
        publish_execution_report(sns_topic_arn, message_body)
        
        LOGGER.info("Lambda execution completed successfully.")
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Execution and notification successful!'})
        }
        
    except ClientError as error:
        # Handling AWS-specific errors gracefully
        LOGGER.error("An AWS API error occurred: %s", error)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'AWS Service operation failed. Check logs for details.'})
        }
    except Exception as error:
        # Catch-all for unexpected Python errors (e.g., memory issues, syntax logic)
        LOGGER.error("An unexpected error occurred: %s", error)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error.'})
        }