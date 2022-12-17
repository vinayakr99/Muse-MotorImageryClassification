# Muse-MotorImageryClassification
The project is aimed at creating a Left-Right Motor Imagery Classifier using CNN.

Following codes have been implemented till now:

OSC_Record_MotorImagery - 
1) Record and save EEG data as CSV files from a Muse 2 headband using the MInd Monitor app and python osc module.

Classifier_MotorImagery - 
1) Loads the CSV data recordings into a Pandas dataframe.
2) Convert the data into MNE epochs, then perform continuous wavelet transform (CWT) and save as scaleograms.
3) Create a new dataframe with the scaleogram paths and labels.
4) Create a model using the Pytorch lightning module and train the model.

Work is still in progress, model needs improvement.
