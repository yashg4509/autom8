import streamlit as st
import boto3
import json
import time
import threading
import schedule
import configparser
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

config = configparser.ConfigParser()

SENDGRID_API_KEY = st.secrets["sg_api_key"]
AWS_LAMBDA_FUNCTION_NAME = st.secrets["aws_func_name"] # Replace with your Lambda function name

# Function to send email using SendGrid
def send_email(to_email, subject, body):
    message = Mail(
        from_email=st.secrets["email"],
        to_emails=to_email,
        subject=subject,
        html_content=body)
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return response.status_code
    except Exception as e:
        return str(e)

# Function to run the script using AWS Lambda
def run_script(script):
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    response = lambda_client.invoke(
        FunctionName=AWS_LAMBDA_FUNCTION_NAME,
        InvocationType='RequestResponse',
        Payload=json.dumps({'script': script})
    )
    return json.load(response['Payload'])

# Function to monitor and send email updates
def monitor_and_send_email(script, interval, email, monitor_keywords):
    try:
        result = run_script(script)
        output = result.get('output', 'No output captured')
        status = result.get('statusCode', 500)

        # Check for monitoring keywords in the output
        monitored_results = []
        for keyword in monitor_keywords:
            if keyword in output:
                monitored_results.append(keyword)

        if status == 200:
            body = f'Script executed successfully.<br>Output:<br>{output}'
        else:
            body = f'Script execution failed with status code {status}.<br>Output:<br>{output}'

        if monitored_results:
            body += f'<br><br>Monitored Results:<br>{", ".join(monitored_results)}'

        send_email(email, 'Script Execution Report', body)
    except Exception as e:
        send_email(email, 'Script Execution Error', str(e))

# Function to run the script periodically
def schedule_script(script, interval, email, monitor_keywords):
    schedule.every(interval).minutes.do(monitor_and_send_email, script=script, interval=interval, email=email, monitor_keywords=monitor_keywords)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Streamlit Interface
st.title('Script Runner App')

script = st.text_area('Enter your script here:')
interval = st.number_input('Interval (in minutes):', min_value=1, value=10)
email = st.text_input('Enter your email:')
run_continuously = st.checkbox('Run continuously')
monitor_keywords = st.text_input('Enter keywords to monitor (comma-separated):').split(',')

if st.button('Start'):
    if run_continuously:
        threading.Thread(target=schedule_script, args=(script, interval, email, monitor_keywords)).start()
    else:
        threading.Thread(target=monitor_and_send_email, args=(script, interval, email, monitor_keywords)).start()
    st.success('Script scheduled to run!')

if st.button('Stop'):
    schedule.clear()
    st.warning('Script scheduling stopped.')
