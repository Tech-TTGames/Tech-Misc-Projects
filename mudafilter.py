import re
import pyperclip

# ==========================================
# Configuration & Scaling
# ==========================================

NOTE_WEIGHT_MAP = {
    "🤷 🎫": 0.5,  # I don't really care
    "???": 0.6,  # ????
    "📷": 0.75,  # I don't know you, but you look interesting
    "📔": 1.0,  # I know you
    "🔖": 1.5,  # I know you and like you a bit
    "▶️": 3.0,  # Like them
    "🔼": 5.0,  # Like them a bunch
    "⏫": 10.0,  # Like them very much
    "❤️": 20.0,  # Love them
    "💖": 40.0,  # Love them a bunch
    "⭐": 60.0  # Best of all Time
}


def combine_lists(list1, list2):
    series_dict = {}

    for text in [list1, list2]:
        current_series = None
        for line in text.split('\n'):
            stripped_line = line.strip()

            if not stripped_line:
                continue

            # Match series header
            header_match = re.match(r'^(.*?)\s*-\s*(\d+)/(\d+)$', stripped_line)
            if header_match:
                current_series = header_match.group(1).strip()
                if not current_series:
                    current_series = "<Unknown Series>"

                # If series isn't in our dictionary, add its header
                if current_series not in series_dict:
                    series_dict[current_series] = [line]
                continue

            # Match character lines
            if current_series is not None:
                # Append character lines (avoiding exact duplicates if any exist)
                if line not in series_dict[current_series]:
                    series_dict[current_series].append(line)

    # Reconstruct the combined list
    combined_output = []
    for lines in series_dict.values():
        combined_output.extend(lines)
        combined_output.append("")  # Add spacing between blocks

    return "\n".join(combined_output)

def calculate_character_weight(rank, best_note_str):
    """
    Computes a continuous score based on a smooth rank curve and note tier.
    """
    # 1. Rank component (Smooth Inverse Curve)
    # Heavily weights Top 1000, trails off smoothly for deep chaff
    rank_score = (2000.0 / (rank + 150.0))

    # 2. Note component (unnoted characters default to lowest baseline)
    note_score = NOTE_WEIGHT_MAP.get(best_note_str, 0) if best_note_str else 0

    return rank_score + (note_score * 2)


def get_filtered_series_weighted(
        text_data,
        disabled_toggles=None,
        min_density=0.0,
        persist=False
):
    if disabled_toggles is None:
        disabled_toggles = []

    lines = text_data.split('\n')
    qualifying_series = []
    rejected_series = []
    persisted_output = []

    current_series = None
    current_series_lines = []

    total_series_chars = 0
    series_weight_sum = 0.0

    def evaluate_current():
        if current_series is None or total_series_chars == 0:
            return

        # Density represents expected value per roll into this series
        density = series_weight_sum / total_series_chars

        if density >= min_density:
            qualifying_series.append((current_series, series_weight_sum, density))
            persisted_output.extend(current_series_lines)
            persisted_output.append("")
        else:
            rejected_series.append((current_series, series_weight_sum, density))

    for line in lines:
        stripped_line = line.strip()

        if not stripped_line:
            if current_series is not None:
                current_series_lines.append(line)
            continue

        # Match series header
        header_match = re.match(r'^(.*?)\s*-\s*(\d+)/(\d+)$', stripped_line)
        if header_match:
            evaluate_current()

            current_series = header_match.group(1).strip()
            total_series_chars = int(header_match.group(3))
            current_series_lines = [line]
            series_weight_sum = 0.0

            if not current_series:
                current_series = "<Unknown Series>"
            continue

        if current_series is not None:
            current_series_lines.append(line)

        # Match character line
        char_match = re.match(r'^#([0-9,]+)\s*-\s*(.*)$', stripped_line)
        if char_match and current_series is not None:
            rank = int(char_match.group(1).replace(',', ''))
            char_info = char_match.group(2)

            if any(toggle in char_info for toggle in disabled_toggles):
                continue

            # Extract note from the last pipe segment
            best_note_str = None
            if '|' in char_info:
                candidate_note = char_info.rsplit('|', 1)[-1].replace('🚫', '').strip()
                if candidate_note in NOTE_WEIGHT_MAP:
                    best_note_str = candidate_note

            # Calculate continuous weight
            w = calculate_character_weight(rank, best_note_str)
            series_weight_sum += w

    # Evaluate final block
    evaluate_current()

    if persist:
        return '\n'.join(persisted_output).strip(), []

    return qualifying_series, rejected_series


