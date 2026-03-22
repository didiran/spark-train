# kibana/Dockerfile
FROM docker.elastic.co/kibana/kibana:8.11.0

COPY --chown=kibana:kibana config/kibana.yml /usr/share/kibana/config/kibana.yml
COPY --chown=kibana:kibana export/ /usr/share/kibana/export/
COPY --chown=kibana:kibana setup-kibana.sh /usr/share/kibana/setup-kibana.sh

USER root
RUN chmod +x /usr/share/kibana/setup-kibana.sh
USER kibana

ENTRYPOINT ["/bin/sh", "-c", "/usr/share/kibana/setup-kibana.sh & /usr/local/bin/kibana-docker"]