# Configuration

Configurable parameters (client timeout, retries, backoff factors, etc.) are defined in a configuration file - [config.ini](../config_modules_vmware/services/config.ini). These define the default configuration parameters for config-modules.

## Overriding configuration

To override these default configuration values, either replace the values in the `config.ini` file or add a file `config-overrides.ini` with the values to override. If providing a `config-overrides.ini` file, set the environment variable `OVERRIDES_PATH` to the directory containing the file. Any values defined in `config-overrides.ini` will take precedence over the defaults. 

### Overriding configuration via SaltStack

1. Create a config-overrides.ini file with the corresponding overrides
```text
# Enabling metadata publishing
[metadata]
PublishMetadata=true
```

2. Copy config-overrides.ini file to some directory on the targetted minion (here it is `/opt/saltstack/salt/extras-3.10/config_modules_vmware/services/` but can be any directory)
```shell
salt-cp --chunked -G 'product:<<product_category>>' config-overrides.ini /opt/saltstack/salt/extras-3.10/config_modules_vmware/services/
```

3. Set the "OVERRIDES_PATH" env variable to that same directory
```shell
salt -G 'product:<<product_category>>' environ.setenv '{"OVERRIDES_PATH": "/opt/saltstack/salt/extras-3.10/config_modules_vmware/services/"}' update_minion=True
```