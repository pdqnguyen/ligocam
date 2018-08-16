# Copyright (C) 2013 Dipongkar Talukder
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from __future__ import division
import numpy as np
import os

from . import plot as lcplot
from . import utils as lcutils
from . import (BLRMS_THRESHOLDS, SEGMENT_FREQS, NUM_SEGMENTS,
               SEGMENT_EDGES, SEGMENT_END_IDX)

#=========================================================

def prep_data(freq, psd, psd_ref, duration,
              segment_freqs=SEGMENT_FREQS,
              num_segments=NUM_SEGMENTS,
              segment_edges=SEGMENT_EDGES,
              segment_end_idx=SEGMENT_END_IDX):
    """
    Prepare data for analysis and plotting. Segments of different
    frequency resolutions are collected into lists.
    """
    
    freq_max = len(psd) // duration
    
    segment_ranges = []
    for i,j in segment_freqs:
        lower_idx = int(np.ceil(i * duration))
        upper_idx = int(np.ceil(j * duration))
        rng = range(lower_idx, upper_idx)
        segment_ranges.append(rng)
    
    # Get last index range of last segment
    upper_bounds = [list(rng)[-1] for rng in segment_ranges]
    upper_bounds = [x for x in upper_bounds if x < len(psd)]
    end_idx = min([len(psd), 10000*duration])
    rng_last = range(upper_bounds[-1]+1, end_idx)
    
    # Number of segments to split data into
    if freq_max in num_segments.keys():
        num_segs = num_segments[freq_max]
    else:
        num_segs = 11
        
    # Unbinned frequency and PSD segments
    freq_segs = []
    psd_segs = []
    for i in range(num_segs):
        if i < num_segs - 1:
            rng = segment_ranges[i]
        else:
            rng = rng_last
        freq_segs.append(freq[rng])
        psd_segs.append(psd[rng])
    if freq_max not in num_segments.keys():
        rng_extras = [range(3000*duration, 4000*duration),
                      range(4000*duration, 5000*duration),
                      range(5000*duration, 6000*duration),
                      range(6000*duration, 7000*duration)]
        if freq_max == 8192:
            rng_extras.append(range(7000*duration, 8192*duration))
        else:
            rng_extras.append(range(7000*duration, 10000*duration))
        for rng in rng_extras:
            freq_segs.append(freq[rng])
            psd_segs.append(psd[rng])
    
    # Binned frequency and PSD segments
    freq_binned_segs = freq_segs[:2]
    psd_binned_segs = psd_segs[:2]
    for i in range(2, num_segs):
        bin_size = 10 ** (i // 2)
        freq_b = lcutils.get_binned(freq_segs[i], bin_size)
        psd_b = lcutils.get_binned(psd_segs[i], bin_size)
        freq_binned_segs.append(freq_b)
        psd_binned_segs.append(psd_b)
    
    # Binned reference PSD segments
    psd_ref_binned_segs = []
    if freq_max in segment_end_idx.keys():
        end_idx = segment_end_idx[freq_max]
    else:
        end_idx = segment_edges[-1]
    for i in range(len(segment_edges) - 1):
        edge1 = segment_edges[i]
        edge2 = segment_edges[i+1]
        if end_idx < edge2:
            edge2 = end_idx
        elif end_idx < edge1:
            break
        psd_ref_binned_segs.append(psd_ref[edge1:edge2])
    
    data_segs = {
        'freq': freq_segs,
        'psd': psd_segs,
        'freq_binned': freq_binned_segs,
        'psd_binned': psd_binned_segs,
        'psd_ref_binned': psd_ref_binned_segs
    }
    return data_segs

def check_status(channel, psd, psd_ref, disconn_hist_file, daqfail_hist_file, duration):
    """
    Check for disconnection or DAQ failure
    """
    
    disconnect, comb = channel_status(channel, psd, duration)
    if disconnect:
        disconnhour = lcutils.get_disconnected_yes_hour(disconn_hist_file, channel)
    else:
        disconnhour = 0
    if comb:
        daqfailhour = lcutils.get_daqfailure_yes_hour(daqfail_hist_file, channel)
    else:
        daqfailhour = 0
    status_dict = {
        'comb': comb,
        'disconnect': disconnect,
        'disconnhour': disconnhour,
        'daqfailhour': daqfailhour
    }
    return status_dict

def check_blrms(channel, psd_binned_segs, psd_ref_binned_segs,
                blrms_thresholds=BLRMS_THRESHOLDS):
    """
    Compute band-limited RMS changes and determine if they exceed thresholds.
    """
    
    blrms_dict = {}
    blrms_changes = []
    for i in range(11):
        if i < len(psd_binned_segs):
            numer = np.sqrt(sum(psd_binned_segs[i]))
            denom = np.sqrt(sum(psd_ref_binned_segs[i]))
            blrms_changes.append(numer / denom)
        else:
            blrms_changes.append(0)
    if '_SEIS_' in channel:
        cond_1 = [x for x in blrms_changes[:3] if \
                  x > blrms_thresholds['GREATER_1'] or \
                  x < blrms_thresholds['LESS_1'] and x > 0]
        cond_2 = [x for x in blrms_changes[3:6] if \
                  x > blrms_thresholds['GREATER_2'] or \
                  x < blrms_thresholds['LESS_2'] and x > 0]
        excess = (len(cond_1) > 0 or len(cond_2) > 0)
    elif '_ACC_' in channel or '_MIC_' in channel:
        cond = [x for x in blrms_changes[6:] if \
                x > blrms_thresholds['GREATER_2'] or \
                x < blrms_thresholds['LESS_2'] and x > 0]
        excess = (len(cond) > 0)
    else:
        cond_1 = [x for x in blrms_changes[:3] if \
                  x > blrms_thresholds['GREATER_1'] or \
                  x < blrms_thresholds['LESS_1'] and x > 0]
        cond_2 = [x for x in blrms_changes[3:] if \
                  x > blrms_thresholds['GREATER_2'] or \
                  x < blrms_thresholds['LESS_2'] and x > 0]
        excess = (len(cond_1) > 0 and len(cond_2) > 0)
    blrms_dict = {'blrms_changes': blrms_changes, 'excess': excess}
    return blrms_dict



#===================================================



#======================
# CHANNEL STATUS
#======================
# This is where things get ugly
# Different calculation methods are performed for
# the various channel types and sampling rates


# DEFAULT THRESHOLDS
COMB_THRESHOLDS = {
    'DEFAULT': 1e-8,
    'SEIS': 1e-7,
    'LOWFMIC_TEMPERATURE': 0.5e-3,
    'TILT': 0.5e-3,
    '0.3-20Hz': 1e-6,
    '1-40Hz': 1e-7
}
DISCONN_THRESHOLDS = {
    8: 0.44,
    16: 0.62,
    32: 0.88,
    64: 1.25,
    128: 1.78,
    'DEFAULT': 2.0,
    'SEIS': 0.1,
    'ACC_MIC': 1.2,
    'LOWFMIC_TEMPERATURE': 0.1,
    'TILT': 0.2,
    'MAG_MAINSMON': 0.2,
    '128Hz_MAINSMON': 0.18
}
MAG_60Hz_THRESHOLDS = {
    'MAG': 1000,
    'MAGEXC': 100,
    'MAINSMON': 1000
}
MAG_WEAK_CHANS = [
    '-CS_MAG_LVEA_INPUTOPTICS_Y_',
    '-EX_MAG_VEA_FLOOR_X_',
    '-EX_MAG_VEA_FLOOR_Y_'
]


#====================================================



def channel_status(channel, psd, duration,
                   comb_thresholds=COMB_THRESHOLDS,
                   disconn_thresholds=DISCONN_THRESHOLDS,
                   mag_60hz_thresholds=MAG_60Hz_THRESHOLDS,
                   mag_weak_chans=MAG_WEAK_CHANS):
    """
    Check channel PSD to determine status. 
    """
    
    freq_max = len(psd) // duration
    
    # Special ranges for avoding with 60 Hz peaks
    # 1-80Hz
    rng1_59 = range(duration, 59*duration + 1)
    rng61_80 = range(61* duration,80*duration + 1)
    rng1_80 = rng1_59 + rng61_80
    # 10-80Hz
    rng10_59 = range(10*duration, 59*duration + 1)
    rng61_80 = range(61*duration, 80*duration + 1)
    rng10_80 = rng10_59 + rng61_80
    # 10-100Hz
    rng10_59 = range(10*duration, 59*duration + 1)
    rng61_100 = range(61*duration,100*duration + 1)
    rng10_100 = rng10_59 + rng61_100
    rng59_61 = range(60*duration - duration//2,
                     60*duration + duration//2)
    
    # Special ranges for other sensors
    rng_seis = range(3*duration, 30*duration + 1)
    rng_lowfmictemp = range(int(np.ceil(0.03*duration)),
                            int(np.ceil(0.3*duration)))
    rng_tilt = range(int(np.ceil(0.03*duration)), 1*duration)
    # Accelerometer 10-300Hz range
    rng10_300 = range(10*duration, 59*duration + 1) +\
                range(61*duration, 119*duration + 1) +\
                range(121*duration, 179*duration + 1) +\
                range(181*duration, 239*duration + 1) +\
                range(241*duration, 299*duration + 1)
    
    
    #### SPECIAL CASES ####
    
    if any([weak_chan in channel for weak_chan in mag_weak_chans]):
        p10_100 = psd[rng10_100]
        p59_61 = np.sqrt(psd[rng59_61])
        comb_th = comb_thresholds['DEFAULT']
        mag_th = mag_60hz_thresholds['MAGEXC']
        disconnect = (np.amax(p59_61) < mag_th and \
                      np.amin(np.sqrt(p10_100)) > comb_th)
        comb = (np.amin(np.sqrt(p10_100)) < comb_th)
    
    
    #### CHANNELS 128 Hz AND BELOW ####
    
    elif freq_max < 128:
        if freq_max == 8:
            rng = range(int(0.3*duration + 1), 5*duration)
            comb_th = comb_thresholds['0.3-20Hz']
        elif freq_max == 16:
            rng = range(int(0.3*duration + 1), 10*duration)
            comb_th = comb_thresholds['0.3-20Hz']
        elif freq_max == 32:
            rng = range(duration, 20*duration)
            comb_th = comb_thresholds['0.3-20Hz']
        elif freq_max == 64:
            rng = range(duration, 40*duration)
            comb_th = comb_thresholds['1-40Hz']
        disconn_th = disconn_thresholds[freq_max]
        psd_seg = psd[rng]
        disconnect = (np.sqrt(sum(psd_seg) * 1/duration) < disconn_th and \
                      np.amin(np.sqrt(psd_seg)) > comb_th)
        comb = (np.amin(np.sqrt(psd_seg)) < comb_th)
    
    
    #### LOW-FREQ SENSORS ####
    
    elif '_SEIS_' in channel:
        p_seis = psd[rng_seis]
        disconn_th = disconn_thresholds['SEIS']
        comb_th = comb_thresholds['SEIS']
        disconnect = (np.sqrt(sum(p_seis) * 1/duration) < disconn_th and \
                      np.amin(np.sqrt(p_seis)) > comb_thresholds['SEIS'])
        comb = (np.amin(np.sqrt(p_seis)) < comb_thresholds['SEIS'])
    elif '_LOWFMIC_' in channel or '_TEMPERATURE_' in channel:
        p_lowfmictemp = psd[rng_lowfmictemp]
        disconn_th = disconn_thresholds['LOWFMIC_TEMPERATURE']
        comb_th = comb_thresholds['LOWFMIC_TEMPERATURE']
        disconnect = (np.sqrt(sum(p_lowfmictemp) * 1/duration) < disconn_th and \
                      np.amin(np.sqrt(p_lowfmictemp)) > comb_th * 0.1)
        asd = np.sqrt(p_lowfmictemp)
        comb_num = sum(j < comb_th for j in asd)
        comb = (comb_num > 5)
    elif '_TILT_' in channel:
        p_tilt = psd[rng_tilt]
        disconn_th = disconn_thresholds['TILT']
        comb_th = comb_thresholds['TILT']
        disconnect = (np.sqrt(sum(p_tilt) * 1/duration) < disconn_th and \
                      np.amin(np.sqrt(p_tilt)) > comb_th * 0.1)
        asd = np.sqrt(p_tilt)
        comb_num = sum(j < comb_th for j in asd)
        comb = (comb_num > 5)
    
    
    #### CHANNELS 256 Hz ####
    
    elif freq_max == 128:
        # Special case for 256hz incorrect LHO MAINSMON
        if '_MAINSMON_' in channel:
            p10_80 = psd[rng10_80]
            p59_61 = np.sqrt(psd[rng59_61])
            disconn_th = disconn_thresholds['128Hz_MAINSMON']
            comb_th = comb_thresholds['DEFAULT']
            mag_th = mag_60hz_thresholds['MAINSMON']
            disconnect = (np.sqrt(sum(p10_80) * 1/duration) < disconn_th and \
                           np.amin(np.sqrt(p10_80)) > comb_th and \
                           np.amax(p59_61) < mag_th)
            comb = (np.amin(np.sqrt(p10_80)) < comb_th)
        else:
            p1_80 = psd[rng1_80]
            disconn_th = disconn_thresholds[freq_max]
            comb_th = comb_thresholds['DEFAULT']
            disconnect = (np.sqrt(sum(p1_80) * 1/duration) < disconn_th and \
                          np.amin(np.sqrt(p1_80)) > comb_th)
            comb = (np.amin(np.sqrt(p1_80)) < comb_th)
    
    
    #### CHANNELS 512 Hz ####
    
    elif freq_max == 256:
        p10_100 = psd[rng10_100]
        disconn_th = disconn_thresholds['DEFAULT']
        comb_th = comb_thresholds['DEFAULT']
        disconnect = (np.sqrt(sum(p10_100) * 1/duration) < disconn_th and \
                      np.amin(np.sqrt(p10_100)) > comb_th)
        comb = (np.amin(np.sqrt(p10_100)) < comb_th)
    
    
    #### CHANNELS 1024 Hz AND OVER ####
    
    else:
        if '_ACC_' in channel or '_MIC_' in channel:
            p10_300 = psd[rng10_300]
            disconn_th = disconn_thresholds['ACC_MIC']
            comb_th = comb_thresholds['DEFAULT']
            disconnect = (np.sqrt(sum(p10_300) * 1/duration) < disconn_th and \
                          np.amin(np.sqrt(p10_300)) > comb_th)
            comb = (np.amin(np.sqrt(p10_300)) < comb_th)
        elif '_MAG_' in channel:
            p10_100 = psd[rng10_100]
            p59_61 = np.sqrt(psd[rng59_61])
            comb_th = comb_thresholds['DEFAULT']
            mag_th = mag_60hz_thresholds['MAG']
            disconnect = (np.amax(p59_61) < mag_th and \
                          np.amin(np.sqrt(p10_100)) > comb_th)
            comb = (np.amin(np.sqrt(p10_100)) < comb_th)
        # Mar 31, 2015 LHO made this choice.
        elif '_MAINSMON_' in channel:
            p10_100 = psd[rng10_100]
            p59_61 = np.sqrt(psd[rng59_61])
            disconn_th = disconn_thresholds['MAG_MAINSMON']
            comb_th = comb_thresholds['DEFAULT']
            mag_th = mag_60hz_thresholds['MAINSMON']
            disconnect = (np.sqrt(sum(p10_100) * 1/duration) < disconn_th and \
                          np.amax(p59_61) < mag_th and \
                          np.amin(np.sqrt(p10_100)) > comb_th)
            comb = (np.amin(np.sqrt(p10_100)) < comb_th)
        else:
            p10_100 = psd[rng10_100]
            disconn_th = disconn_thresholds['DEFAULT']
            comb_th = comb_thresholds['DEFAULT']
            disconnect = (np.sqrt(sum(p10_100) * 1/duration) < disconn_th and \
                          np.amin(np.sqrt(p10_100)) > comb_th)
            comb = (np.amin(np.sqrt(p10_100)) < comb_th)
    
    return disconnect, comb