"""Moving and living things
"""

import logging
from math import sqrt

from .nbt import consume, check
from . import geometry


class BodyPart(object):
    """This class allows associating something with each part of the body of
    a Mob, being it an item, a probability...
    """

    __slots__ = ("hand", "feet", "legs", "chest", "head")

    def __init__(self, default_value = None):
        self.hand = default_value
        self.feet = default_value
        self.legs = default_value
        self.chest = default_value
        self.head = default_value



class Entity(object):
    """An Entity is anything that is not in the map itself
    """

    __slots__ = ("_position", "_speed",
                 "yaw", "pitch",
                 "on_ground", "fall_distance",
                 "fire", "air_level",
                 "can_die", "dimension", "uuid", "name")


    def __init__(self, nbt_info = None):
        self.init()
        if nbt_info != None:
            self.init_from(nbt_info)


    def init(self):
        """Initialize instance with default values
        """
        self._position = geometry.Triple(0.0, 0.0, 0.0)
        self._speed = geometry.Triple(0.0, 0.0, 0.0)

        self.yaw = 0.0
        self.pitch = 0.0

        self.on_ground = True
        self.fall_distance = 0.0

        self.fire = 0
        self.air_level = 0

        self.can_die = True

        self.dimension = 0

        self.uuid = 0

        self.name = "Michel"


    def init_from(self, nbt_info):
        """Initialize instance with information stored in NBT format
        """
        self._position = geometry.Triple(consume(nbt_info["Pos"], 0),
                                         consume(nbt_info["Pos"], 1),
                                         consume(nbt_info["Pos"], 2))

        self._speed = geometry.Triple(consume(nbt_info["Motion"], 0),
                                      consume(nbt_info["Motion"], 1),
                                      consume(nbt_info["Motion"], 2))

        self.yaw = consume(nbt_info["Rotation"], 0)
        self.pitch = consume(nbt_info["Rotation"], 1)

        self.on_ground = consume(nbt_info, "OnGround") == 1
        self.fall_distance = consume(nbt_info, "FallDistance")

        self.fire = consume(nbt_info, "Fire")
        self.air_level = consume(nbt_info, "Air")

        self.can_die = consume(nbt_info, "Invulnerable")

        self.dimension = consume(nbt_info, "Dimension")

        low_uuid = consume(nbt_info, "UUIDLeast")
        if low_uuid < 0:
            low_uuid += 2**64
        high_uuid = consume(nbt_info, "UUIDMost")
        if high_uuid < 0:
            high_uuid += 2**64
        self.uuid = (high_uuid << 64) + low_uuid

        self.name = consume(nbt_info, "CustomName")


    @property
    def position(self):
        """Lower North-West end of the Entity
        """
        return self._position


    @property
    def speed(self):
        """Velocity for the next tick
        """
        return self._speed



class Mob(Entity):
    """A Mob is any living Entity
    """

    __slots__ = ("health", "attack_time", "hurt_time", "death_time",
                 "remaining_time",
                 "show_name",
                 "drop_chances", "can_steal",
                 "is_persistent")


    def init(self):
        super(Mob, self).init()

        self.health = 20
        self.attack_time = 0
        self.hurt_time = 0
        self.death_time = 0
        self.remaining_time = 1

        self.show_name = False

        self.drop_chances = BodyPart(0.0)
        self.can_steal = True

        self.is_persistent = True


    def init_from(self, nbt_info):
        super(Mob, self).init_from(nbt_info)

        self.health = consume(nbt_info, "Health")
        self.attack_time = consume(nbt_info, "AttackTime")
        self.hurt_time = consume(nbt_info, "HurtTime")
        self.death_time = consume(nbt_info, "DeathTime")
        self.remaining_time = consume(nbt_info, "PortalCooldown")

        self.show_name = consume(nbt_info, "CustomNameVisible") == 1

        self.drop_chances = BodyPart()
        self.drop_chances.hand = consume(nbt_info["DropChances"], 0)
        self.drop_chances.feet = consume(nbt_info["DropChances"], 1)
        self.drop_chances.legs = consume(nbt_info["DropChances"], 2)
        self.drop_chances.chest = consume(nbt_info["DropChances"], 3)
        self.drop_chances.head = consume(nbt_info["DropChances"], 4)
        self.can_steal = consume(nbt_info, "CanPickUpLoot") == 1

        self.is_persistent = consume(nbt_info, "PersistenceRequired")



class UnknownMob(Mob):
    """This class is used to manage any Mob that has not a specificaly
    tailored Python class
    """

    pass



