import gevent

from gevent.queue import Empty

from pysms import SmsException
from pysms.providers import NajdiSiSms

class dispatcher(object):
    def __init__(self, config, warnings, messengers = None):
        self.config = config
        self.warnings = warnings
        self.messengers = messengers

        self.sms = NajdiSiSms("username", "password")

    def start(self):
        self.run = True
        self.dispatcher_worker = gevent.spawn(self.dispatcher)

    def stop(self):
        self.run = False
        self.dispatcher_worker.join()

    def dispatcher(self):
        while self.run:
            warnings = []
            warning = True
            while warning:
                try:
                    warning = self.warnings.get(timeout = 1)
                except Empty:
                    break
                warnings.append(warning)

            if not warnings: continue
            print "processing new warnings"

            clients = self.config.getClients()
            for devices in warnings:
                time = devices[0]
                for device in devices[1]:
                    client = filter(lambda c: c[1]["mac"] == device.mac,
                                    clients)
                    if not client: client = [("unknown", {"mac": device.mac})]

                    client= client[0]

                    for number in self.config.getNumbers():
                        try:
                            self.sms.send(number,
                                "Device %s with mac %s got missing at %s"
                                %(client[0], client[1]["mac"], time.strftime("%H:%M:%S")))
                        except SmsException:
                            pass

class messenger(object):
    def send(data):
        raise NotImplementedError

class formatter(object):
    def format(data):
        raise NotImplementedError

class string_formatter(formatter):
    def format(data):
        return "Device with name {name} stolen at {time:%H:%M:%S}!".format(**data)
