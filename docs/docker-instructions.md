# Running the Config Modules API server in Docker
## Building the Docker image
To build the docker image, run the following command in the repo's root directory:
```shell
docker build -t config-modules-server .
```

## Running the Docker container
###With ssl certs and config overrides:
```shell
docker run -p 443:443 \
  -v /etc/ssl/certs/:/etc/ssl/certs/vmware/ \
  -v /etc/opt/config-modules/config-overrides.ini:/usr/lib/config-modules/config-overrides.ini \
  --env SERVER_CERT=cert.pem \
  --env SERVER_KEY=key.pem \
  --env OVERRIDES_PATH=/usr/lib/config-modules \
  -d --name config-modules \
  config-modules-server
```
where,
* /etc/ssl/certs/vmware contains both server cert for northbound APIs and client certs for southbound connections.
* /etc/opt/config-modules/config-overrides.ini is a file containing any configuration overrides. Must be absolute path. If the file is not provided or for any keys omitted, default values will be used. The mount directory should match the path specified by `OVERRIDES_PATH` and the file should be named `config-overrides.ini`
* SERVER_CERT is the certificate filename, located under /etc/ssl/certs/ in the host, to use for the northbound APIs,
* SERVER_KEY is the private key filename, located under /etc/ssl/certs/ in the host, used to validate the public server certificate,
* OVERRIDES_PATH is the path to the directory containing any override files (e.g. config-overrides.ini). This will be the path within the container which the override files will be retrieved.

###Without ssl certs or config overrides:
```shell
docker run -p 80:80 \
  -d --name config-modules \
  config-modules-server
```

## Accessing the APIs
After running, the config modules APIs can be accessed at 127.0.0.1.
###If using ssl certs
```shell
curl --cacert /etc/ssl/certs/cert.pem --location 'https://127.0.0.1/config-modules/about'
```
The Swagger UI can be accessed at https://127.0.0.1:443/config-modules/docs  

###If not using ssl certs
```shell
curl --location 'http://127.0.0.1:80/config-modules/about'
```
The Swagger UI can be accessed at http://127.0.0.1:80/config-modules/docs.
