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

""" This file is part of LIGO Channel Activity Monitor (LigoCAM)."""

from __future__ import division
import numpy as np
import matplotlib.mlab as mlab
import sys
import os
import re
import shutil
import fileinput
from gwpy.time import from_gps
from glue import lal
from pylal import frutils
from . import plot as lcplot
from . import ALPHA

__author__ = 'Dipongkar Talukder <dipongkar.talukder@ligo.org>'

#================================================================

def find_frame_files(cache_dir):
    """
    Find frame cache files for current time and all reference times.
    """
    cache_files = os.listdir(cache_dir)
    frame_cache_refs = []
    for fname in cache_files:
        fullname = os.path.join(cache_dir, fname)
        current_match = re.findall('current', fname)
        ref_match = re.findall('reference-(\d+).txt', fname)
        if len(current_match) > 0:
            with open(fullname, 'r') as cache:
                cache_entries = [lal.CacheEntry(x.replace('\n', '')) for x in cache.readlines()]
            frame_cache_current = frutils.FrameCache(cache_entries, scratchdir=None, verbose=False)
        elif len(ref_match) > 0:
            with open(fullname, 'r') as cache:
                cache_entries = [lal.CacheEntry(x.replace('\n', '')) for x in dache.readlines()]
            frame_cache_ref = frutils.FrameCache(cache_entries, scratchdir=None, verbose=False)
            ref_time = ref_match[0]
            frame_cache_refs.append((ref_time, frame_cache_ref))
    return frame_cache_current, frame_cache_refs

def get_data(frame_cache, channel_name, time, duration, overlap=0):
    """
    Fetch time series, and PSD for a channel from frame cache.
    """
    timeseries = frame_cache.fetch(channel_name, current_time, current_time + duration)
    sample_rate = len(timeseries) / duration
    psd, freq = mlab.psd(timeseries, NFFT=len(timeseries), Fs=int(sample_rate), \
                         noverlap=int(overlap*sample_rate), detrend=mlab.detrend_none, \
                         window=mlab.window_hanning, pad_to=None, sides='default', \
                         scale_by_freq=1)
    psd = psd.reshape(freq.shape)
    return timeseries, psd, freq

def get_disconnected_yes_hour(history_file, channel):
    """
    Add an hour to a channel's disconnection counter
    """
    
    with open(history_file, 'r') as file:
        lines = file.readlines()
    hournew = 0
    for line in lines:
        word = line.split()
        chan = word[0]
        hour = word[1]
        if chan == channel:
            hournew = hournew + float(hour) + 1
            break
        else:
            notinterested = 'ignore'
    if hournew == 0:
        hournew = 1
    else:
        hournew = hournew
    return hournew

def get_daqfailure_yes_hour(history_file, channel):
    """
    Add an hour to a channel's DAQ failure counter
    """
    
    with open(history_file, 'r') as file:
        lines = file.readlines()
    hournew = 0
    for line in lines:
        word = line.split()
        chan = word[0]
        hour = word[1]
        if chan == channel:
            hournew = hournew + float(hour) + 1
            break
        else:
            notinterested = 'ignore'
    if hournew == 0:
        hournew = 1
    else:
        hournew = hournew
    return hournew

def get_binned(x, bin_size):
    """
    Perform a linear binning on a power spectrum.
    """
    
    n_bins = len(x) // bin_size
    x_chunks = x[:bin_size * n_bins].reshape((-1, bin_size))
    x_binned = x_chunks.mean(axis=1)
    if len(x) > bin_size * n_bins:
        x_edge = x[range(bin_size * n_bins, len(x))]
        x_binned_edge = np.array([x_edge.mean()])
        x_binned = np.concatenate((x_binned, x_binned_edge), axis=0)
    return x_binned

def combine_files(files, new_file):
    """
    Concatenate files and save to new file.
    """
    
    with open(new_file, 'w') as f_out:
        for file in files:
            with open(file) as f_in:
                lines = f_in.readlines()
                lines.sort()
                f_out.writelines(lines)

def fix_weak_magnetometers(results_file, weak_channels=[]):
    """
    Make sure each of these (manually provided) channels is only flagged as
    disconnected if all three axes are. Note that it can still be flagged
    as DAQ failure since that is independent of the magnetometer.
    """
    
    if len(weak_channels) == 0:
        return
    with open(results_file, 'r') as f:
        lines = f.readlines()
    for weak_chan in weak_channels:
        for i, x in enumerate(lines):
            if weak_chan in x:
                weak_chan_idx = i
                weak_chan_line = x
                other_disconnected_axes = 0
                for i, x in enumerate(lines):
                    if (weak_chan[:-2] in x) and \
                       (weak_chan not in x) and \
                       (x.split(',')[14] == 'Yes') and \
                       (x.split(',')[13] == 'No'):
                        other_disconnected_axes += 1
                if other_disconnected_axes < 2:
                    new_line = weak_chan_line.split(',')
                    new_line[14] = 'No'
                    new_line[15] = 'Ok'
                    lines[weak_chan_idx] = ','.join(new_line)
                break
    with open(results_file, 'w') as f:
        f.writelines(sorted(lines))

def filter_results(results_file, blrms_idx=12, status_idx=15):
    """
    Sort a results file by alert status and BLRMS excess.
    """
    
    with open(results_file, 'r') as f:
        lines = f.readlines()
    new_1, new_2, new_3, new_4 = [[], [], [], []]
    for line in lines:
        if line.split(',')[status_idx] == 'Alert':
            if line.split(',')[blrms_idx] == 'Yes':
                new_1.append(line)
            else:
                new_2.append(line)
        elif line.split(',')[blrms_idx] == 'Yes':
            new_3.append(line)
        else:
            new_4.append(line)
    with open(results_file, 'w') as f:
        f.writelines(sorted(new_1) + sorted(new_2) + sorted(new_3) + sorted(new_4))

def edit_calendar(calendar_file, results_url, current_gps):
    """
    Add a results url link to calendar file.
    """
    
    ymdh = from_gps(current_gps).strftime('%Y%m%d%H')
    year= ymdh[:4]
    month = ymdh[4:6]
    hour = ymdh[-2:]
    month_dir = '%s_%s' % (year, month)
    calendar_temp = '%s_%s.html' % (calendar_file.rstrip('.html'), current_gps)
    
    # String to be replaced
    stringold = '<!-- %s --> <li class="sgrayl l1"><p>%s:00</p></li>' % (ymdh, hour)
    stringnew = '<li class="greenish l1"><p><a href="%s">%s:00</a></p></li>' % (results_url, hour)
    shutil.copy2(calendar_file, calendar_temp)
    for j, line in enumerate(fileinput.input(calendar_temp, inplace=1)):
        sys.stdout.write(line.replace(stringold, stringnew))
    shutil.copy2(calendar_temp, calendar_file)
    os.remove(calendar_temp)
