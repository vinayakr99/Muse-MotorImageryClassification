from pythonosc import dispatcher
from pythonosc import osc_server
import mne
import tensorflow as tf
import numpy as np
import pandas as pd
import multiprocessing
from timeit import default_timer as timer
import sys

ip = "0.0.0.0"
port = 5000

Fs = 256                                                                         #Sampling Frequency
n_channels = 4                                                                   #Number of Channels
Wn = 1                                                                           #Prediction Window Duration
Wn_overlap = 0.2                                                                 #Prediction Window Overlap
                                                               
buffer_main = np.empty((0,n_channels))
buffer_transfer = np.empty((0,n_channels))

start = 0  
recording = False
lock = False 

queue = multiprocessing.Queue()
wait = multiprocessing.Value('i',1)
 
   
def convertDF2MNE(sub):
    mne.set_log_level(verbose=False, return_old_level=False, add_frames=None)
    info = mne.create_info(list(sub.columns), ch_types=['eeg'] * len(sub.columns), sfreq=Fs)
    info.set_montage('standard_1020')
    data=mne.io.RawArray(sub.T, info)
    data.set_eeg_reference()
    epochs=mne.make_fixed_length_epochs(data,duration=Wn)
    return epochs.get_data()
              

def eeg_handler(address: str,*args):  
    global buffer_main
    global recording
    global lock
    
    if recording:
        buffer_main = np.append(buffer_main,[args[:4]],axis=0)

    if buffer_main.shape[0]>=Wn*Fs and lock==False:
        lock=True
        buffer_transfer = buffer_main[:Wn*Fs]
        buffer_main = buffer_main[int((Wn*(1-Wn_overlap*0.5)*Fs)):]
        queue.put(buffer_transfer)
        wait.value = 0 
        lock=False
          
            
def marker_handler(address: str,i):
    global recording
    global start
    markerNum = address[-1]
    
    if (markerNum=="1"):        
        recording = True
        print("Prediction Started")
        start=timer()
        print(str(start))
        print('time is {}'.format(str(start)))

    if (markerNum=="2"):
        recording = False
        server.shutdown()
        print("Prediction Stopped")
 
def Model_Run(test_model,queue,wait): 
    
    while wait.value!=0:
        continue
    
    np_array = queue.get() 
    df = pd.DataFrame(np_array,columns=["TP9","AF7", "AF8","TP10"])             #Converting to Dataframe for MNE epoch
    x_pred = convertDF2MNE(df)
    x_pred = x_pred[:,:,:,np.newaxis]
    y_pred = test_model.predict(x_pred)                                         #Predict
    if y_pred[0][0]>y_pred[0][1]:
        print('Predicted : Left with accuracy = {0:.3f}'.format(y_pred[0][0]))
    else:
        print('Predicted : Left with accuracy = {0:.3f}'.format(y_pred[0][1]))
    sys.stdout.flush()
    
    wait.value=1
    Model_Run(test_model, queue, wait)

        
def Inference(queue,wait):
    
    test_model = tf.keras.models.load_model('Models/EEG-ITNet/model.h5')
    Model_Run(test_model, queue, wait)
    

if __name__ == "__main__":
    
    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/muse/eeg", eeg_handler)
    dispatcher.map("/Marker/*", marker_handler)
    
    inference = multiprocessing.Process(target=Inference, args=(queue,wait))
    inference.start()
    
    server = osc_server.ThreadingOSCUDPServer((ip, port), dispatcher)
    print("Listening on UDP port "+str(port)+"\nSend Marker 1 to Start Predicting and Marker 2 to Stop Predicting.")
    server.serve_forever()
    
    inference.terminate()
   