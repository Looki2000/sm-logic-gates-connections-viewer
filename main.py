import json

file_path = "blueprint.json"

with open(file_path, "r") as f:
	data = json.load(f)

childs = data["bodies"][0]["childs"]

for child in childs:
	print(child["color"])