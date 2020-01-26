import boto3,json

# List all Public ALBs
client = boto3.client('elbv2','eu-west-1')
elbv2response = client.describe_load_balancers()
albs,cfs,wafid,wafarn,wafnalbs = [],[],[],[],[]
if bool(elbv2response):
    for elb in elbv2response['LoadBalancers']:
        if elb['Type']  == 'application' and elb['Scheme'] == 'internet-facing':
            albs.append(elb['LoadBalancerArn'])

# List all WAFv1 and associated ALBs
client = boto3.client('waf-regional','eu-west-1')
wafv1response = client.list_web_acls()
if bool(wafv1response):
    for waf in wafv1response['WebACLs']:
        wafid.append(waf['WebACLId'])
for waf in wafid:
    wafv1response = client.list_resources_for_web_acl(
        WebACLId=waf,
        ResourceType='APPLICATION_LOAD_BALANCER'
    )
    for albinwaf in wafv1response['ResourceArns']:
        if bool(albinwaf):
            wafnalbs.append(albinwaf)

# List all WAFv2 and associated ALBs
client = boto3.client('wafv2','eu-west-1')
wafv2response = client.list_web_acls(Scope='REGIONAL')
if bool(wafv2response):
    for waf in wafv2response['WebACLs']:
        wafarn.append(waf['ARN'])
for waf in wafarn:
    wafv2response = client.list_resources_for_web_acl(
        WebACLArn=waf,
        ResourceType='APPLICATION_LOAD_BALANCER'
    )
    for albinwaf in wafv2response['ResourceArns']:
        if bool(albinwaf):
            wafnalbs.append(albinwaf)

# Compare ALB list with WAFnALB list
waflessalb = set(albs).difference(set(wafnalbs))
albout = "ALBs that don't have WAF" +str(waflessalb)

# List all CFs that does not have WAF associations
client = boto3.client('cloudfront')
cfresponse = client.list_distributions()
if bool(cfresponse):
    for cf in cfresponse['DistributionList']['Items']:
        if not len(cf['WebACLId']):
            cfs.append(cf['ARN'])
cfout = "CloudFront that don't have WAF" +str(cfs)

# If there is any Public ALB or CFs without WAF send out SNS notification
if cfs or bool(waflessalb):
    sns = boto3.client('sns','us-east-1')
    response = sns.publish(
        TopicArn='arn:aws:sns:us-east-1:4XXXXXXXXXXXXX8:Akhil',   
        Message="'"+albout+'\n'+cfout+"'"
    )
    print(albout+'\n'+cfout)
else:
    print("No resource found ! (or) All resources are found to be with WAF association")
