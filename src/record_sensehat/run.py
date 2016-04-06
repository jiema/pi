from sense_hat import SenseHat
sense = SenseHat()
sense.clear()
while True:
    o = sense.get_orientation()
    pitch = o["pitch"]
    roll = o["roll"]
    yaw = o["yaw"]

    pitch = round(pitch, 1)
    roll = round(roll, 1)
    yaw = round(yaw, 1)
    print("pitch %s roll %s yaw %s" % (pitch, roll, yaw))