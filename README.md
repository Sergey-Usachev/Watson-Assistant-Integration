# Watson-Assistant-Integration
### Watson-Assistant with integration capabilities

1. "__main__.py" should be deployed as Cloud Function (Action) on IBM Cloud.  For this you should carefully run commands from "script for installation.txt"

2. Then link registered Cloud Function as a webhook in Watson Assistant

The bot calls predictive model. For building and deployment this model please follow the code pattern:
https://developer.ibm.com/patterns/create-an-application-to-predict-your-insurance-premium-cost-with-autoai/

For working wih use cases related to tariff plans (reading CSV file from COS etc) - please try to find code pattern:
- https://ibm.ent.box.com/folder/130849296802?v=serverles-workshop
- https://khalil-faraj.gitbook.io/go-serverless-with-watson-assistant/creating-a-cloud-function
- https://developer.ibm.com/depmodels/serverless/tutorials/go-serverless-in-watson-assistant-with-ibm-cloud-function/
- Some of web pages became broken
