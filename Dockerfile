FROM ubuntu

ENV DEBIAN_FRONTEND noninteractive

RUN apt update
RUN apt install -y python3-dev python3-pip

RUN python3 -m pip install --no-cache blackclue blackvue_gps hansken_extraction_plugin

LABEL maintainer="fbda@nfi.nl"
LABEL hansken.extraction.plugin.image="blackvue"
LABEL hansken.extraction.plugin.name="Blackvue"

COPY . /

EXPOSE 8999

ENTRYPOINT ["/usr/local/bin/serve_plugin"]
CMD ["blackvue.py", "8999"]
