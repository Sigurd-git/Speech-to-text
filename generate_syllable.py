import os
import glob
from textgrid import TextGrid, IntervalTier, Interval
from typing import List, Dict
import re
from generate_syllable_group import SyllableGenerator


def load_syllable_mapping(syllable_dir: str) -> Dict[str, str]:
    """
    Load phoneme to syllable mapping from syllable files
    Args:
        syllable_dir: Directory containing syllable files with comma-separated syllables
    Returns:
        Dictionary mapping phonemes to syllables
    """
    # Dictionary to store mappings for each file
    file_mappings = {}
    syllable_files = glob.glob(os.path.join(syllable_dir, "*.txt"))

    for file in syllable_files:
        # Get filename without extension as the key
        filename = os.path.splitext(os.path.basename(file))[0]
        groups = []

        with open(file, "r") as f:
            lines = f.readlines()
            for line in lines:
                # Split line by commas to get individual syllable groups
                syllable_groups = line.strip().split(",")
                for group in syllable_groups:
                    # Remove leading/trailing whitespace from each group
                    group = group.strip()
                    # Use the entire phoneme sequence as the key
                    groups.append(group)

        # Store mapping for this file
        file_mappings[filename] = groups

    return file_mappings


def add_syllable_tier(
    textgrid_path: str,
    phoneme_syllable_map: Dict[str, str] = None,
    syllable_generator: SyllableGenerator = None,
) -> TextGrid:
    """
    Add syllable tier to TextGrid based on phoneme-syllable mapping
    Args:
        textgrid_path: Path to input TextGrid file
        phoneme_syllable_map: Dictionary mapping phonemes to syllables
        syllable_generator: SyllableGenerator object
    Returns:
        Modified TextGrid object with new syllable tier
    """
    # Load TextGrid
    tg = TextGrid.fromFile(textgrid_path)

    # Find phoneme tier
    phoneme_tier = None
    for tier in tg.tiers:
        if tier.name.lower() == "phones":
            phoneme_tier = tier
        if tier.name.lower() == "words":
            word_tier = tier

    # Create new syllable tier
    syllable_tier = IntervalTier(
        name="syllables", minTime=phoneme_tier.minTime, maxTime=phoneme_tier.maxTime
    )
    if syllable_generator is not None:
        word_intervals = [
            interval for interval in word_tier.intervals if interval.mark != ""
        ]
        for word_interval in word_intervals:
            phoneme_intervals = [
                interval
                for interval in phoneme_tier.intervals
                if interval.minTime >= word_interval.minTime
                and interval.maxTime <= word_interval.maxTime
            ]
            extract_syllables_from_phoneme_intervals(
                phoneme_intervals, syllable_generator, syllable_tier
            )
    else:
        # Get filename from textgrid path
        # Extract Pair and Sent info from filename (e.g. "Pair1_Prosody1_SentA_stretched.TextGrid" -> "Pair1_SentA")
        filename = os.path.basename(textgrid_path)
        filename = "_".join(
            [part for part in filename.split("_") if "Pair" in part or "Sent" in part]
        )
        # Get mapping for this file
        syllables = phoneme_syllable_map.get(filename, {})
        intervals = [
            interval for interval in phoneme_tier.intervals if interval.mark != ""
        ]
        n_phoneme_past = 0
        # Convert phonemes to syllables
        for syllable in syllables:
            phonemes = syllable.split(" ")
            # find all of the corrsponding intervals in the phoneme tier
            # remove all of the digits from the phonemes
            phonemes = [re.sub(r"\d+", "", phoneme) for phoneme in phonemes]

            n_phonemes = len(phonemes)
            syl_intervals = intervals[n_phoneme_past : n_phoneme_past + n_phonemes]
            n_phoneme_past += n_phonemes

            marks = [interval.mark for interval in syl_intervals]
            # remove all of the digits from the marks
            marks = [re.sub(r"\d+", "", mark) for mark in marks]
            if len(marks) != len(phonemes):
                raise ValueError(
                    f"Mismatch between marks and phonemes: {marks} != {phonemes}"
                )
            marks = [mark.lower() for mark in marks]
            minTime = syl_intervals[0].minTime
            maxTime = syl_intervals[-1].maxTime
            syllable = ".".join(marks)
            syllable_interval = Interval(minTime, maxTime, syllable)
            syllable_tier.addInterval(syllable_interval)
    # Add syllable tier to TextGrid
    tg.append(syllable_tier)
    return tg


def extract_syllables_from_phoneme_intervals(
    intervals, syllable_generator, syllable_tier
):
    phonemes = [interval.mark for interval in intervals if interval.mark != ""]
    stress_pattern = [
        None if "1" not in phoneme and "0" not in phoneme else int(phoneme[-1])
        for phoneme in phonemes
    ]
    # remove stress pattern from phonemes
    phonemes = [re.sub(r"\d+", "", phoneme).lower() for phoneme in phonemes]
    syllables = syllable_generator.generate_syllables(phonemes, stress_pattern)
    index_phonemes = 0

    remap = {
        "ax-h": "ax",
        "hv": "hh",
        "eng": "enx",
        "ng": "nx",
    }
    backmap = {v: k for k, v in remap.items()}
    for i, syllable in enumerate(syllables):
        for j, phoneme in enumerate(syllable):
            phoneme_interval = intervals[index_phonemes]
            if phoneme.lower() in backmap:
                if phoneme_interval.mark != phoneme:
                    phoneme = backmap[phoneme.lower()].upper()
                    assert (
                        phoneme_interval.mark == phoneme
                    ), f"Mismatch between marks and phonemes: {phoneme_interval.mark} != {phoneme}"
            if j == 0:
                minTime = phoneme_interval.minTime
            if j == len(syllable) - 1:
                maxTime = phoneme_interval.maxTime
            index_phonemes += 1
        syllable = ".".join(syllable).lower()
        syllable_interval = Interval(minTime, maxTime, syllable)
        syllable_tier.addInterval(syllable_interval)


def add_syllable_tier_to_textgrids(
    textgrid_dir=(
        "/Users/sigurd/Documents/Projects/prosody-invariance/outputs/stretched_audio"
    ),
    tsylb2_folder="/Users/sigurd/tsylb2_mac",
):
    # Define paths

    syllable_generator = SyllableGenerator(tsylb2_folder)
    # Load phoneme-syllable mapping

    textgrid_files = glob.glob(os.path.join(textgrid_dir, "*.TextGrid"))
    textgrid_files.sort()
    # Process all TextGrid files
    for textgrid_file in textgrid_files:
        # Add syllable tier
        modified_tg = add_syllable_tier(
            textgrid_file,
            syllable_generator=syllable_generator,
        )

        # Save modified TextGrid
        modified_tg.write(textgrid_file)
        print(f"Successfully processed: {textgrid_file}")


if __name__ == "__main__":
    add_syllable_tier_to_textgrids()
