FROM photon:4.0-20240507

WORKDIR /usr/lib/config-modules

COPY ./config_modules_vmware ./config_modules_vmware
COPY ./devops/scripts ./devops/scripts
COPY ./requirements ./requirements

# Install Python and dependencies.
RUN tdnf install -y python3 python3-pip &&\
    python3 -m pip install -r requirements/api-requirements.txt

EXPOSE 443

ENTRYPOINT ["./devops/scripts/start_api_server.sh"]
