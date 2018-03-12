"""
Plot the output file(s) created by the wifi_monitoring bash script

Author: Rozgonyi Kristof
Date  : 2018
License: MIT
"""
#==============================
#			IMPORTS
#==============================
import numpy as np;
import subprocess;

from matplotlib import pylab;
from matplotlib import pyplot as plt;

pylab.rcParams['figure.figsize'] = (18.0, 12.0);

#==============================
#			FUNCTIONS
#==============================
def insert_zeros_to_logfile(log,column=1):
    """This is a VERY UGLY function (written during a class) to fix logfiles in case of wifi dropout

    Sometimes wifi can go wrong, in which case /proc/net/wireless is empty.
    Thus some lines will contain only 7 columns.

    This function fill the missing column wit zeros, however it is not scalable as it reads the
    whole logfile and creates a temp.log file. Thus using it for really large files is
    NOT RECOMMENDED!

    :param log: path and name of logfile
    :param column: the number of the column (-1 due to python indexing) wich is missing from some lines
    """

    #Read old file
    with open(log) as f:
        content = f.readlines();
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content];

    #Write header to temp.log
    subprocess.call('echo {} >> temp.log'.format(content[0]), shell=True);
    subprocess.call('echo {} >> temp.log'.format(content[1]), shell=True);

    #Check each line and fill the missing column wit zeros
    for i in range(2,len(content)):
        line = np.array([int(float(j)) for j in str(content[i]).split(' ')]);
        if line.size < 8:
            newline=np.zeros(8);

            l=0;
            for k in range(0,8):
                newline[k] = line[l];
                if k != column:
                    l += 1;
                else:
                    newline[k] = 0;

            line.astype(int);
            line = newline;

        line.astype(str);

        #Write lines to temp.log
        subprocess.call("echo '{}' '{}' '{}' '{}' '{}' '{}' '{}' '{}' >> temp.log".format(line[0],
                                                                                        line[1],
                                                                                        line[2],
                                                                                        line[3],
                                                                                        line[4],
                                                                                        line[5],
                                                                                        line[6],
                                                                                        line[7]),
                        shell=True);

    #Remove old file and rename temp.log
    subprocess.call("rm {}".format(log), shell=True);
    subprocess.call("mv ./temp.log {}".format(log), shell=True);


def human_readable_memory_size(number_of_bytes, vectorize=False, base_dimension='B'):
    """Function changes bytes (or higher dimensions) to human readable format
    
    The function operates from Bites only up to Yottabytes
    
    :param number_of_bytes: Number of bytes need to convert human readable cannot be numpy array
    :param vectorize: Bool, allows param to be a numpy array
    :param base_dimension: String the dimension of the input data 
    :return: output_memory_size, output_memory_dimension
    """
    dimensions = np.array(['B','KB','MB','GB','TB','PB','EB','ZB','YB']);

    if vectorize == False:
        #=== Change up ===
        b_change_up = lambda x: x / 1024;#Function to change between B->KB->MB->GB->...ect
        b_change_down = lambda x: x * 1024;#Function to change between ect.. ->GB->MB->KB->B
               
        output_memory_size = number_of_bytes;
        output_memory_dimension = 'B';
    
        i = int(np.argwhere(dimensions==base_dimension)[0]);
        while True:
            if i == 8:
                output_memory_dimension = dimensions[i];
                break;
            if output_memory_size > 1023: #I suppose to be 1024 but need to be 1023 to get egzact output  
                output_memory_size = b_change_up(output_memory_size);
                i += 1;
            else:
                output_memory_dimension = dimensions[i];
                break;
                
        if output_memory_dimension != base_dimension:
            return output_memory_size, output_memory_dimension;
        
        #=== Change down ===
        i = int(np.argwhere(dimensions==base_dimension)[0]);
        while True:
            if i <= 0:
                i = 0;
                output_memory_dimension = dimensions[i];
                break;
            if output_memory_size < 1023:
                output_memory_size = b_change_down(output_memory_size);
                i -= 1;
            else:
                output_memory_dimension = dimensions[i];
                break;
                
        return output_memory_size, output_memory_dimension; 
    
    else:
        b_change_up = lambda x: np.divide(x,1024);#Function to change between B->KB->MB->GB->...ect

        output_memory_size = np.copy(number_of_bytes);
        output_memory_dimension = base_dimension;
        
        #=== Change up ===
        i = int(np.argwhere(dimensions==base_dimension)[0]);
        while True:
            if i == 8:
                output_memory_dimension = dimensions[i];
                break;
            if np.any(np.greater(output_memory_size,1023)): #I suppose to be 1024 but need to be 1023 to get egzact output  
                output_memory_size = np.divide(output_memory_size,1024);
                i += 1;
            else:
                output_memory_dimension = dimensions[i];
                break;
        
        if output_memory_dimension != base_dimension:
            return output_memory_size, output_memory_dimension;
                
        #=== Change down ===
        i = int(np.argwhere(dimensions==base_dimension)[0]);
        while True:
            if i <= 0:
                i = 0;
                output_memory_dimension = dimensions[i];
                break;
            if np.any(np.less(output_memory_size,1)):
                output_memory_size = np.multiply(output_memory_size,1024);
                i -= 1;
            else:
                output_memory_dimension = dimensions[i];
                break;
                
        return output_memory_size, output_memory_dimension;

