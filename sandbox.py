import configparser
import os

def create_config():
	config = configparser.ConfigParser()

	# Add sections and key-value pairs
	config['General'] = {'sg_api_key': os.environ['sg_api_key'], 'aws_func_name': os.environ['aws_func_name'], 'email': os.environ['email']}
	
	# Write the configuration to a file
	with open('config.ini', 'w') as configfile:
		config.write(configfile)


if __name__ == "__main__":
	create_config()
