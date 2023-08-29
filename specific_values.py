"""
Specific parameters and values to customize the look of the app

The possible color maps are
    ['Pastel1', 'Pastel2', 'Paired', 'Accent', 'Dark2', 'Set1', 'Set2', 'Set3', 'tab10', 'tab20', 'tab20b','tab20c']

"""

# Initial value
redraw_auto = True

# Turtle parameters
coeff = 1.02
step = 10.0

# Number of the maximum of colors and color map
color_length = 3
color_map = "Set1"

# Other
renderer = 'matplot'  # 'matplot' or 'bokeh'
return_type = 'figure'  # 'figure' or 'image' -- Beware figure is only possible for the matplot renderer
if (renderer, return_type) not in [('matplot', 'image'), ('matplot', 'figure'), ('bokeh', 'image')]:
    raise NotImplementedError("The current combination of renderer and return_type is not implemented")

save_files = False
verbose = False