def change_memory_dimension(number_of_bytes, base_dimension, output_dimension, vectorize=False):
    """Function changes from a base dimension to a given dimension

    :param number_of_bytes: Number of bytes need to convert human readable cannot be numpy array
    :param base_dimension: String, the dimension of the input data 
    :param output_dimension: Strin,g the dimension of the output data 
    :param vectorize: Bool, allows param to be a numpy array
    :return: output_memory_size, output_memory_dimension
    """

    dimensions = np.array(['B','KB','MB','GB','TB','PB','EB','ZB','YB']);

    #Check if we need to change or not
    if np.argwhere(dimensions == base_dimension) == np.argwhere(dimensions == output_dimension):
        return number_of_bytes, base_dimension;
    else:
        diff = int(np.argwhere(dimensions == output_dimension)[0])\
                - int(np.argwhere(dimensions == base_dimension)[0]);

    if vectorize == False:
        #=== Change up ===
        b_change_up = lambda x: x / 1024;#Function to change between B->KB->MB->GB->...ect
        b_change_down = lambda x: x * 1024;#Function to change between ect.. ->GB->MB->KB->B
        
        output_memory_size = number_of_bytes;

        if diff > 0:
            for i in range(0,diff):
                output_memory_size = b_change_up(output_memory_size);
        else:
            for i in range(0,-diff):
                output_memory_size = b_change_down(output_memory_size);

        return output_memory_size, output_dimension;

    else:
        b_change_up = lambda x: np.divide(x,1024);#Function to change between B->KB->MB->GB->...ect

        output_memory_size = np.copy(number_of_bytes);

        if diff > 0:
            for i in range(0,diff):
                output_memory_size = b_change_up(output_memory_size);
        else:
            for i in range(0,-diff):
                output_memory_size = np.multiply(output_memory_size,1024);

        return output_memory_size, output_dimension;

