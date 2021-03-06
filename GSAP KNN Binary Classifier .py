
# coding: utf-8

# In[ ]:


import numpy as np
from scipy import signal, ndimage

class DataConditioner:
    def __init__(self):
        pass

    def find_peaks(self, data):
        """
        Returns a np.array with the indices of all local maxima in data.
        """
        peakInd = (np.diff(np.sign(np.diff(data))) < 0).nonzero()[0] + 1 # local max_
        return peakInd

    def Peak_Threshold(self, peakInd, data, noOfPeaks):
        """
        Find the noOfPeaks highest peaks within data.
        Return 70% of the average of these peaks.
        """
        highestPeaks = list()
        for index in peakInd:
            if len(highestPeaks) < 5:
                highestPeaks.append(data[index])
                next
            for peak in highestPeaks:
                if data[index] > peak:
                    highestPeaks[highestPeaks.index(peak)] = data[index]
                    break
        arr = np.array(highestPeaks)
        return 0.7 * arr.mean()

    def find_low_peaks(self, data):
        """
        Returns a list of indices that mark the temporal location of R peaks in
        data. Data is assumed to be a standard ECG lead 1 signal.
        """
        # Find all peaks.
        peakInd = self.find_peaks(data)
        # Find threshold for R peaks.
        threshold = self.find_peak_threshold(peakInd, data, 5)
        # Accept peaks if higher than threshold.
        rPeaksInd = self.remove_small_peaks(peakInd, data, threshold)
        rPeaksVal = data[rPeaksInd]
        return rPeaksInd, rPeaksVal

    def KNN_Time_Between_Peaks(self, rPeaksInd):
        """
        Calculate the average time between two consecutive peaks in rPeaksInd..
        """
        periods = list()
        for i in range(0,len(rPeaksInd)-1):
            periods.append(rPeaksInd[i+1] - rPeaksInd[i])
        periods = np.array(periods)
        return periods.mean()

    def cut_data_into_signals(self, data, rPeaksInd):
        """
        Cut the signal into single signals, centered around the R peak.
        Return a list of signal slices.
        The first and last R peak in the signal are discarded.
        """
        beatPeriod = self.KNN_Time_Between_Peaks(rPeaksInd)
        slices = list()
        for peak in rPeaksInd[1:-1]:
            start = peak - int(beatPeriod / 2)
            end = peak + int(beatPeriod / 2)
            slices.append(data[start:end])
        return slices

    def zoom_to_length(self, data, length):
        """
        Zoom all 1D arrays in the list data so that their length equals length.
        """
        dataOut = list()
        for arr in data:
            zoomFactor = length / len(arr)
            new = ndimage.zoom(arr, zoomFactor, order=1)
            dataOut.append(new)
        return dataOut
    
    def scale_to_int(self, data, resolution):
        dataOut = list()
        for arr in data:
            scaled = arr * resolution
            rounded = np.rint(scaled)
            dataOut.append(rounded.astype(int))
        return dataOut

    def Binary_Classification(self, data):
        """
        Condition a continuous signal so that it can be used as
        samples to train a classifier.
        Returns a list of arrays where each array is a signal slice of one ion channel activity,
        centered around the R peak.
        """
        # Smooth the data.
        Wn = 0.08
        b, a = signal.butter(6, Wn, 'lowpass', analog=False)
        lead1_smoothed = signal.filtfilt(b, a, lead1_driftless)
        # Find location and value of R peaks.
        rPeaksInd, rPeaksVal = self.find_low_peaks(lead1_smoothed)
        # Cut the signal into individual heart beats centered around R peaks.
        slices = self.cut_data_into_signals(lead1_smoothed, rPeaksInd)
        slicesZoomed = self.zoom_to_length(slices, 100)
        slicesScaled = self.scale_to_int(slicesZoomed, 100)
        return slicesScaled

