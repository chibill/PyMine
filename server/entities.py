class Entity:
    def __init__(self, eid, position=(0,64,0), look=(0, 0),type = "", name="", uuid="", inventory=None):
        self.EID = eid
        self.location = position
        self.look = look
        self.type = type
        self.name = name
        self.uuid = uuid
        self.inventory = inventory