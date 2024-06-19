import streamlit as st
import boto3
import json

# AWS Lambda client
lambda_client = boto3.client('lambda', region_name='us-east-1')

# Streamlit Interface
st.title('Script Runner App')

script = st.text_area('Enter your script here:')
interval = st.number_input('Interval (in minutes):', min_value=1, value=10)
email = st.text_input('Enter your email:')

if st.button('Start'):
    payload = {
        'script': script,
        'interval': interval,
        'email': email
    }
    lambda_client.invoke(
        FunctionName='your_lambda_function_name',  # Replace with your Lambda function name
        InvocationType='Event',
        Payload=json.dumps(payload)
    )
    st.success('Script scheduled to run!')

if st.button('Stop'):
    st.warning('Stop functionality not implemented yet.')