# ==========================================
# Interactive Usage
# ==========================================

if __name__ == "__main__":
    FILE_PATH_1 = 'dls.txt'
    DISABLED_TOGGLES = ['$togglewestern', '$toggleirl', '$serverdisable']

    print("=== Data Input ===")

    # Optional dual-file reading
    file_2_name = "topli.txt"
    # file_2_name = input("Enter the filename for second list to combine or just click enter if none: ").strip()

    try:
        if file_2_name:
            with open(FILE_PATH_1, 'r', encoding='utf-8') as file1:
                text1 = file1.read()
            with open(file_2_name, 'r', encoding='utf-8') as file2:
                text2 = file2.read()

            text_input = combine_lists(text1, text2)
            print("Lists successfully combined!")
        else:
            with open(FILE_PATH_1, 'r', encoding='utf-8') as file:
                text_input = file.read()

        print("\n=== Efficiency Filter ===")

        # Minimum Density Threshold
        min_density_input = input(
            "Enter minimum Series Density (Total Score / Total Characters, e.g., 0.5, 0 to keep all): ")
        try:
            min_density = float(min_density_input)
        except ValueError:
            print("Invalid density. Defaulting to 0.0.")
            min_density = 0.0

        # Persist Mode Toggle
        persist_input = input(
            "\nEnable Persist Mode? (Outputs original list format instead of '$' separated names) (y/n): ").strip().lower()
        use_persist_mode = persist_input == 'y'

        # Run the function
        result_output, rejected_series = get_filtered_series_weighted(
            text_input,
            disabled_toggles=DISABLED_TOGGLES,
            min_density=min_density,
            persist=use_persist_mode
        )

        # Output Results
        if use_persist_mode:
            if result_output:
                pyperclip.copy(result_output)
                print(f"\nSuccessfully copied {len(result_output.splitlines())} lines of persisted text to clipboard!")
            else:
                print("\nNo series matched the criteria. Clipboard was not updated.")
        else:
            if result_output:
                series_names = [item[0] for item in result_output]
                pyperclip.copy("$".join(series_names))
                print(f"\nFound {len(series_names)} highly-efficient series.")

                # Print top 10 series by density for immediate feedback
                print("\nTop 10 series by Density (Efficiency):")
                sorted_results = sorted(result_output, key=lambda x: x[2], reverse=True)
                for s_name, s_weight, s_dens in sorted_results[:10]:
                    print(f" - {s_name}: Density {s_dens:.2f} (Total Score: {s_weight:.2f})")

                print("\nSuccessfully copied main series names to clipboard!")
            else:
                print("\nNo series matched the criteria. Clipboard was not updated.")

            # --- HEAVY REJECTS RESCUE ---
            if rejected_series:
                print("\n" + "=" * 30)
                rescue_input = input(
                    "Check for 'Heavy' rejected series? (Enter minimum Total Score, e.g., 15, or press Enter to skip): ").strip()
                if rescue_input:
                    try:
                        min_heavy = float(rescue_input)
                        heavy_rescues = [s for s in rejected_series if s[1] >= min_heavy]

                        if heavy_rescues:
                            heavy_names = [s[0] for s in heavy_rescues]
                            pyperclip.copy("$".join(heavy_names))
                            print(
                                f"\nFound {len(heavy_rescues)} heavy rejected series. OVERWROTE clipboard with this new list!")

                            print("\nTop Heavy Series Rescued:")
                            heavy_rescues_sorted = sorted(heavy_rescues, key=lambda x: x[1], reverse=True)
                            for s_name, s_weight, s_dens in heavy_rescues_sorted:
                                print(f" - {s_name}: Total Score {s_weight:.2f} (Density: {s_dens:.2f})")
                        else:
                            print("\nNo rejected series met that weight threshold.")
                    except ValueError:
                        print("\nSkipping heavy rescue.")

    except FileNotFoundError as e:
        print(f"Error: Could not find the file. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")