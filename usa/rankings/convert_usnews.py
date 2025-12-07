import csv
import re

def parse_usnews_txt(input_file, output_file):
    with open(input_file, 'r') as f:
        content = f.read()

    pattern = r'#(\d+(?:-\d+)?)\s+in\s+National Universities[^\n]*\n([^\n]+)'
    matches = re.findall(pattern, content)

    records = []
    blocks = re.split(r'\n#\d+(?:-\d+)?\s+in\s+National Universities', content)

    i = 0
    for match_idx, (rank, first_line_after) in enumerate(matches):
        block_idx = match_idx + 1
        if block_idx >= len(blocks):
            break

        block_lines = blocks[block_idx].strip().split('\n')
        block_lines = [first_line_after] + block_lines[1:]

        name = ''
        location = ''
        tuition = None
        out_of_state = None
        category = ''

        for idx, line in enumerate(block_lines):
            line = line.strip()

            if not line or '(fall' in line or '(out-of-state)' in line or '(in-state)' in line:
                continue
            elif re.match(r'^\d{1,3},?\d{0,3}$', line):
                continue
            elif '(tie)' in line:
                category = 'National Universities (tie)'
            elif line.startswith('$') or line == 'N/A':
                if tuition is None:
                    tuition = line
                elif out_of_state is None:
                    out_of_state = line
            elif ',' in line and re.search(r'\b[A-Z]{2}$', line):
                location = line
            elif not name and line and not line.startswith('#'):
                name = line

        if not category:
            category = 'National Universities'

        if tuition == out_of_state:
            out_of_state = None

        records.append({
            'rank': rank,
            'name': name,
            'location': location,
            'category': category,
            'tuition': tuition,
            'out_of_state_tuition': out_of_state
        })

    with open(output_file, 'w', newline='') as f:
        fieldnames = ['rank', 'name', 'location', 'category', 'tuition', 'out_of_state_tuition']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

if __name__ == '__main__':
    parse_usnews_txt(
        'data/USA/US News/national_universities.txt',
        'data/USA/US News/national_universities.csv'
    )
