# The-Real-time-Visualization-System-Based-on-CSI
This project is designed for showing realtime curves that can show the change of CSI signals.

This project is designed as a plug-in of CSI-Tool, which means you need to include all the files of CSI-Tool(https://github.com/dhalperi/linux-80211n-csitool-supplementary) to see how the project work.

For more detailed information, check https://github.com/lubingxian/Realtime-processing-for-csitool and https://github.com/dhalperi/linux-80211n-csitool-supplementary.

In matlab:
run read_bf_socket using Matlab

or in Python
run read_bf_file.py using Python


In netlink:
gcc log_to_server.c -o log_to_server

sudo ./log_to_server <ip> <port>
  
Thanks for the direction and help from Mr. Lu Bingxian, who directed me in my last two year in undergraduate study and led me to acquire precious experience.
