#!/bin/bash

#==============================
#This program is monitor:
#	- The wifi signal strenght (in %) &
#	- Recieved (download) bytes of a given interface
#	- Thransmitted (upload) bytes of a given interface
#	- All data transfer (up- and download) in bytes
#	- Reciving speed (download speed) in byte/s
#	- Transmission speed (upload speed) in byte/s
#	- Total speed (up+download speed) in byte/s
#
#All of these values are written into a logfile 
#The inportant parameters could be set in the PREDEFINITIONS section
#
#:param LOGFILE: the name of the logfile where the output goes
#:param MONITORING_LENGHT: lenght of the monitoring process (+1s) in seconds
#:param INTERFACE_NUMBER: the number of the interface the iser wishes to monitor.
#							e.g lo is the loopback interface is the firts in my
#							case, as I didn't have eno1 at the moment of the code
#							write. The second interface is wlp3s0, which is the 
#							wifi thus I will give 2 ast this parameter if I want
#							to monitor the wifi traffic.
#							To check what do you need run: $: cat /proc/net/dev
#							and choose the interface ==> add the 'number' as parameter
#
#
#	Author: Rozgonyi Kristof
#	Date  : 2018
#	License: MIT
#==============================

#==============================
#		PREDEFINIONS
#==============================
#Set logfile name
LOGFILE=eduroam_test_1.log

#Set monitoring time in seconds
MONITORING_LENGHT=180;

#Set port to moitor in /proc/net/dev
INTERFACE_NUMBER=2;
#Add 2 that stands for the first two lines in /proc/net/dev
let "INTERFACE_NUMBER+=2";

#==============================
#			MAIN
#==============================
#Set date for the header
RUN_DATE="`date +%Y.%m.%d`";
RUN_TIME="`date +%H:%M:%S`";

#Print date as header to the logfile
echo Monitoring started "in" $RUN_DATE at $RUN_TIME >> $LOGFILE;

#Set initial values for speed calculations 
PREVIOUS_RECIEVED=`awk -v int_num="$INTERFACE_NUMBER" 'FNR == int_num{print $2}' /proc/net/dev`;
PREVIOUS_TRANSMITTED=`awk -v int_num="$INTERFACE_NUMBER" 'FNR == int_num{print $10}' /proc/net/dev`;
PREVIOUS_TOTAL=$((PREVIOUS_TRANSMITTED+PREVIOUS_RECIEVED));

#Print the base values to the second line to the header
echo $PREVIOUS_RECIEVED $PREVIOUS_TRANSMITTED $PREVIOUS_TOTAL >> $LOGFILE;

sleep 1;


#Set parameters for write out status
j=0;
STATUS=0;
let "STATUS=MONITORING_LENGHT/10";
TEN_PERCENT=0;
let "TEN_PERCENT=MONITORING_LENGHT/10";

i=0;
while sleep 1
	do
		let "i+=1"

		#Get wifi signal goodness (in %) from  /proc/net/wireless
    	WIFI_SIGNAL_STRENGHT=`awk 'NR==3 {print $3 "00"}''' /proc/net/wireless`;

    	#Get the traffic data of the chhosen interface from /proc/net/dev
		RECIEVED=`awk -v int_num="$INTERFACE_NUMBER" 'FNR == int_num{print $2}' /proc/net/dev`;
		TRANSMITTED=`awk -v int_num="$INTERFACE_NUMBER" 'FNR == int_num{print $10}' /proc/net/dev`;
		TOTAL=$((TRANSMITTED+RECIEVED));

		#Calculate traffic speed
		RECIEVED_SPEED=$((RECIEVED-PREVIOUS_RECIEVED));
		TRANSMITTED_SPEED=$((TRANSMITTED-PREVIOUS_TRANSMITTED));
		TOTAL_SPEED=$((TRANSMITTED_SPEED+RECIEVED_SPEED));

		PREVIOUS_RECIEVED=$RECIEVED;
		PREVIOUS_TRANSMITTED=$TRANSMITTED;

		#Print stuff to logfile
		echo $i $WIFI_SIGNAL_STRENGHT $RECIEVED $TRANSMITTED $TOTAL $RECIEVED_SPEED $TRANSMITTED_SPEED $TOTAL_SPEED >> $LOGFILE;

		#Print status
		if [ $i = $STATUS ]; then
			let "j+=10";
			let "STATUS+=TEN_PERCENT";
			echo $j%;
		fi

    	if [ $i = $MONITORING_LENGHT ]; then
    		break;
    	fi
	done
