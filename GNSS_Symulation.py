#this is basically the file that has all the background stuff about the GNSS sim, bc the main file is 500+ lines and is getting complicated.
import random

habitat_pos = (0,0)#the habitat is at the very centre of the axis

#lists all the different positions of the beacon points
beacon_pos = [
    (50,50),
    (-50,50),
    (-50,-50),
    (50,-50),
    (100,0),
    (0,100),
    (-100,0),
    (0,-100)
]

#randomly makes the poisitions of the rovers in the right axis
rovers = []
for _ in range(16):
    x = random.uniform(-200,200)
    y = random.uniform(-200,200)
    rovers.append((x,y))

#averages 3 beacon positions with added noise to estimate an astronauts current position
def sim_astronaut_pos(beacons, noise_lvl = 0.5):
    selected = random.sample(beacons,3)

    sum_x = 0
    sum_y = 0

    for beacon in selected:
        sum_x += beacon[0]
        sum_y += beacon[1]

    avg_x = sum_x / 3
    avg_y = sum_y / 3

    noisy_x = avg_x + random.uniform(-noise_lvl, noise_lvl)
    noisy_y = avg_y + random.uniform(-noise_lvl, noise_lvl)

    return (noisy_x, noisy_y)

astronauts = []


#randomly adjusts each rovers x and y coordinates within a small realistic range to simulate the movement of the rover
def update_rover_pos():
    global rovers

    for i in range(len(rovers)):
        x, y = rovers[i]
        delta_x = random.uniform(-2,2)
        delta_y = random.uniform(-2,2)
        new_x = x + delta_x
        new_y = y + delta_y
        rovers[i] = (new_x, new_y)


#moves each astronaut 50% of the time by adding random x/y deltas, simulating realistic movement(we arent always moving sometimes we stay still)
def update_astro_pos():
    global astronauts

    for i in range(len(astronauts)):
        x,y = astronauts[i]
        move_chance = random.random() #pick num from 0-1

        if move_chance < 0.5:
            delta_x = random.uniform(-1,1)
            delta_y = random.uniform(-1,1)
            new_x = x + delta_x
            new_y = y + delta_y
            astronauts[i] = (new_x, new_y)


#calls both the rover and astronaut positions, helps with making the code look cleaner
def update_all_pos():
    update_rover_pos()
    update_astro_pos()

for _ in range(4):
    pos = sim_astronaut_pos(beacon_pos , noise_lvl = 0.5)
    astronauts.append(pos) 

#prints the coordinates of everything, habitat, astronauts, beacon points, and rovers to the terminal when asked for.
def show_positions():

    print("Main Habitat Position:", habitat_pos)

    print("\nBeacon Points:")
    for i in range(len(beacon_pos)):
        point = beacon_pos[i]
        print(f" Beacon {i+1}: {round(point[0], 2)}, {round(point[1], 2)}")

    print("\nRover Positions:")
    for i in range(len(rovers)):
        rover = rovers[i]
        print(f" Rover {i+1}: {round(rover[0], 2)}, {round(rover[1], 2)}")

    print("\nAstronaut Positions:")
    for i in range(len(astronauts)):
        astro = astronauts[i]
        print(f" Astronaut {i+1}: {round(astro[0], 2)}, {round(astro[1], 2)}")


#only prints the positions of the beacons
def show_beacons():
    print("\nBeacon Positions: ")
    for i, beacon in enumerate(beacon_pos, start = 1):
        print(f" Beacon {i}: ({round(beacon[0], 2)}, {round(beacon[1], 2)})")