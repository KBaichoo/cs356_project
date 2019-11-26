"""
Contains parsers used to support the detectors detecting features.
"""
import logging
import os.path
import subprocess
import re


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
            object_file_regex = re.compile('g\+\+ .* -c')
            defined_flag_regex = re.compile('-D\w*=[^\s]+')

            with open(self.build_log_path, 'r') as fh:
                line = fh.readline()
                while line != '':
                    if line.startswith('g++ '):
                        old_line = line
                        # Filter line, removing -D[name]=foo flags.
                        # TODO(kbaichoo: as it, will remove any D_FORTIFY flags
                        line = defined_flag_regex.sub('', line)
                        logging.debug(
                            'After removing line went from\n %s to\n %s',
                            old_line, line)
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
                                'line with the binary name. Instead found %d',
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
            os.system(copy_command)

            # Modify the altered version to include printing vars.
            alteration_command = """
                echo 'print-%  : ; @echo $* = $($*)' >> {}
                """.format(self.altered_file)
            os.system(alteration_command)
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
            logging.warning(
                self.name, ' was called without flag_name in kwargs.')
            return None
        flag = kwargs['flag_name']
        return self._get_flag_value(flag)
