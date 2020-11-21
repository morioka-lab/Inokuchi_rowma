#!/usr/bin/python
# coding: UTF-8
import rospy
import tf
import actionlib
import time
import argparse
import csv
import math
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from wifi_radio_intensity_map.msg import Wifidata
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped, Point, Quaternion
from std_msgs.msg import Int8
from std_msgs.msg import String


max_rssi = -100
permitRead = False
PositionX = []
PositionY = []
SSID1 = []
SSID2 = []
SSID3 = []
SSID4 = []
SSID5 = []
RSSI1 = []
RSSI2 = []
RSSI3 = []
RSSI4 = []
RSSI5 = []
row = []
ssid = []
rssi = []
g_ssid = [''] * 5
g_rssi = [''] * 5
G_rssi = []
presubssid = ''
prePositionX = 20
prePositionY = -3
num = 0
followmode = 1

maxPosX = 0
maxPosY = 0

robo_orientation = Quaternion()

goal_point = Point()

stationary_time = time.time()



"""class RosNode(object):
    def wait_for_subscriber(self, pub, timeout):
        timeout_t = time.time() + timeout
        while pub.get_num_connections() == 0 and timeout_t > time.time():
            self.sleep(0.01)

    def sleep(self, duration):
        rospy.rostime.wallsleep(duration)
"""

