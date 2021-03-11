import math

# Steer type const values
STOP = 1
RESERVED = 2
SEEK = 3
FLEE = 4
ARRIVE = 5

# Simple vector class, this is missing alot of methods a normal vector
# object should have but it has what is needed for this assignment
class Vector:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y  # Z in this sense

    def normalize(self):    # Normalize to unit vector
        self /= self.length()

    def length(self):   # Returns the vector's magnitude
        return math.sqrt(math.pow(self[0], 2) + math.pow(self[1], 2))

    # Operator overloading
    def __add__(self, vector2):
        return Vector(self[0] + vector2[0], self[1] + vector2[1])

    def __sub__(self, vector2):
        return Vector(self[0] - vector2[0], self[1] - vector2[1])

    def __mul__(self, scalar):
        return Vector(self[0] * scalar, self[1] * scalar)

    def __truediv__(self, scalar):
        return Vector(self[0] / scalar, self[1] / scalar)

    def __getitem__(self, key): # Bracket overloading
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        return None

# Data class to store linear and angular acceleration
class Steering:
    def __init__(self, linear = Vector(0, 0), angular = 0):
        self.linear = linear
        self.angular = angular

# Character class to store each individual character's movements
class Character:
    def __init__(self, ID = 0, steer = STOP, position = Vector(0, 0), velocity = Vector(0, 0), linear = Vector(0, 0), orientation = 0, rotation = 0,
                angular = 0, maxSpeed = 0, maxAccleration = 0, target = 0, targetRadius = 4, slowRadius = 20,
                timeToTarget = 1, align = False, collideRadius = 0.5, avoidRadius = 2):

        self.id = ID
        self.steer = steer
        self.position = position
        self.velocity = velocity
        self.linear = linear
        self.orientation = orientation
        self.rotation = rotation
        self.angular = angular
        self.maxSpeed = maxSpeed
        self.maxAcceleration = maxAccleration
        self.target = target
        self.targetRadius = targetRadius
        self.slowRadius = slowRadius
        self.timeToTarget = timeToTarget
        # These members are not needed for this assignment
        self.align = align
        self.collideRadius = collideRadius
        self.avoidRadius = avoidRadius

    # Turns all relevant character data to a string (comma seperated) for the output file
    def toString(self, time):
        data = [time, self.id, self.position[0], self.position[1], self.velocity[0], self.velocity[1], self.linear[0], self.linear[1], self.orientation, self.steer]
        data = [str(i) for i in data] # Turns all data values (required for trajectory file) of character into a list of strings
        return ','.join(data) + '\n'  # Returns all data values in the form of a comma seperated string


# Seek algorithm described in book
def getSteeringSeek(character, target):
    result = Steering()

    # Get the direction to the target
    result.linear = target.position - character.position

    # Give full acceleration along this direction
    result.linear.normalize()
    result.linear *= character.maxAcceleration

    result.angular = 0
    return result

# Flee algorithm described in book
def getSteeringFlee(character, target):
    result = Steering()

    # Get the direction to the target
    result.linear = character.position - target.position

    # Give full acceleration along this direction
    result.linear.normalize()
    result.linear *= character.maxAcceleration

    result.angular = 0
    return result

# Arrive algorithm described in book
def getSteeringArrive(character, target):
    result = Steering()

    # Get the direction to the target
    direction = target.position - character.position
    distance = direction.length()

    if distance < character.targetRadius:
        targetSpeed = 0
    
    elif distance > character.slowRadius:
        targetSpeed = character.maxSpeed

    else:
        targetSpeed = character.maxSpeed * distance / character.slowRadius

    direction.normalize()
    targetVelocity = direction * targetSpeed

    # Acceleration tries to get to the target velocity
    result.linear = targetVelocity - character.velocity
    result.linear /= character.timeToTarget

    if result.linear.length() > character.maxAcceleration:
        result.linear.normalize()
        result.linear *= character.maxAcceleration

    result.angular = 0
    return result

# Stop algorithm used in Dr Petty's R code
def getSteeringStop(character):
    result = Steering()
    result.linear = character.velocity

    if result.linear.length() > character.maxAcceleration:
        result.linear.normalize()
        result.linear *= character.maxAcceleration

    result.angular = character.rotation
    return result

# Dynamically update the character's values using the new steering calculated from steering algorithms
def dynamicUpdate(character, steering, timeStep, hsPhysics = True):
    # Updating the character's position and orientation
    if hsPhysics:
        sq = 0.5 * math.pow(timeStep, 2)
        character.position += (character.velocity * timeStep) + (steering.linear * sq)
        character.orientation += (character.rotation * timeStep) + (steering.angular * sq)
    else:
        character.position += (character.velocity * timeStep)
        character.orientation += (character.rotation * timeStep)

    # Updating character's velocity and rotation using the current acceleration
    character.velocity += (steering.linear * timeStep)
    character.rotation += (steering.angular * timeStep)
    
    # If character's velocity is greater than their max speed
    if character.velocity.length() > character.maxSpeed:
        character.velocity.normalize()
        character.velocity *= character.maxSpeed

    # If the character's velocity has slowed down past stop speed
    if character.velocity.length() < stopSpeed:
        character.velocity = Vector(0, 0)
    
    # If the character's rotation speed has slowed down past stop rotation speed
    if character.rotation < stopRotate:
        character.rotation = 0

    return character    

# Hard coded characters with attributes described in Programming Assignment 1 Requirements
character1 = Character(ID = 161, steer = STOP, position = Vector(0, 0), velocity = Vector(0, 0), orientation = 0, maxSpeed = 0, maxAccleration = 0)
character2 = Character(ID = 162, steer = FLEE, position = Vector(-25, 50), velocity = Vector(0, -8), orientation = math.pi/4, maxSpeed = 10, maxAccleration = 2)
character3 = Character(ID = 163, steer = SEEK, position = Vector(50, -25), velocity = Vector(0, -8), orientation = (3 * math.pi) / 2, maxSpeed = 8, maxAccleration = 2)
character4 = Character(ID = 164, steer = ARRIVE, position = Vector(-50, -75), velocity = Vector(-6, 4), orientation = math.pi, maxSpeed = 8, maxAccleration = 2)

characters = [character1, character2, character3, character4] # List of all the characters


time = 0            # Starting time of simulation
timeStep = 0.5      # Difference in time between moments in the simulation
stopSpeed = 0.01    # Speed at which a character will stop if going under
stopRotate = 0.01   # Speed at which a character will stop rotating if going under
hsPhysics = False   # Will calculate character's position and orientation using HS physics if set to true
stopTime = 50       # Time at which simulation will stop

outFile = open('Output.txt', 'w')   # Opening output file

# Write initial positions and movement variables for all characters to trajectory file
for character in characters:
    outFile.write(character.toString(time))


# Calculate trajectory, timestep by timestep
while time < stopTime:  # Loop until stoptime is reached
    time += timeStep

    for character in characters:
        
        # Call the proper steering routine for the character
        if character.steer == STOP:
            steering = getSteeringStop(character)
        
        elif character.steer == SEEK:
            steering = getSteeringSeek(character, characters[character.target])

        elif character.steer == FLEE:
            steering = getSteeringFlee(character, characters[character.target])

        elif character.steer == ARRIVE:
            steering = getSteeringArrive(character, characters[character.target])

        # Update the movement variables
        character.linear = steering.linear
        character.angular = steering.angular
        character = dynamicUpdate(character, steering, timeStep, hsPhysics)


        # Write updated position and movement variables for current character to trajectory file
        outFile.write(character.toString(time))



outFile.close()
# End of program