#
# Dockerfile for ARM rsyslog's relay
#

# Run arm64 on x86 using qemu: 
# https://www.cisco.com/c/en/us/support/docs/routers/1101-industrial-integrated-services-router/214383-build-and-deploy-a-docker-iox-package-fo.html

#FROM arm64v8/alpine:latest
FROM alpine:latest

# See list of available package: https://pkgs.alpinelinux.org/packages?name=rsyslog*&branch=edge&arch=aarch64
RUN	apk --no-cache update  \
	&& apk add --no-cache --purge -uU \
        logrotate \
        rsyslog \
        rsyslog-tls \
        rsyslog-relp \
        rsyslog-mmjsonparse \
        rsyslog-mmutf8fix \ 
        tzdata \
	&& rm -rf /var/cache/apk/* /tmp/*

# Copy the qemu emulator into the container.
#COPY qemu/qemu-aarch64-static /usr/bin/

# Copy certificates
COPY certs/* /etc/ssl/rsyslog/

# Used by rsyslog when converting RFC3164 to RFC5424.
ENV TZ=UTC

# Copy rsyslog configuration files.
COPY rsyslog.conf /etc/rsyslog.conf
COPY rsyslog.conf.d/*.conf /etc/rsyslog.conf.d/

# Hold log files if the container is configured to write them (store and forward).
VOLUME [ "/var/lib/rsyslog"]

# Runs with -dn if debugging required.
ENTRYPOINT [ "rsyslogd", "-n" ]