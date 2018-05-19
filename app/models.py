class Station:
    def __init__(self):
        self.place_id = None
        self.name = None
        self.brand= None
        self.cre_id = None
        self.category = None
        self.address = None
        self.lat = None
        self.lng = None
        self.prices = list()

class Price:
    def __init__(self):
        self.type = None
        self.price = None