class BreedableMob(Mob):
    """A mob that can breed can also be a youngster. When adult, it alternates
    periods of seasons and refractory ones.
    """

    __slots__ = ("_state", "_count")

    CHILDHOOD = 0
    ADULTHOOD = 1
    SEASONS = 2

    def init(self):
        super(BreedableMob, self).init()

        self._state = self.ADULTHOOD
        self._count = 0


    def init_from(self, nbt_info):
        super(BreedableMob, self).init_from(nbt_info)

        age = consume(nbt_info, "Age")
        in_love = consume(nbt_info, "InLove")

        if age < 0:
            self._state = self.CHILDHOOD
            self._count = -age
        elif in_love > 0:
            self._state = self.SEASONS
            self._count = in_love
        else:
            self._state = self.ADULTHOOD
            self._count = age


    @property
    def count(self):
        """Number of ticks until automatic state change. If 0, state is stable
        """
        return self._count


    @count.setter
    def count(self, count):
        assert 0 <= count

        self._count = count


    @property
    def state(self):
        """Any Breedable Mob follows a finite-state automaton:
        CHILDHOOD -> ADULTHOOD
        ADULTHOOD -> SEASONS
        SEASONS -> ADULTHOOD
        """
        return self._state


    @state.setter
    def state(self, state):
        assert state in [CHILDHOOD, ADULTHOOD, SEASONS]

        self._state = state



class Bat(Mob):

    __slots__ = ("is_flying")

    def init(self):
        super(Bat, self).init()

        self.is_flying = False


    def init_from(self, nbt_info):
        super(Bat, self).init_from(nbt_info)

        self.is_flying = (consume(nbt_info, "BatFlags") == 0)



class CaveSpider(Mob):

    pass



class Cow(BreedableMob):

    pass



class Creeper(Mob):

    __slots__ = ("_charge", "_countdown")

    def init(self):
        super(Creeper, self).init()

        self.charge = 3
        self.countdown = 0


    def init_from(self, nbt_info):
        super(Creeper, self).init_from(nbt_info)

        self.charge = consume(nbt_info, "ExplosionRadius")
        self.countdown = consume(nbt_info, "Fuse")


    @property
    def charge(self):
        """Explosion radius
        """
        return self._charge


    @charge.setter
    def charge(self, charge):
        assert 0 <= charge

        self._charge = charge


    @property
    def countdown(self):
        """Number of ticks remaining before explosion. A countdown of 0
        indicates that Creeper is not currently in the explosion process
        """
        return self._countdown


    @countdown.setter
    def countdown(self, countdown):
        assert 0 <= countdown

        self._countdown = countdown



class Enderman(Mob):

    __slots__ = ("_item")

    def init(self):
        super(Enderman, self).init()

        self.carried_item = None


    def init_from(self, nbt_info):
        super(Enderman, self).init_from(nbt_info)

#TODO replace all this with a wrapped item
        self.carried_item = consume(nbt_info, "carried")
        consume(nbt_info, "carriedData")


    @property
    def carried_item(self):
        """An Enderman may take an item from the map and carry it to drop it
        somewhere else later
        """
        return self._item


    @carried_item.setter
    def carried_item(self, carried_item):
        self._item = carried_item



class Ghast(Mob):

    __slots__ = ("_radius")

    def init(self):
        super(Ghast, self).init()

#TODO What's the usual explosion radius?
        self.explosion = 1


    def init_from(self, nbt_info):
        super(Ghast, self).init_from(nbt_info)

        self.explosion = consume(nbt_info, "ExplosionPower")


    @property
    def explosion(self):
        """Radius of the explosion created by the fireballs this Ghast fires
        """
        return self._radius


    @explosion.setter
    def explosion(self, explosion):
        assert 1 <= explosion

        self._radius = explosion



class Horse(Mob):

    pass



class MushroomCow(BreedableMob):

    pass



class Pig(BreedableMob):

    __slots__ = ("saddle_on")

    def init(self):
        super(Pig, self).init()

        self.saddle_on = False


    def init_from(self, nbt_info):
        super(Pig, self).init_from(nbt_info)

        self.saddle_on = (consume(nbt_info, "Saddle") == 1)



