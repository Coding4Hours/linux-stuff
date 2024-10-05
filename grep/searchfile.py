def read_file(file_path):
    with open(file_path, "r") as file:
        return file.readlines()


def preprocess_bad_character_heuristic(pattern):
    """Create the bad character shift table."""
    bad_char_shift = {}
    for i, char in enumerate(pattern):
        bad_char_shift[char] = i
    return bad_char_shift


def preprocess_good_suffix_heuristic(pattern):
    """Create the good suffix shift table."""
    m = len(pattern)
    good_suffix_shift = [0] * (m + 1)
    z_suffix = [0] * (m + 1)

    z_suffix[m] = m
    for i in range(m - 1, 0, -1):
        z_suffix[i] = i
        while z_suffix[i] > 0 and pattern[i - 1] == pattern[z_suffix[i] - 1]:
            z_suffix[i] -= 1

    j = 0
    for i in range(m):
        while j <= i and i + 1 < m and z_suffix[i + 1] + i == m:
            good_suffix_shift[j] = i + 1
            j += 1
        good_suffix_shift[j] = m - z_suffix[i + 1]
        j += 1

    return good_suffix_shift


def boyer_moore_search(lines, pattern):
    """Search for a pattern in the given lines using the Boyer-Moore algorithm."""
    m = len(pattern)

    if m == 0:
        return

    bad_char_shift = preprocess_bad_character_heuristic(pattern)
    good_suffix_shift = preprocess_good_suffix_heuristic(pattern)

    results = []

    for line_index, line in enumerate(lines):
        text = line
        n = len(text)
        s = 0  # Shift of the pattern with respect to text

        while s <= n - m:
            j = m - 1

            while j >= 0 and pattern[j] == text[s + j]:
                j -= 1

            if j < 0:
                results.append(
                    (line_index + 1, s + 1)
                )  # Line and character positions (1-based index)
                s += good_suffix_shift[0] if s + m < n else 1
            else:
                bad_char = text[s + j]
                s += max(good_suffix_shift[j], j - bad_char_shift.get(bad_char, -1))

    return results


def main():
    file_path = "testfile.txt"  # Replace with your file path
    pattern = "ABC"  # Replace with the pattern you want to search for

    lines = read_file(file_path)
    results = boyer_moore_search(lines, pattern)

    for line_num, char_pos in results:
        print(f"Pattern found at line {line_num}, character {char_pos}")


if __name__ == "__main__":
    main()
