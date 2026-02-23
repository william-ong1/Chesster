"""Tests the binary files required to build the project."""

import os
import os.path
from pathlib import Path


class TestBinaries:
    """
    Tests all required binary files for the project. Ensures that the paths
    are correct, and that all the necessary files are present.

    Fields:
    - _bin_dir: the path to the bin/ directory.
    - _protobuf_dir: the path to the protobuf directory.
    """

    _bin_dir = "bin/"
    _protobuf_dir = f"{_bin_dir}subprojects/protobuf-3.5.1/"

    def test_bin_paths_exist(self):
        """
        Tests whether all of the required paths to binary files exist.
        """
        assert os.path.exists(
            self._bin_dir
        ), f"Directory {self._bin_dir} does not exist."
        assert os.path.exists(
            self._protobuf_dir
        ), f"Directory {self._protobuf_dir} does not exist."

    def test_bin_files_exist(self):
        """
        Tests whether all of the required binaries files exist.
        """
        expected_bin_dir_files = [
            f"{self._bin_dir}lc0",
            f"{self._bin_dir}liblc0_lib.dylib",
            f"{self._bin_dir}pgn-extract",
            f"{self._bin_dir}trainingdata-tool",
        ]

        expected_protobuf_dir_files = [
            f"{self._protobuf_dir}libprotobuf-lite.dylib",
            f"{self._protobuf_dir}libprotobuf.dylib",
            f"{self._protobuf_dir}libprotoc.dylib",
        ]

        self._dir_is_correct(expected_bin_dir_files, self._bin_dir)

        self._dir_is_correct(expected_protobuf_dir_files, self._protobuf_dir)

    def _dir_is_correct(self, expected_files, base_dir):
        """
        Checks that the correct files are in a given directory.

        Args:
        - expected_files: a list of the expected filepaths.
        - base_dir: the directory to check.
        """

        num_files = 0
        for filename in os.listdir(base_dir):
            full_path = os.path.join(base_dir, filename)

            if not Path(full_path).is_dir():
                # Test if this file should exist
                assert (
                    full_path in expected_files
                ), f"File {full_path} should not exist.\n\
                   Expected files: {expected_files}"

                # Test if this file exists
                assert Path(
                    full_path
                ).is_file(), f"File does not exist: {full_path}"

                num_files += 1

        # Test if the correct number of files exist for this directory
        assert num_files == len(expected_files)
