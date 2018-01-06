class Card:

    def __init__(self, fc, cc, dec):
        self.fc = fc
        self.cc = cc
        self.dec = dec

    def __eq__(self, other):
        return (self.fc == other.fc) and (self.cc == other.cc) and (self.dec == other.dec)
