
import geopandas
world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
cities = geopandas.read_file(geopandas.datasets.get_path('naturalearth_cities'))


##################################################################### BASICS

# find the column where geometry exists
world.geometry.name


# preview using plot
world.plot()


# create centroids of each country
world['centroids'] = world.centroid


# must reset the geometry (permanently or temporarily) to plot
world.set_geometry('centroids').plot()      #temp: precede with 'world =' to reset


# define a column in the plot to get a choropleth map. Matplotlib cmap for color
world.plot(column = 'pop_est', cmap = 'coolwarm')



##################################################################### LAYERING
# bring in cities layer
cities.plot(marker = '*', color = 'green', markersize = 5)


# make sure cities and world are in the same crs
cities.crs == world.crs
# if not run the following to align:    cities.to_crs(world.crs)


# plot the two layers on top of one another
base = world.plot(color = 'white', edgecolor = 'grey')
cities.plot(ax = base, marker = '*', color = 'blue', markersize = 4)


# http://geopandas.org/geometric_manipulations.html