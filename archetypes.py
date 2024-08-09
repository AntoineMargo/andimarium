from talents import *


class Archetype:
    def __init__(self, name):
        self.name = name
        self.talents = {1:[[], []],
                        2:[[], []],
                        3:[[], []],
                        4:[[], []],
                        5:[[], []],
                        6:[[], []],
                        7:[[], []],
                        8:[[], []],
                        9:[[], []],
                        10:[[], []],
                        11:[[], []],
                        12:[[], []],
                        13:[[], []],
                        14:[[], []],
                        15:[[], []],
                        16:[[], []],
                        17:[[], []],
                        18:[[], []],
                        19:[[], []],
                        20:[[], []],
                        21:[[], []],
                        22:[[], []],
                        23:[[], []],
                        24:[[], []]}

    def __str__(self) -> str:
        return f"{self.name}"
    
    def __repr__(self) -> str:
        return f"{self.name}"



archetypes = {"paragon": Archetype("Paragon"),
              "mage": Archetype("Mage")}


archetypes["paragon"].talents = {1:[[data.talents["paragon_vigour_1"]], []],
                                2:[[], []],
                                3:[[], []],
                                4:[[], []],
                                5:[[data.talents["paragon_vigour_2"]], []],
                                6:[[], []],
                                7:[[], []],
                                8:[[], []],
                                9:[[data.talents["paragon_vigour_3"]], []],
                                10:[[], []],
                                11:[[], []],
                                12:[[], []],
                                13:[[data.talents["paragon_vigour_4"]], []],
                                14:[[], []],
                                15:[[], []],
                                16:[[], []],
                                17:[[data.talents["paragon_vigour_5"]], []],
                                18:[[], []],
                                19:[[], []],
                                20:[[], []],
                                21:[[data.talents["paragon_vigour_6"]], []],
                                22:[[], []],
                                23:[[], []],
                                24:[[], []]}


archetypes["mage"].talents = {1:[[data.talents["mage_spellcasting"], data.talents["basic_spells"]], []],
                                2:[[], []],
                                3:[[], []],
                                4:[[], []],
                                5:[[], []],
                                6:[[], []],
                                7:[[], []],
                                8:[[], []],
                                9:[[], []],
                                10:[[], []],
                                11:[[], []],
                                12:[[], []],
                                13:[[], []],
                                14:[[], []],
                                15:[[], []],
                                16:[[], []],
                                17:[[], []],
                                18:[[], []],
                                19:[[], []],
                                20:[[], []],
                                21:[[], []],
                                22:[[], []],
                                23:[[], []],
                                24:[[], []]}


data.load_archetypes(archetypes)