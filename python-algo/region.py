class Region:
    number = 0
    coordinates = []
    walls = []
    turrets = []
    supports = []

    def __init__(self, number, coordinates, walls, turrets, supports):
        self.number = number
        self.coordinates = coordinates
        self.walls = walls
        self.turrets = turrets
        self.supports = supports

    """
    Returns the number of the region.
    """
    def get_number(self):
        return self.number

    """
    Returns the wall object in the coordinates.
    """
    def get_wall(self, coordinates):
        if coordinates in self.walls:
            return coordinates
        return None
    
    """
    Adds the coordinates to the wall list.

    Parameters: coordinates (list)
    """
    def add_wall(self, coordinates):
        self.walls.append(coordinates)


    """
    Returns the turret object in the coordinates.
    """
    def get_turret(self, coordinates):
        if coordinates in self.turrets:
            return coordinates
        return None
    

    """
    Adds the coordinates to the turret list.

    Parameters: coordinates (list)
    """
    def add_turret(self, coordinates):
        self.turrets.append(coordinates)
        

    """
    Returns the support object in the coordinates.
    """
    def get_support(self, coordinates):
        if coordinates in self.supports:
            return coordinates
        return None
    

    """
    Adds the coordinates to the support list.
    
    Parameters: coordinates (list)
    """
    def add_support(self, coordinates):
        self.supports.append(coordinates)

    """
    Returns the walls list.
    """
    def getWallsList(self):
        return self.walls
    
    """
    Returns the turrets list.
    """
    def getTurretsList(self):
        return self.turrets
    
    """
    Returns the supports list.
    """
    def getSupportsList(self):
        return self.supports
    

    """"
    Checks if a set of coordinates is empty.
    """
    def is_empty(self, coordinates):
        if coordinates in self.walls or coordinates in self.turrets or coordinates in self.supports:
            return False
        return True