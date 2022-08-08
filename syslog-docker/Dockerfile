#
# Dockerfile for ARM rsyslog's relay
#

# Run arm64 on x86 using qemu: 
# https://www.cisco.com/c/en/us/support/docs/routers/1101-industrial-integrated-services-router/214383-build-and-deploy-a-docker-iox-package-fo.html

# multiarch/qemu-user-static:$to_arch
FROM multiarch/qemu-user-static:aarch64 as qemu
FROM arm64v8/alpine:latest

ARG CONFIG_FILE
ARG EXTRA_CONFIG_FILE

MAINTAINER Egon Scheer <e.scheer@student.uliege.be>
LABEL Description="Reliable syslog relay for IOx"

# Copy the qemu emulator into the container.
COPY --from=qemu /usr/bin/qemu-aarch64-static /usr/bin

# Add community packages (for cgroup-tools, but using it for resource control still triggers an OOM)
# RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories

# See list of available package: https://pkgs.alpinelinux.org/packages?name=rsyslog*&branch=edge&arch=aarch64
RUN	apk --no-cache update  \
	&& apk add --no-cache --purge -uU \
        bash \
        logrotate \
        rsyslog \
        rsyslog-tls \
        rsyslog-mmnormalize \
        rsyslog-elasticsearch \
        tzdata \
	&& rm -rf /var/cache/apk/* /tmp/*

# Used by rsyslog for RFC 3339 timestamp.
ENV TZ=UTC

# Copy rsyslog configuration files.
COPY ${CONFIG_FILE} /etc/rsyslog.conf
COPY ${EXTRA_CONFIG_FILE} /etc/rsyslog.conf.d/

# Hold log files if the container is configured to write them (store and forward).
VOLUME [ "/var/lib/rsyslog"]

# Copies the wrapper (entrypoint).
COPY start.sh /

ENTRYPOINT ["./start.sh"]