from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_lambda as _lambda,
)
from constructs import Construct

##########################
# Infrastructure As Code #
##########################

class CdkInfrastructureStack(Stack):
    """
    AWS CDK Stack definition for the DevOps Serverless Assignment.
    Provisions and configures S3, SNS, Lambda, and IAM permissions.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        """
        Initializes the AWS CDK Stack and builds the cloud resources.

        Args:
            scope (Construct): The scope in which to define this construct (usually the CDK App).
            construct_id (str): The scoped construct ID.
            **kwargs: Additional keyword arguments passed to the base Stack class.
            
        Returns:
            None
        """
        super().__init__(scope, construct_id, **kwargs)

        ##########################################
        # S3 Bucket & Deployment (Requirement 4) #
        ##########################################
        
        # Create the bucket. 
        bucket = s3.Bucket(
            self, "AssignmentBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # Deploy local sample files to the S3 bucket during infrastructure creation
        s3deploy.BucketDeployment(
            self, "DeploySampleFiles",
            sources=[s3deploy.Source.asset("../sample_files")],
            destination_bucket=bucket
        )

        # ==========================================
        # SNS Topic & Subscription (Requirement 6)
        # ==========================================
        
        # Create the SNS Topic for execution reports
        topic = sns.Topic(self, "AssignmentExecutionTopic")
        
        # Subscribe email to the topic 
        topic.add_subscription(subscriptions.EmailSubscription("maozbar100@gmail.com"))

        # ==========================================
        # 3. Lambda Function (Requirement 3)
        # ==========================================
        
        # Define the Lambda function, configure runtime, and inject environment variables
        my_lambda = _lambda.Function(
            self, "AssignmentLambda",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="app.lambda_handler",
            code=_lambda.Code.from_asset("../lambda"),
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                "SNS_TOPIC_ARN": topic.topic_arn
            },
            timeout=Duration.seconds(15)
        )

        # ==========================================
        # 4. IAM Permissions - Least Privilege (Requirement 5)
        # ==========================================
        
        # Grant specific access rights to the Lambda execution role
        # AWS CDK automatically creates the execution role and attaches the AWSLambdaBasicExecutionRole policy.
        bucket.grant_read(my_lambda)
        topic.grant_publish(my_lambda)