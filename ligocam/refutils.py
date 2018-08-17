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
import os
from glue import lal
from pylal import frutils

from . import utils as lcutils
from . import (SEGMENT_FREQS, ALPHA)

__author__ = 'Dipongkar Talukder <dipongkar.talukder@ligo.org>'

#=======================================================================

def get_psd_ref_binned(psd, duration, segment_freqs=SEGMENT_FREQS):
    """
    Break reference PSD into segments and bin them separately.
    """
    
    segment_ranges = []
    for i,j in segment_freqs:
        lower_idx = int(np.ceil(i * duration))
        upper_idx = int(np.ceil(j * duration))
        rng = range(lower_idx, upper_idx)
        segment_ranges.append(rng)
    upper_bounds = [list(rng)[-1] for rng in segment_ranges]
    upper_bounds = [x for x in upper_bounds if x < len(psd)]
    end_idx = min([len(psd), 10000*duration])
    rng_last = range(upper_bounds[-1], end_idx)
    segment_ranges = segment_ranges[:len(upper_bounds)] + [rng_last]
    segments = []
    for i, rng in enumerate(segment_ranges):
        seg = psd[rng]
        if i > 1:
            seg = lcutils.get_binned(seg, 10 ** (i // 2))
        segments.append(seg)
    new_psd = np.concatenate(segments, axis=0)
    return new_psd

def save_new_ref(psd, psd_new, filename, alpha=ALPHA):
    """
    Combine the current psd to the reference and save it for future use.
    """
    
    psd_new = psd + alpha * (psd_new - psd)
    np.savetxt(filename, psd_new)