#!/usr/bin/python

import boto3, os, sys, argparse

parser = argparse.ArgumentParser()
parser.add_argument("aws_account", help="The name of the AWS account")
parser.add_argument("aws_access_key", help="The AWS access key to use")
parser.add_argument("aws_secret_key", help="The AWS secret key associated with the access key")
args = parser.parse_args()
credlist=[]

creds={}
creds['account'] = args.aws_account
creds['accesskey'] = args.aws_access_key
creds['secretkey'] = args.aws_secret_key
credlist.append(creds)

regions=['us-west-2','us-east-1','us-west-1','eu-west-1','ap-southeast-1','ap-southeast-2','ap-northeast-1']

InstanceEvents=[]

for account in credlist:
	Account=account['account']
	AccessKey=account['accesskey']
	SecretKey=account['secretkey']

	for region in regions:

		ec2 = boto3.client('ec2',
			aws_access_key_id=AccessKey,
			aws_secret_access_key=SecretKey,
			region_name=region)

		status = ec2.describe_instance_status()

		for instance in status['InstanceStatuses']:
			if 'Events' in instance:
				InstanceId=instance['InstanceId']
				for event in instance['Events']:
					if (event['Description'].find('Completed')==-1):
						InstanceDetails=ec2.describe_instances(InstanceIds=[InstanceId])
						for reservation in InstanceDetails['Reservations']:
							for instance in reservation['Instances']:
								for tag in instance['Tags']:
									if (tag['Key'] == 'Name') or (tag['Key'] == 'name'):
										InstanceName = tag['Value']
						InstanceEvent={}
						InstanceEvent['Account'] = Account
						InstanceEvent['Region'] = region
						InstanceEvent['InstanceId'] = InstanceId
						InstanceEvent['InstanceName'] = InstanceName
						Code=event['Code']
						InstanceEvent['Code'] = Code
						InstanceEvent['Description']=event['Description']
						if 'NotBefore' in event:
							NotBefore=event['NotBefore']
							InstanceEvent['NotBefore'] = NotBefore
						if 'NotAfter' in event:
							NotAfter=event['NotAfter']
							InstanceEvent['NotAfter'] = NotAfter
						InstanceEvents.append(InstanceEvent)
OverallStatus=''
for event in InstanceEvents:
	StatusDetails = 'INSTANCE: '+event['InstanceName']+" ("+event['InstanceId']+"): "+event['Description']+' ACTION: '+event['Code']+' EFF DATE: '+event['NotBefore'].strftime('%m/%d/%Y %H:%M')+ ' ACCOUNT:'+event['Account']+' REGION: '+event['Region']
	OverallStatus = OverallStatus+' '+StatusDetails

if OverallStatus == '':
	print "Everything looks OK"
	sys.exit(0)
else:
	print 'WARNING: '+OverallStatus
	sys.exit(1)
