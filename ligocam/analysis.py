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
from . import (SEGMENT_FREQS, NUM_SEGMENTS,
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

def check_status(channel, psd, psd_ref, disconn_hist_file, \
                 daqfail_hist_file, duration, \
                 daqfail_thresholds, disconn_thresholds):
    """
    Check for disconnection or DAQ failure
    """
    
    disconn, daqfail = channel_status(
        channel, psd, duration,
        daqfail_thresholds, disconn_thresholds
    )
    if disconn:
        disconnhour = lcutils.get_disconnected_yes_hour(
            disconn_hist_file, channel
        )
    else:
        disconnhour = 0
    if daqfail:
        daqfailhour = lcutils.get_daqfailure_yes_hour(
            daqfail_hist_file, channel
        )
    else:
        daqfailhour = 0
    status_dict = {
        'daqfail': daqfail,
        'disconn': disconn,
        'disconn_hour': disconnhour,
        'daqfail_hour': daqfailhour
    }
    return status_dict

def check_blrms(channel, psd_binned_segs, psd_ref_binned_segs, 
                blrms_thresholds):
    """
    Compute band-limited RMS changes and determine
    if they exceed thresholds.
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
                  x > blrms_thresholds['greater_1'] or \
                  x < blrms_thresholds['less_1'] and x > 0]
        cond_2 = [x for x in blrms_changes[3:6] if \
                  x > blrms_thresholds['greater_2'] or \
                  x < blrms_thresholds['less_2'] and x > 0]
        excess = (len(cond_1) > 0 or len(cond_2) > 0)
    elif '_ACC_' in channel or '_MIC_' in channel:
        cond = [x for x in blrms_changes[6:] if \
                x > blrms_thresholds['greater_2'] or \
                x < blrms_thresholds['less_2'] and x > 0]
        excess = (len(cond) > 0)
    else:
        cond_1 = [x for x in blrms_changes[:3] if \
                  x > blrms_thresholds['greater_1'] or \
                  x < blrms_thresholds['less_1'] and x > 0]
        cond_2 = [x for x in blrms_changes[3:] if \
                  x > blrms_thresholds['greater_2'] or \
                  x < blrms_thresholds['less_2'] and x > 0]
        excess = (len(cond_1) > 0 and len(cond_2) > 0)
    blrms_dict = {'blrms_changes': blrms_changes, \
                  'excess': excess}
    return blrms_dict



#===================================================



#======================
# CHANNEL STATUS
#======================
# This is where things get ugly
# Different calculation methods are performed for
# the various channel types and sampling rates


#====================================================



def channel_status(channel, psd, duration, daqfail_thresholds, \
                   disconn_thresholds):
    """
    Check channel PSD to determine status. Different
    calculation methods are performed for the various
    channel types and sampling rates.
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
    
    weak_mag_chans = disconn_thresholds['weak_mag_chans']
    if any([weak_chan in channel for weak_chan in weak_mag_chans]):
        p10_100 = psd[rng10_100]
        p59_61 = np.sqrt(psd[rng59_61])
        daqfail_th = daqfail_thresholds['default']
        mag_th = disconn_thresholds['magexc']
        daqfail = (np.amin(np.sqrt(p10_100)) < daqfail_th)
        disconn = (np.amax(p59_61) < mag_th and not daqfail)
    
    
    #### CHANNELS 128 Hz AND BELOW ####
    
    elif freq_max < 128:
        if freq_max == 8:
            rng = range(int(0.3*duration + 1), 5*duration)
            daqfail_th = daqfail_thresholds['0.3-20hz']
        elif freq_max == 16:
            rng = range(int(0.3*duration + 1), 10*duration)
            daqfail_th = daqfail_thresholds['0.3-20hz']
        elif freq_max == 32:
            rng = range(1 * duration, 20*duration)
            daqfail_th = daqfail_thresholds['0.3-20hz']
        elif freq_max == 64:
            rng = range(1 * duration, 40*duration)
            daqfail_th = daqfail_thresholds['1-40hz']
        disconn_th = disconn_thresholds[str(freq_max) + 'hz']
        psd_seg = psd[rng]
        daqfail = (np.amin(np.sqrt(psd_seg)) < daqfail_th)
        disconn = (np.sqrt(sum(psd_seg) * 1/duration) < disconn_th and \
                   not daqfail)
    
    
    #### LOW-FREQ SENSORS ####
    
    elif '_SEIS_' in channel:
        p_seis = psd[rng_seis]
        disconn_th = disconn_thresholds['seis']
        daqfail_th = daqfail_thresholds['seis']
        daqfail = (np.amin(np.sqrt(p_seis)) < daqfail_thresholds['seis'])
        disconn = (np.sqrt(sum(p_seis) * 1/duration) < disconn_th and \
                   not daqfail)
    elif '_LOWFMIC_' in channel or '_TEMPERATURE_' in channel:
        p_lowfmictemp = psd[rng_lowfmictemp]
        disconn_th = disconn_thresholds['lowfmic_temperature']
        daqfail_th = daqfail_thresholds['lowfmic_temperature']
        disconn = (np.sqrt(sum(p_lowfmictemp) * 1/duration) < disconn_th and \
                   np.amin(np.sqrt(p_lowfmictemp)) > daqfail_th * 0.1)
        asd = np.sqrt(p_lowfmictemp)
        daqfail_num = sum(j < daqfail_th for j in asd)
        daqfail = (daqfail_num > 5)
    elif '_TILT_' in channel:
        p_tilt = psd[rng_tilt]
        disconn_th = disconn_thresholds['tilt']
        daqfail_th = daqfail_thresholds['tilt']
        disconn = (np.sqrt(sum(p_tilt) * 1/duration) < disconn_th and \
                   np.amin(np.sqrt(p_tilt)) > daqfail_th * 0.1)
        asd = np.sqrt(p_tilt)
        daqfail_num = sum(j < daqfail_th for j in asd)
        daqfail = (daqfail_num > 5)
    
    
    #### CHANNELS 256 Hz ####
    
    elif freq_max == 128:
        # Special case for 256hz incorrect LHO MAINSMON
        if '_MAINSMON_' in channel:
            p10_80 = psd[rng10_80]
            p59_61 = psd[rng59_61]
            disconn_th = disconn_thresholds['128hz_mainsmon']
            daqfail_th = daqfail_thresholds['default']
            mag_th = disconn_thresholds['mainsmon']
            daqfail = (np.amin(np.sqrt(p10_80)) < daqfail_th)
            disconn = (np.sqrt(sum(p10_80) * 1/duration) < disconn_th and \
                       np.amax(np.sqrt(p59_61)) < mag_th and not daqfail)
        else:
            p1_80 = psd[rng1_80]
            disconn_th = disconn_thresholds[str(freq_max) + 'hz']
            daqfail_th = daqfail_thresholds['default']
            daqfail = (np.amin(np.sqrt(p1_80)) < daqfail_th)
            disconn = (np.sqrt(sum(p1_80) * 1/duration) < disconn_th and \
                       not daqfail)
    
    
    #### CHANNELS 512 Hz ####
    
    elif freq_max == 256:
        p10_100 = psd[rng10_100]
        disconn_th = disconn_thresholds['default']
        daqfail_th = daqfail_thresholds['default']
        daqfail = (np.amin(np.sqrt(p10_100)) < daqfail_th)
        disconn = (np.sqrt(sum(p10_100) * 1/duration) < disconn_th and \
                   not daqfail)
    
    
    #### CHANNELS 1024 Hz AND OVER ####
    
    else:
        if '_ACC_' in channel or '_MIC_' in channel:
            p10_300 = psd[rng10_300]
            disconn_th = disconn_thresholds['acc_mic']
            daqfail_th = daqfail_thresholds['default']
            daqfail = (np.amin(np.sqrt(p10_300)) < daqfail_th)
            disconn = (np.sqrt(sum(p10_300) * 1/duration) < disconn_th and \
                       not daqfail)
        elif '_MAG_' in channel:
            p10_100 = psd[rng10_100]
            p59_61 = psd[rng59_61]
            daqfail_th = daqfail_thresholds['default']
            mag_th = disconn_thresholds['mag']
            daqfail = (np.amin(np.sqrt(p10_100)) < daqfail_th)
            disconn = (np.amax(np.sqrt(p59_61)) < mag_th and not daqfail)
        # Mar 31, 2015 LHO made this choice.
        elif '_MAINSMON_' in channel:
            p10_100 = psd[rng10_100]
            p59_61 = psd[rng59_61]
            disconn_th = disconn_thresholds['mag_mainsmon']
            daqfail_th = daqfail_thresholds['default']
            mag_th = disconn_thresholds['mainsmon']
            daqfail = (np.amin(np.sqrt(p10_100)) < daqfail_th)
            disconn = (np.sqrt(sum(p10_100) * 1/duration) < disconn_th and \
                       np.amax(np.sqrt(p59_61)) < mag_th and not daqfail)
        else:
            p10_100 = psd[rng10_100]
            disconn_th = disconn_thresholds['default']
            daqfail_th = daqfail_thresholds['default']
            daqfail = (np.amin(np.sqrt(p10_100)) < daqfail_th)
            disconn = (np.sqrt(sum(p10_100) * 1/duration) < disconn_th and \
                       not daqfail)
    
    return disconn, daqfail