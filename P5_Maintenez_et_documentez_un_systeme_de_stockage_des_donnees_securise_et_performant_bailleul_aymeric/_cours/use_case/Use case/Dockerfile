# base image
FROM python:latest

# copy just the requirements.txt first to leverage Docker cache
# install all dependencies for Python app
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

# install dependencies in requirements.txt
RUN pip install -r requirements.txt

# copy all content to work directory /app
COPY . /app

# specify the port number the container should expose
EXPOSE 5000

# run the application
CMD ["python", "/app/main.py"]