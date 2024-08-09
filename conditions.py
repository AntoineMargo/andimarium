
class Condition:
    def __init__(self, name, effects: list):
        self.name = name
        self.effects = effects
    def __str__(self):
        return f"{self.name}"
    
dying = Condition("dying", [])