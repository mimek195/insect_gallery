import re


input_file = "arthropoda_ids.txt"
output_file = "taxonomy.txt"

lines = [line.rstrip("\n") for line in open(input_file)]

parent_id_list = []  # tracks parent IDs per indentation level
filter_output = []

# looking up [no rank] using regex
no_rank_regex = re.compile(r'^(\d+)\s+\[([^\]]+)\]\s+(.+)$')

for line in lines:
    if not line.strip():
        continue

    # Line's length without the indentations
    stripped = line.lstrip()
    # Detects indentations
    indentation_level = len(line) - len(stripped)

    regex_match = no_rank_regex.match(stripped)
    if not regex_match:
        continue

    taxon_id, taxon_rank, taxon_name = regex_match.groups()
    print(taxon_id, taxon_rank, taxon_name)
    taxon_rank = taxon_rank.strip().lower()
    taxon_name = taxon_name.strip()

    # Skipping unnecessary or rarely used ranks.
    ignored_ranks = ["no rank", "strain", "isolate", "forma specialis", ]
    if any(ignored_rank in taxon_rank for ignored_rank in ignored_ranks):
        continue

    # Filters out uncertain species, marked with sp., ssp., etc. Filters out environmental samples.
    if "." in taxon_name or "environmental sample" in taxon_name:
        continue

    # Check whether list has enough levels
    while len(parent_id_list) <= indentation_level:
        parent_id_list.append(None)

    # Determine parent ID. Last taxon_id with lower indentation level.
    parent_id = ""
    for i in range(indentation_level - 1, -1, -1):
        if parent_id_list[i] is not None:
            parent_id = parent_id_list[i]
            break

    # Update parent_id_list
    parent_id_list[indentation_level] = taxon_id

    # Adds current taxon to the output list
    filter_output.append([taxon_id, taxon_rank, taxon_name, parent_id])

# Write output
with open(output_file, "w") as f:
    for row in filter_output:
        f.write("\t".join(row) + "\n")

print("Data filtering and reformatting complete")
