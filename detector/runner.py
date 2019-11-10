#!/usr/bin/python3
import argparse
import logging
import json
import os.path
import subprocess
import yaml
import re


class Detector:
    """
    An abstract class for detecting nodes.
    """
    def __init__(self, name, parser_to_use):
        self.name = name
        self.parser_to_use = parser_to_use

    def detect_feature(self, source):
        pass

    def run(self, parsers):
        pass

class FlagDetector(Detector):
    """
    A detector for flags passed to binaries.
    """
    pass

class ALSRDetector(FlagDetector):
    """
    Given a string source of a command line flags detects for ASLR protection.
    """
    def detect_feature(self, source):
        # TODO(kbaichoo): improve the detection.
        import pdb; pdb.set_trace()
        if "-fPIE" in source or "-pie" in source:
            return True
        else:
            return False

    def run(self, parsers):
        parser = parsers[self.parser_to_use]
        linking_results = parser.parse(stage='linker')
        detection_results = self.detect_feature(linking_results[0])

        logging.debug('Ran detector %s and detected feature? %s', self.name, detection_results)
        return detection_results  

class BuildLogParser:
    """
    Parser for command line flags.
    """
    def __init__(self, name, binary_name, build_log_path):
        self.name = name
        self.binary_name = binary_name
        self.build_log_path = build_log_path
        self.parser_ready = False
        # lines prefixing g++
        self.compiler_lines = []
        # lines that compile into object files.
        self.object_file_lines = []
        # lines containing the final binary created (-o [binaryname])
        self.linker_lines = []
        # other g++ prefix lines not either of those two.
        self.other_lines = []
        logging.info('Parsers %s was created.', self.name)

    def _setup_parser(self):
        """
        Sets up the parser if it wasn't correctly set up.
        """
        if not self.parser_ready:
            # Copy the file to our modified version
            if not os.path.exists(self.build_log_path):
                raise ValueError('Class should be instantiated with a filepath'
                        'representing the buildlog')
            if not os.path.isfile(self.build_log_path):
                raise ValueError('Filepath points to a non file object')
            
            linker_output_flag = '-o ' + self.binary_name.lower()
            object_file_regex =  re.compile('g\+\+ .* -c')
            defined_flag_regex = re.compile('-D\w*=[^\s]+')

            with open(self.build_log_path, 'r') as fh:
                line = fh.readline()
                while line != '':
                    if line.startswith('g++ '):
                        old_line = line 
                        # Filter line, removing -D[name]=foo flags.
                        # TODO(kbaichoo: as it, will remove any D_FORTIFY flags
                        line = defined_flag_regex.sub('', line)
                        logging.debug('After removing line went from\n %s to\n %s', old_line, line)
                        self.compiler_lines.append(line)
                        if linker_output_flag in line.lower():
                            self.linker_lines.append(line)
                        elif object_file_regex.match(line):
                            self.object_file_lines.append(line)
                        else:
                            self.other_lines.append(line)
                    line = fh.readline()
             
            self.parser_ready = True
            logging.info('Parsers %s was setup.', self.name)

    def _get_compiler_calls(self, stage):
        """
        Returns all lines corresponding to a particular stage for the compiler.
        stage is a string repesenting the stage; values: linker, objects, all,
            others.

        parse is the interface that should be used by external classes.
        """
        stage = stage.lower()
        if stage == 'linker':
            if len(self.linker_lines) > 1:
                logging.warning('Expected only a single linking',
                        'line with the binary name... instead found %d',
                        len(self.linker_lines))
            return self.linker_lines
        elif stage == 'objects':
            return self.object_file_lines
        elif stage == 'others':
            return self.other_lines
        else:
            return self.compiler_lines

    def parse(self, **kwargs):
        """
        Access point from which to call into the parser.

        kwargs is expected to have a key 'flag_name' mapping to a string 
        representing a flag.
        """
        if 'stage' not in kwargs:
            logging.warning(self.name, ' was called without stage in kwargs.')
            return None
        if not self.parser_ready:
            self._setup_parser()
        return self._get_compiler_calls(kwargs['stage'])

