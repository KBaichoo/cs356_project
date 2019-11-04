#!/usr/bin/python3
import argparse
import subprocess
import os.path

class Detector:
    """
    An abstract class for detecting nodes.
    """
    def detect_feature(self, source):
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
        if "-fPIE" in source or "-pie" in source:
            return True
        else:
            return False

class RulesFlagParser:
    """
    Parser for command line flags.
    """
    def __init__(self, filepath):
        self.filepath = filepath
        self.altered_file = filepath + "_flag_parser"
        self.parser_ready = False

    def setup_parser(self):
        if not self.parser_ready:
            # Copy the file to our modified version
            if not os.path.exists(self.filepath):
                raise ValueError('Class should be instantiated with a filepath'
                        'representing a debian rules file.')
            if not os.path.isfile(self.filepath):
                raise ValueError('Filepath points to a non file object')
            copy_command = 'cp {} {}'.format(self.filepath, self.altered_file)
            print('Copying rules file using command: {}'.format(copy_command))
            result = os.system(copy_command)
            
            # Modify the altered version to include printing vars.
            alteration_command = """
                echo 'print-%  : ; @echo $* = $($*)' >> {}
                """.format(self.altered_file)
            result = os.system(alteration_command)
            self.parser_ready = True

    def get_flag_value(self, flag_name):
        if not self.parser_ready:
            self.setup_parser()

        # Run the command via a shell since string constructed.
        command = '{} print-{}'.format(self.altered_file, flag_name)
        output = subprocess.check_output(command, shell=True)

        # Clean up output, looking for the line with the flag.
        decoded_output = output.decode('utf-8').split('\n')
        filtered_output = list(
                filter(lambda x: x.startswith(flag_name), decoded_output))
        print('Filtered Output: {}'.format(filtered_output))

        assert(len(filtered_output) == 1)
        return filtered_output[0] 


if __name__ == '__main__':
    parser = RulesFlagParser('./rules')
    flag_output = parser.get_flag_value('CPPFLAGS')
    aslr_detector = ALSRDetector()
    detected_aslr = aslr_detector.detect_feature(flag_output)
    print('Found aslr in rules?{}'.format(detected_aslr))
