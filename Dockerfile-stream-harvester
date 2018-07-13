FROM gwul/sfm-base@sha256:e68cb98bdc9dc23bbed734f3e507a0ffb866b007dffea038b6af8d88a62150e6
MAINTAINER Social Feed Manager <sfm@gwu.edu>

# Install supervisor
RUN apt-get update && apt-get install -y \
    supervisor=3.3*
VOLUME /etc/supervisor/conf.d

ADD . /opt/sfm-twitter-harvester/
WORKDIR /opt/sfm-twitter-harvester
RUN pip install -r requirements/common.txt -r requirements/release.txt

ADD docker/stream-harvester/invoke.sh /opt/sfm-setup/
RUN chmod +x /opt/sfm-setup/invoke.sh

ENTRYPOINT ["/opt/sfm-setup/invoke.sh"]
