import gamelib
import random
import math
import warnings
from sys import maxsize
import json
from region_coordinates import region1_values, region2_values, region3_values, region5_values, region6_values
from region import Region
"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

  - You can analyze action frames by modifying on_action_frame function

  - The GameState.map object can be manually manipulated to create hypothetical 
  board states. Though, we recommended making a copy of the map to preserve 
  the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):
    region1 = None
    region2 = None
    region3 = None
    region5 = None

    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

        self.region1 = Region(1, [], region1_values["valid_walls"], region1_values["valid_turrets"], [])
        self.region2 = Region(2, [], region2_values["valid_walls"], region2_values["valid_turrets"], [])
        self.region3 = Region(3, [], region3_values["valid_walls"], region3_values["valid_turrets"], [])
        self.region5 = Region(5, [], region5_values["valid_walls"], region5_values["valid_turrets"], [])
        self.region6 = Region(6, [], [], [], region6_values["valid_supports"])

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, MP, SP
        WALL = config["unitInformation"][0]["shorthand"]
        SUPPORT = config["unitInformation"][1]["shorthand"]
        TURRET = config["unitInformation"][2]["shorthand"]
        SCOUT = config["unitInformation"][3]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        MP = 1
        SP = 0
        # This is a good place to do initial setup
        self.scored_on_locations = []

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        game_state.attempt_spawn(DEMOLISHER, [24, 10], 3)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        game_state.suppress_warnings(False)  #Comment or remove this line to enable warnings.

        self.starter_strategy(game_state)

        game_state.submit_turn()


    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """

    def starter_strategy(self, game_state):
        """
        1. first two turns: build walls and send scouts
        2. third turn: send interceptors and make turrets
        3. fourth turn: send stacked demolishers and build support

        Clash of Clans style:
        Walls on the outside with a few gaps for troops
        Build walls around turrets so that the demolisher can't reach it, but the turrets can attack them.
        Pathways for the rest of the troops to pass through
        """
        # First, place basic defenses
        self.build_defences(game_state)
        # Now build reactive defenses based on where the enemy scored
        self.build_reactive_defense(game_state)

        if game_state.turn_number == 0:
            game_state.attempt_spawn(SCOUT, [13, 0], 5)

        if game_state.turn_number % 3 == 0:
            # To simplify we will just check sending them from back left and right
            scout_spawn_location_options = [[17, 3], [10, 3]]
            best_location = self.least_damage_spawn_location(game_state, scout_spawn_location_options)
            game_state.attempt_spawn(SCOUT, best_location, 5)

    def build_defences(self, game_state):
        """
        Build basic defenses using hardcoded locations.
        Remember to defend corners and avoid placing units in the front where enemy demolishers can attack them.
        """
        wall_locations = [self.region1.getWallsList() + self.region2.getWallsList() + self.region5.getWallsList() + self.region3.getWallsList()]
        turret_locations = [self.region1.getTurretsList() + self.region2.getTurretsList() + self.region5.getTurretsList() + self.region3.getTurretsList()]

        # attempt_spawn will try to spawn units if we have resources, and will check if a blocking unit is already there
        if (game_state.turn_number == 0 or game_state.turn_number % 1 == 0): # every round 
            game_state.attempt_spawn(WALL, self.region1.getWallsList() + self.region2.getWallsList() + self.region5.getWallsList())
            game_state.attempt_spawn(TURRET, self.region1.getTurretsList() + self.region2.getTurretsList() + self.region5.getTurretsList())

        # If we have enough SP, we can add more walls to region 3
        if (game_state.turn_number == 1 or game_state.turn_number % 2 == 0): # every other round 
            game_state.attempt_spawn(WALL, self.region3.getWallsList())
            game_state.attempt_spawn(TURRET, self.region3.getTurretsList())
            
        # for i in range(0, len(self.region1.getWallsList())):
        #         if (game_state.get_resource(SP) > 21):
        #             game_state.attempt_spawn(WALL, self.region1.getWallsList()[i])
        #         else:
        #             break

        # if (game_state.turn_number > 2 and game_state.turn_number % 4 == 0 and game_state.get_resource(SP) > 30):
        #     for i in range(0, len(self.region1.getTurretsList())):
        #         if (game_state.get_resource(SP) > 21):
        #             game_state.attempt_spawn(WALL, self.region1.getTurretsList()[i])
        #         else:
        #             break

        # self.rebuild_defences(game_state, wall_locations, turret_locations)


    def rebuild_defences(self, game_state, walls, turrets):
        """
        Rebuild basic defenses using hardcoded locations.
        """
        # attempt_spawn will try to spawn units if we have resources, and will check if a blocking unit is already there
        game_state.attempt_spawn(WALL, walls)
        game_state.attempt_spawn(TURRET, turrets)
    
    def scout_strategy(self, game_state):
        """
        Send out scouts to the enemy's base to get a peak at what they are doing.
        """
        # First let's figure out the most vulnerable areas in the enemy's base.
        # We only need the first 5 or so locations to get a good view of the enemy's base
        path = game_state.find_path_to_edge([13, 0])
        # Only pick the first 5 to send to
        path = path[:5]
        # Send out scouts on the path
        for location in path:
            game_state.attempt_spawn(SCOUT, location, 5)

    def build_reactive_defense(self, game_state):
        """
        This function builds reactive defenses based on where the enemy scored on us from.
        We can track where the opponent scored by looking at events in action frames 
        as shown in the on_action_frame function
        """
        for location in self.scored_on_locations:
            # Build turret one space above so that it doesn't block our own edge spawn locations
            build_location = [location[0], location[1]+1]
            game_state.attempt_spawn(TURRET, build_location)

    # def stall_with_interceptors(self, game_state):
    #     # Remove locations that are blocked by our own structures 
    #     # since we can't deploy units there.
    #     deploy_locations = self.get_deployable_locations(game_state)
        
    #     # While we have remaining MP to spend lets send out interceptors randomly.
    #     while game_state.get_resource(MP) >= game_state.type_cost(INTERCEPTOR)[MP] and len(deploy_locations) > 0:
    #         # Choose a random deploy location.
    #         deploy_index = random.randint(0, len(deploy_locations) - 1)
    #         deploy_location = deploy_locations[deploy_index]
            
    #         game_state.attempt_spawn(INTERCEPTOR, deploy_location)
    #         """
    #         We don't have to remove the location since multiple mobile 
    #         units can occupy the same space.
    #         """

    def get_friendly_edges(self, game_state):
        return game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)

    def get_deployable_locations(self, game_state):
        return  self.filter_blocked_locations(self.get_friendly_edges(), game_state)

    def demolisher_line_strategy(self, game_state):
        """
        Build a line of the cheapest stationary unit so our demolisher can attack from long range.
        """
        # First let's figure out the cheapest unit
        # We could just check the game rules, but this demonstrates how to use the GameUnit class
        stationary_units = [WALL, TURRET, SUPPORT]
        cheapest_unit = WALL
        for unit in stationary_units:
            unit_class = gamelib.GameUnit(unit, game_state.config)
            if unit_class.cost[game_state.MP] < gamelib.GameUnit(cheapest_unit, game_state.config).cost[game_state.MP]:
                cheapest_unit = unit

        # Now let's build out a line of stationary units. This will prevent our demolisher from running into the enemy base.
        # Instead they will stay at the perfect distance to attack the front two rows of the enemy base.
        for x in range(27, 5, -1):
            game_state.attempt_spawn(cheapest_unit, [x, 11])

        # Now spawn demolishers next to the line
        # By asking attempt_spawn to spawn 1000 units, it will essentially spawn as many as we have resources for
        game_state.attempt_spawn(DEMOLISHER, [24, 10], 1000)

    def least_damage_spawn_location(self, game_state, location_options):
        """
        This function will help us guess which location is the safest to spawn moving units from.
        It gets the path the unit will take then checks locations on that path to 
        estimate the path's damage risk.
        """
        damages = []
        # Get the damage estimate each path will take
        for location in location_options:
            path = game_state.find_path_to_edge(location)
            damage = 0
            for path_location in path:
                # Get number of enemy turrets that can attack each location and multiply by turret damage
                damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(TURRET, game_state.config).damage_i
            damages.append(damage)
        
        # Now just return the location that takes the least damage
        return location_options[damages.index(min(damages))]

    # detect_enemy_unit is a helper function to count the number of enemy units in a given location
    def detect_enemy_unit(self, game_state, unit_type=None, valid_x = None, valid_y = None):
        total_units = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit(location):
                for unit in game_state.game_map[location]:
                    if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
                        total_units += 1
        return total_units
        
    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered

    def on_action_frame(self, turn_string):
        """
        This is the action frame of the game. This function could be called 
        hundreds of times per turn and could slow the algo down so avoid putting slow code here.
        Processing the action frames is complicated so we only suggest it if you have time and experience.
        Full doc on format of a game frame at in json-docs.html in the root of the Starterkit.
        """
        # Let's record at what position we get scored on
        state = json.loads(turn_string)
        events = state["events"]
        breaches = events["breach"]
        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            # When parsing the frame data directly, 
            # 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
            if not unit_owner_self:
                gamelib.debug_write("Got scored on at: {}".format(location))
                self.scored_on_locations.append(location)
                gamelib.debug_write("All locations: {}".format(self.scored_on_locations))


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
