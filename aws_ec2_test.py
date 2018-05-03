#!/usr/bin/env python


#  Need to be installed:
#  pip install termcolor
#  pip install colorama - Only for windows cmd
#  pip install boto3
#  

import boto3 # Boto library
from termcolor import colored # Add colors to console print
from colorama import init # For add color in windows cmd
from platform   import system as system_name  # Returns the system/OS name
from subprocess import call   as system_call  # Execute a shell command
from urllib2 import Request, urlopen, URLError # For our curl function
import datetime # Datetime
import socket
import warnings # Bug on windows with unicode warning
warnings.filterwarnings("ignore", category=UnicodeWarning) # Bug on windows with unicode warning

init() # init cmd color
date = datetime.datetime.now().strftime('%Y/%m/%dT%H-%M-%S')
hosts = ['foropsworks.tk', 'a.foropsworks.tk', 'b.foropsworks.tk']

akey = raw_input("Enter your Access key ID: ")
skey = raw_input("Enter your Secret access key: ")

def curl(host):
    req = Request(host)
    try:
        response = urlopen(req)
    except URLError as e:
    
        if hasattr(e, 'code'):
            print (format(colored('The server couldn\'t fulfill the request.', 'red')))
            print ('Error code: {0}'.format(colored(e.code, 'red')))
        elif hasattr(e, 'reason'):
            print (format(colored('We failed to reach a server.', 'red')))
            print ('Reason: {0}'.format(colored(e.reason[0], 'red')))
    else:
        print (response.getcode()).format(colored('red'))

def ping(host):

    # Ping command count option as function of OS
    param = '-n 1' if system_name().lower() == 'windows' else '-c 1'

    # Building the command. Ex: "ping -c 1 or ping -n 1"
    command = "ping " + param + " " + host
    # Pinging
    return system_call(command) == 0

def check_ssh(host):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.setdefaulttimeout(5)
    port = 22  # port number is a number, not string
    try:
        s.connect((host, port))
        print (format(colored('Host port 22 is open!', 'green')))
    except socket.error as e: 
        print ("Something's wrong with {0}:{1}. Exception is: {2}" .format(
            colored(host, 'cyan' ),
            colored(port, 'cyan'),
            colored(e, 'red')))
    finally:
        s.close()

for host in hosts:
    print (format(colored('Ping the host:', 'cyan')))
    print (format(colored('Server is OK!', 'green')) if ping(host) == True else format(colored('Server is not responding!', 'red')))
    print (format(colored('Try to get HTTP responce from host:', 'cyan')))
    curl('http://' + host)
    print (format(colored('Check ssh port:', 'cyan')))
    check_ssh(host)

filters = [{'Name': 'tag:Name', 'Values': ['Ivanov_Oleg_1st', 'Ivanov_Oleg_2nd', 'Ivanov_Oleg_3rd']}]
ec2 = boto3.resource('ec2',aws_access_key_id = akey, aws_secret_access_key = skey, region_name = 'eu-west-1')

def deregister_old_images():
    images = ec2.images.filter(Owners=["self"])
    deleted_images = []
    for image in images:
        created_at = datetime.datetime.strptime(image.creation_date, "%Y-%m-%dT%H:%M:%S.000Z")
        if datetime.datetime.now() - created_at > datetime.timedelta(days = 7):
            deleted_images.append(image.id)
            image.deregister()
    print 'Deleting images older than week:'
    for item in deleted_images:
        print (format(colored(item, 'red')))

def create_image():
    print (format(colored('Creating image and add tag Name:', 'cyan')))
    responce = i.create_image(
        InstanceId =ami_id,
        Name = 'ion_image' + date,
        NoReboot = True
    )
    image = ec2.Image(responce.id)
    image.create_tags(
        Tags=[
            {
                'Key': 'Name',
                'Value': ami_name
            },
    ])
    print (format(colored('Image was created, image id:' + responce.id, 'green')))

def terminate_stopped_instance():
    print (format(colored('Terminating instance: ' + i.id, 'red')))
    i.terminate()

for i in ec2.instances.filter(Filters = filters):
    for tag in i.tags:
        if tag['Key'] == 'Name':
            if i.state['Name'] == 'stopped':
                ami_name = tag['Value'] + '-' + date
                ami_id = i.id
                create_image()
                terminate_stopped_instance()

deregister_old_images()

for i in ec2.instances.filter(Filters = filters):
    for tag in i.tags:   
        print("Name: {0}\tId: {1}\tState: {2}\tLaunched: {3}".format(
            colored(tag['Value'], 'cyan'),
            colored(i.id, 'cyan'),
            colored(i.state['Name'], 'green') if i.state['Name'] == 'running' else colored(i.state['Name'], 'red') ,
            colored(i.launch_time, 'cyan')
        ))
print("--------------------------------------------------------------------------------------------------------------")