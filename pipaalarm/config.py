from config_parser import config_parser
from arping import arping, device
from dispatcher import dispatcher

config_file = "pipaalarm.ini"
config = config_parser(config_file)

arping = arping(ip_range = config.getScanRange())
arping.monitored_devices |= (
    set([device("", d[1]["mac"]) for d in config.getClients()])
)
dispatcher = dispatcher(config, arping.warnings)
