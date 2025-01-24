import re

class Item:
    name = ""
    modifiers = []



    def __init__(self, identifier):
        self.identifier = identifier
        self.parse_identifier(identifier)

    def parse_identifier(self, identifier):
        match = re.search(r'[a-z][A-Z]', identifier)

        if match:
            name_end = match.start()
            name_end += 1
            self.name = identifier[:name_end]
            self.modifiers = list(identifier[name_end:])
        else:
            self.name = identifier

    def __str__(self):
        #return self.name + "\t" + str(self.modifiers)
        return self.name + "\t" + str(self.modifiers)