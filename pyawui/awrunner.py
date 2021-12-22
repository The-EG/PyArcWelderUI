# Copyright 2021 Taylor Talkington
# 
# This file is part of PyArcWelderUI.
#
# PyArcWelderUI is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyArcWelderUI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyArcWelderUI.  If not, see <https://www.gnu.org/licenses/>.

import subprocess
import re
import threading

_VERSION_PAT = re.compile(r'(?P<path>[\w\d \\/\-]*?)  version: (?P<major>\d+).(?P<minor>\d+).(?P<revision>\d+)(?P<patch>.*)')

# Progress line patterns
_PROG_LINE_PAT = re.compile(r'^Progress:  .*$')
_PROG_PERC_COM = re.compile(r'^Progress:  .*?percent_complete: ?(?P<value>\d+\.\d+).*?$')
_PROG_CUR_LINE = re.compile(r'^Progress:  .*?current_file_line: ?(?P<value>\d+).*?$')
_PROG_SIZE_RED = re.compile(r'^Progress:  .*?size_reduction: ?(?P<value>\d+\.\d+)%.*?$')
_PROG_SECS_REM = re.compile(r'^Progress:  .*?seconds_remaining: ?(?P<value>\d+\.\d+).*?$')

_STATS_MM_CHANGE = re.compile(r'^\| +(?:(?P<min>\d+\.\d+)mm to|>=) +(?P<max>\d+\.\d+)mm +(?P<src>\d+) +(?P<tgt>\d+) +(?P<chg>-?\d+\.\d+)%\|$')

_TTL_DIST_SRC = re.compile(r'^\| ?Total distance source:\.+(?P<value>-?\d+\.\d+)mm\|$')
_TTL_DIST_TGT = re.compile(r'^\| ?Total distance target:\.+(?P<value>-?\d+\.\d+)mm\|$')
_TTL_CNT_SRC = re.compile(r'^\| +Total count source:\.+(?P<value>-?\d+)\|$')
_TTL_CNT_TGT = re.compile(r'^\| +Total count target:\.+(?P<value>-?\d+)\|$')
_TTL_PERC_CHNG = re.compile(r'^\| Total percent change:\.+(?P<value>-?\d+\.\d+)%\|$')

class ArcWelderRunner:
    """
    A class that runs ArcWelder console, optionally providing progress and completion info.
    
    If set, progress_cb and finished_cb will be called with a single argument containing a
    dict of appropriate info.

    aw_flags and aw_options can be used to pass flags and options to ArcWelder, respectively.
    These flags must be in long form, ie. '--flag-name,' without the leading '--' ('flag-name').
    """
    def __init__(self, arc_welder_path="ArcWelder"):
        self._awpath = arc_welder_path

        self._thread = None

        self.progress_cb = None
        self.finished_cb = None

        # ArcWelder Options
        self.aw_flags = []
        self.aw_options = {}

        # final stats
        self._total_perc_change = None
        self._total_dist_source = None
        self._total_dist_target = None
        self._total_count_source = None
        self._total_count_target = None
        self._welding_stats = {}

    def verify_version(self):
        """Verify the version of ArcWelder. Currently only 1.2 or greater is supported. Not used."""
        out = subprocess.check_output([self._awpath, '--version']).decode('utf8').splitlines()
        for line in out:
            m = _VERSION_PAT.match(line)
            if m is None:
                continue
            if m.group('major') and m.group('minor'):
                # at least version 1.2
                if int(m.group('major')) >= 1 and int(m.group('minor')) >= 2:
                    return True
        return False

    def _parse_output_line(self, line):
        m = _TTL_PERC_CHNG.match(line)
        if m:
            self._total_perc_change = float(m.group("value"))
            return

        m = _TTL_DIST_SRC.match(line)
        if m:
            self._total_dist_source = float(m.group("value"))
            return
        
        m = _TTL_DIST_TGT.match(line)
        if m:
            self._total_dist_target = float(m.group("value"))
            return

        m = _TTL_CNT_SRC.match(line)
        if m:
            self._total_count_source = int(m.group("value"))
            return

        m = _TTL_CNT_TGT.match(line)
        if m:
            self._total_count_target = int(m.group("value"))
            return

        if _PROG_LINE_PAT.match(line) and self.progress_cb:
            perc = _PROG_PERC_COM.match(line)
            lc = _PROG_CUR_LINE.match(line)
            data = {
                'perc_complete': float(perc.group('value')),
                'lines_complete': int(lc.group('value'))
            }

            self.progress_cb(data)
            return
        
        m = _STATS_MM_CHANGE.match(line)
        if m:
            name = f'{m.group("min")}mm - {m.group("max")}mm' if m.group('min') else f'over {m.group("max")}mm'
            self._welding_stats[name] = {
                'name': name,
                'min': float(m.group('min')) if m.group('min') else None,
                'max': float(m.group('max')),
                'source': int(m.group('src')),
                'target': int(m.group('tgt')),
                'change': float(m.group('chg'))
            }
            return

    def _do_weld(self, aw_args):
        print("Started.")
        p = subprocess.Popen(aw_args, stdout=subprocess.PIPE, universal_newlines=True)

        while(p.poll() is None):
            line = p.stdout.readline()
            self._parse_output_line(line)
        
        # read any remaining output
        lines = p.stdout.readlines()
        for line in lines: self._parse_output_line(line)
        print("Ended.")

        if self.finished_cb:
            self.finished_cb({
                'total_dist_source': self._total_dist_source,
                'total_dist_target': self._total_dist_target,
                'total_count_source': self._total_count_source,
                'total_count_target': self._total_count_target,
                'total_perc_change': self._total_perc_change, 
                'stats': self._welding_stats
            })

    def start_weld(self, input_path, output_path=None):
        if self._thread:
            if self._thread.is_alive(): return
            else: self._thread = None

        args = [self._awpath, '-p=FULL']

        args += [f'--{a.replace("_","-")}' for a in self.aw_flags]
        args += [f'--{a.replace("_","-")}={self.aw_options[a]}' for a in self.aw_options.keys()]
        args += [input_path]

        if output_path: args += [output_path]
        
        self._thread = threading.Thread(target=self._do_weld, args=(args,))
        self._thread.start()
