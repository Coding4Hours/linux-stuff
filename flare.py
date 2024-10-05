def preprocess_pattern(pattern):
    """Preprocess the pattern for a Boyer-Moore-like regex search."""
    bad_char_table = {}
    last_occurrence = {}
    pattern_length = len(pattern)

    # Build the bad character table
    for i, char in enumerate(pattern):
        bad_char_table[char] = pattern_length - i - 1
        last_occurrence[char] = i

    return bad_char_table, last_occurrence


def match_star(text, index, char):
    """Match zero or more of the given character."""
    while index < len(text) and (text[index] == char or char == "."):
        index += 1
    return index


def match_plus(text, index, char):
    """Match one or more of the given character."""
    if index < len(text) and (text[index] == char or char == "."):
        return match_star(text, index + 1, char)
    return index


def match_question(text, index, char):
    """Match zero or one of the given character."""
    if index < len(text) and (text[index] == char or char == "."):
        return index + 1
    return index


def regex_search(text, pattern):
    """Search for regex pattern in text using a Boyer-Moore-like approach."""
    bad_char_table, last_occurrence = preprocess_pattern(pattern)
    pattern_length = len(pattern)
    text_length = len(text)

    index = 0
    while index <= text_length - pattern_length:
        shift = 1
        j = pattern_length - 1

        while j >= 0:
            if pattern[j] == "*":
                # Match zero or more of the previous character
                match_index = match_star(text, index + j, pattern[j - 1])
                j -= 2
                shift = max(shift, match_index - index)
                continue
            elif pattern[j] == "+":
                # Match one or more of the previous character
                match_index = match_plus(text, index + j, pattern[j - 1])
                j -= 2
                shift = max(shift, match_index - index)
                continue
            elif pattern[j] == "?":
                # Match zero or one of the previous character
                match_index = match_question(text, index + j, pattern[j - 1])
                j -= 2
                shift = max(shift, match_index - index)
                continue

            if pattern[j] != text[index + j] and pattern[j] != ".":
                bad_char_shift = bad_char_table.get(text[index + j], pattern_length)
                good_suffix_shift = last_occurrence.get(text[index + j], -1)
                shift = max(shift, bad_char_shift, j - good_suffix_shift)
                break
            j -= 1

        if j < 0:
            print(f"Pattern found at index {index}")
            index += shift
        else:
            index += shift


def search_in_file(file_path, pattern):
    """Search for a regex pattern in a file."""
    try:
        with open(file_path, "r") as file:
            text = file.read()

        regex_search(text, pattern)

    except FileNotFoundError:
        print(f"File not found: {file_path}")


# Example usage:
# Save this script and create a text file named "example.txt" with some content.

# Specify the file path and pattern to search
file_path = input("Filename: \n")
pattern = input("Search Query: \n")  # Example regex pattern

search_in_file(file_path, pattern)
