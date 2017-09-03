#import subprocess
#import sys

#process = subprocess.call(['omxplayer','-s','--win','0 0 200 200','/home/pi/Downloads/Fashion_DivX720p_ASP.divx'])

from omxplayer import OMXPlayer
from time import sleep
import logging
    
logging.basicConfig(filename='dw_log.log',level=logging.DEBUG)    
file_path_or_url = 'asset_Nyxvq6sMM_Nexa_Baleno_Ad_-_Made_of_Mettle.mp4'

# This will start an `omxplayer` process, this might
# fail the first time you run it, currently in the
# process of fixing this though.
#player1 = OMXPlayer(file_path_or_url)
player2 = OMXPlayer('assets/asset_Nyxvq6sMM_Nexa_Baleno_Ad_-_Made_of_Mettle.mp4', args=['--win','0 0 1920 600'])


while(True):
    if player2.playback_status()== None:
        break;
    print(player2.position())
    sleep(1)
  

    
