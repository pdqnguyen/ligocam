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
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

def timeseries_plot(channel, filename, data, duration, current_utc):
    """
    Plot current time series for three different time ranges.
    """
    
    sample_rate = len(data) // duration
    time = np.linspace(0, duration, len(data))
    fig = plt.figure(figsize=(10,8))
    plt.suptitle('Epoch: ' + current_utc + '\nChannel: ' + channel, fontsize=14)
    
    # 500 second time series plot
    plt.subplot(311)
    t_ranges = []
    t_step = 1 + len(data) // 1e5
    plt.plot(time[::t_step], data[::t_step], 'green')
    plt.xlim([0, duration])
    plt.grid(True)
    plt.xticks(range(0, duration, 100))
    
    # 1 second time series plot (start)
    plt.subplot(312)
    rng = range(0, sample_rate+1)
    plt.plot(time[rng], data[rng], 'green')
    plt.grid(True)
    plt.xlim([0, 1])
    plt.xticks([0, 0.5, 1])
    plt.ylabel('Amplitude [counts]', fontsize=14)
    
    # 1 second time series plot (end)
    plt.subplot(313)
    rng = range(len(data) - 1*sample_rate - 1, len(data))
    plt.plot(time[rng], data[rng], 'green')
    plt.xlim([duration-1, duration])
    plt.xticks([duration - 1, duration - 0.5, duration])
    plt.xlabel('Time [s]', fontsize=14)
    plt.grid(True)
    
    # Save and close
    fig.savefig(filename)
    fig.clf()
    return

def asd_plot(channel, filename, freq_segs, freq_binned_segs, asd_segs,
             asd_binned_segs, asd_binned_ref_segs, current_utc):
    """
    Plot ASDs for three different frequency ranges, showing current
    and reference ASDs.
    
    Parameters
    ----------
    channel : str
        Channel name.
    filename : str
        Plot filename.
    freq_segs : list
        Frequency segments.
    freq_binned_segs : list
        Binned frequency segments.
    asd_segs : list
        ASD segments.
    asd_binned_segs : list
        Binned ASD segments.
    asd_ref_binned_segs : list
        Binned reference ASD segments.
    current_utc : str
        UTC start time of current data.
    """
    
    num_segs = len(freq_segs)
    num_binned_segs = len(freq_binned_segs)
    
    fig = plt.figure(figsize=(10,8))
    plt.suptitle('Epoch: ' + current_utc + '\nChannel: ' + channel, fontsize=14)
    
    # 0.3 TO 3 HZ ASD
    plt.subplot(311)
    plt.loglog(
        freq_segs[0], asd_segs[0], 'red',
        freq_segs[0], asd_segs[0], 'blue'
    )
    for i in range(4):
        plt.loglog(freq_segs[i], asd_segs[i], 'LightBlue')
    plt.loglog(
        np.concatenate(freq_binned_segs[:4]),
        np.concatenate(asd_binned_ref_segs[:4]),
        'red',
        np.concatenate(freq_binned_segs[:4]), 
        np.concatenate(asd_binned_segs[:4]),
        'blue'
    )
    plt.xlim([0.03, 3])
    plt.xticks([0.03, 0.1, 0.3, 1, 3], ['0.03', '0.1', '0.3', '1', '3'])
    plt.grid(True)
    legend_lines = [matplotlib.lines.Line2D([0], [0], color='red'),
                    matplotlib.lines.Line2D([0], [0], color='blue')]
    leg = plt.legend(legend_lines, ['Reference', 'Current'], 
                     loc='lower left', shadow=False, fancybox=False)
    leg.get_frame().set_alpha(0.5)
    
    # 3 TO 300 HZ ASD
    plt.subplot(312)
    if num_binned_segs > 4:
        upper_idx = min([8, num_binned_segs])
        for i in range(4, upper_idx):
            plt.loglog(freq_segs[i], asd_segs[i], 'LightBlue')
        plt.loglog(
            np.concatenate(freq_binned_segs[4:upper_idx]),
            np.concatenate(asd_binned_ref_segs[4:upper_idx]),
            'red',
            np.concatenate(freq_binned_segs[4:upper_idx]),
            np.concatenate(asd_binned_segs[4:upper_idx]),
            'blue'
        )
    else:
        plt.loglog(1, 1, 'w', 1, 1, 'w')
    plt.xlim([3, 300])
    plt.xticks([3, 10, 30, 100, 300], ['3', '10', '30', '100', '300'])
    plt.ylabel('Amplitude [counts/sqrt(Hz)]', fontsize=14)
    plt.grid(True)
    
    # 300 TO 10K HZ ASD
    plt.subplot(313)
    if num_binned_segs > 8:
        for i in range(8, num_binned_segs):
            plt.loglog(freq_segs[i][::10], asd_segs[i][::10], 'LightBlue')
        plt.plot(
            np.concatenate(freq_binned_segs[8:num_binned_segs]),
            np.concatenate(asd_binned_ref_segs[8:num_binned_segs]),
            'red',
            np.concatenate(freq_binned_segs[8:num_binned_segs]),
            np.concatenate(asd_binned_segs[8:num_binned_segs]),
            'blue'
        )
    else:
        plt.loglog(1, 1, 'w', 1, 1, 'w')
    plt.xlim([300, 10000])
    plt.xticks([300, 1000, 3000, 10000], ['300', '1000', '3000', '10000'])
    plt.xlabel('Frequency [Hz]', fontsize=14)
    plt.grid(True)
    
    # Save and close
    fig.savefig(filename)
    fig.clf()
    return