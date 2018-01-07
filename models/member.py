from models.card import Card


class Member:

    def __init__(self, name: str, is_active: bool, card: Card):
        self.name = name
        self.is_active = is_active
        self.card = card

    def __eq__(self, other):
        return (self.name == other.name) and \
            (self.card == other.card) and \
            (self.is_active == other.is_active)
