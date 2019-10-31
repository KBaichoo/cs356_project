#!/usr/bin/env python2

import argparse
import json
import os
import yaml

DEFAULT_NUM_PACKAGES = 1000
DEFAULT_OUT_FILENAME = 'package_finder_results.json'

class PackageFinder:
   def __init__(self, num_packages, package_repos_contents):
      self._num_packages = num_packages
      self._package_repos_contents = package_repos_contents

   def run(self):
      return self._package_repos_contents

if __name__ == '__main__':
   parser = argparse.ArgumentParser()
   parser.add_argument('num_packages',
                       help='number of packages to find, default: %d' % DEFAULT_NUM_PACKAGES,
                       default=DEFAULT_NUM_PACKAGES)
   parser.add_argument('package_repos_file', help='YAML file containing repos to search')
   parser.add_argument('--out', help="output file path, default: %s" % DEFAULT_OUT_FILENAME,
                       default=DEFAULT_OUT_FILENAME)
   args = parser.parse_args()

   # Verify repo info file is present.
   package_repos_path = os.path.join(os.getcwd(), args.package_repos_file)
   if not os.path.isfile(package_repos_path):
      sys.stderr.write('repo yaml file "%s" does not exist' % args.search_databases_file)
      exit(errno.ENOENT)

   # Load package repo yaml contents.
   with open(package_repos_path) as f:
      package_repos_contents = yaml.load(f)

   # Run package finder.
   package_finder = PackageFinder(args.num_packages, package_repos_contents)
   results = package_finder.run()

   # Save results to output file.
   with open(os.path.join(os.getcwd(), args.out), 'w') as f:
      json.dump(results, f, indent=4)
      f.write('\n')
