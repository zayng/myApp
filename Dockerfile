FROM tiangolo/uwsgi-nginx-flask:flask-python3.5

# If you're going to need to troubleshoot with vim
# RUN apt-get -y update && apt-get -y install vim

ADD requirements.txt /tmp/requirements.txt 

RUN pip install -r /tmp/requirements.txt 

# Assuming you're in the directory

EXPOSE 80 443 5000

COPY . /app
