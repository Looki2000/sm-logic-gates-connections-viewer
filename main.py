import json

file_path = "blueprint3.json"

with open(file_path, "r") as f:
	data = json.load(f)["bodies"][0]["childs"]

def shapeid_to_name(id):
	return "logic gate" if id == logic_gate_shapeid else "timer" if id == timer_shapeid else "unknown block"

logic_gate_shapeid = "9f0f56e8-2c31-4d83-996c-d00a9b296c3f"
timer_shapeid = "8f7fd0e7-c46e-4944-a414-7ce2437bb30f"

base_pos = None

blocks = []
id_lookup = []

for block in data:
	if block["shapeId"] == logic_gate_shapeid or block["shapeId"] == timer_shapeid:
		
		# get base position if not already set
		if base_pos is None:
			base_pos = block["pos"]["z"]
			print(f"base position established: {base_pos}")

		# use only blocks that are on the base position
		if block["pos"]["z"] == base_pos:
			#print(f"{shapeid_to_name(block['shapeId'])} at {block['pos']}")

			blocks.append([
				block["color"], 
				block["pos"]["x"], 
				block["pos"]["y"], 
				[controller["id"] for controller in block["controller"]["controllers"]] if "controllers" in block["controller"] and block["controller"]["controllers"] is not None else None
			])

			id_lookup.append((
				block["controller"]["id"],
				block["pos"]["x"],
				block["pos"]["y"]
			))


# replace controllers ids in blocks to x, y coordinates
id_lookup = tuple(id_lookup)

for block_idx, block in enumerate(blocks):
	if block[3] is not None:

		controllers = block[3]

		for controller_idx, controller in enumerate(controllers):
			for lookup_idx in range(len(id_lookup)):
				if controller == id_lookup[lookup_idx][0]:
					controllers[controller_idx] = (id_lookup[lookup_idx][1], id_lookup[lookup_idx][2])
					break
			
		block[3] = tuple(controllers)
	
	blocks[block_idx] = tuple(block)




for block in blocks:
	print(block)