class Player(Mob):

    __slots__ = ("game_type",
                 "_experience", "_experience_total",
                 "score",
                 "is_sleeping", "sleep_timer",
                 "_food_level", "food_exhaustion_level", "food_tick_timer",
                 "selected_item_slot",
                 "spawn_x", "spawn_y", "spawn_z", "mandatory_spawn",
                 "walking_speed",
                 "can_fly", "is_flying", "flying_speed",
                 "can_build", "instantly_build",
                 "can_die")


    OVERWORLD = 0
    THE_NETHER = -1
    THE_END = 1

    SURVIVAL_MODE = 0
    CREATIVE_MODE = 1
    ADVENTURE_MODE = 2

    def init(self):
        super(Player, self).init()

        self.game_type = self.SURVIVAL_MODE
        self.food_level = 20
        self.experience = 0


    def init_from(self, nbt_info):
        super(Player, self).init_from(nbt_info)

        optional = "<Player>"

        self.dimension = consume(nbt_info, "Dimension")
        self.game_type = consume(nbt_info, "playerGameType")

        xp_level = consume(nbt_info, "XpLevel")
        progress = consume(nbt_info, "XpP")
        if xp_level < 16:
            bonus = 17 * progress
        elif xp_level < 31:
            bonus = (3 * xp_level - 28) * progress
        else:
            bonus = (7 * xp_level - 148) * progress
        self.experience_level = xp_level
        self.experience += int(bonus)
        self.experience_total = consume(nbt_info, "XpTotal")
        self.score = consume(nbt_info, "Score")

        self.is_sleeping = consume(nbt_info, "Sleeping") == 1
        self.sleep_timer = consume(nbt_info, "SleepTimer")

        self.food_level = consume(nbt_info, "foodLevel") \
            + consume(nbt_info, "foodSaturationLevel")
        self.food_exhaustion_level = consume(nbt_info, "foodExhaustionLevel")
        self.food_tick_timer = consume(nbt_info, "foodTickTimer")

        self.selected_item_slot = consume(nbt_info, "SelectedItemSlot")

        self.spawn_x = consume(nbt_info, "SpawnX", optional)
        self.spawn_y = consume(nbt_info, "SpawnY", optional)
        self.spawn_z = consume(nbt_info, "SpawnZ", optional)
        self.mandatory_spawn = consume(nbt_info, "SpawnForced", optional) == 1

        self.walking_speed = consume(nbt_info["abilities"], "walkSpeed")

        self.can_fly = consume(nbt_info["abilities"], "mayfly") == 1
        self.is_flying = consume(nbt_info["abilities"], "flying") == 1
        self.flying_speed = consume(nbt_info["abilities"], "flySpeed")

        self.can_build = consume(nbt_info["abilities"], "mayBuild") == 1
        self.instantly_build = consume(nbt_info["abilities"], "instabuild")

