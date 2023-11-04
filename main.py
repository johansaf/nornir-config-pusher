# pylint: disable=missing-module-docstring,missing-function-docstring,redefined-outer-name

import resource

from nornir_napalm.plugins.tasks import napalm_configure
from tqdm import tqdm

from nornir import InitNornir
from nornir.core.inventory import Host
from nornir.core.task import Task

configs = {}


class PlatformNotFound(Exception):
    pass


def get_config(platform: str) -> str:
    try:
        # pylint: disable=invalid-name
        with open(file=f"configs/{platform}.txt", mode="r", encoding="utf-8") as fp:
            return ''.join(fp.readlines())
    except FileNotFoundError:
        return ""


def transform_host(host: Host) -> None:
    # This function transform the netbox data into a format that napalm can use.
    # For instance using the netbox platform and converting that into the appropriate
    # napalm module
    host.hostname = host.get("name")

    match host.platform:
        case "cisco-ios":
            host.platform = "ios"
        case "cisco-ios-xe":
            host.platform = "ios"
        case "huawei-vrp-v5":
            host.platform = "huawei_vrp"
        case _:
            raise PlatformNotFound(
                f"Could not transform platform {host.platform}")

    configs[host.platform] = get_config(host.platform)


def push_config(task: Task, progress_bar: tqdm) -> None:
    # if the config doesn't exist, skip this host.
    if len(configs[task.host.platform]) == 0:
        return

    task.host.open_connection("napalm", configuration=task.nornir.config)
    task.run(task=napalm_configure,
             configuration=configs[task.host.platform],
             replace=False,    # Change to true for replacing the config, instead of merging
             dry_run=False
             )
    progress_bar.update()
    tqdm.write(f"{task.host}: config updated")
    task.host.close_connection("napalm")
    return


if __name__ == "__main__":
    # Raise resource limits, we're probably going to hit limits once
    # we start connecting to devices
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    resource.setrlimit(resource.RLIMIT_NOFILE, (4096, hard))

    nr = InitNornir(config_file="config.yaml")

    # https://github.com/twin-bridges/nornir_course/blob/4a10b472cf01dc94b811d1c06b9d53c84aa68fe9/nornir3_changes.md
    for host in nr.inventory.hosts.values():
        transform_host(host)

    # Execute the task and show a fancy progress bar
    # pylint: disable=line-too-long
    with tqdm(total=len(nr.inventory.hosts), desc="updating config") as progress_bar:
        nr.run(task=push_config, progress_bar=progress_bar)

    print("=" * 50)
    if len(nr.data.failed_hosts) > 0:
        print("Some hosts failed and requires attention:")
        for host in nr.data.failed_hosts:
            print(f"- {host}")
    else:
        print("All hosts seems to have completed successfully!")
