from activities import *

class Talent:
    def __init__(self, name: str, activities: list = None, bonuses: dict = None, rank: int = 1) -> None:
        self.name = name
        self.activities = activities or []
        self.bonuses = bonuses or {}
        self.rank = rank

    def apply(self, character) -> None:
            if self.bonuses:
                for attribute, bonus in self.bonuses.items():
                    method_name = attribute + "_change"
                    method = getattr(character, method_name, None)
                    if method is not None:
                        method(bonus)

    def unapply(self, character) -> None:
            if self.bonuses:
                for attribute, bonus in self.bonuses.items():
                    method_name = attribute + "_change"
                    method = getattr(character, method_name, None)
                    if method is not None:
                        method(-bonus)

    def __str__(self) -> str:
        return f"{self.name}"
    
    def __repr__(self) -> str:
        return f"{self.name}"


class Spellcasting(Talent):
    def __init__(self, name: str, table: dict = None, rank: int = 1) -> None:
        super().__init__(name, activities=[], bonuses={}, rank=rank)
        self.table = table or {}

    def load_table(self, character) -> None:
        if self.table:
            if hasattr(character, "spellcasting_table"):
                setattr(character, "spellcasting_table", self.table)

    def unload_table(self, character) -> None:
        if hasattr(character, "spellcasting_table"):
            setattr(character, "spellcasting_table", {})


mage_spellcasting_table =  {1:[3],
                            2:[3],
                            3:[2, 3],
                            4:[2, 3],
                            5:[1, 2, 3],
                            6:[1, 2, 3],
                            7:[0, 1, 2, 4],
                            8:[0, 1, 2, 4],
                            9:[0, 0, 1, 3, 5],
                            10:[0, 0, 1, 3, 5],
                            11:[0, 0, 0, 2, 4, 7],
                            12:[0, 0, 0, 2, 4, 7],
                            13:[0, 0, 0, 1, 3, 6, 9],
                            14:[0, 0, 0, 1, 3, 6, 9],
                            15:[0, 0, 0, 0, 2, 5, 8, 12],
                            16:[0, 0, 0, 0, 2, 5, 8, 12],
                            17:[0, 0, 0, 0, 1, 4, 7, 11, 15],
                            18:[0, 0, 0, 0, 1, 4, 7, 11, 15],
                            19:[0, 0, 0, 0, 0, 3, 6, 10, 14, 19],
                            20:[0, 0, 0, 0, 0, 3, 6, 10, 14, 19],
                            21:[0, 0, 0, 0, 0, 2, 5, 9, 13, 18, 23],
                            22:[0, 0, 0, 0, 0, 2, 5, 9, 13, 18, 23],
                            23:[0, 0, 0, 0, 0, 1, 4, 8, 12, 17, 22, 28],
                            24:[0, 0, 0, 0, 0, 1, 4, 8, 12, 17, 22, 28]}


talents = {"paragon_vigour_1": Talent("paragon_vigour", None, {"vigour": 1}, 1),
           "paragon_vigour_2": Talent("paragon_vigour", None, {"vigour": 2}, 2),
           "paragon_vigour_3": Talent("paragon_vigour", None, {"vigour": 3}, 3),
           "paragon_vigour_4": Talent("paragon_vigour", None, {"vigour": 4}, 4),
           "paragon_vigour_5": Talent("paragon_vigour", None, {"vigour": 5}, 5),
           "paragon_vigour_6": Talent("paragon_vigour", None, {"vigour": 6}, 6),
           "mage_spellcasting": Spellcasting("mage_spellcasting", mage_spellcasting_table),
           "basic_spells": Talent("basic_spells", [activities["example_spell"]])}

data.load_talents(talents)
