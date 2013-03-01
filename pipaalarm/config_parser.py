import configparser

class config_parser(object):
    def __init__(self, config_file):
        self.config_file = config_file

        self.config = configparser.ConfigParser()

    def getParam(self, name, default):
        self.config.read(self.config_file)

        if "config" in self.config:
            if name in self.config["config"]:
                return self.config["config"][name]

        return default

    def getScanRange(self):
        return self.getParam("scan_range", "192.168.2.0/24")

    def getUsername(self):
        return self.getParam("username", "username")

    def getPassword(self):
        return self.getParam("password", "password")

    def getNumbers(self):
        return self.getParam("numbers", "041928491").split(",")

    def getClients(self):
        self.config.read(self.config_file)

        clients = []
        if "config" in self.config:
            if "clients" in self.config["config"]:
                for client in self.config["config"]["clients"].split(","):
                    if not client in self.config:
                        continue

                    if not "mac" in self.config[client]:
                        continue

                    clients.append((client, self.config[client]))

        return clients

    def addClient(self, client, mac):
        self.config.read(self.config_file)
        conf = self.config["config"]

        if not client in self.config:
            if not "clients" in conf:
                conf["clients"] = ""

            self.config.add_section( client )
            conf["clients"] = ",".join(conf["clients"].split(",") + [client])

        self.config[client]["mac"] = mac
        self.save()

    def removeClient(self, client):
        self.config.read(self.config_file)
        conf = self.config["config"]

        if client in self.config:
            self.config.remove_section(client)

        conf["clients"] = ",".join([x for x in conf["clients"].split(",") if x!=client])
        self.save()

    def save(self):
        with open(self.config_file, 'w') as configfile:
           self.config.write(configfile)
