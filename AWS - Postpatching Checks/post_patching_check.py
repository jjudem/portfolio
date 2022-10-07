import boto3
import os
from prettytable import PrettyTable
from botocore.config import Config

#Jenkins Agent Environment Variable
accountId = os.getenv('accountId') #aws account
roleId = os.getenv('roleId') #aws role
AccessKeyId = os.getenv('AWS_ACCESS_KEY_ID')
SecretAccessKey = os.getenv('AWS_SECRET_ACCESS_KEY')
SessionToken = os.getenv('AWS_SESSION_TOKEN')
REGION = os.getenv('REGION')

#os.environ['AWS_PROFILE'] = os.getenv('AWSPROFILE')
config = Config(
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

svcChecker = 0
tgChecker = 0
asgChecker = 0
sts_client = boto3.client('sts')
ecs_client = boto3.client('ecs', region_name=REGION, config=config)
elbv2_client = boto3.client('elbv2', region_name=REGION, config=config)
asg_client = boto3.client('autoscaling', region_name=REGION, config=config)
ec2_client = boto3.client('ec2', region_name=REGION, config=config)

assumed_role_object=sts_client.assume_role(RoleArn='arn:aws:iam::%s:role/%s'%(accountId,roleId),RoleSessionName="AssumeRoleSession1")
credentials=assumed_role_object['Credentials']

#ECS clusters
ecss = os.getenv('CLUSTERS').strip('][').split(', ')
asgList = os.getenv('CONTAINERIZED').strip('][').split(', ')
target_group_list = []

#asgList = ["co-asg-svc-dev-1"]
def stringAdder(placeholder, totalLength):
    spaces = " "
    diff = int(totalLength) - int(len(placeholder))
    newSpaces = diff * spaces
    return str(placeholder + str(newSpaces))


#Service and Target groups
svc_table = PrettyTable()
svc_table.field_names = [stringAdder("ECS", 30),stringAdder("Service", 40),stringAdder("Desired Tasks", 15),stringAdder("Pending Tasks", 15),stringAdder("Running Tasks", 15)]
report_svc_table = PrettyTable()
report_svc_table.field_names = [stringAdder("ECS", 30),stringAdder("Service", 40),stringAdder("Desired Tasks", 15),stringAdder("Pending Tasks", 15),stringAdder("Running Tasks", 15)]
tg_table = PrettyTable()
tg_table.field_names = [stringAdder("ECS", 30),stringAdder("Service Name", 40),stringAdder("Target Group", 40),stringAdder("Port Number", 15),stringAdder("Target Health", 15)]
fail_tg_table = PrettyTable()
fail_tg_table.field_names = [stringAdder("ECS", 30),stringAdder("Service Name", 40),stringAdder("Target Group", 40),stringAdder("Port Number", 15),stringAdder("Target Health", 15)]
instance_table = PrettyTable()
#instance_table.field_names = ["Auto scaling group","Instance ID","Lifecycle state","Health Status"]
instance_table.field_names = ["Auto scaling group","Instance ID","Private IP", "Lifecycle state","Health Status"]
fail_instance_table = PrettyTable()
fail_instance_table.field_names = ["Auto scaling group","Instance ID","Lifecycle state","Health Status"]


def fileWr(filename, action, text):
    f = open(filename, action)
    f.write(str(text))
    f.close()
    return True

def serviceCaller(ecs_list):
    serviceArns = []
    maxCall = 100
    for ecs in ecs_list:
        svc_list = ecs_client.list_services(cluster=ecs,maxResults=maxCall)
        temp_service_arns = svc_list.get('serviceArns')
        for j in temp_service_arns:
            if [ecs,j] in serviceArns:
                break
            else:
                serviceArns.append([ecs,j])
                while True:
                    if 'nextToken' in svc_list:
                        svc_list = ecs_client.list_services(cluster=ecs,maxResults=maxCall,nextToken=svc_list['nextToken'])
                    else:
                        svc_list = ecs_client.list_services(cluster=ecs,maxResults=maxCall)
                        temp_service_arns = svc_list.get('serviceArns')
                        for j in temp_service_arns:
                            if [ecs,j] in serviceArns:
                                break
                            else:
                                serviceArns.append([ecs,j])
                        if 'nextToken' not in svc_list:
                            break
                        return serviceArns

#Functions for each AWS Service checks       
def describeService(svc_list, c):
    for i in svc_list:
        if "job" not in i[0]:
            service_def = ecs_client.describe_services(cluster=i[0],services=[i[1]])
            service = service_def.get('services')
            serviceName = service[0].get('serviceName')
            desiredCount = service[0].get('desiredCount')
            pendingCount = service[0].get('pendingCount')
            runningCount = service[0].get('runningCount')
            if desiredCount != runningCount:
                c += 1
                report_svc_table.add_row([stringAdder(str(i[0]), 30),stringAdder(str(serviceName), 40), stringAdder(str(desiredCount), 15), stringAdder(str(pendingCount), 15), stringAdder(str(runningCount), 15)])
            else:
                svc_table.add_row([stringAdder(str(i[0]), 30),stringAdder(str(serviceName), 40), stringAdder(str(desiredCount), 15), stringAdder(str(pendingCount), 15), stringAdder(str(runningCount), 15)])
                lbs = service[0].get('loadBalancers')
                if lbs == []:
                    pass
        else:
            targetGroupArn = lbs[0].get('targetGroupArn')
            target_group_list.append(targetGroupArn)
            i.append(serviceName)
            i.append(targetGroupArn)
            return c
        
def describeTargetGroup(svc_list, b):
    for i in svc_list:
        if len(i) > 3:
            targetGroupDef = elbv2_client.describe_target_groups(TargetGroupArns=[i[3]])
            targetGroup = targetGroupDef.get('TargetGroups')
            targetGroupName = targetGroup[0].get('TargetGroupName')
            targetGroupHealth = elbv2_client.describe_target_health(TargetGroupArn=i[3])
            targetGroupHealths = targetGroupHealth.get('TargetHealthDescriptions')
            for j in targetGroupHealths:
                if j["TargetHealth"]["State"] == "healthy":
                    tg_table.add_row([i[0], i[2], targetGroupName, j["Target"]["Port"], j["TargetHealth"]["State"]])
                else:
                    b += 1
                    fail_tg_table.add_row([i[0], i[2], targetGroupName, j["Target"]["Port"], j["TargetHealth"]["State"]])
                    return b
                
def getIpAddress(instanceId):
    ec2Def = ec2_client.describe_instances(Filters=[{'Name':'instance-id', 'Values': [instanceId]}])
    ec2Rsv = ec2Def.get('Reservations')
    ec2Instances = ec2Rsv[0].get('Instances')
    for i in ec2Instances:
        return (i["PrivateIpAddress"])
    
def describeAsg(asg_list, a):
    for i in asg_list:
        asgDef = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[i],MaxRecords=100)
        asgGroup = asgDef.get('AutoScalingGroups')
        asgInstances = asgGroup[0].get('Instances')
        for j in asgInstances:
            if j["HealthStatus"] == "Healthy":
                instance_table.add_row([i, j["InstanceId"], getIpAddress(str(j["InstanceId"])), j["LifecycleState"], j["HealthStatus"]])
            else:
                a += 1
                instance_table.add_row([i, j["InstanceId"], getIpAddress(str(j["InstanceId"])), j["LifecycleState"], j["HealthStatus"]])
                return a
            
#Get services
finalServiceArns = serviceCaller(ecss)
#Describe Services
svcChecker1 = describeService(finalServiceArns, svcChecker)
#Describe TG and TG Health
tgChecker1 = describeTargetGroup(finalServiceArns, tgChecker)
#ASg instance health
asgChecker1 = describeAsg(asgList, asgChecker)
fileWr("ecs_service_list.txt", "w+", svc_table)
fileWr("target_group_list.txt", "w+", tg_table)
fileWr("asg_instance_list.txt", "w+", instance_table)

if svcChecker1 > 0:
    fileWr("failed_services_table.txt", "w+", report_svc_table)
if tgChecker1 > 0:
    fileWr("failed_tgs_table.txt", "w+", fail_tg_table)
if asgChecker1 > 0:
    fileWr("failed_instances_table.txt", "w+", fail_instance_table)