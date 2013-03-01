import __builtin__
import logging
import time
import gevent

from datetime import datetime
from pprint import pformat

from gevent.queue import Queue
from gevent.coros import BoundedSemaphore

from pysms.providers import NajdiSiSms

# HAck to import scapy
scapy_builtins = __import__("scapy.all",globals(),locals(),".").__dict__
__builtin__.__dict__.update(scapy_builtins)

conf.verb = 0

class device(object):
    def __init__(self, ip, mac):
        self.ip = ip
        self.mac = mac

    def __eq__(self, device):
        # Equality check is only made on mac,
        # because that's only unique indicator
        return self.mac == device.mac

    def __hash__(self):
        # Equality check is only made on mac,
        # because that's only unique indicator
        return hash(self.mac)

    def __repr__(self):
        return "Device {ip:`%s`, mac:`%s`}" %(self.ip, self.mac)

class arping(object):
    def __init__(self, ip_range, interval = 10):
        self.logger = logging.getLogger(__name__)

        self.ip_range = ip_range
        self.interval = interval

        self.active_devices_lock = BoundedSemaphore(1)
        self.active_devices = set()
        self.monitored_devices = set()
        self.warned_devices = set()

        self.run = True
        self.warnings = Queue()

    def start(self):
        self.logger.info("Starting arping")
        self.run = True
        self.scanner_worker = gevent.spawn(self.scanner)
        self.pinger_worker = gevent.spawn(self.pinger)

    def stop(self):
        if self.run:
            self.logger.info("Stopping arping")
            self.run = False
            self.pinger_worker.join()
            self.scanner_worker.join()
            self.logger.info("Arping stopped")

    def scan(self, ip, timeout = 5):
        try:
            ans,unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip),
                        timeout = timeout)
        except Exception:
            self.logger.warning("Problem sending packets, some wierd bug down there,"
                                " wait, retry and hopefully everything will be ok")
            time.sleep(5)
            ans,unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip),
                        timeout = timeout)

        active_devices = set()
        for snd,rcv in ans:
            active_devices.add(device(rcv.psrc, rcv.src))

        return active_devices

    def get_active_devices(self):
        return self.active_devices

    def scan_active_devices(self, devices):
        scanned = self.scan([device.ip for device in devices], 3)
        return scanned

    def warn(self, devices):
        if not devices: return

        self.logger.warning("Devices got missing, raising alarm: %s", pformat(devices))
        self.warnings.put_nowait((datetime.now(), devices))

    def get_warning(self):
        return self.warnings.get()

    def scanner(self):
        self.logger.info("Starting scanner")
        while self.run:
            active_devices = self.scan(self.ip_range)
            self.logger.info("Active devices update\n%s", pformat(active_devices))
            with self.active_devices_lock:
                removed = self.active_devices - active_devices - self.warned_devices
                self.active_devices = active_devices - self.warned_devices
                self.warned_devices = set()
                self.warn(removed - (removed - self.monitored_devices))

            if self.run: time.sleep(self.interval)

        self.logger.info("Scanner stopped")

    def pinger(self):
        self.logger.info("Starting pinger")
        while self.run:
            with self.active_devices_lock:
                scan_devices = self.active_devices - (self.active_devices - self.monitored_devices)
                self.logger.debug("Scanning monitored devices\n%s",
                                  pformat(scan_devices))
                # For all active & monitored devices warn if they are not active
                warn_devices = scan_devices - self.scan_active_devices(scan_devices)
                self.logger.debug("Monitored devices scanned")

                self.warned_devices |=  warn_devices
                self.active_devices -= warn_devices
                self.warn(warn_devices)

            if self.run: time.sleep(0.3)

        self.logger.info("Pinger stopped")
