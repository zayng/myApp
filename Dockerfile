FROM python:3.5

MAINTAINER susume <orcexzy@163.com>
# Install uWSGI
RUN pip install uwsgi

# Standard set up Nginx
#ENV NGINX_VERSION 1.9.11-1~jessie
#
#RUN apt-key adv --keyserver hkp://pgp.mit.edu:80 --recv-keys 573BFD6B3D8FBC641079A6ABABF5BD827BD9BF62 \
#	&& echo "deb http://nginx.org/packages/mainline/debian/ jessie nginx" >> /etc/apt/sources.list \
#	&& apt-get update \
#	&& apt-get install -y ca-certificates nginx=${NGINX_VERSION} gettext-base \
#	&& rm -rf /var/lib/apt/lists/*
## forward request and error logs to docker log collector
#RUN ln -sf /dev/stdout /var/log/nginx/access.log \
#	&& ln -sf /dev/stderr /var/log/nginx/error.log

ENV NGINX_VERSION 1.10.1-1~jessie

RUN apt-key adv --keyserver hkp://pgp.mit.edu:80 --recv-keys 573BFD6B3D8FBC641079A6ABABF5BD827BD9BF62 \
	&& echo "deb http://nginx.org/packages/debian/ jessie nginx" >> /etc/apt/sources.list \
	&& apt-get update \
	&& apt-get install --no-install-recommends --no-install-suggests -y \
						ca-certificates \
						nginx=${NGINX_VERSION} \
						nginx-module-xslt \
						nginx-module-geoip \
						nginx-module-image-filter \
						nginx-module-perl \
						nginx-module-njs \
						gettext-base \
	&& rm -rf /var/lib/apt/lists/*

# forward request and error logs to docker log collector
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
	&& ln -sf /dev/stderr /var/log/nginx/error.log

#ENV NGINX_VERSION 1.11.4-1~jessie
#
#RUN apt-key adv --keyserver hkp://pgp.mit.edu:80 --recv-keys 573BFD6B3D8FBC641079A6ABABF5BD827BD9BF62 \
#	&& echo "deb http://nginx.org/packages/mainline/debian/ jessie nginx" >> /etc/apt/sources.list \
#	&& apt-get update \
#	&& apt-get install --no-install-recommends --no-install-suggests -y \
#						ca-certificates \
#						nginx=${NGINX_VERSION} \
#						nginx-module-xslt \
#						nginx-module-geoip \
#						nginx-module-image-filter \
#						nginx-module-perl \
#						nginx-module-njs \
#						gettext-base \
#	&& rm -rf /var/lib/apt/lists/*
#
## forward request and error logs to docker log collector
#RUN ln -sf /dev/stdout /var/log/nginx/access.log \
#	&& ln -sf /dev/stderr /var/log/nginx/error.log

#EXPOSE 80 443
EXPOSE 5050
# Finished setting up Nginx


# Make NGINX run on the foreground
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
# Remove default configuration from Nginx
RUN rm /etc/nginx/conf.d/default.conf
# Copy the modified Nginx conf
COPY nginx.conf /etc/nginx/conf.d/
# Copy the base uWSGI ini file to enable default dynamic uwsgi process number
COPY uwsgi.ini /etc/uwsgi/

# Install Supervisord
RUN apt-get update && apt-get install -y supervisor \
&& rm -rf /var/lib/apt/lists/*
# Custom Supervisord config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

ADD requirements.txt /tmp/requirements.txt 

RUN pip install -r /tmp/requirements.txt 

COPY . /app
WORKDIR /app

CMD ["/usr/bin/supervisord"]
