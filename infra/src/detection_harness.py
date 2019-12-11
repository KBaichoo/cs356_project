#!/usr/bin/env python2

import argparse
import datetime
import errno
import git
import json
import os
import shutil
import subprocess
import sys
import yaml

MOCK = False
DEFAULT_OUT_FILENAME = 'detection_results.json'
SOURCE_DOWNLOADS_PATH = 'source_package_downloads_tmp'
BINARY_DOWNLOADS_PATH = 'binary_package_downloads_tmp'
BUILD_LOG_DIR_PATH = 'build_log_dir_tmp'
GIT_REPO_PATH = 'git_bisection_repo_tmp'
GITHUB_REPO_WHITELIST = './results/github_repo_whitelist.txt'
BISECTION_RUNNER_PATH = './src/bisect_runner.sh'
DETECTOR_BISECT_PATH = './src/detector_bisect.sh'
CREATION_TIME_CMD = './src/creation_time.sh %s'
BUILD_LOG_DOWNLOAD_CMD = 'getbuildlog %s last amd64'
if MOCK:
   DETECTION_TOOL_CMD = './src/mock_detection_tool.sh %s'
else:
   CONFIG_FILE = '../detector/config.yaml'
   CONFIG_NO_LOG_FILE = '../detector/config_no_log.yaml'
   CONFIG_NO_BINARY_FILE = '../detector/config_no_binary.yaml'
   CONFIG_NO_BINARY_NO_LOG_FILE = '../detector/config_no_binary_no_log.yaml'
   RUNNER_PATH = '../detector/runner.py'
   DETECTION_TOOL_CMD = ('../detector/runner.py '
                         '--config_file %s '
                         '--binary_package_directory %s '
                         '--binary_name %s '
                         '--source_package_directory %s')
   DETECTION_TOOL_LOG_CMD = ('../detector/runner.py '
                             '--config_file %s '
                             '--binary_package_directory %s '
                             '--binary_name %s '
                             '--source_package_directory %s '
                             '--build_log_path %s')
   DETECTION_TOOL_NO_BINARY_CMD = ('../detector/runner.py '
                                   '--config_file %s '
                                   '--source_package_directory %s')
   DETECTION_TOOL_NO_BINARY_LOG_CMD = ('../detector/runner.py '
                                       '--config_file %s '
                                       '--source_package_directory %s '
                                       '--build_log_path %s')
EXTRACTION_CMD = 'dpkg -x %s %s'
DEB_EXTRACTION_PATH = os.path.join(BINARY_DOWNLOADS_PATH, 'extraction_root')
BINARY_PATH_FINDER_CMD = "%s" % os.path.join(os.getcwd(), 'src/binary_finder.sh')
DATE_FMT = '%Y-%m-%d'

