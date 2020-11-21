#!/usr/bin/env python
import rospy
import csv
import argparse
import functools
from p3dx_navigation.msg import Wifidata
from geometry_msgs.msg import PoseWithCovarianceStamped

posx = 0
posy = 0
g_ssid = []
g_rssi = []
permitWrite = False

sub_ssid = []
sub_rssi = []
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


class WifiPosLabelingNode:
    def __init__(self, file_name):
        rospy.init_node('wifipossaver_node')

        self.__csv_file = open(file_name, "w")
        rospy.on_shutdown(self.__csv_file.close);
        writer = csv.writer(self.__csv_file, lineterminator="\n")
        writer.writerow(["Position x", "Position y",
            "SSID1", "RSSI1", "SSID2", "RSSI2", "SSID3", "RSSI3", "SSID4", "RSSI4", "SSID5", "RSSI5", "Frame ID"])
        #rospy.Subscriber("amcl_pose", PoseWithCovarianceStamped, functools.partial(self.position_callback, writer=writer))
        #rospy.Subscriber("wifi_state", Wifidata, self.wifi_callback)

    def readCSV(self, csv_file):
        # super(WifiPosReaderNode, self).wait_for_subscriber(self.__pub, timeout=1.0) #timeout=5.0
        global row, PositionX, PositionY, SSID1, SSID2, SSID3, SSID4, SSID5, RSSI1, RSSI2, RSSI3, RSSI4, RSSI5
        maxPosX = 0
        maxPosY = 0

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
        node.writeCSV()

    def writeCSV(self, writer):
        global row, PositionX, PositionY, SSID1, SSID2, SSID3, SSID4, SSID5, RSSI1, RSSI2, RSSI3, RSSI4, RSSI5
        if not self.__csv_file.closed:
            writer.writerow([PositionX[i], PositionY[i], SSID1[i], RSSI1[i], SSID2[i], RSSI2[i], SSID3[i], RSSI3[i], SSID4[i], RSSI4[i], SSID5[i], RSSI5[i], frame])
            print("saved!!!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="wifipos_labeling node save the list of goals to csv file.")
    parser.add_argument("csv", metavar="file", type=str, help="name of csv file to read")
    parser.add_argument("-f", metavar="file", type=str, required=True, help="name of csv file to save")
    args = parser.parse_args()
    node = WifiPosLabelingNode(args.f)
    try:
        node.readCSV(args.csv)
    except rospy.ROSInterruptException:
        pass

    rospy.spin()