class RulesFlagParser:
    """
    Parser for command line flags.
    """
    def __init__(self, name, filepath):
        self.name = name
        self.filepath = filepath
        self.altered_file = filepath + "_flag_parser"
        self.parser_ready = False
        logging.info('Parsers %s was created.', self.name)

    def _setup_parser(self):
        """
        Sets up the parser if it wasn't correctly set up.
        """
        if not self.parser_ready:
            # Copy the file to our modified version
            if not os.path.exists(self.filepath):
                raise ValueError('Class should be instantiated with a filepath'
                        'representing a debian rules file.')
            if not os.path.isfile(self.filepath):
                raise ValueError('Filepath points to a non file object')
            copy_command = 'cp {} {}'.format(self.filepath, self.altered_file)
            logging.info('Copying rules file using command: {}'.format(
                copy_command))
            result = os.system(copy_command)
            
            # Modify the altered version to include printing vars.
            alteration_command = """
                echo 'print-%  : ; @echo $* = $($*)' >> {}
                """.format(self.altered_file)
            result = os.system(alteration_command)
            self.parser_ready = True
            logging.info('Parsers %s was setup.', self.name)

    def _get_flag_value(self, flag_name):
        """
        Runs the modified rules makefile to output the FLAG value.
        Returns the the line begining with {FLAGNAME} : {FLAGVALUE}.

        parse is the interface that should be used by external classes.
        """
        if not self.parser_ready:
            self._setup_parser()

        # Run the command via a shell since string constructed.
        command = '{} print-{}'.format(self.altered_file, flag_name)
        output = subprocess.check_output(command, shell=True)

        # Clean up output, looking for the line with the flag.
        decoded_output = output.decode('utf-8').split('\n')
        filtered_output = list(
                filter(lambda x: x.startswith(flag_name), decoded_output))
        logging.debug('Filtered Output: {}'.format(filtered_output))

        assert(len(filtered_output) == 1)
        return filtered_output[0]

    def parse(self, **kwargs):
        """
        Access point from which to call into the parser.

        kwargs is expected to have a key 'flag_name' mapping to a string 
        representing a flag.
        """
        if 'flag_name' not in kwargs:
            logging.warning(self.name, ' was called without flag_name in kwargs.')
            return None
        flag = kwargs['flag_name'] 
        return self._get_flag_value(flag)
        
class Runner:

    @classmethod
    def create(cls, config_filepath, package_directory, binary_name):
        """
        Use this classmethod to construct the class. 
        
        If does validation of arguments, and raises errors if incorrect.
        """
        # Validates the existence of these paths, and correct node types.
        if not os.path.exists(config_filepath):
            raise ValueError('config_filepath %s does not exists.', 
                    config_filepath)
            
        if not os.path.exists(package_directory):
            raise ValueError('package_directory %s does not exists.', 
                    package_directory)
        
        if not os.path.isfile(config_filepath):
            raise ValueError('config_filepath %s is not a file.', 
                    config_filepath)
            
        if not os.path.isdir(package_directory):
            raise ValueError('package_directory %s is not a dir.', 
                    package_directory)
        return cls(config_filepath, package_directory, binary_name)


    def __init__(self, config_filepath, package_directory, binary_name):
        self.config_filepath = config_filepath
        self.package_directory = package_directory
        if self.package_directory[-1] != '/':
            self.package_directory += '/'
        self.binary_name = binary_name
        # Mapping from 'name' -> instantiated class
        self.detector_mapping = {}
        self.parser_mapping = {}

    def setup(self):
        # Parse config file + detectors and parsers added and create them.
        logging.info('Runner is setting up with config %s on pkg directory %s', 
                self.config_filepath, self.package_directory)
        with open(self.config_filepath) as f:
            config_data = yaml.load(f, Loader=yaml.FullLoader)

            for detector_config_mapping in config_data['detectors']:
                detector_config = detector_config_mapping['detector']
                detector_type = detector_config['type'] 
                name = detector_config['name']
                parser_name = detector_config['parser_to_use']
                
                # TODO(kbaichoo): make this more general / less brittle.
                if detector_type == 'ALSRDetector':
                    self.detector_mapping[name] = ALSRDetector(name, parser_name)         
                else:
                    logging.ERROR('Detector type %s is unsupported!', detector_type)
            
            for parser_config_mapping in config_data['parsers']:
                parser_config = parser_config_mapping['parser']
                name = parser_config['name']
                parser_type = parser_config['type']

                # TODO(kbaichoo): make this more general / less brittle.
                if parser_type == 'RulesFlagParser':
                    rules_filepath = self.package_directory + 'debian/rules'
                    self.parser_mapping[name] = RulesFlagParser(name, rules_filepath)
                elif parser_type == 'BuildLogParser':
                    build_log_path = self.package_directory + '/cs356_data/build.log'
                    self.parser_mapping[name] = BuildLogParser(name, self.binary_name, build_log_path)
                else:
                    logging.ERROR('Parser type %s is unsupported!', detector_type)
        logging.info('Finished setting up the Parsers and Detectors.')


    def run(self):
        results_dict = {}

        # Run the detectors using the parsers.
        for detector_name, detector in self.detector_mapping.items():
            logging.info('Running detector %s', detector_name)
            result = detector.run(self.parser_mapping)
            results_dict[detector_name] = result
        
        # Output the detection output
        print(json.dumps(results_dict))

if __name__ == '__main__':
    # TODO(kbaichoo): use deb build logs :)...
    # also expect <pkg_path>/cs356_data/build.log
    # to contain more information...
    # Will get full path to root
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_file',
            help='Path to the config file that will be parsed to'
            'instantiate the necessary detectors.', required=True)
    parser.add_argument('--package_directory',
            help='Path to the package directory.', required=True)
    parser.add_argument('--binary_name',
            help='Name of the prog ultimately produced. Should match what'
            'debtags outputs.', required=True)
    
    # Enable logging.
    # TODO(kbaichoo): add cli flag to set logging levels.
    logging.getLogger().setLevel(logging.INFO)
    args = parser.parse_args()
    
    # Run the detectors and parsers specified in the config flag
    # on the package directory.
    runner = Runner.create(args.config_file, args.package_directory, 
            args.binary_name)
    runner.setup()
    runner.run()
