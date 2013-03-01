from unittest import TestCase
from mock import Mock

from pipaalarm.arping import arping, device

class unit_tests(TestCase):
    def setUp(self):
        self.a = arping("192.168.1.0/24", interval=0.1)

    def test_scanner(self):
        self.a.monitored_devices = set([
            device("192.168.1.3", "11:22:33:44:55:88"),
            device("192.168.1.4", "11:22:33:44:55:99"),
            device("192.168.1.5", "11:22:33:44:55:00")
        ])
        self.a.active_devices = set([
            device("192.168.1.1", "11:22:33:44:55:66"),
            device("192.168.1.2", "11:22:33:44:55:77"),
            device("192.168.1.3", "11:22:33:44:55:88"),
            device("192.168.1.4", "11:22:33:44:55:99")
        ])
        self.a.warned_devices = set([
            device("192.168.1.3", "11:22:33:44:55:88"),
        ])

        self.a.scan = Mock(side_effect=[
            set([device("192.168.1.2", "11:22:33:44:55:77"),
                 device("192.168.1.3", "11:22:33:44:55:88"),
                 device("192.168.1.5", "11:22:33:44:55:00")]),
            set([device("192.168.1.2", "11:22:33:44:55:77"),
                 device("192.168.1.3", "11:22:33:44:55:88")]),
            ValueError
        ])
        self.a.warn = Mock()

        try: self.a.scanner()
        except ValueError: pass

        self.a.warn.assert_any_call(
            set([device("192.168.1.4", "11:22:33:44:55:99")])
        )
        self.a.warn.assert_any_call(
            set([device("192.168.1.5", "11:22:33:44:55:00")])
        )

    def test_pinger(self):
        self.a.monitored_devices = set([
            device("192.168.1.2", "11:22:33:44:55:77"),
            device("192.168.1.3", "11:22:33:44:55:88"),
            device("192.168.1.4", "11:22:33:44:55:99")
        ])
        self.a.active_devices = set([
            device("192.168.1.1", "11:22:33:44:55:66"),
            device("192.168.1.2", "11:22:33:44:55:77"),
            device("192.168.1.3", "11:22:33:44:55:88"),
            device("192.168.1.4", "11:22:33:44:55:99")
        ])

        self.a.scan_active_devices = Mock(
            side_effect=[
                set([device("192.168.1.2", "11:22:33:44:55:77"),
                     device("192.168.1.3", "11:22:33:44:55:88")]),
                set([device("192.168.1.3", "11:22:33:44:55:88")])
            ]
        )
        self.a.warn = Mock(
            side_effect=[None, ValueError]
        )

        try: self.a.pinger()
        except ValueError: pass

        expected = set([device("192.168.1.2", "11:22:33:44:55:77"),
                        device("192.168.1.4", "11:22:33:44:55:99")])

        self.assertEqual(self.a.warned_devices, expected)
        self.a.warn.assert_any_call(
                         set([device("192.168.1.4", "11:22:33:44:55:99")])
        )
        self.a.warn.assert_any_call(
            set([device("192.168.1.2", "11:22:33:44:55:77")])
        )
