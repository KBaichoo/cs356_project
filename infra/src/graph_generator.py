#!/usr/bin/env python2
import argparse
import csv
import matplotlib
from matplotlib.dates import DateFormatter
import numpy as np

class GraphGenerator:
   def __init__(self, data_file, output_file, graph_type,
                title, x_axis_label, y_axis_label, render_local):
      # Constructor arguments.
      self._data_file = data_file
      self._output_file = output_file
      self._graph_type = graph_type
      self._title = title
      self._x_axis_label = x_axis_label
      self._y_axis_label = y_axis_label
      self._render_local = render_local

      # Internal state.
      self._data = None

   def _load_data(self):
      with open(self._data_file) as f:
         # Read the CSV data.
         self._data = np.array(list(csv.reader(f, delimiter=',')))

   def _generate_bar_graph(self):
      fig = plt.figure()

      # Set title and axes.
      fig.suptitle(self._title)
      plt.xlabel(self._x_axis_label)
      plt.ylabel(self._y_axis_label)

      # Add data.
      x_data = self._data[:,0]
      x_pos = np.arange(len(x_data))
      y_data = self._data[:,1]
      y_pos = np.arange(len(y_data))
      plt.bar(y_pos, y_data, align='center')
      plt.xticks(y_pos, x_data)

      # Add values on top of the bars.
      height_offset = 0.02 * max(y_data.astype(np.int))
      for i, v in enumerate(y_data):
         plt.text(x_pos[i], int(v) + height_offset, str(v),
                  ha='center', va='center')

      # Hide x-axis tick marks.
      plt.tick_params(axis=u'x', which=u'both', length=0)

      # Render graph.
      if self._render_local:
         plt.show()
      else:
         plt.savefig(self._output_file)
      plt.close()

   def _generate_grouped_bar_graph(self):
      pass

   def _generate_cdf_graph(self):
      pass

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
   parser.add_argument('-r', '--render-local', action='store_true',
                       help='render figure locally using X11')
   args = parser.parse_args()

   if not args.render_local:
      matplotlib.use('Agg')
   import matplotlib.pyplot as plt

   g = GraphGenerator(args.data_file, args.output_file, args.graph_type,
                      args.title, args.x_axis_label, args.y_axis_label,
                      args.render_local)
   g.run()
