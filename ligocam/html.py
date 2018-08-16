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

from optparse import OptionParser
import os
import shutil
from gwpy.time import from_gps

from . import (htmllib, BLRMS_THRESHOLDS)

__author__ = 'Dipongkar Talukder <dipongkar.talukder@ligo.org>'


# CHANNEL MAP ON PEM.LIGO.ORG
PEM_MAP_URL = "http://pem.ligo.org/channelinfo/index.php"

#========================================================

def create_html(filename, results_file, ifo, subsystem, current_utc,
                asd_path, ts_path, pem_map_url=PEM_MAP_URL,
                blrms_thresholds=BLRMS_THRESHOLDS):
    """
    Create HTML results page for a full LigoCAM run.
    """
    
    # Begin HTML table
    table = htmllib.Table(
        header_row=[
            htmllib.TableCell('Channel name', width='29%', header=True),
            htmllib.TableCell('Channel<BR>info', width='4%', header=True),
            htmllib.TableCell('Image', width='5%', header=True),
            htmllib.TableCell('Status', width='4%', header=True),
            htmllib.TableCell('Disconnected?', width='6%', header=True),
            htmllib.TableCell('DAQ<BR>failure?', width='4%', header=True),
            htmllib.TableCell('BLRMS<BR>change', width='4%', header=True),
            htmllib.TableCell('0.03-0.1', width='4%', header=True),
            htmllib.TableCell('0.1-0.3', width='4%', header=True),
            htmllib.TableCell('0.3-1', width='4%', header=True),
            htmllib.TableCell ('1-3', width='4%', header=True),
            htmllib.TableCell('3-10', width='4%', header=True),
            htmllib.TableCell('10-30', width='4%', header=True),
            htmllib.TableCell('30-100', width='4%', header=True),
            htmllib.TableCell('100-<BR>300', width='4%', header=True),
            htmllib.TableCell('300-<BR>1000', width='4%', header=True),
            htmllib.TableCell('1000-<BR>3000', width='4%', header=True),
            htmllib.TableCell('3000-<BR>10000', width='4%', header=True)
        ]
    )
    
    # Read results and generate HTML table rows
    with open(results_file, 'r') as f:
        lines = f.readlines()
    for line in lines:
        results = line.rstrip().split(',')
        chan = results[0]
        chan_url = chan.replace(':', '%3A').rstrip('_DQ')
        chan_file = chan.replace(':', '_') + '.png'
        info_url = "%s?channelname=%s" % (pem_map_url, chan_url)
        asd_url = os.path.join(asd_path, chan_file)
        ts_url = os.path.join(ts_path, chan_file)
        row = create_html_row(results, asd_url, ts_url,
                              blrms_thresholds=blrms_thresholds, info_url=info_url)
        table.rows.append(row)
    
    # Write HTML page to file
    html = table_to_html(table, ifo, subsystem, current_utc)
    with open(filename, 'w') as f:
        f.write(html)
    return

def create_single_htmls(save_dir, results_file, ifo, subsystem,
                        current_utc, asd_path, ts_path):
    """
    Creat HTML result page for a single channel's LigoCAM status.
    """
    
    with open(results_file, 'r') as f:
        results_lines = f.readlines()
    for line in results_lines:
        results = line.rstrip().split(',')
        chan = results[0]
        chan_url = chan.replace(':', '%3A').rstrip('_DQ')
        chan_file = chan.replace(':', '_')
        asd_url = os.path.join(asd_path, chan_file + '.png')
        ts_url = os.path.join(ts_path, chan_file + '.png')
        row = create_html_row(results, asd_url, ts_url)
        table = htmllib.Table(
            header_row=[
                htmllib.TableCell('Channel name', width='31%', header=True),
                htmllib.TableCell('STATUS', width='7%', header=True),
                htmllib.TableCell('Disconnected?', width='6%', header=True),
                htmllib.TableCell('DAQ<BR>failure?', width='4%', header=True),
                htmllib.TableCell('BLRMS<BR>change', width='4%', header=True),
                htmllib.TableCell('0.03-0.1', width='4%', header=True),
                htmllib.TableCell('0.1-0.3', width='4%', header=True),
                htmllib.TableCell('0.3-1', width='4%', header=True),
                htmllib.TableCell('1-3',width='4%', header=True),
                htmllib.TableCell('3-10', width='4%', header=True),
                htmllib.TableCell('10-30', width='4%', header=True),
                htmllib.TableCell('30-100', width='4%', header=True),
                htmllib.TableCell('100-<BR>300', width='4%', header=True),
                htmllib.TableCell('300-<BR>1000', width='4%', header=True),
                htmllib.TableCell('1000-<BR>3000', width='4%', header=True),
                htmllib.TableCell('3000-<BR>10000', width='4%', header=True),
                htmllib.TableCell('Image', width='4%', header=True)
            ]
        )
        table.rows.append(row)
        html = table_to_html(table, ifo, subsystem, current_utc)
        filename = os.path.join(save_dir, chan_file + '_status.html')
        with open(filename, 'w') as f:
            f.write(html)
    return

