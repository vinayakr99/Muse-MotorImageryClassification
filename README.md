# Muse-MotorImageryClassification
The project is aimed at creating a Real-time Left-Right Motor Imagery Classifier using CNN. Device used is a Muse 2 brain sensing headband with 4 electrode channels - TP9, AF7, AF8, TP10. Data is streamed using the 'Mind Monitor' app.

Following codes have been implemented till now:

MotorImagery_OSC_Record - 
1) Record and save EEG data as CSV files from a Muse 2 headband using the MInd Monitor app and python osc module.
2) Events can be configured in the rec_dictionary

MotorImagery_Training - 
1) Configure and train a CNN model based on 'EEG-ITNet'
2) Load the CSV data recordings into a Pandas dataframe and convert into MNE epochs for training

MotorImagery_OSC_Predict -
1) Make real time predictions using the trained model.
