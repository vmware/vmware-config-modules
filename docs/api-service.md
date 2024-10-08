# API Service

Config-module functions are exposed as APIs using FastAPI framework. Below are steps to build and run config-modules as an API service:

1. Build config-modules artifact:
    ```shell
    ./devops/scripts/build.sh
    ```
2. Install config-modules along with extra **api** layer:
    ```shell
    python3 -m pip install 'dist/config_modules-*-py3-none-any.whl[api]' --force-reinstall
    ```
3. Start the server:
    ```shell
    ./devops/scripts/start_api_server.sh
    ```

The above commands will start the api server at http://127.0.0.1:80. Swagger UI can be accessed at http://127.0.0.1:80/config-modules/docs.

**Note:** API service requires minimum of python 3.8 as a dependency.
