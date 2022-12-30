# Set base image (host OS)
FROM python:slim

# By default, listen on port 5000
EXPOSE 5000/tcp

# Set the working directory in the container
WORKDIR /app

# Copy the content of the local src directory to the working directory
COPY /app .

# Install any dependencies
RUN pip install -r requirements.txt

EXPOSE 5000

# Specify the command to run on container start
CMD [ "python", "server.py" ]