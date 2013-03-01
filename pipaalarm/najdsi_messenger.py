from messenger import messenger, register_messenger, string_formatter

@register_messenger
class najdisi_messenger(messenger):
    def send(data):
        msg = string_formatter(data)
