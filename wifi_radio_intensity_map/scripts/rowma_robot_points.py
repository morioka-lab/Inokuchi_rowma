#!/usr/bin/env python

from rowmapy import Rowma
import json
import pdb

import tf
import rospy
import actionlib
from random import random
from visualization_msgs.msg import Marker
from geometry_msgs.msg import PoseWithCovarianceStamped, PoseStamped

rowma = Rowma()

conn_list = rowma.get_current_connection_list()
## Get the first robot in the official public network
robot = conn_list[0]
rowma.connect()
print('robot: '+robot['uuid'])
print('application: '+rowma.uuid)

# rowma.set_topic_route(robot['uuid'], 'application', rowma.uuid, '/robot_position')

rospy.init_node("marker_pub")

class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

robot = Robot(0, 0)

start_point_x = 21.7
start_point_y = -3

def on_chatter(msg):
    _depict_marker(msg.pose.pose.position.x, msg.pose.pose.position.y)
    print(abs(robot.x - msg.pose.pose.position.x))
    print(abs(robot.y - msg.pose.pose.position.y))

def on_receive_robot_position(msg):
    robot.x = msg.pose.pose.position.x
    robot.y = msg.pose.pose.position.y

def _depict_marker(x, y):
    pub = rospy.Publisher("arrow_pub", Marker, queue_size = 10)

    marker_data = Marker()
    marker_data.header.frame_id = "map"
    marker_data.header.stamp = rospy.Time.now()

    marker_data.ns = "basic_shapes"
    marker_data.id = 0

    marker_data.action = Marker.ADD

    marker_data.pose.position.x = x
    marker_data.pose.position.y = y
    marker_data.pose.position.z = 0.0

    marker_data.pose.orientation.x=0.0
    marker_data.pose.orientation.y=0.0
    marker_data.pose.orientation.z=0.0
    marker_data.pose.orientation.w=1.0

    marker_data.color.r = random()
    marker_data.color.g = random()
    marker_data.color.b = random()
    marker_data.color.a = 1.0

    marker_data.scale.x = 1.1
    marker_data.scale.y = 1.1
    marker_data.scale.z = 0.05

    marker_data.lifetime = rospy.Duration()

    marker_data.type = 3

    pub.publish(marker_data)


def cb(msg):
    print("cb")
    print(msg)

rospy.Subscriber('robot_position_a', PoseWithCovarianceStamped, on_receive_robot_position)

rospy.Subscriber('robot_position_b', PoseWithCovarianceStamped, on_chatter)
rowma.subscribe('/robot_position_b', cb)
