def read_file(filename):
    # Initialize an empty list to store the 2D array
    grid = []

    # Open the file and read its contents
    with open(filename, 'r') as file:
        # Read the first line containing the grid size
        grid_size = int(file.readline().strip())

        # Read the remaining lines and split them based on dots
        for _ in range(grid_size):
            # Read each line, strip whitespace, split by dots, and filter out empty strings
            row = list(filter(None, file.readline().strip().split('.')))
            
            # Append the row to the grid list
            grid.append(row)
    
    print( grid_size )
    for row in grid:
        for column in row: 
            print( column, end = ' ' )
        print()

    return grid_size, grid