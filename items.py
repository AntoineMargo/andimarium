
class WeaponDamageType:
    def __init__(self, name: str, multiplier: list):
        self.name = name
        self.multiplier = multiplier

    def __str__(self):
        return f"{self.name}: {self.multiplier}"


damage_slashing = WeaponDamageType("slashing", [0, 1, 2, 3])
damage_piercing = WeaponDamageType("piercing", [0, 0, 2, 4])
damage_crushing = WeaponDamageType("crushing", [0, 0, 3, 3])


class Item:
    def __init__(self, name: str, sprite: str, load: int = 1, value: int = 10):
        self.name = name
        self.sprite = sprite
        self.load = load
        self.value = value
        self.activity = None

    def __str__(self):
        return f"{self.name} (load: {self.load}, value: {self.value})"
    
    def add_activity(self, function):
        self.activity = function


class Weapon(Item):
    def __init__(self, name: str, sprite: str, load: int = 1, value: int = 10, dice_number: int = 1, damage_die: int = 6, 
                 weapon_damage_types: list = [damage_slashing], onehanded: bool = True, twohanded: bool = False, melee_range: tuple = (1, 2), 
                 throw_increment: int = 5, ranged_increment: int = 0, defence_bonus: int = 0, speed_penalty : int = 0, 
                 projectile_image : str = r"assets/graphics/objects/bolt.png", projectile_speed: int = 70):
        super().__init__(name, sprite, load, value)
        self.dice_number = dice_number
        self.damage_die = damage_die
        self.weapon_damage_types = weapon_damage_types
        self.onehanded = onehanded
        self.twohanded = twohanded
        self.melee_range = melee_range # A tuple with the minimum range and maximum range, they can be the same value (e.g.:( 1, 1))
        self.throw_increment = throw_increment
        self.ranged_increment = ranged_increment
        self.defence_bonus = defence_bonus
        self.speed_penalty = speed_penalty
        self.projectile_image = projectile_image
        self.projectile_speed = projectile_speed

    def __str__(self):
        damage_types = " & ".join(damage_type.name for damage_type in self.weapon_damage_types)
        return f"{self.name}: {self.dice_number}d{self.damage_die} {damage_types}, range {self.melee_range} (load: {self.load}, value: {self.value})"
    
    def __repr__(self):
        return f"{self.name}"


class Armour(Item):
    def __init__(self, name: str, sprite: str, load: int = 1, value: int = 10, damage_reduction: list = [0, 0, 0, 0, 0, 0, 0, 0],  vigour_penalty: int = 0):
        super().__init__(name, sprite, load, value)
        self.damage_reduction = damage_reduction
        self.vigour_penalty = vigour_penalty

    def __str__(self):
        return f"{self.name}: {self.damage_reduction} damage reduction, {self.vigour_penalty} vigour (load: {self.load}, value: {self.value})"

    def __repr__(self):
        return f"{self.name}"

items = {"rope": Item("rope", r"assets/graphics/interface/items/placeholder.png", 1, 5), 
        "fist": Weapon("fist", r"assets/graphics/interface/items/fist.png", 0, 0, 1, 4, [damage_crushing], True, False, (1, 1)),
        "straightsword": Weapon("straightsword", r"assets/graphics/interface/items/straightsword.png", 1, 500, 1, 10, [damage_slashing, damage_piercing], True, False, (1, 2)),
        "spear": Weapon("spear", r"assets/graphics/interface/items/spear.png", 1, 500, 1, 10, [damage_piercing], True, False, (2, 2)),
        "greatsword": Weapon("greatsword", r"assets/graphics/interface/items/greatsword2.png", 2, 1000, 2, 6, [damage_slashing, damage_piercing], False, True, (1, 3)),
        "poleaxe": Weapon("poleaxe", r"assets/graphics/interface/items/pollaxe.png", 2, 1000, 2, 8, [damage_crushing, damage_slashing, damage_piercing], False, True, (1, 2)),
        "bow": Weapon("bow", r"assets/graphics/interface/items/bow.png", 2, 400, 2, 6, [damage_piercing], False, True, (0, 0), 5, 15),
        "small_shield": Weapon("small shield", r"assets/graphics/interface/items/small_shield.png", 2, 100, 1, 4, [damage_crushing], True, False, (1, 1), 5, 0, 1),
        "medium_shield": Weapon("medium shield", r"assets/graphics/interface/items/medium_shield.png", 2, 100, 1, 6, [damage_crushing], True, False, (1, 1), 5, 0, 2, -1),
        "heavy_shield": Weapon("heavy shield", r"assets/graphics/interface/items/large_shield.png", 2, 100, 1, 8, [damage_crushing], True, False, (1, 1), 5, 0, 3, -2),
        "light_armour": Armour("light armour", r"assets/graphics/interface/items/placeholder.png", 1, 20, [0, 0, 0, 0, 0, 0, 0, 0], 0),
        "medium_armour": Armour("medium armour", r"assets/graphics/interface/items/placeholder.png", 4, 2000, [10, 0, 0, 0, 0, 0, 0, 0], -1),
        "heavy_armour": Armour("heavy armour", r"assets/graphics/interface/items/placeholder.png", 8, 4000, [20, 0, 0, 0, 0, 0, 0, 0], -2)}

