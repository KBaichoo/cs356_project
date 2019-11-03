#!/usr/bin/env python2

import argparse
import json
import os
import re
import shutil
import subprocess
import yaml

DEFAULT_OUT_FILENAME = 'package_finder_results.json'
DOWNLOADS_PATH = 'package_downloads'
CHANGELOG_PATH = 'debian/changelog'
MAKEFILE_PATHS = ['Makefile', 'Makefile.am', 'CMakeLists.txt']
CPP_REGEX_STRINGS = [
   'CXX_FLAGS'
]
CPP_REGEXES = [re.compile(regex) for regex in CPP_REGEX_STRINGS]

class PackageError(Exception):
   pass

class BenignError(Exception):
   pass

class PackageFinder:
   def __init__(self, num_packages, package_repos_contents, start_offset):
      self._num_packages = num_packages
      self._package_repos_contents = package_repos_contents
      self._start_offset = start_offset

      # [(repo_name, rank, package_name)]
      self._packages_list = []
      # [package_info]
      self._package_infos = []

   def _extract_package_names(self):
      for repo_name, package in self._package_repos_contents[0].iteritems():
         popcon_path = os.path.join(os.getcwd(), package['popcon_path'])
         with open(popcon_path) as f:
            for line in f:
               if not line or line[0] == '-':
                  break
               if line[0] == '#':
                  continue
               self._packages_list.append(tuple([repo_name] + line.split()[:2]))

   @staticmethod
   def _download_package(package_name):
      # Enter download path.
      cwd = os.getcwd()
      os.chdir(DOWNLOADS_PATH)

      try:
         # Pull down source.
         subprocess.call(('apt-get source %s' % package_name).split(),
                         stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)

         # Find source path.
         subdirs = next(os.walk('.'))[1]
         if len(subdirs) != 1:
            raise PackageError('package source could not be extracted')
      except Exception as e:
         raise e
      finally:
         # Return to earlier working directory.
         os.chdir(cwd)

      return os.path.join(DOWNLOADS_PATH, subdirs[0])

   @staticmethod
   def _is_cpp_project(src_path):
      for relative_makefile_path in MAKEFILE_PATHS:
         makefile_path = os.path.join(src_path, relative_makefile_path)
         if not os.path.isfile(makefile_path):
            continue
         with open(makefile_path) as f:
            contents = f.read()
         for cpp_regex in CPP_REGEXES:
            if cpp_regex.search(contents):
               return True
      return False

   @staticmethod
   def _extract_version_number(src_path):
      with open(os.path.join(src_path, CHANGELOG_PATH)) as f:
         first_line = f.readline()

      first_line_split = first_line.split()
      if len(first_line_split) < 2:
         return None

      version_string = first_line_split[1]
      if len(version_string) < 2 or version_string[0] != '(' or version_string[-1] != ')':
         return None

      return version_string[1:-1]

   def _generate_package_infos(self):
      for repo_name, rank, package_name in self._packages_list[self._start_offset:]:
         # If we've found enough packages, stop.
         if len(self._package_infos) == self._num_packages:
            break

         print 'Extracting information for: (%s, %s, %s)' % (repo_name, rank, package_name)

         # Create the downloads directory.
         if os.path.isdir(DOWNLOADS_PATH):
            shutil.rmtree(DOWNLOADS_PATH)
         os.makedirs(DOWNLOADS_PATH)

         try:
            # Download the package source.
            src_path = self._download_package(package_name)
            if not src_path or not os.path.isdir(src_path):
               raise PackageError('could not download source')

            # Check if it is a C++ project.
            if not self._is_cpp_project(src_path):
               raise BenignError('not a C++ project')

            # Extract version number from changelog.
            version_number = self._extract_version_number(src_path)
            if not version_number:
               raise PackageError('no version number found')

            # TODO(jayden): Extract git repo URL if it exists.
            git_repo_url = None

            # TODO(jayden): Extract build log URL.
            build_log_url = None
         except Exception as e:
            print 'Error: %s\n' % str(e)
            continue
         finally:
            # Delete the downloads directory.
            shutil.rmtree(DOWNLOADS_PATH)

         print "Success: project meets all requirements\n"

         package_info = {
            'package_name': package_name,
            'version_number': version_number,
            'source': repo_name,
            'rank': rank,
            'download_cmd': 'apt-get source %s=%s' % (package_name, version_number),
         }
         if git_repo_url:
            package_info['git_repo_url'] = git_repo_url
         if build_log_url:
            package_info['build_log_url'] = build_log_url

         self._package_infos.append(package_info)

   def run(self):
      # Extract package names from popcon rank file.
      self._extract_package_names()

      # Generate package infos for each package.
      self._generate_package_infos()

      print 'Found %d C++ package(s).' % len(self._package_infos)

      return self._package_infos

if __name__ == '__main__':
   parser = argparse.ArgumentParser()
   parser.add_argument('num_packages', help='number of packages to find')
   parser.add_argument('package_repos_file', help='YAML file containing repos to search')
   parser.add_argument('--out', help="output file path, default: %s" % DEFAULT_OUT_FILENAME,
                       default=DEFAULT_OUT_FILENAME)
   parser.add_argument('--start-offset', help='package index to start at', default=0)
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
   package_finder = PackageFinder(int(args.num_packages), package_repos_contents,
                                  int(args.start_offset))
   results = package_finder.run()

   # Save results to output file.
   with open(os.path.join(os.getcwd(), args.out), 'w') as f:
      json.dump(results, f, indent=4)
      f.write('\n')
