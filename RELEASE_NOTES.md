# 1.0

* Parameter parsing reimplemented in python, faster and more secure
* Python3 support
* Serverless project support
* Most commands moved from the path to behind ndt command to consistently provide command completion and reduce polluting global path
* Parameter expansions in tempolate pre-processing with multiple syntaxes ($param, ${param} or ((param)))
* Project env setting via git config to make working with multiple ndt repositories a breeze
* MFA handling - import, export and code generation for MFA tokens and integration into `assume-role`
* Stack tags: add a top level element "Tags" to a cloudformation stack and they will be given to CloudFormation as separate stack tags
