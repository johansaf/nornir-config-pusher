# Nornir config pusher
Small [Nornir](https://nornir.readthedocs.io/en/latest/) runbook for reading devices from Netbox and pushing small config snippets to them,.

If you use something older than Python3 v3.10 some minor code changes are necessary.

## Installation
### Clone the repo
`git clone https://github.com/johansaf/nornir-config-pusher.git`

### Create the virtual environment
```shell
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install --upgrade pip
$ pip install -r requirements.txt
```

### Modify the configuration
```shell
$ cp config_example.yaml config.yaml
$ cp defaults_example.yaml defaults.yaml
```

Change the `username` and `password` parameter in the `defaults.yaml` file to match your login. Modify the other parameters as you see fit.

## Usage
### Create the configuration files
Create the configuration that should be pushed to devices in the `configs/` directory. Name each file after the NAPALM driver that's used, for instance `huawei_vrp.txt` and `ios.txt`.

In my experience it's better to push do smaller config changes in batches, rather than trying to do several changes in one push. If you want to update for instance two ACLs then do each ACL in two runs instead of doing both at the same time.

### Run
```shell
$ python main.py
```

### Problems?
If there seems to be a problem two variables can be changed to show debug output. Change the `verbose` variable `defaults.yaml` to `true` and `to_console` to `true` in the `config.yaml` file.