def create_html_row(results, asd_url, ts_url, info_url=None,
                    blrms_thresholds=BLRMS_THRESHOLDS):
    """
    Create an HTML table row from a list of results for a single channel.
    """
    
    chan = results[0]
    blrms = [float(x) for x in results[1:12]]
    excess = results[12]
    comb = results[13]
    disconnect = results[14]
    status = results[15]
    disconhour = results[16]
    daqfailhour = results[17]
    
    thd1g = blrms_thresholds['GREATER_1']
    thd1l = blrms_thresholds['LESS_1']
    thd2g = blrms_thresholds['GREATER_2']
    thd2l = blrms_thresholds['LESS_2']
    
    cells = {}
    
    # General channel info/links
    cells['chan'] = htmllib.TableCell(chan, bgcolor='white', width='29%')
    if info_url is not None:
        info = '<a href="%s" target="_blank">link</a>' % (info_url)
        cells['info'] = htmllib.TableCell(info, bgcolor='white', width='4%')
    image = '<a href="%s" target="_blank">ASD</a>, ' % asd_url + \
            '<a href="%s" target="_blank">TS</a>' % ts_url
    cells['image'] = htmllib.TableCell(image, bgcolor='white', width='5%')

    # Cells for channel status
    if excess == 'Yes':
        cells['excess'] = htmllib.TableCell(excess, bgcolor='FFD280', width='4%')
    else:
        cells['excess'] = htmllib.TableCell(excess, bgcolor='white', width='4%')
    if comb == 'Yes':
        cells['comb'] = htmllib.TableCell(comb + '     (' + daqfailhour + ' h)', \
                                            bgcolor='FF9771', width='4%')
    else:
        cells['comb'] = htmllib.TableCell(comb, bgcolor='white', width='4%')
    if disconnect == 'Yes':
        cells['disconnect'] = htmllib.TableCell(disconnect + '     (' + disconhour + \
                                        ' h)', bgcolor='FF6633', width='6%')
    else:
        cells['disconnect'] = htmllib.TableCell(disconnect, bgcolor='white', width='6%')
    if status == 'Alert':
        cells['status'] = htmllib.TableCell(status, bgcolor='FFFF00', width='4%')
    else:
        cells['status'] = htmllib.TableCell(status, bgcolor='00FF00', width='4%')
    
    # Create BLRMS cells
    blrms_cells = []
    for i, x in enumerate(blrms):
        if i < 3:
            if x > thd1g or (x < thd1l and x != 0):
                if '_ACC_' in chan or '_MIC_' in chan:
                    blrms_cells.append(htmllib.TableCell(x, bgcolor='E8E8E8', width='4%'))
                else:
                    blrms_cells.append(htmllib.TableCell(x, bgcolor='FFD280', width='4%'))
            elif x == 0:
                blrms_cells.append(htmllib.TableCell(' ', bgcolor='white', width='4%'))
            else:
                blrms_cells.append(htmllib.TableCell(x, bgcolor='white', width='4%'))
        else:
            if x > thd2g or (x < thd2l and x != 0):
                if (i < 5) and ('_ACC_' in chan or '_MIC_' in chan) or\
                   (i > 5) and ('_SEIS_' in chan):
                    blrms_cells.append(htmllib.TableCell(x, bgcolor='E8E8E8', width='4%'))
                else:
                    blrms_cells.append(htmllib.TableCell(x, bgcolor='FFD280', width='4%'))
            elif x == 0:
                blrms_cells.append(htmllib.TableCell(' ', bgcolor='white', width='4%'))
            else:
                blrms_cells.append(htmllib.TableCell(x, bgcolor='white', width='4%'))
    
    # Combine cells to form a table row
    if info_url is not None:
        row = [cells['chan'], cells['info'], cells['image'], cells['status'],
               cells['disconnect'], cells['comb'], cells['excess']] + blrms_cells
    else:
        row = [cells['chan'], cells['status'], cells['disconnect'], cells['comb'],
               cells['excess']] + blrms_cells + [cells['image']]
    return row

def table_to_html(table, ifo, subsystem, current_utc):
    """
    Create an HTML table from an html.Table object.
    """
    
    title = 'LigoCAM @ %s | %s' % (ifo, subsystem)
    html =  '<!DOCTYPE html>\n'
    html += '<html lang="en" class="no-js">\n\n'
    html += '    <head>\n'
    html += '        <meta charset="UTF-8" />\n'
    html += '		 <meta http-equiv="X-UA-Compatible" content="IE=edge, chrome=1">\n'
    html += '		 <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
    html += '		 <title>%s</title>\n' % title
    html += '		 <link rel="stylesheet" type="text/css" href="css/component.css" />\n'
    html += '    </head>\n\n'
    html += '	 <body>\n'
    html += '		 <div class="header" style="color:green; background-color:#C8C8C8;">\n'
    html += '            <h1>%s</h1>\n' % title
    html += '	     </div>\n'
    html += '        <p align="center" style="background-color:white;color:black;'
    html += ' font-size:20px;margin-top:4px;margin-bottom:4px;">\n'
    html += 'Epoch: %s </p>\n' % current_utc
    html += '        <table class="">\n'
    html += '        <thead>\n'
    html += str(table)
    html += '\n'
    html += '        </table>\n\n'
    html += '        <script src="js/jquery.min.js"></script>\n'
    html += '        <script src="js/jquery.ba-throttle-debounce.min.js"></script>\n'
    html += '        <script src="js/jquery.stickyheader.js"></script>\n\n'
    html += '    </body>\n'
    html += '</html>'
    return html

def create_empty_html(filename, results_file, channel):
    """
    Create an empty HTML page for channels with no results.
    """
    
    channel = channel.rstrip()
    if channel not in open(results_file).read():
        with open(filename, 'w') as status_err:
            status_err.write('No data or not enough data to determine the status.')
    return