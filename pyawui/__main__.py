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

from awui import AWProgress
from awrunner import ArcWelderRunner

import sys
import os
import tkinter as tk

from configparser import ConfigParser

if 1 < len(sys.argv) < 4:
    source_file = sys.argv[1]
    target_file = sys.argv[2] if len(sys.argv) > 2 else source_file

    config = ConfigParser(allow_no_value=True)
    conf_path = os.sep.join(__file__.split(os.sep)[:-2] + ['pyawui.ini'])


    config.read(conf_path)

    awpath = config['PyArcWelderUI'].get('ArcWelderPath')

    if not os.path.exists(awpath):
        sys.stderr.write('You need to specify the path to ArcWelder in pyawui.ini!\n')
        sys.exit(1)

    awrunner = ArcWelderRunner(awpath)

    for opt in config['ArcWelder'].keys():
        if config['ArcWelder'][opt] is not None:
            awrunner.aw_options[opt] = config['ArcWelder'].get(opt)
        else:
            awrunner.aw_flags.append(opt)

    root = tk.Tk()
    prog = AWProgress(root)

    awrunner.progress_cb = prog.on_progress
    awrunner.finished_cb = prog.on_finished

    awrunner.start_weld(source_file, target_file)
    prog.set_progress_label(f'Welding {source_file}...')
    prog.mainloop()