class WifiPosReaderNode:
    def __init__(self):
        # self.__pub = rospy.Publisher("/goal", PoseStamped, queue_size=100)
        rospy.init_node("wifiposreader_node")
        rospy.Subscriber("follow_mode", Int8, self.mode_callback)
        rospy.Subscriber("chatter", String, self.wifi_ssid_callback)
        rospy.Subscriber("chatter2", String, self.wifi_rssi_callback)
        rospy.Subscriber("amcl_pose", PoseWithCovarianceStamped, self.amcl_pose_callback)
        rospy.Subscriber("/move_base_simple/goal", PoseStamped, self.goal_callback)
        #self.__pub = rospy.Publisher("/move_base_simple/goal", PoseStamped, queue_size=100)
        self.__pub_mode = rospy.Publisher("follow_mode", Int8, queue_size=1)

    def readCSV(self, csv_file):
        # super(WifiPosReaderNode, self).wait_for_subscriber(self.__pub, timeout=1.0) #timeout=5.0
        global row, PositionX, PositionY, SSID1, SSID2, SSID3, SSID4, SSID5, RSSI1, RSSI2, RSSI3, RSSI4, RSSI5

        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                if rospy.is_shutdown():
                    break;
                # rospy.loginfo(row)
                PositionX.append(float(row[0]))
                PositionY.append(float(row[1]))
                SSID1.append(row[2])
                RSSI1.append(int(row[3]))
                SSID2.append(row[4])
                RSSI2.append(int(row[5]))
                SSID3.append(row[6])
                RSSI3.append(int(row[7]))
                SSID4.append(row[8])
                RSSI4.append(int(row[9]))
                SSID5.append(row[10])
                RSSI5.append(int(row[11]))
        print("CSV file was read")

    def mode_callback(self, mode):
        global followmode
        followmode =  mode.data


    def goal_callback(self, sub_goal):
        global goal_point, stationary_time
        goal_point = sub_goal.pose.position
        stationary_time = time.time()



    def amcl_pose_callback(self, sub_amcl_pose):
        print("robot pose is received!! ")
        global followmode, maxPosX, maxPosY, robo_orientation, goal_point
        robo_pos = sub_amcl_pose.pose.pose.position
        robo_orient = sub_amcl_pose.pose.pose.orientation
        robo_orientation = robo_orient

        print("follow mode is " + str(followmode))
        #print(str(robo_pos.x) + ", " + str(robo_pos.y) + ", " + str(maxPosX) + ", " + str(maxPosY))
        goal_distance = math.sqrt((robo_pos.x - maxPosX)*(robo_pos.x - maxPosX) + (robo_pos.y - maxPosY)*(robo_pos.y - maxPosY))
        print("goal_distance is " + str(goal_distance))
        if followmode == 0:
            if goal_distance <= 1.0:
                followmode = 1
                print("Change to Local!!!!!!!!!!!!!!!!!!!!!!!!!")
                self.__pub_mode.publish(followmode)
        else:#followmode == 1（local following中）のとき
            distance_global_local = math.sqrt((goal_point.x - maxPosX)*(goal_point.x - maxPosX) + (goal_point.y - maxPosY)*(goal_point.y - maxPosY))
            if 15.0 < distance_global_local:
                followmode = 0
                print("D:Change to Global!!!!!!!!!!!!!!!!!!!!!!!!!")
                self.__pub_mode.publish(followmode)

        """
        if goal_distance <= 0.5 and followmode == 0: # 1/29 1m => 0.5mに変更
            followmode = 1
            print("followmode change!!!!!!!!!!!!!!!!!!!!!!!!!")
            self.__pub_mode.publish(followmode)
        elif 10 <= goal_distance and followmode == 1:
            followmode = 0
            print("followmode change!!!!!!!!!!!!!!!!!!!!!!!!!")
            self.__pub_mode.publish(followmode)
        """
    def wifi_rssi_callback(self, chatter2):
        print("Scaned Max SSID is " + str(g_ssid[0]))
        #print("Max RSSI is " + str(g_rssi[0]))
        j = 0
        RSSI = []
        global  permitWrite
        rssi = str(chatter2)
        num2 = 8
        while num2 < len(rssi)-2: 
           if(rssi[num2] != ',' and rssi[num2] != ' '):
              RSSI += rssi[num2]
           elif(rssi[num2] == ','):
              g_rssi[j] = int(''.join(RSSI))
              j += 1
              RSSI = []
           num2 += 1 
        if(j == 4):
           g_rssi[j] = int(''.join(RSSI))
           #print("rssi received!!")

    def wifi_ssid_callback(self, chatter):
        global sub_ssid, sub_rssi, max_rssi, presubssid, prePositionX, prePositionY, num, maxPosX, maxPosY, robo_orientation, followmode, G_rssi
        permitPub = False
        rate = rospy.Rate(10) # 10hz
        max_rssi = -100
        i = 0
        SSID = []
        ssid = str(chatter)
        num = 8;
        while num < len(ssid)-2: 
           if(ssid[num] != ',' and ssid[num] != ' '):
              SSID += ssid[num]
           elif(ssid[num] == ','):
              g_ssid[i] = ''.join(SSID)
              i += 1
              SSID = []
           num += 1 
        if(i == 4):
           g_ssid[i] = ''.join(SSID)
        #print("wifi_state is received !!")
        #print(sub_ssid)
        #print(sub_rssi)

        i = 0
        for i in range(len(SSID1)):
            if SSID1[i] == g_ssid[0] and RSSI1[i] > max_rssi:
                #print("goal updated!!")
                maxPosX = PositionX[i]
                maxPosY = PositionY[i]
                max_rssi = RSSI1[i]
                #rospy.loginfo(maxPosX)
                #rospy.loginfo(maxPosY)
                #rospy.loginfo(max_rssi)
                #print("updated max")
                #print(g_rssi[0])
                #print(g_rssi[1]) 
                if int(g_rssi[0]) > -45 and abs(int(g_rssi[0]) - int(g_rssi[1])) > 1:
                    #print("rssi = " + str(int(g_rssi[0])))
                    permitPub = True
                elif int(g_rssi[0]) > -50 and abs(int(g_rssi[0]) - int(g_rssi[1])) > 1:
                    permitPub = True
                
                elif int(g_rssi[0]) > -50 and abs(int(g_rssi[0]) - int(g_rssi[1])) > 1:
                    permitPub = True
                else:
                    permitPub = False
                #print(abs(int(g_rssi[0]) - int(g_rssi[1])))
        if permitPub == False:
            print("not found")
            """
            for i in range(len(SSID2)):
                if SSID2[i] == g_ssid[0] and RSSI2[i] > max_rssi:
                    maxPosX = PositionX[i]
                    maxPosY = PositionY[i]
                    max_rssi = RSSI2[i]
                    #rospy.loginfo(maxPosX)
                    ##rospy.loginfo(maxPosY)
                    #rospy.loginfo(max_rssi)
                    print("updated max")
                    permitPub = True
           """

        """
        if permitPub == False:
            print("Not matching")
            for i in range(len(SSID1)):
                if SSID1[i] == sub_ssid[1] and RSSI1[i] > max_rssi:
                    maxPosX = PositionX[i]
                    maxPosY = PositionY[i]
                    max_rssi = RSSI1[i]
                    rospy.loginfo(maxPosX)
                    rospy.loginfo(maxPosY)
                    rospy.loginfo(max_rssi)
                    print("updated max")
                    permitPub = True
        """

        """
        if permitPub == False:
            print("Not matching")
        """

        """
        if permitPub:
            if sub_rssi[] #??????
        """
        #print("prepositon is " + str(prePositionX))
        distance = ((maxPosX - prePositionX) * (maxPosX - prePositionX)) + ((maxPosY - prePositionY) * (maxPosY - prePositionY)) #distance of 2points(published point and publishing point)

        #print("distance is" + str(distance))

        """
        if distance < 16: #一時消去　ここはあとで検証
            permitPub = False
            print("Too near the point set")
        """

        """
        if 0 < distance < 5: #distance to the second power
            permitPub = False
            print("Too near the point set")
        """
        """
        if presubssid == g_ssid[0]:
            permitPub = False
            print("SSID is not changing")
        """


        if permitPub:
            #goal = self.__parse_row(row, maxPosX, maxPosY)
            listener = tf.TransformListener()
            client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
            client.wait_for_server()
            listener.waitForTransform("map", "base_link", rospy.Time(), rospy.Duration(4.0))
            goal = self._create_al_goal_pose(maxPosX, maxPosY)
            if followmode == 0:
                #self.__pub.publish(goal)#########################################publish
                client.send_goal(goal)
                print("published")
                print(goal)
                prePositionX = maxPosX
                prePositionY = maxPosY
            else:
                print("Local following is performing")
                nowtime = time.time()

                if 30.0 < nowtime-stationary_time:
                    followmode = 0
                    print( str(nowtime-stationary_time) + "s! Change to GlobalFollowing!!!!!!!!!!!!!!!!!!!!!!!!!")
                    self.__pub_mode.publish(followmode)

           
            rate.sleep()
            num = num + 1
            #rospy.loginfo(num)
        elif permitPub == False:
            print("Not publishing")

        presubssid = g_ssid[0]

    """
    def __parse_row(self, row, x, y):
        frame = row[-1]

        goal = PoseStamped()
        goal.pose.position.x = x
        goal.pose.position.y = y
        goal.pose.position.z = 0
        goal.pose.orientation.x = 0
        goal.pose.orientation.y = 0
        goal.pose.orientation.z = robo_orientation.z
        goal.pose.orientation.w = robo_orientation.w
        goal.header.frame_id = frame
        goal.header.stamp = rospy.Time.now()

        return goal
    """

    def _create_al_goal_pose(self, x, y):
        goal_pose = MoveBaseGoal()
        goal_pose.target_pose.header.frame_id = 'map'
        goal_pose.target_pose.pose.position.x = x
        goal_pose.target_pose.pose.position.y = y
        goal_pose.target_pose.pose.position.z = 0
        goal_pose.target_pose.pose.orientation.x = 0
        goal_pose.target_pose.pose.orientation.y = 0
        goal_pose.target_pose.pose.orientation.z = robo_orientation.z
        goal_pose.target_pose.pose.orientation.w = robo_orientation.w
        goal_pose.target_pose.header.stamp = rospy.Time.now()
        
        return goal_pose


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="wifipos_reader node publish goals from csv file.")
    parser.add_argument("csv", metavar="file", type=str, help="name of csv file to read")
    args = parser.parse_args()
    node = WifiPosReaderNode()

    try:
        node.readCSV(args.csv)
    except rospy.ROSInterruptException:
        pass

    rospy.spin()
