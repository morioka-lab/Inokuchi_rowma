#!/usr/bin/env python
import rospy
import csv
import argparse
import functools
import pdb
#from wifi_radio_intensity_map.msg import Wifidata
from geometry_msgs.msg import PoseWithCovarianceStamped
from std_msgs.msg import String

posx = 0
posy = 0
g_ssid = [''] * 5
g_rssi = [''] * 5
permitWrite = False
ssid = []
rssi = []


class WifiPosSaverNode:
    def __init__(self, file_name):
        rospy.init_node('wifipossaver_node')

        self.__csv_file = open(file_name, "w")
        rospy.on_shutdown(self.__csv_file.close);
        writer = csv.writer(self.__csv_file, lineterminator="\n")
        writer.writerow(["Position x", "Position y",
            "SSID1", "RSSI1", "SSID2", "RSSI2", "SSID3", "RSSI3", "SSID4", "RSSI4", "SSID5", "RSSI5", "Frame ID"])
        rospy.Subscriber("amcl_pose", PoseWithCovarianceStamped, functools.partial(self.position_callback, writer=writer))
        rospy.Subscriber("chatter2", String, self.wifi_rssi_callback)
        rospy.Subscriber("chatter", String, self.wifi_ssid_callback)
        
        #rospy.Subscriber("wifi_state", Wifidata, functools.partial(self.wifi_callback, writer=writer))

   
    """
    def position_callback(self, point):
        global posx, posy, permitWrite
        posx = point.pose.pose.position.x
        posy = point.pose.pose.position.y
        print("amcl_pose is received")
        permitWrite =True


    def wifi_callback(self, wifi_state, writer):
        if not self.__csv_file.closed and permitWrite:
            wifi = wifi_state
            writer.writerow([posx, posy, wifi.ssid[0], wifi.rssi[0], wifi.ssid[1], wifi.rssi[1], wifi.ssid[2], wifi.rssi[2], wifi.ssid[3], wifi.rssi[3], wifi.ssid[4], wifi.rssi[4]])
            print("wifi_state is received")
    """

    def position_callback(self, goal, writer):
        global posx, posy, permitWrite
        print("amcl_pose is received")
        if not self.__csv_file.closed and permitWrite:
            frame = goal.header.frame_id
            posx = goal.pose.pose.position.x
            posy = goal.pose.pose.position.y
            writer.writerow([posx, posy, g_ssid[0], g_rssi[0], g_ssid[1], g_rssi[1], g_ssid[2], g_rssi[2], g_ssid[3], g_rssi[3], g_ssid[4], g_rssi[4], frame])
            print("saved!!!")
        permitWrite = False


    def wifi_ssid_callback(self, chatter):
        #print("a")
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
        # print("SSID is received")
        

    def wifi_rssi_callback(self, chatter2):
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
        # print("RSSI is received")
        print("wifi_state is received!")
        permitWrite = True

  


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="goal_saver node save the list of goals to csv file.")
    parser.add_argument("-f", metavar="file", type=str, required=True, help="name of csv file to save")
    args = parser.parse_args()
    node = WifiPosSaverNode(args.f)
    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()
