import os
import subprocess
import re
from typing import List, Dict, Tuple


class SyllableGenerator:
    def __init__(self, tsylb2_folder: str):
        """
        Initialize the syllable generator

        Args:
            tsylb2_path: Path to tsylb2 executable
        """
        self.tsylb2_folder = tsylb2_folder

        # Define phoneme mappings and rules
        self.closures = {"bcl", "dcl", "gcl", "pcl", "tcl", "kcl"}
        self.remap = {
            "ax-h": ["ax"],
            "hv": ["hh"],
            "eng": ["enx"],
            "ng": ["nx"],
            "h#": ["#"],
            "pau": ["#"],
            "epi": [],
        }

    def format_phonemes(self, phonemes: List[str], stress_pattern: List[int]) -> str:
        """
        Format phonemes with stress patterns for tsylb2 input

        Args:
            phonemes: List of phonemes
            stress_pattern: List of stress values (0, 1, 2 or None)

        Returns:
            Formatted string for tsylb2 input
        """
        formatted = []
        self.stress_pattern = stress_pattern
        for phon, stress in zip(phonemes, stress_pattern):
            # Remap phonemes if needed
            if phon in self.remap:
                phon = self.remap[phon][0] if self.remap[phon] else None
                if not phon:
                    continue

            # Add stress marker if exists
            if stress is not None:
                formatted.extend([f"'{stress}", phon])
            else:
                formatted.append(phon)

        return " ".join(formatted)

    def run_tsylb2(self, input_str: str) -> str:
        """
        Run tsylb2 on input string and return output

        Args:
            input_str: Formatted phoneme string

        Returns:
            tsylb2 output string
        """
        # Write input to temporary file in the tsylb2 folder
        temp_input_path = os.path.join(self.tsylb2_folder, "temp_input.txt")
        with open(temp_input_path, "w") as f:
            f.write(input_str + "\n")

        # Run tsylb2 with working directory set via cwd parameter
        # Change to tsylb2 directory, run command, and capture output
        current_dir = os.getcwd()
        os.chdir(self.tsylb2_folder)
        os.system("./tsylb2 -n phon1ax.pcd 0 < temp_input.txt > temp_output.txt")
        with open("temp_output.txt", "r") as f:
            result = f.read()
        os.chdir(current_dir)

        return result

    def parse_tsylb2_output(self, output: str) -> List[Dict]:
        """
        Parse tsylb2 output to extract syllable structure

        Args:
            output: tsylb2 output string

        Returns:
            List of syllable dictionaries containing phonemes and boundaries
        """
        syllables = []

        # Parse each line of output
        for line in output.split("\n"):
            line = line.strip()

            # Skip empty lines and non-pronunciation lines
            if not line or not line[0].isdigit():
                continue

            # Extract pronunciation parts between /# and #
            match = re.search(r"1 /# (.*?) #", line)
            if not match:
                continue

            content = match.group(1)

            # Process nested brackets using stack
            content = content.split()

            # Find all of the '['
            left_bracket_index = [i for i, x in enumerate(content) if x == "["]
            right_bracket_index = [i for i, x in enumerate(content) if x == "]"]

            assert len(left_bracket_index) == len(
                right_bracket_index
            ), "Number of left and right brackets do not match"

            for i in range(len(left_bracket_index)):
                start = left_bracket_index[i]
                end = right_bracket_index[i]

                # if overlap, then move the right bracket to the next left bracket
                if i < len(left_bracket_index) - 1 and end > left_bracket_index[i + 1]:
                    end = left_bracket_index[i + 1]

                syllable = content[start + 1 : end]

                # remove possible '[' and ']' and numbers
                syllable = [x for x in syllable if x not in ["[", "]"] and x[0] != "'"]

                # add stress pattern to syllable

                syllables.append(syllable)
            index_phonemes = 0
            new_syllables = []
            for i, syl in enumerate(syllables):
                syllable = []
                for j, phoneme in enumerate(syl):
                    # upper case phoneme
                    phoneme = phoneme.upper()
                    if self.stress_pattern[index_phonemes] is not None:
                        phoneme += f"{self.stress_pattern[index_phonemes]}"
                    index_phonemes += 1
                    syllable.append(phoneme)
                new_syllables.append(syllable)
            syllables = new_syllables
        return syllables

    def generate_syllables(
        self, phonemes: List[str], stress_pattern: List[int]
    ) -> List[Dict]:
        """
        Main function to generate syllable structure

        Args:
            phonemes: List of phonemes
            stress_pattern: List of stress values

        Returns:
            List of syllable dictionaries
        """
        # Format input
        input_str = self.format_phonemes(phonemes, stress_pattern)

        # Run tsylb2
        output = self.run_tsylb2(input_str)

        # Parse output
        return self.parse_tsylb2_output(output)


# Example usage
if __name__ == "__main__":
    # Initialize generator with path to tsylb2
    generator = SyllableGenerator("/Users/sigurd/tsylb2")

    # Example phonemes and stress pattern
    phonemes = ["hh", "ae", "p", "iy"]
    stress = [None, 1, None, 0]

    # Generate syllables
    syllables = generator.generate_syllables(phonemes, stress)

    # Print results
    for i, syl in enumerate(syllables):
        print(f"Syllable {i+1}:")
        print(f"  Phonemes: {' '.join(syl['phonemes'])}")