class DetectionHarness:
   def __init__(self, package_infos, start_offset, count, github_repo_whitelist, features,
                skip_bisect):
      self._package_infos = package_infos
      self._start_offset = start_offset
      self._count = count
      self._github_repo_whitelist = github_repo_whitelist
      self._features = features
      self._skip_bisect = skip_bisect

      self._detection_results = []

   @staticmethod
   def _download_source_package(download_cmd):
      # Enter download path.
      cwd = os.getcwd()
      os.chdir(SOURCE_DOWNLOADS_PATH)

      try:
         # Pull down source.
         subprocess.call(download_cmd.split(),
                         stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)

         # Find source path.
         subdirs = next(os.walk('.'))[1]
         if len(subdirs) != 1:
            raise Exception('package source could not be extracted')
      except Exception as e:
         raise e
      finally:
         # Return to earlier working directory.
         os.chdir(cwd)

      return os.path.join(os.getcwd(), SOURCE_DOWNLOADS_PATH, subdirs[0])

   @staticmethod
   def _download_binary_package(download_cmd):
      # Enter download path.
      cwd = os.getcwd()
      os.chdir(BINARY_DOWNLOADS_PATH)

      try:
         # Pull down source.
         subprocess.call(download_cmd.split(),
                         stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)

         # Find source path.
         subfiles = os.listdir('.')
         if len(subfiles) != 1:
            raise Exception('package source could not be extracted')
      except Exception as e:
         raise e
      finally:
         # Return to earlier working directory.
         os.chdir(cwd)

      return os.path.join(os.getcwd(), BINARY_DOWNLOADS_PATH, subfiles[0])

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

   @staticmethod
   def _run_git_bisect(new_commit, old_commit, feature):
      # Get full paths to tools.
      bisection_runner_path = os.path.abspath(BISECTION_RUNNER_PATH)
      detector_bisect_path = os.path.abspath(DETECTOR_BISECT_PATH)
      runner_path = os.path.abspath(RUNNER_PATH)
      config_no_binary_path = os.path.abspath(CONFIG_NO_BINARY_FILE)
      repo_path = os.path.abspath(GIT_REPO_PATH)

      # Enter git repo root.
      cwd = os.getcwd()
      os.chdir(GIT_REPO_PATH)

      try:
         # Get bisection commit.
         return subprocess.check_output(
            [bisection_runner_path,
             str(new_commit),
             str(old_commit),
             detector_bisect_path,
             runner_path,
             config_no_binary_path,
             repo_path,
             feature]).strip()
      except:
         return None
      finally:
         # Return to earlier working directory.
         os.chdir(cwd)

   @staticmethod
   def _feature_detected(feature):
      try:
         subprocess.check_call([DETECTOR_BISECT_PATH, RUNNER_PATH, CONFIG_NO_BINARY_FILE,
                                GIT_REPO_PATH, feature])
         return False
      except subprocess.CalledProcessError:
         return True

   @staticmethod
   def _run_git_bisection(git_repo_url, features):
      try:
         data = {}

         repo = git.Repo.clone_from(git_repo_url, GIT_REPO_PATH)

         # Get head commit and first commit.
         main_branch = repo.active_branch
         head_commit = next(repo.iter_commits(main_branch))
         first_commit = None
         for first_commit in repo.iter_commits(main_branch):
            pass

         # Add the repo URL.
         data['git_repo_url'] = git_repo_url

         # Extract initial commit timestamp.
         data['creation_timestamp'] = first_commit.authored_datetime.strftime(DATE_FMT)

         # Iterate over features, running git bisection on each.
         features_data = {}
         for feature in features:
            # If feature not detected in head commit, continue.
            repo.git.checkout(head_commit)
            if not DetectionHarness._feature_detected(feature):
               continue

            # If feature detected in first commit, continue.
            repo.git.checkout(first_commit)
            if DetectionHarness._feature_detected(feature):
               continue

            # Run bisection.
            repo.git.checkout(main_branch)
            introduction_hash = DetectionHarness._run_git_bisect(head_commit, first_commit, feature)
            if introduction_hash:
               introduction_commit = repo.commit(introduction_hash)
               features_data[feature] = {
                  'commit': introduction_hash,
                  'timestamp': introduction_commit.authored_datetime.strftime(DATE_FMT)
               }
         data['features'] = features_data

         return data
      except:
         print "Failed to run git bisection on %s" % git_repo_url
         return None
      finally:
         shutil.rmtree(GIT_REPO_PATH, ignore_errors=True)

   @staticmethod
   def _download_build_log(package_name):
      # Enter log dir.
      cwd = os.getcwd()
      os.chdir(BUILD_LOG_DIR_PATH)

      try:
         # Pull down source.
         subprocess.call((BUILD_LOG_DOWNLOAD_CMD % package_name).split(),
                         stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)

         # Find source path.
         subfiles = os.listdir('.')
         if len(subfiles) != 1:
            raise Exception('package source could not be extracted')
      except:
         print "Failed to download build log for %s" % package_name
         return None
      finally:
         os.chdir(cwd)

      return os.path.join(os.getcwd(), BUILD_LOG_DIR_PATH, subfiles[0])

   @staticmethod
   def _extract_creation_time(package_name):
      try:
         creation_time_secs = subprocess.check_output((CREATION_TIME_CMD % package_name).split())
         return datetime.datetime.fromtimestamp(int(creation_time_secs))
      except Exception as e:
         print e
         print "Failed to get creation time for %s" % package_name
         return None

   def run(self):
      for package_info in self._package_infos[self._start_offset:]:
         if len(self._detection_results) == self._count:
            break

         (repo_name,
          rank,
          package_name,
          maintainer,
          git_repo_url) = (
             package_info['source'],
             package_info['rank'],
             package_info['package_name'],
             # Optional data.
             package_info.get('maintainer'),
             package_info.get('git_repo_url'))
         print 'Running tool on: (%s, %s, %s)' % (repo_name, rank, package_name)

         # Create the download directories.
         if os.path.isdir(SOURCE_DOWNLOADS_PATH):
            shutil.rmtree(SOURCE_DOWNLOADS_PATH)
         os.makedirs(SOURCE_DOWNLOADS_PATH)
         if os.path.isdir(BINARY_DOWNLOADS_PATH):
            shutil.rmtree(BINARY_DOWNLOADS_PATH)
         os.makedirs(BINARY_DOWNLOADS_PATH)
         if os.path.isdir(BUILD_LOG_DIR_PATH):
            shutil.rmtree(BUILD_LOG_DIR_PATH)
         os.makedirs(BUILD_LOG_DIR_PATH)

         try:
            # Download the source package.
            source_extraction_path = self._download_source_package(
               package_info['download_source_cmd'])

            # Download the binary package.
            binary_package_path = self._download_binary_package(
               package_info['download_binary_cmd'])

            # Extract download from the deb.
            binary_extraction_path = self._extract_deb(binary_package_path)

            # Get binary paths.
            binary_paths = self._get_binary_paths(binary_extraction_path)

            # If not correct number of binary paths included, don't pass into detector.
            # TODO(jayden): Cleanly support multiple binaries.
            if len(binary_paths) == 1:
               binary_path = binary_paths[0]
            else:
               binary_path = None

            # Get the build log.
            build_log_path = self._download_build_log(package_name)

            # Get the package creation time from changelog.
            creation_time = self._extract_creation_time(package_name)

            # Run the detection tool on the package.
            if MOCK:
               cmd = DETECTION_TOOL_CMD % binary_package_path
            else:
               if binary_path:
                  if build_log_path:
                     cmd = DETECTION_TOOL_LOG_CMD % (CONFIG_FILE,
                                                     binary_extraction_path,
                                                     binary_path,
                                                     source_extraction_path,
                                                     build_log_path)
                  else:
                     cmd = DETECTION_TOOL_CMD % (CONFIG_NO_LOG_FILE,
                                                 binary_extraction_path,
                                                 binary_path,
                                                 source_extraction_path)
               else:
                  if build_log_path:
                     cmd = DETECTION_TOOL_NO_BINARY_LOG_CMD % (CONFIG_NO_BINARY_FILE,
                                                               source_extraction_path,
                                                               build_log_path)
                  else:
                     cmd = DETECTION_TOOL_NO_BINARY_CMD % (CONFIG_NO_BINARY_NO_LOG_FILE,
                                                           source_extraction_path)
            detection_result_string = subprocess.check_output(cmd.split())

            # If repo has a git URL, run git bisection on it. If it's a github
            # URL make sure it's in the whitelist.
            git_bisection_data = None
            if (not self._skip_bisect and git_repo_url and
                ('github.com' not in git_repo_url or
                 git_repo_url in self._github_repo_whitelist)):
               git_bisection_data = self._run_git_bisection(git_repo_url, self._features)

            result = {
               'package_name': package_name,
               'rank': rank,
               'source': repo_name,
               'version_number': package_info['version_number'],
               'data_collection_timestamp': datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S'),
               'detection_tool_output': json.loads(detection_result_string)
            }
            if creation_time:
               result['creation_date'] = creation_time.strftime(DATE_FMT)
            if git_bisection_data:
               result['git_bisection_data'] = git_bisection_data
            if maintainer:
               result['maintainer'] = maintainer
            self._detection_results.append(result)
         except Exception as e:
            print 'Error: %s\n' % str(e)
            continue
         finally:
            # Delete the download directories.
            shutil.rmtree(SOURCE_DOWNLOADS_PATH)
            shutil.rmtree(BINARY_DOWNLOADS_PATH)
            shutil.rmtree(BUILD_LOG_DIR_PATH)

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
   parser.add_argument('--no-bisect', help='whether to skip bisection',
                       default=False, type=bool)
   args = parser.parse_args()

   # Verify package infos file exists.
   package_infos_path = os.path.join(os.getcwd(), args.package_infos_file)
   if not os.path.isfile(package_infos_path):
      sys.stderr.write('package infos file "%s" does not exist\n' % args.package_infos_file)
      exit(errno.ENOENT)

   # Read package infos.
   with open(package_infos_path) as f:
      package_infos = json.load(f)

   count = len(package_infos) if not args.count else int(args.count)

   # Read in github repo whitelist.
   with open(GITHUB_REPO_WHITELIST) as f:
      github_repo_whitelist = set(f.read().splitlines())

   # Read in features from no-binary config.
   with open(CONFIG_NO_BINARY_FILE) as f:
      no_binary_config = yaml.load(f)
      features = no_binary_config['features_selected']

   # Run detection harness.
   detection_harness = DetectionHarness(package_infos, int(args.start_offset), count,
                                        github_repo_whitelist, features, args.no_bisect)
   results = detection_harness.run()

   # Save results to output file.
   with open(os.path.join(os.getcwd(), args.out), 'w') as f:
      json.dump(results, f, indent=4)
      f.write('\n')
