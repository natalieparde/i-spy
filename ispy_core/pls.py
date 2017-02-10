from naoqi import ALBroker
from robot import Robot, robot, connect, broker

broker = ALBroker("broker1", "0.0.0.0", 0, "bobby.local", 9559)
r = Robot("r")
print r.ask_object()

broker.shutdown()


connect("bobby.local")
print robot().ask_object()
broker().shutdown()
