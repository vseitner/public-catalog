import os
import json

collections_path = "collections/"
indicators_path = "indicators/"
catalog_path = "catalogs/gtif-austria.json"

ALL_CHANGED_FILES = os.environ.get("ALL_CHANGED_FILES")
changed_files = ALL_CHANGED_FILES.split(" ")
print("ALL_CHANGED_FILES: ", changed_files)

collections_files = [
    file for file in changed_files if file.startswith(collections_path)
]
indicator_files = [file for file in changed_files if file.startswith(indicators_path)]

print("changed collections files: ", collections_files)
print("changed indicator files: ", indicator_files)

# Track which collections are referenced inside indicators
collections_in_indicators = set()

# Collect indicator names
indicator_names = []

for file in indicator_files:
    with open(file, "r") as f:
        indicator = json.load(f)

    # Save indicator filename (without extension)
    indicator_name = os.path.splitext(os.path.basename(file))[0]
    indicator_names.append(indicator_name)

    # Collect referenced collections
    if "Collections" in indicator:
        for c in indicator["Collections"]:
            collections_in_indicators.add(c)

# Load current catalog
with open(catalog_path, "r") as f:
    catalog = json.load(f)

# Make sure catalog["collections"] exists
if "collections" not in catalog:
    catalog["collections"] = []

# Start from existing catalog (to avoid overwriting completely)
existing_entries = set(catalog["collections"])

# Determine which changed collections should be added
for file in collections_files:
    collection_name = os.path.splitext(os.path.basename(file))[0]
    if (
        collection_name not in collections_in_indicators
        and collection_name not in existing_entries
    ):
        catalog["collections"].append(collection_name)
        existing_entries.add(collection_name)

# Add changed indicators (avoid duplicates)
for indicator_name in indicator_names:
    if indicator_name not in existing_entries:
        catalog["collections"].append(indicator_name)
        existing_entries.add(indicator_name)

with open(catalog_path, "w") as f:
    print(
        "Final catalog collections: ",
        catalog["collections"],
    )
    json.dump(catalog, f, indent=2)
