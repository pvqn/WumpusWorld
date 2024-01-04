# Define the bit indices for each item
G, S, W, B, P = range(5)

# Your encoded map
encoded_map = [[2, 0, 0, 0, 0, 0, 0, 0, 0, 0], [4, 2, 0, 0, 0, 0, 2, 8, 0, 0], [2, 0, 0, 0, 0, 2, 12, 18, 8, 0], [0, 0, 0, 0, 0, 0, 2, 8, 0, 0], [0, 8, 8, 0, 0, 0, 0, 0, 0, 0], [8, 24, 24, 8, 0, 0, 0, 0, 0, 0], [0, 8, 8, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 8, 0, 0, 0, 0, 0, 0, 0, 8], [8, 16, 8, 0, 0, 0, 0, 0, 8, 16]]

# Initialize a new map layout with empty strings
new_map_layout = [['' for _ in range(len(encoded_map[0]))] for __ in range(len(encoded_map))]

# Iterate over the encoded map
for i in range(len(encoded_map)):
    for j in range(len(encoded_map[i])):
        # Get the value of the cell
        cell_value = encoded_map[i][j]
        
        # Check each bit in the cell's value
        if cell_value & (1 << W):
            new_map_layout[i][j] += 'W'
        if cell_value & (1 << P):
            new_map_layout[i][j] += 'P'
        if cell_value & (1 << G):
            new_map_layout[i][j] += 'G'
        if cell_value & (1 << S):
            new_map_layout[i][j] += 'S'
        if cell_value & (1 << B):
            new_map_layout[i][j] += 'B'

# Print the new map layout
for row in new_map_layout:
    print(row)