import logging
import platform
import re
import socket
import subprocess
import uuid

import psutil

logger = logging.getLogger(__name__)


def getsysteminfo():
    try:
        info = {'platform': platform.system(),
                'platform-release': platform.release(),
                'platform-version': platform.version(),
                'architecture': platform.machine(),
                'hostname': socket.gethostname(),
                'ip-address': socket.gethostbyname(socket.gethostname()),
                'mac-address': ':'.join(re.findall('..', '%012x' % uuid.getnode())),
                'processor': platform.processor(),
                'ram': str(round(psutil.virtual_memory().total / (1024.0 ** 3))) + " GB",
                'python': platform.python_version()}
        return info
    except Exception as e:
        logger.exception(e)


def get_process_uptime(service):
    p = subprocess.Popen(["systemctl", "status", service], stdout=subprocess.PIPE)
    (output, err) = p.communicate()
    output = output.decode('utf-8')

    service_regx = r"Loaded:.*\/(.*service);"
    status_regx = r"Active:(.*) since (.*);(.*)"
    service_status = {}
    for line in output.splitlines():
        service_search = re.search(service_regx, line)
        status_search = re.search(status_regx, line)

        if service_search:
            service_status['service'] = service_search.group(1)

        elif status_search:
            service_status['status'] = status_search.group(1).strip()
            service_status['since'] = status_search.group(2).strip()
            service_status['uptime'] = status_search.group(3).strip()
    return service_status
