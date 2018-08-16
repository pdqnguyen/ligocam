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

import os
import subprocess
from ConfigParser import ConfigParser

SENDMAIL = '/usr/sbin/sendmail'

#================================================

def find_bad_channels(file, search_for=1):
    """
    Search for channels which have been disconnected
    or have had DAQ failures in the last hour.
    """
    bad_channels = []
    with open(file, 'r') as f:
        lines = [x.rstrip() for x in f.readlines()]
    for line in lines:
        split = line.split()
        if int(split[1]) == int(search_for):
            bad_channels.append(split[0])
    return sorted(set(bad_channels))

def write_email(email_to, email_from, email_replyto,
                disconn_channels, daqfail_channels,
                ifo, subsystem, url, alert_epoch):
    """
    Write email alert for disconnected and DAQ failure channels.
    """
    if len(disconn_channels) > 0 and len(daqfail_channels) > 0:
        alertby = 'Disconnection and DAQ failure'
    elif len(disconn_channels) > 0:
        alertby = 'Disconnection'
    elif len(daqfail_channels) > 0:
        alertby = 'DAQ failure'
    else:
        return
    subject_line = '[LigoCAM] %s alert for %s %s' % (alertby, ifo, subsystem)
    message =  'To: %s\n' % email_to
    message += 'From: %s\n' % email_from
    message += 'Reply-to: %s\n' % email_replyto
    message += 'Subject: %s\n' % subject_line
    message += 'Alert epoch:\n%s\n\nURL:\n<%s>\n\n' % (alert_epoch, url)
    if 'Disconnection' in alertby:
        message += 'Disconnected channels:\n'
        message += '\n'.join(disconn_channels)
    message += '\n\n'
    if 'DAQ failure' in alertby:
        message += 'DAQ failure channels:\n'
        message += '\n'.join(daqfail_channels)
    return message

def send_email(message_file):
    subprocess.call(SENDMAIL + ' -t < ' + message_file, shell=True)