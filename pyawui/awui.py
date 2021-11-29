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

import tkinter as tk
import tkinter.ttk as ttk

import matplotlib
matplotlib.use('TkAgg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter

import numpy as np

_PADX = (5, 5)
_PADY = (2, 2)

class AWProgress(tk.Frame):
    def __init__(self, master=None,):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

        self.master.title("ArcWelder")
        self.master.resizable(False, False)

    def set_progress_label(self, value):
        self.progress_lbl['text'] = value

    def create_widgets(self):
        self.progress_lbl = ttk.Label(self)
        self.progress_lbl.grid(row=0, column=0, columnspan=2, sticky='w', padx=_PADX, pady=_PADY)

        self.progress_bar = ttk.Progressbar(self, mode='determinate', maximum=100)
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky='ew', padx=_PADX, pady=_PADY)

        self.progress_dtl = ttk.Label(self)
        self.progress_dtl.grid(row=2, column=0, columnspan=2, sticky='w', padx=_PADX, pady=_PADY)

        self.stats_sep = ttk.Separator(self, orient='horizontal')

        self.stats_fig = Figure(figsize=(5,4), dpi=100)
        self.stats_plot = self.stats_fig.add_subplot(1, 1, 1)
        self.stats_canvas = FigureCanvasTkAgg(self.stats_fig, self)

        self.stats_lbl = ttk.Label(self, text="ArcWelding Statistics")

        self.ttldistsrc_lbl = ttk.Label(self, text="Total distance source:")
        self.ttldistsrc_val = ttk.Label(self)
        
        self.ttldisttgt_lbl = ttk.Label(self, text="Total distance output:")
        self.ttldisttgt_val = ttk.Label(self)

        self.ttlcntsrc_lbl = ttk.Label(self, text="Total count source:")
        self.ttlcntsrc_val = ttk.Label(self)

        self.ttlcnttgt_lbl = ttk.Label(self, text="Total count output:")
        self.ttlcnttgt_val = ttk.Label(self)

        self.ttlchng_lbl = ttk.Label(self, text="Total % Changed:")
        self.ttlchng_val = ttk.Label(self)

        self.close_btn = ttk.Button(self, text='Close')
        self.close_btn['command']=self.on_close

    def on_close(self):
        self.master.destroy()

    def on_progress(self, data):
        self.progress_bar['value'] = data['perc_complete']
        self.progress_dtl['text'] = f'Lines completed: {data["lines_complete"]}'
        print(data)

    def on_finished(self, data):
        stats = [data['stats'][x] for x in data['stats'].keys()]
        stats.sort(key=lambda x: x['min'] if x['min'] is not None else float('inf'), reverse=True)
        x = np.arange(len(stats))
        srcs = [x['source'] for x in stats]
        tgts = [x['target'] for x in stats]
        percs = [x['change'] for x in stats]
        width = 0.45

        perc_plot = self.stats_plot.twiny()

        self.stats_plot.barh(x + width/2, srcs, width, label='Source')
        self.stats_plot.barh(x - width/2, tgts, width, label='Output')        
        perc_plot.plot(percs, x, 'ro', label='% Change')
        perc_plot.set_xlabel('% Change')
        perc_plot.tick_params(axis='x', colors='red')

        self.stats_plot.set_xlabel('GCode Lines')
        self.stats_plot.set_ylabel('Line length')
        self.stats_plot.set_yticks(x)
        self.stats_plot.set_yticklabels([x['name'] for x in stats])
        self.stats_plot.xaxis.set_major_formatter(FuncFormatter(lambda x,p: f'{x/1000:,.0f}k'))
        self.stats_plot.legend()

        self.stats_fig.tight_layout()

        self.ttldistsrc_val['text'] = f'{data["total_dist_source"]:,.0f}mm'
        self.ttldisttgt_val['text'] = f'{data["total_dist_target"]:,.0f}mm'
        self.ttlcntsrc_val['text'] = f'{data["total_count_source"]:,.0f}'
        self.ttlcnttgt_val['text'] = f'{data["total_count_target"]:,.0f}'

        self.ttlchng_val['text'] = f'{data["total_perc_change"]}%'

        self.stats_sep.grid(row=3, column=0, columnspan=2, sticky='ew', padx=_PADX, pady=_PADY)
        self.stats_lbl.grid(row=4, column=0, columnspan=2, padx=_PADX, pady=_PADY)
        self.stats_canvas.get_tk_widget().grid(row=5, column=0, columnspan=2, padx=_PADX, pady=_PADY)

        self.ttldistsrc_lbl.grid(row=6, column=0, sticky='w', padx=_PADX, pady=_PADY)
        self.ttldistsrc_val.grid(row=6, column=1, sticky='e', padx=_PADX, pady=_PADY)

        self.ttldisttgt_lbl.grid(row=7, column=0, sticky='w', padx=_PADX, pady=_PADY)
        self.ttldisttgt_val.grid(row=7, column=1, sticky='e', padx=_PADX, pady=_PADY)

        self.ttlcntsrc_lbl.grid(row=8, column=0, sticky='w', padx=_PADX, pady=_PADY)
        self.ttlcntsrc_val.grid(row=8, column=1, sticky='e', padx=_PADX, pady=_PADY)

        self.ttlcnttgt_lbl.grid(row=9, column=0, sticky='w', padx=_PADX, pady=_PADY)
        self.ttlcnttgt_val.grid(row=9, column=1, sticky='e', padx=_PADX, pady=_PADY)

        self.ttlchng_lbl.grid(row=10, column=0, sticky='w', padx=_PADX, pady=_PADY)
        self.ttlchng_val.grid(row=10, column=1, sticky='e', padx=_PADX, pady=_PADY)

        self.close_btn.grid(row=11, column=0, columnspan=2, sticky='ew', padx=_PADX, pady=_PADY)

        print(data)
        
