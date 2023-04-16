import json

import pygame

##### CONFIG #####
window_size = (1280, 720)
tile_size = 40
tile_margin = 5

position_x = 0
position_y = 0

file_path = "blueprint1.json"

##################

half_tile_size = tile_size // 2
margin_tile_size = tile_size - (tile_margin * 2)

# pygame init
pygame.init()
window = pygame.display.set_mode(window_size)
clock = pygame.time.Clock()


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


			if block["zaxis"] == -1:
				offset_x = 1
				offset_y = 1

			elif block["zaxis"] == 1:
				offset_x = 0
				offset_y = 0

			elif block["zaxis"] == -2:
				offset_x = 1
				offset_y = 0

			elif block["zaxis"] == 2:
				offset_x = 0
				offset_y = 1


			pos_x = -block["pos"]["y"] + offset_x
			pos_y = -block["pos"]["x"] + offset_y


			blocks.append([
				block["color"], 
				pos_x,
				pos_y,
				[controller["id"] for controller in block["controller"]["controllers"]] if "controllers" in block["controller"] and block["controller"]["controllers"] is not None else None
			])

			id_lookup.append((
				block["controller"]["id"],
				pos_x,
				pos_y
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


# remove lookup table
del id_lookup

# sort controllers by distance to block from farthest to closest
for block_idx, block in enumerate(blocks):
	if block[3] is not None:
		controllers = block[3]

		# sort by distance
		controllers = tuple(sorted(controllers, key=lambda controller: (controller[0] - block[1]) ** 2 + (controller[1] - block[2]) ** 2, reverse=True))

		block[3] = controllers

	blocks[block_idx] = tuple(block)


# calculate avagarage position and center the blocks positions based on that
avg_pos_x = 0
avg_pos_y = 0

for block in blocks:
	avg_pos_x += block[1]
	avg_pos_y += block[2]

avg_pos_x //= len(blocks)
avg_pos_y //= len(blocks)

for block_idx, block in enumerate(blocks):
	# also controllers
	new_controller = tuple((controller[0] - avg_pos_x, controller[1] - avg_pos_y) for controller in block[3]) if block[3] is not None else None

	blocks[block_idx] = (block[0], block[1] - avg_pos_x, block[2] - avg_pos_y, new_controller)


blocks = tuple(blocks)




update_map_draw_range = True

mouse_pressed = False
mouse_moved = False

cursor_tile_x, cursor_tile_y = 0, 0

draw_connections = False

# main loop
while True:
	# events
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			quit()

	

	# mouse dragging
	if pygame.mouse.get_pressed()[0]:
		mouse_pos = pygame.mouse.get_pos()

		if not mouse_pressed:
			mouse_pressed = True
			last_mouse_pos = mouse_pos

		mouse_rel_x = mouse_pos[0] - last_mouse_pos[0]
		mouse_rel_y = mouse_pos[1] - last_mouse_pos[1]

		if mouse_rel_x != 0 or mouse_rel_y != 0:
			position_x -= mouse_rel_x
			position_y -= mouse_rel_y

			update_map_draw_range = True
			mouse_moved = True

		last_mouse_pos = mouse_pos

	elif mouse_pressed:
		mouse_pressed = False

		if mouse_moved:
			mouse_moved = False
		else:
			# mouse click
			cursor_tile_x = (mouse_pos[0] + position_x) // tile_size
			cursor_tile_y = (mouse_pos[1] + position_y) // tile_size
		
	

	if update_map_draw_range:
		map_draw_range_x = (int(position_x / tile_size), int((position_x + window_size[0]) / tile_size))
		map_draw_range_y = (int(position_y / tile_size), int((position_y + window_size[1]) / tile_size))

		update_map_draw_range = False

	
	

	window.fill((0, 0, 0))
	
	# draw grid lines
	for x in range(map_draw_range_x[0], map_draw_range_x[1] + 1):
		pygame.draw.line(window, (50, 50, 50), (x * tile_size - position_x, 0), (x * tile_size - position_x, window_size[1]))

	for y in range(map_draw_range_y[0], map_draw_range_y[1] + 1):
		pygame.draw.line(window, (50, 50, 50), (0, y * tile_size - position_y), (window_size[0], y * tile_size - position_y))

	# draw world center dot
	if -window_size[0] < position_x <= 0 and -window_size[1] < position_y <= 0:
		pygame.draw.circle(window, (255, 255, 255), (-position_x, -position_y), 5)
	

	# draw blocks
	for block_idx, block in enumerate(blocks):
		# outer color
		pygame.draw.rect(window, pygame.Color(f"#{block[0]}"), (block[1] * tile_size - position_x, block[2] * tile_size - position_y, tile_size, tile_size))
		# inner gray color
		pygame.draw.rect(window, (50, 50, 50), (block[1] * tile_size - position_x + tile_margin, block[2] * tile_size - position_y + tile_margin, margin_tile_size, margin_tile_size))
		
		# if hovered, make sure to draw draw lines between this block and all connected blocks (controllers) later
		if block[1] == cursor_tile_x and block[2] == cursor_tile_y:
			if block[3] is not None:
				draw_connections = True
				draw_connections_block_idx = block_idx
				draw_connections_max_idx = len(block[3]) - 1

	# draw cursor hovered tile outline
	pygame.draw.rect(window, (255, 255, 255), (cursor_tile_x * tile_size - position_x, cursor_tile_y * tile_size - position_y, tile_size, tile_size), 1)

	if draw_connections:
		for controller_idx, controller in enumerate(blocks[draw_connections_block_idx][3]):
			try:
				rg = (1 - (controller_idx / draw_connections_max_idx)) ** 1.3 * 255

			except ZeroDivisionError:
				rg = 128

			end_pos = (controller[0] * tile_size - position_x + half_tile_size, controller[1] * tile_size - position_y + half_tile_size)

			# draw line
			pygame.draw.line(window, (rg, rg, 255), (blocks[draw_connections_block_idx][1] * tile_size - position_x + half_tile_size, blocks[draw_connections_block_idx][2] * tile_size - position_y + half_tile_size), end_pos, 8)
			
			# draw end circle
			pygame.draw.circle(window, (0, 200, 0), end_pos, 8)

		draw_connections = False

		# draw start circle
		pygame.draw.circle(window, (255, 50, 0), (blocks[draw_connections_block_idx][1] * tile_size - position_x + half_tile_size, blocks[draw_connections_block_idx][2] * tile_size - position_y + half_tile_size), 8)

	# update
	pygame.display.update()
	clock.tick(60)