# TODO this is redundant with "<Entity>/Invulnerable". Which one is actually
# used? Both?
        self.can_die = consume(nbt_info["abilities"], "invulnerable") == 0


    @property
    def experience(self):
        """Total number of experience points
        """
        return self._experience


    @experience.setter
    def experience(self, experience):
        assert 0 <= experience <= 1760
        self._experience = experience


    @property
    def experience_level(self):
        """Level corresponding to player's total number of experience points
        """
        result = 0
        if self.experience < 272:
            result = self.experience // 17
        else:
            if self.experience < 887:
                a = 3
                b = -59
                c = 720 - 2 * self.experience
            else:
                a = 7
                b = -303
                c = 4440 - 2 * self.experience

            delta = b**2 - 4 * a * c
            result = int((-b + sqrt(delta)) // (2 * a))

        return result


    @experience_level.setter
    def experience_level(self, experience_level):
        assert 0 <= experience_level <= 40

        if experience_level < 17:
            self.experience = 17 * experience_level
        elif experience_level < 32:
            self.experience = 272 + ((experience_level - 16) * (3 * experience_level - 11)) // 2
        else:
            self.experience = 956 + ((experience_level - 32) * (7 * experience_level - 79)) // 2


    @property
    def experience_total(self):
        """Total amount of experience points accumulated through time,
        whatever the player done with them
        """
        if self.experience > self._experience_total:
            return self.experience
        else:
            return self._experience_total


    @experience_total.setter
    def experience_total(self, experience_total):
        assert experience_total >= 0

        self._experience_total = experience_total


    @property
    def food_level(self):
        """Food level is a positive integer. Values from 0 to 20 are visible
        in the "food bar", each level corresponding to half a shank. Values
        greater than 20 are not visible, but are consumed first. Values
        greater or equal to 18 ensure health regeneration. Values lower
        or equal to 6 prevent player from running. When value is finally 0,
        player starts suffering from starvation.
        """
        return self._food_level


    @food_level.setter
    def food_level(self, food_level):
        assert food_level >= 0
        self._food_level = food_level



class SilverFish(Mob):

    pass



class Skeleton(Mob):

    pass



class Spider(Mob):

    pass



class Cube(Mob):
    """A Cube is a huge cube of matter that hops around. When defeated, a
    Cube splits up into smaller ones. Cubes can be made of green jelly or
    magma, depending on the world they spawn in. We then talk of LavaSlimes,
    or MagmaCube.

    This class should be considered ABSTRACT. For CONCRETE implementations,
    see Slime and LavaSlime classes.
    """

    __slots__ = ("_size")

    def init(self):
        super(Cube, self).init()

        self.size = 4


    def init_from(self, nbt_info):
        super(Cube, self).init_from(nbt_info)

        self.size = consume(nbt_info, "Size")


    @property
    def size(self):
        """When he dies, a Cube is replaced by four Cubes half his size,
        until this size reaches 0
        """
        return self._size


    @size.setter
    def size(self, size):
#TODO Cubes with zero size seems to exist anyhow, even though Wiki specifies
# that natural sizes are 1, 2 and 4 for Cubes
        assert 0 <= size <= 4

        self._size = size



class LavaSlime(Cube):
    """A LavaSlime is a huge cube of magma that hops around in the Nether.
    When defeated, a LavaSlime splits up into smaller ones.
    """

    pass



class Slime(Cube):
    """A Slime is a huge cube of green jelly that hops around. When defeated,
    a Slime splits up into smaller ones.
    """

    pass



class Villager(Mob):

    __slots__ = ("_profession", "_will_grow_in", "riches")

    FARMER = 0
    LIBRARIAN = 1
    PRIEST = 2
    BLACKSMITH = 3
    BUTCHER = 4

    def init(self):
        super(Villager, self).init()

        self.profession = self.FARMER
        self.will_grow_in = 0
#TODO what's that?
        self.riches = 0


    def init_from(self, nbt_info):
        super(Villager, self).init_from(nbt_info)

        self._profession = consume(nbt_info, "Profession")
        self._will_grow_in = -consume(nbt_info, "Age")
        self.riches = consume(nbt_info, "Riches")


    @property
    def profession(self):
        """Profession determines Villager's wardrobe color and the kind
        of offers he may propose
        """
        return self._profession


    @profession.setter
    def profession(self, profession):
        assert profession in [self.FARMER, self.LIBRARIAN, self.PRIEST,
                              self.BLACKSMITH, self.BUTCHER]
        self._profession = profession


    @property
    def will_grow_in(self):
        """Number of ticks until Villager become an adult. 0 indicates it
        is already an adult
        """
        return self._will_grow_in


    @will_grow_in.setter
    def will_grow_in(self, will_grow_in):
        self._will_grow_in = will_grow_in



class WitherSkeleton(Mob):
    """Wither skeletons live in the Nether, are equipped with an enchanted
    stone sword, and are immune to fire, lava and daylight
    """

    pass



class Zombie(Mob):

    __slots__ = ("_convert", "_is_villager")

    def init(self):
        super(Zombie, self).init()

        self.will_convert_in = 0
        self._is_villager = False


    def init_from(self, nbt_info):
        super(Zombie, self).init_from(nbt_info)

        conversion_time = consume(nbt_info, "ConversionTime")
        if conversion_time != -1:
            self.will_convert_in = conversion_time

        self._is_villager = consume(nbt_info, "IsVillager", "<Zombie>")


    @property
    def will_convert_in(self):
        """Number of ticks until Zombie converts back to a Villager.
        0 indicates that this conversion will never happen.
        """
        return self._convert


    @will_convert_in.setter
    def will_convert_in(self, will_convert_in):
        assert 0 <= will_convert_in
        self._convert = will_convert_in



class PigZombie(Zombie):

    __slots__ = ("anger")

    def init(self):
        super(PigZombie, self).init()


    def init_from(self, nbt_info):
        super(PigZombie, self).init_from(nbt_info)

        self.anger = consume(nbt_info, "Anger")



class Projectile(Entity):
    """A Projectile in any non-living moving Entity
    """

    pass


_ENTITIES = {
    "Bat" : Bat,
    "CaveSpider" : CaveSpider,
    "Cow" : Cow,
    "Creeper" : Creeper,
    "Enderman" : Enderman,
    "Ghast" : Ghast,
    "EntityHorse" : Horse,
    "LavaSlime" : LavaSlime,
    "MushroomCow" : MushroomCow,
    "Pig" : Pig,
    "PigZombie" : PigZombie,
    "Silverfish" : SilverFish,
# For Skeleton and WitherSkeleton, see 'read' function specificities
#   "Skeleton" : Skeleton,
    "Spider" : Spider,
    "Slime" : Slime,
    "Villager" : Villager,
    "Zombie" : Zombie,
    }


def read(nbt_info):
    """Interpret stored information in NBT format
    """
    if "id" not in nbt_info:
        kind = "Player"
        entity_class = Player
    else:
        kind = consume(nbt_info, "id")
        if kind in _ENTITIES:
            entity_class = _ENTITIES[kind]
        elif kind == "Skeleton":
            skeleton_type = consume(nbt_info, "SkeletonType")
            if skeleton_type == 1:
                entity_class = WitherSkeleton
            else:
                entity_class = Skeleton
        else:
            logging.warning("Unknown entity: {}".format(kind))
            entity_class = UnknownMob

    result = entity_class(nbt_info)
    check(nbt_info, "<{}>".format(kind))

    return result
