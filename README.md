# AWS Task

This repository contains the infrastructure and application code for a serverless AWS assignment. The project is built using the AWS Cloud Development Kit (CDK) in Python and demonstrates Infrastructure as Code (IaC) principles, automated deployment, and serverless event handling.

## Architecture Overview

The solution provisions the following AWS resources:
* **Amazon S3:** A storage bucket configured to hold sample files.
* **AWS Lambda:** A Python-based function that reads the contents of the S3 bucket and generates an execution summary report.
* **Amazon SNS:** A notification topic that receives the execution report from the Lambda function and forwards it via email to a subscribed user.
* **IAM Roles & Policies:** Configured strictly using the principle of least privilege, allowing the Lambda function only the necessary access to read from the specific S3 bucket and publish to the designated SNS topic.

## Prerequisites

To deploy and run this project locally, ensure you have the following installed and configured:
* Node.js and npm (required for the AWS CDK engine)
* Python 3.10 or higher
* AWS CLI, fully configured with your account credentials (`aws configure`)
* AWS CDK CLI (`npm install -g aws-cdk`)

## Local Deployment Instructions

1. Clone the repository and navigate to the infrastructure directory:
   ```bash
   cd cdk_infrastructure
   ```

2. Activate the virtual environment and install the required Python dependencies:
   ```bash
   # On Windows
   .venv\Scripts\activate
   
   # On Linux/macOS
   # source .venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. Bootstrap the AWS environment (required only once per AWS account/region):
   ```bash
   cdk bootstrap
   ```

4. Deploy the infrastructure stack to your AWS account:
   ```bash
   cdk deploy
   ```

*Note: Upon successful deployment, an SNS subscription confirmation email will be sent to the configured address. You must confirm this subscription to receive the Lambda execution reports.*

## CI/CD Pipeline

This repository includes a GitHub Actions workflow (`.github/workflows/deploy.yml`) for continuous deployment.

To trigger the deployment via GitHub:
1. Navigate to the "Actions" tab in the repository.
2. Select the "Deploy AWS Infrastructure" workflow.
3. Click "Run workflow" on the main branch.

*Configuration requirement: Ensure `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are securely stored in the repository's Action Secrets.*

## Manual Testing

To verify the system functionality end-to-end, you can manually invoke the Lambda function using the AWS CLI. Replace `us-east-1` with your deployed region if necessary:

```bash
aws lambda invoke --function-name $(aws lambda list-functions --region us-east-1 --query "Functions[?contains(FunctionName, 'AssignmentLambda')].FunctionName" --output text) --region us-east-1 response.json
```

Expected outcomes:
* The CLI returns a `StatusCode: 200`.
* A `response.json` file is generated locally with the execution details.
* An email containing the list of S3 files is delivered to your inbox.

## Cleanup

To prevent ongoing charges on your AWS account, destroy the deployed resources once testing is complete:

```bash
cdk destroy
```
