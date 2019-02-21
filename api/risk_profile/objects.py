class Home(object):
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def asdict(self):
        return {'key': self.key, 'value': self.value}


class Auto(object):
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def asdict(self):
        return {'key': self.key, 'value': self.value}


class Profile(object):
    def __init__(self, auto, disability, home, life, umbrella):
        self.auto = auto
        self.disability = disability
        self.home = home
        self.life = life
        self.umbrella = umbrella
