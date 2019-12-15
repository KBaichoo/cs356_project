#!/usr/bin/env python2
import argparse
import csv
from itertools import cycle
import matplotlib
import numpy as np
import os
import scipy.optimize
import scipy.stats

def is_float(s):
   try:
      float(s)
   except ValueError:
      return False
   else:
      return True

def is_int(s):
   try:
      a = float(s)
      b = int(a)
   except ValueError:
      return False
   else:
      return a == b

class GraphGenerator:
   def __init__(self, data_file, output_file, graph_type,
                title, x_axis_label, y_axis_label, render_local,
                groups, default_color, num_bins, cycle_colors,
                slant, fixed_bins, disable_value_above_bar):
      # Constructor arguments.
      self._data_file = data_file
      self._output_file = output_file
      self._graph_type = graph_type
      self._title = title
      self._x_axis_label = x_axis_label
      self._y_axis_label = y_axis_label
      self._render_local = render_local
      self._groups = groups
      self._default_color = default_color
      self._num_bins = num_bins
      self._cycle_colors = cycle_colors
      self._slant = slant
      self._fixed_bins = fixed_bins
      self._disable_value_above_bar = disable_value_above_bar

      # Internal state.
      self._data = None
      self._colors = ['blue', 'orange', 'seagreen', 'firebrick']

   def _load_data(self):
      with open(self._data_file) as f:
         # Read the CSV data.
         self._data = np.array(list(csv.reader(f, delimiter=',')))

   def _get_colors(self, values):
      colors = []
      color = cycle(self._colors)
      for value in values:
         if value.lower() == 'yes':
            colors.append('forestgreen')
         elif value.lower() == 'no':
            colors.append('tomato')
         else:
            colors.append(next(color))
      return colors

   def _generate_bar_graph(self):
      fig = plt.figure()

      # Set title and axes.
      fig.suptitle(self._title, y=0.99)
      plt.xlabel(self._x_axis_label)
      plt.ylabel(self._y_axis_label)

      # Add data.
      x_data = self._data[:,0]
      x_pos = np.arange(len(x_data))
      data_elem = self._data[:,1][0]
      if is_int(data_elem):
         # If integer, convert to integer array.
         y_data = self._data[:,1].astype(np.int)
      elif is_float(data_elem):
         # If float, convert to float array.
         y_data = self._data[:,1].astype(np.float)
      y_pos = np.arange(len(y_data))
      if self._cycle_colors:
         c = self._get_colors(x_data)
      else:
         c = self._default_color
      plt.bar(y_pos, y_data, align='center', color=c)
      plt.xticks(y_pos, x_data)

      # Add values on top of the bars.
      max_bar = max(y_data.astype(np.float))
      height_offset = 0.02 * max_bar
      if not self._disable_value_above_bar:
         for i, v in enumerate(y_data):
            plt.text(x_pos[i], int(v) + height_offset, str(v),
                     ha='center', va='center')

      # Hide x-axis tick marks.
      plt.tick_params(axis=u'x', which=u'both', length=0)

      # Set layout.
      plt.tight_layout()

      # Set y-lim based on max bar value.
      axes = plt.gca()
      axes.set_ylim([0.0, max_bar * 1.1])
      axes.margins(0.04, 0)

      if self._slant is not None:
         # Slant the x-axis labels.
         plt.setp(axes.get_xticklabels(), fontsize=10, rotation=self._slant)

      # Render graph.
      if self._render_local:
         plt.show()
      else:
         plt.savefig(self._output_file)
      plt.close()

   def _generate_grouped_bar_graph(self):
      fig = plt.figure()

      # Set title and axes.
      fig.suptitle(self._title, y=0.99)
      plt.xlabel(self._x_axis_label)
      plt.ylabel(self._y_axis_label)

      # Add data.
      labels = self._data[:,0]
      num_groups = len(self._groups)
      group_data = [self._data[:,i] for i in range(1, num_groups + 1)]
      x_pos = np.arange(len(labels))
      bar_width = 0.4
      if num_groups % 2 == 0:
         bar_offsets = np.arange(-(num_groups // 2) * bar_width,
                                 (num_groups // 2) * bar_width,
                                 bar_width)
      else:
         bar_offsets = np.arange(-(num_groups // 2 + 0.5) * bar_width,
                                 (num_groups // 2) * bar_width,
                                 bar_width)
      color = iter(self._get_colors(self._groups))
      group_rects = [plt.bar(x_pos + bar_offset, data, bar_width, label=name,
                             color=next(color))
                     for bar_offset, name, data
                     in zip(bar_offsets, self._groups, group_data)]
      plt.xticks(x_pos, labels)

      # Add legend.
      plt.legend()

      # Add values on top of the bars.
      if not self._disable_value_above_bar:
         height_offset = 0.02 * max([max(data.astype(np.int)) for data in group_data])
         for rects in group_rects:
            for rect in rects:
               height = int(rect.get_height())
               plt.text(rect.get_x() + bar_width / 2, height + height_offset, str(height),
                        ha='center', va='center')

      # Hide x-axis tick marks.
      plt.tick_params(axis=u'x', which=u'both', length=0)

      # Set layout.
      plt.tight_layout()

      # Render graph.
      if self._render_local:
         plt.show()
      else:
         plt.savefig(self._output_file)
      plt.close()

   def _generate_cdf_graph(self):
      fig = plt.figure()

      # Set title and axes.
      fig.suptitle(self._title, y=0.99)
      plt.xlabel(self._x_axis_label)
      plt.ylabel(self._y_axis_label)

      # Generate data.
      data = self._data[:,0].astype(np.float)
      if self._fixed_bins:
         bins = range(self._num_bins + 1)
      else:
         bins = self._num_bins
      values, base = np.histogram(data, bins=bins)
      cumulative = np.cumsum(values).astype(np.float)
      cumulative /= cumulative[-1]
      base = base[:-1]

      # Add plot.
      plt.plot(base, cumulative, color=self._default_color)

      # Constrain y-axis values.
      axes = plt.gca()
      axes.set_ylim([0.0, 1.0])
      axes.margins(0, 0)

      # Set layout.
      plt.tight_layout()

      # Render graph.
      if self._render_local:
         plt.show()
      else:
         plt.savefig(self._output_file)
      plt.close()

   def run(self):
      # Load data from file.
      self._load_data()

      # Generate graph.
      if self._graph_type == 'bar':
         self._generate_bar_graph()
      elif self._graph_type == 'grouped_bar':
         self._generate_grouped_bar_graph()
      elif self._graph_type == 'cdf':
         self._generate_cdf_graph()

if __name__ == '__main__':
   parser = argparse.ArgumentParser()
   parser.add_argument('data_file', help='filename for data to graph')
   parser.add_argument('output_file', help='output filename')
   parser.add_argument('graph_type', help='graph type',
                       choices={'bar', 'grouped_bar', 'cdf'})
   parser.add_argument('title', help='title for the graph')
   parser.add_argument('x_axis_label', help='label for x-axis')
   parser.add_argument('y_axis_label', help='label for y-axis')
   parser.add_argument('--groups', help='group names for grouped bar graph', nargs='+')
   parser.add_argument('-r', '--render-local', action='store_true',
                       help='render figure locally using X11')
   parser.add_argument('--color', help='color for primary line/bar in graph', default='forestgreen')
   parser.add_argument('--num-bins', help='number of bins for the CDF',
                       type=int, default=1000)
   parser.add_argument('--cycle-colors', help='use multiple colors for bar graph',
                       action='store_true')
   parser.add_argument('--slant', help='slant x-axis labels in bar graph',
                       type=int, nargs='?', default=None, const=40)
   parser.add_argument('--fixed-bins', help='Use bins from range(0, N, 1)',
                       action='store_true')
   parser.add_argument('--disable-value-above-bar', help='Don\'t display value above bar',
                       action='store_true')
   args = parser.parse_args()

   render_local = args.render_local or 'RENDER_LOCAL' in os.environ
   if not render_local:
      matplotlib.use('Agg')
   import matplotlib.pyplot as plt

   g = GraphGenerator(args.data_file, args.output_file, args.graph_type,
                      args.title, args.x_axis_label, args.y_axis_label,
                      render_local, args.groups, args.color, args.num_bins,
                      args.cycle_colors, args.slant, args.fixed_bins,
                      args.disable_value_above_bar)
   g.run()