def plot_monitoring_statistics(log, title, save=False, resolution=1):
    """Plot the % of the wifi signal strenght

    :param log: path and name of logfile
    :param title: the title of the plot and the name of the output file if save is True
    :param save: bool, if true the plot is saven
    :param resolution: every nth point given by the resolution will be plotted.
                        e.g if resolution is 60 every 60th point, thus a point in every second
                        will be plotted ==> it is for smoothening the plot
    """

    #Load data and set up monitoring result arrays
    data = np.loadtxt(log, skiprows=2);

    #Read header 
    header = str(subprocess.check_output('head -n 2 %s | sed -n 1p' %log, shell=True), 'utf-8');
    #First line of the file (from the first two line)

    #This is what I use to scale to the real measurment 
    base_transfer_values = str(subprocess.check_output('head -n 2 %s | sed -n 2p' %log, shell=True), 'utf-8')[:-1];
    base_transfer_values = np.array([int(i) for i in base_transfer_values.split(' ')]);

    #Read logfile
    time = data[:,0];
    wifi_signal_strenght = data[:,1];
    recieved, recieved_dimension = human_readable_memory_size(data[:,2]-base_transfer_values[0],vectorize=True);
    transmitted, transmitted_dimension = human_readable_memory_size(data[:,3]-base_transfer_values[1],vectorize=True);
    total, total_dimension = human_readable_memory_size(data[:,4]-base_transfer_values[2],vectorize=True);
    recieved_speed, recieved_speed_dimension = human_readable_memory_size(data[:,5],vectorize=True);
    transmitted_speed, transmitted_speed_dimension = human_readable_memory_size(data[:,6],vectorize=True);
    total_speed, total_speed_dimension = human_readable_memory_size(data[:,7],vectorize=True);
    
    #Find smallest dimension & change everything to that base
    ax2_dimension_list = [transmitted_dimension, recieved_dimension, total_dimension];
    ax2_dimension = ax2_dimension_list[np.unravel_index(np.argmin(data[:,2:5], axis=None),
                                        data[:,2:5].shape)[1]];

    recieved, recieved_dimension = change_memory_dimension(recieved,
                                                            recieved_dimension,
                                                            ax2_dimension,
                                                            vectorize=True);

    transmitted, transmitted_dimension = change_memory_dimension(transmitted,
                                                                transmitted_dimension,
                                                                ax2_dimension,
                                                                vectorize=True);

    total, total_dimension = change_memory_dimension(total,
                                                    total_dimension,
                                                    ax2_dimension,
                                                    vectorize=True);

    ax3_dimension_list = [transmitted_speed_dimension, recieved_speed_dimension, total_speed_dimension];
    ax3_dimension = ax3_dimension_list[np.unravel_index(np.argmin(data[:,5:7], axis=None),
                                        data[:,5:7].shape)[1]];

    recieved_speed, recieved_speed_dimension = change_memory_dimension(recieved_speed,
                                                                        recieved_speed_dimension,
                                                                        ax3_dimension,
                                                                        vectorize=True);

    transmitted_speed, transmitted_speed_dimension = change_memory_dimension(transmitted_speed,
                                                                            transmitted_speed_dimension,
                                                                            ax3_dimension,
                                                                            vectorize=True);

    total_speed, total_speed_dimension = change_memory_dimension(total_speed,
                                                                total_speed_dimension,
                                                                ax3_dimension,
                                                                vectorize=True);

    #======
    #Plot
    #======
    fig, (ax1, ax2, ax3)  = plt.subplots(3, sharex=True);

    plt.suptitle('%s\n%s' %(title, header[:-1]), fontsize=24);
     
    #=== First plot: wifi signal strenght ===  
    ax1.plot(time[0::resolution],wifi_signal_strenght[0::resolution], '-', lw=2, color='#246EB3', zorder=2);

    ax1.set_xlim([time[0],time[-1]]);
    ax1.set_ylim([0,100]);

    ax1.tick_params(labelsize=16);
    ax1.grid(True);

    #ax1.set_xlabel('Monitoring time [s]', fontsize=18);
    ax1.set_ylabel('Wifi signal strenght %', fontsize=18);

    #=== Second plot: data transfer rates ===  
    ax2.plot(time[0::resolution], recieved[0::resolution],
            '-', lw=2, color='#246EB3', zorder=3, label='Recieved', alpha=1);
    ax2.plot(time[0::resolution], transmitted[0::resolution],
            '-', lw=2, color='#3CB371', zorder=2, label='Transmitted', alpha=1);
    ax2.plot(time[0::resolution], total[0::resolution],
            '--', lw=2, color='#fa4506', zorder=4, label='Total', alpha=1);
    
    ax2.set_xlim([time[0],time[-1]]);

    ax2.tick_params(labelsize=16);
    ax2.grid(True);

    ax2.set_ylabel('Traffic [%s]' %ax2_dimension, fontsize=18);

    ax2.legend(fontsize=16);

    #=== Second plot: data transfer rates ===  
    ax3.plot(time[0::resolution], recieved_speed[0::resolution],
            '-', lw=2, color='#246EB3', zorder=3, label='Recieved', alpha=1);
    ax3.plot(time[0::resolution], transmitted_speed[0::resolution],
             '-', lw=2, color='#3CB371', zorder=2, label='Transmitted', alpha=1);
    ax3.plot(time[0::resolution], total_speed[0::resolution],
            '--', lw=2, color='#fa4506', zorder=4, label='Total', alpha=1);
    
    ax3.set_xlim([time[0],time[-1]]);

    ax3.tick_params(labelsize=16);
    ax3.grid(True);

    ax3.set_xlabel('Monitoring time [s]', fontsize=18);
    ax3.set_ylabel('Traffic speed [%s/s]' %ax3_dimension, fontsize=18);

    ax3.legend(fontsize=16);

    #=====
    plt.tight_layout(rect=[0, 0.03, 1, 0.9]);

    if save == True:
        plt.savefig('%s.pdf' %title);
    else:        
        plt.show(fig);

#==============================
#			MAIN
#==============================
#insert_zeros_to_logfile('./eduroam_random_downloads_test.log',1);

plot_monitoring_statistics('./eduroam_random_downloads_test.log',
                            'Randomly_downloading_large_packages',
                            save=True,
                            resolution=1);
    