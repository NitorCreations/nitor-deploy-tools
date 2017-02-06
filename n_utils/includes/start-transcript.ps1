$ErrorActionPreference="SilentlyContinue"
Stop-Transcript | out-null
$ErrorActionPreference = "Continue"
Start-Transcript -path C:\nitor\cloud-init-output.log
pip install -U pip setuptools nitor-deploy-tools awscli boto3
$selfOutput = Start-Job {logs-to-cloudwatch 'C:\nitor\cloud-init-output.log'}
$cfnOutput = Start-Job {logs-to-cloudwatch 'C:\cfn\log\cfn-init.log'}
$ec2configOutput = Start-Job {logs-to-cloudwatch 'C:\Program Files\Amazon\Ec2ConfigService\Logs\Ec2ConfigLog.txt'}
