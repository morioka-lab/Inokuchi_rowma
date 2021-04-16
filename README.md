# Inokuchi_rowma
# 猪口システム（大竹さん＋末永さん融合システム）を実装する操作手順
 
## rowma_ros
 アプリとROSをつなぐ仲介役の役割をしているネットワークシステム  
 必要なパッケージやインストールについてはGithub／rowma／rowma＿rosを参照してください  
 $ rosrun rowma_ros rowma
 
## joy_twist
 PS４のjoyコントローラでロボットに速度指令値を送るROSパッケージ  
 Wifi電波強度マップを作成する際に使用します。  
 $ roslaunch joy_twist joy_twist.launch  
 
## icart_navigation
 ロボットの自律走行を実装するROSパッケージ  
 Wifi電波強度マップを作成する際にjoy_twistから速度指令値を受け取り、ロボットを実際に走行させます。  
 また、ロボットの自己位置をセンサにより観測します。（amcl）  
 $ roslaunch icart_navigation icart_navigation.launch  
 
### Wifi電波強度マップ作成の手順
$ roscore  
$ rosrun rowma_ros rowma    
アプリのボタンを操作し「OFF」→　「Publish」にする。  
$ roslaunch joy_twist joy_twist.launch  
$ roslaunch icart_navigation icart_navigation.launch  
$ roslaunch my_utility rviz.lauch
$ rosrun wifi_radio_intensity_map rowma_wifipos_saver.py -f (FILE NAME)    

以上の手順でROSのノードやlaunchファイルを実行し、PS4のjoyコントローラでロボットで走行させると、  
Wifiのスキャンデータと自己位置の情報からWIFi電波強度マップを作成します。  
保存する電波強度マップのファイル名は(FILE NAME)で指定してください。（例）wifi_pos.csv  

### Wifi電波強度マップに基づく人追従の手順
$ roscore  
$ rosrun rowma_ros rowma
このコマンドを実行することによりrowmaを起動したロボットに対してUUIDが発行されます。
その後アプリのUUID一覧から操作したいロボットのUUIDを選択し、
アプリのボタンを操作し「OFF」→　「Publish」にする。  
$ rosrun wifi_radio_intensity_map wifi wifipos_reader.py (FILE NAME)  
$ roslaunch icart_navigation icart_navigation.launch  
使用するWifi電波強度マップのファイル名は(FILE NAME)で指定してください。（例）wifi_pos.csv
