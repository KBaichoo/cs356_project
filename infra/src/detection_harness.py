#!/usr/bin/env python2

import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys

MOCK = False
DEFAULT_OUT_FILENAME = 'detection_results.json'
DOWNLOADS_PATH = 'package_downloads'
if MOCK:
   DETECTION_TOOL_CMD = './src/mock_detection_tool.sh %s'
else:
   CONFIG_FILE = '../detector/config.yaml'
   DETECTION_TOOL_CMD = ('../detector/runner.py --config_file %s --package_directory %s '
                         '--binary_name %s')
EXTRACTION_CMD = 'dpkg -x %s %s'
DEB_EXTRACTION_PATH = os.path.join(DOWNLOADS_PATH, 'extraction_root')
BINARY_PATH_FINDER_CMD = "%s" % os.path.join(os.getcwd(), 'src/binary_finder.sh')

class DetectionHarness:
   def __init__(self, package_infos, start_offset, count):
      self._package_infos = package_infos
      self._start_offset = start_offset
      self._count = count

      self._detection_results = []

   @staticmethod
   def _download_package(download_cmd):
      # Enter download path.
      cwd = os.getcwd()
      os.chdir(DOWNLOADS_PATH)

      try:
         # Pull down source.
         subprocess.call(download_cmd.split(),
                         stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)

         # Find source path.
         subfiles = os.listdir('.')
         if len(subfiles) != 1:
            raise Exception('package source could not be extracted')

         # subdirs = next(os.walk('.'))[1]
         # if len(subdirs) != 1:
         #    raise Exception('package source could not be extracted')
      except Exception as e:
         raise e
      finally:
         # Return to earlier working directory.
         os.chdir(cwd)

      return os.path.join(os.getcwd(), DOWNLOADS_PATH, subfiles[0])

   @staticmethod
   def _extract_deb(deb_path):
      subprocess.call((EXTRACTION_CMD % (deb_path, DEB_EXTRACTION_PATH)).split(),
                      stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)
      return os.path.join(os.getcwd(), DEB_EXTRACTION_PATH)

   @staticmethod
   def _get_binary_paths(extraction_path):
      # Enter extraction path.
      cwd = os.getcwd()
      os.chdir(extraction_path)

      try:
         # Get the binary path.
         binary_paths = subprocess.check_output(BINARY_PATH_FINDER_CMD.split()).splitlines()
      except Exception as e:
         raise e
      finally:
         # Return to earlier working directory.
         os.chdir(cwd)

      return binary_paths

   def run(self):
      for package_info in self._package_infos[self._start_offset:]:
         if len(self._detection_results) == self._count:
            break

         (repo_name, rank, package_name) = (package_info['source'], package_info['rank'],
                                            package_info['package_name'])
         print 'Running tool on: (%s, %s, %s)' % (repo_name, rank, package_name)

         # Create the downloads directory.
         if os.path.isdir(DOWNLOADS_PATH):
            shutil.rmtree(DOWNLOADS_PATH)
         os.makedirs(DOWNLOADS_PATH)

         try:
            # Download the package source.
            package_path = self._download_package(package_info['download_cmd'])

            # Extract download from the deb.
            extraction_path = self._extract_deb(package_path)

            # Get binary paths.
            binary_paths = self._get_binary_paths(extraction_path)

            # If more than one binary path, ignore for now.
            # TODO(jayden): Cleanly support multiple binaries.
            if (len(binary_paths) != 1):
               raise Exception('wrong number of binary paths: %d (expected %d)' %
                               (len(binary_paths), 1))
            binary_path = binary_paths[0]

            # Run the detection tool on the package.
            if MOCK:
               cmd = DETECTION_TOOL_CMD % package_path
            else:
               cmd = DETECTION_TOOL_CMD % (CONFIG_FILE, extraction_path, binary_path)
            detection_result_string = subprocess.check_output(cmd.split())
            self._detection_results.append({
               'package_name': package_name,
               'rank': rank,
               'source': repo_name,
               'version_number': package_info['version_number'],
               'data_collection_timestamp': datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S'),
               'detection_tool_output': json.loads(detection_result_string)
            })
         except Exception as e:
            print 'Error: %s\n' % str(e)
            continue
         finally:
            # Delete the downloads directory.
            shutil.rmtree(DOWNLOADS_PATH)

         print 'Success: Added detection results for package.\n'

      return self._detection_results

if __name__ == '__main__':
   parser = argparse.ArgumentParser()
   parser.add_argument('package_infos_file',
                       help=('JSON file with package infos, generated by '
                             'package_finder'))
   parser.add_argument('--out', help="output file path, default: %s" % DEFAULT_OUT_FILENAME,
                       default=DEFAULT_OUT_FILENAME)
   parser.add_argument('--start-offset', help='package index to start at', default=0)
   parser.add_argument('--count', help='number of packages to process, default to all',
                       default=None)
   args = parser.parse_args()

   # Verify package infos file exists.
   package_infos_path = os.path.join(os.getcwd(), args.package_infos_file)
   if not os.path.isfile(package_infos_path):
      sys.stderr.write('package infos file "%s" does not exist' % args.package_infos_file)
      exit(errno.ENOENT)

   # Read package infos.
   with open(package_infos_path) as f:
      package_infos = json.load(f)

   count = len(package_infos) if not args.count else int(args.count)

   # Run detection harness.
   detection_harness = DetectionHarness(package_infos, int(args.start_offset), count)
   results = detection_harness.run()

   # Save results to output file.
   with open(os.path.join(os.getcwd(), args.out), 'w') as f:
      json.dump(results, f, indent=4)
      f.write('\n')
