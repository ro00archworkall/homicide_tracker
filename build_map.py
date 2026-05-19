"""
build_map.py
------------
Joins city_directory.csv (coordinates) with city_data.csv (live data)
on city name. Writes cities_merged.csv for the Astro component.

Run before `npm run build` or add as prebuild in package.json:
  "prebuild": "python build_map.py"

Input files (both in src/data/):
  city_directory.csv  — name, row, col  (you maintain, static)
  city_data.csv       — name, homicides, rate, model, flag, color  (data script writes)

Output:
  src/data/cities_merged.csv  — all fields joined, only cities present in both files
  src/data/city_rankings.csv  — full ranked list from city_data.csv (all cities, for sidebar)
"""

import csv
import os

DATA_DIR = './src/data'

directory_path = os.path.join(DATA_DIR, 'city_directory.csv')
data_path      = os.path.join(DATA_DIR, 'city_data.csv')
merged_path    = os.path.join(DATA_DIR, 'cities_merged.csv')
rankings_path  = os.path.join(DATA_DIR, 'city_rankings.csv')

# Load directory (coordinates)
directory = {}
with open(directory_path, newline='') as f:
    for row in csv.DictReader(f):
        directory[row['name'].strip()] = row

# Load data (live stats)
data = {}
rankings = []
with open(data_path, newline='') as f:
    for row in csv.DictReader(f):
        name = row['name'].strip()
        data[name] = row
        rankings.append(row)

# Write merged (map markers — only cities in both files)
merged_fields = ['name', 'row', 'col', 'hex', 'homicides', 'rate', 'model', 'flag']
matched = 0
skipped = []
with open(merged_path, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=merged_fields)
    writer.writeheader()
    for name, dir_row in directory.items():
        if name not in data:
            skipped.append(name)
            continue
        d = data[name]
        writer.writerow({
            'name':      name,
            'row':       dir_row['row'],
            'col':       dir_row['col'],
            'hex':       d.get('color', '#ffffff'),
            'homicides': d.get('homicides', ''),
            'rate':      d.get('rate', ''),
            'model':     d.get('model', ''),
            'flag':      d.get('flag', ''),
        })
        matched += 1

# Write full rankings (sidebar — all cities from data script, preserve rank order)
rankings_fields = ['rank', 'name', 'homicides', 'rate', 'color', 'model', 'flag']
with open(rankings_path, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=rankings_fields)
    writer.writeheader()
    for i, row in enumerate(rankings, start=1):
        writer.writerow({
            'rank':      row.get('Rank', i),
            'name':      row['City'].strip(),
            'homicides': row.get('Homicides', ''),
            'rate':      row.get('Rate/100k', ''),
            'color':     row.get('Color', '#ffffff'),
            'model':     row.get('Model', ''),
            'flag':      row.get('Flag', ''),
        })

print(f"Merged:  {matched} cities written to cities_merged.csv")
if skipped:
    print(f"Skipped: {len(skipped)} directory cities not found in data: {', '.join(skipped)}")
print(f"Rankings: {len(rankings)} cities written to city_rankings.csv")
