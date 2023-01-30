from datetime import datetime
from pythonosc import dispatcher
from pythonosc import osc_server
from timeit import default_timer as timer
from playsound import playsound

ip = "0.0.0.0"
port = 5000
filePath = 'Recordings/MotorImagery/'
recording = False
initial_reading = 1
row = 1
current_file = ''
current_event = 0
start=timer()
end=timer()
secs = 10
lock=False
header = 'timestamp,RAW_TP9,RAW_AF7,RAW_AF8,RAW_TP10\n'
filename_array=[]

rec_dict = {
    "Left"     : 20,
    "Neutral" : 10,
    "Right" : 20,
    "Break" : 10
}  

#Initial Warmup
dateTimeObj = datetime.now()
timestampStr = dateTimeObj.strftime("%Y-%m-%d %H_%M_%S.%f")
ev = 'Warmup'
current_file = filePath + ev + '.' + timestampStr + '.csv'
f = open (current_file,'a+')


def eeg_handler(address: str,*args):
    global recording
    global initial_reading, row, header, current_event
    global start,end,secs
    global f, lock, filename_array
    
    
    if recording:
        
        if initial_reading==1:
            initial_reading = 0
            start=timer()
            f.write(header)
            print(f"Warmup \t{secs}  seconds")
            
        else:
            end=timer()
            if (end - start) >= (secs) and lock==False:
                lock=True
                
                f.close()
                row=1
                #start=timer()
                
                dateTimeObj = datetime.now()
                timestampStr = dateTimeObj.strftime("%Y-%m-%d %H_%M_%S.%f")            
                ev = list(rec_dict.items())[current_event][0]
                secs = list(rec_dict.items())[current_event][1]
                current_file = filePath + ev + '.' + timestampStr + '.csv'
                filename_array.append(current_file)
                f = open (current_file,'a+')
                f.write(header)
                playsound('Audio/{}.wav'.format(ev))
                start=timer()
                print(f"Think:\t {ev}   \t\t{secs}  seconds")
                dict_length = len(rec_dict)                                 
                if current_event < dict_length-1:                          
                    current_event += 1
                else:
                    current_event = 0
                    
                lock=False
                
            else:
                if lock==False:
                    fileString = str(row)
                    row+=1
                    for i in range(0,4):
                        fileString += ","+str(args[i])            
                    fileString+="\n"
                    f.write(fileString)

    
            
def marker_handler(address: str,i):
    global recording
    global start, current_event
    markerNum = address[-1]
    
    if (markerNum=="1"):        
        recording = True
        start = timer()
        print("Recording Started.")
        '''ev = list(rec_dict.items())[current_event][0]
        print(f"Think:\t {ev}   \t\t{secs}  seconds")'''
    if (markerNum=="2"):
        f.close()
        recording = False
        server.shutdown()
        print("Recording Stopped.")    

if __name__ == "__main__":
    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/muse/eeg", eeg_handler)
    dispatcher.map("/Marker/*", marker_handler)

    server = osc_server.ThreadingOSCUDPServer((ip, port), dispatcher)
    print("Listening on UDP port "+str(port)+"\nSend Marker 1 to Start recording and Marker 2 to Stop Recording.")
    server.serve_forever()