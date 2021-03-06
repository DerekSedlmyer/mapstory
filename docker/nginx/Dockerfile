FROM nginx:1.14-alpine
LABEL maintainer="Tyler Battle <tbattle@boundlessgeo.com>"

ENV MEDIA_ROOT=/var/lib/mapstory/media
ENV STATIC_ROOT=/var/lib/mapstory/static
ENV CONSUL_TEMPLATE_VERSION=0.18.1

VOLUME $MEDIA_ROOT

# Install tools and openssl/cert support
RUN apk --no-cache add \
    ca-certificates \
    wget

# Install consul-template
RUN set -ex \
    && mkdir /opt \
    && wget -qO /opt/consul-template.tgz https://releases.hashicorp.com/consul-template/$CONSUL_TEMPLATE_VERSION/consul-template_${CONSUL_TEMPLATE_VERSION}_linux_amd64.tgz \
    && tar xf /opt/consul-template.tgz -C /opt/ consul-template \
    && rm /opt/consul-template.tgz

COPY docker.crt /etc/nginx/
COPY docker.key /etc/nginx/

COPY config.hcl /opt/
COPY templates/ /opt/templates

COPY run.sh /opt/

CMD /opt/run.sh
