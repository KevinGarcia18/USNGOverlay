from osgeo import gdal
from usng import USNGtoLL, LLtoUSNG
from PyQt5.QtCore import QLineF
import math

def compute_gridlines( data ):
	# Goal: Given GPS coords of the four corners of the image, the dimensions, and the pixelsize
	# compute the coordinates of the 1000-meter grid lines to be drawn on the tiff image
	if data is None:
		return None

	pixelscale = data["pxscale"]
	tl = data["tl"]
	tr = data["tr"]
	bl = data["bl"]
	br = data["br"]
	xdim = int(data["xdim"])
	ydim = int(data["ydim"])

	tl_usng = LLtoUSNG( tl[0], tl[1], 5 ).split()	# USNG of form e.g. [ '15R', 'TN', '54', '69' ]
	br_usng = LLtoUSNG( br[0], br[1], 5 ).split()

	# Using the top left USNG coordinate, to find grid intersections we want to find the pixels defined by
	# a usng position of 2 decimal precision that lie within the image
	# e.g. next grid intersection for 15R TN 53713 69563 would be at 15R TN 54 70

	cur_usng = tl_usng

	# The grid line to our east has a higher value, ciel to next thousand
	east = round( int(cur_usng[2]) + 49, -2 )
	# The grid line to our south has a lower value, floor to previous thousand
	north = round( int(cur_usng[3]) - 50, -2 )

	lines = [ [], [] ]
	labels = [ [], [] ]
	for i in range(0,500):
	# Compute USNG coords of next (south east) grid intersection

		# If either of the grid lines goes through the scene, we want to draw it
		if (east < int(br_usng[2])) or (north > int(br_usng[3])):

			cross_usng = cur_usng[0] + " " + cur_usng[1] + " " + str(east) + " " + str(north)
			next_cross = USNGtoLL(cross_usng)
			next_cross[0] = clamp(next_cross[0]) # latitude
			next_cross[1] = clamp(next_cross[1]) # longitude
			tl = [ clamp(tl[0]), clamp(tl[1]) ]

			# get the image coordinates for that gps location using pixelscale
			x_span = abs(int( (next_cross[1] - tl[1]) / pixelscale[1] ))
			y_span = abs(int( (tl[0] - next_cross[0]) / pixelscale[0] ))

			if east < int(br_usng[2]):
				#True -> 1000m gridline, False -> 100m gridline
				lines[0].append( [QLineF(x_span, 0, x_span, ydim), (east % 1000 == 0) ])
				#Add the gridline number this line has 
				if east % 1000 == 0:
					labels[0].append( east//1000 )
				else:
					labels[0].append( east//100 )
			if north > int(br_usng[3]):
				lines[1].append( [QLineF(0, y_span, xdim, y_span), (north % 1000 == 0) ] )
				if north % 1000 == 0:
					labels[1].append( north//1000 )
				else:
					labels[1].append( north//100 )

			# Update cur_usng to the just found grid intersection
			cur_usng = cross_usng.split()
			east += 100
			north -= 100
		else:
			break

	return lines, labels

def get_points( filename ):
	dataset = gdal.Open(filename, gdal.GA_ReadOnly)
	data = {}
	if not dataset:
		return { "error" : "Unable to open tif file" }
	geotransform = dataset.GetGeoTransform()
	if not geotransform:
		return { "error" : "Unable to read GeoTIF EXIF tags"}
	if len(geotransform) == 6:
		# Note: the geotif tags come in as [ long, lat ] and are flipped here. pixelScale is also flipped

		# This set uses all of the decimal places provided (13 usually- micron level precision)
		# however there is no chance the drone has that level of accuracy, but it's unclear how to
		# set the precision gdal uses to compute pixelScale, so either we must deal with the imprecision
		# or get gdal to compute pixelscale using GPS coords to 5 decimal places only.
		if (-80 < geotransform[3] < 84) and (-180 <= geotransform[0] < 180):
			data["pxscale"] = ( geotransform[5], geotransform[1] )
			data["tl"] = ( geotransform[3], geotransform[0] )
			data["tr"] = ( geotransform[3], geotransform[0] + ( geotransform[1] * dataset.RasterXSize )  )
			data["bl"] = ( geotransform[3] + ( geotransform[5] * dataset.RasterYSize ), geotransform[0] )
			data["br"] = ( data["bl"][0], data["tr"][1] )
			data["xdim"] = dataset.RasterXSize
			data["ydim"] = dataset.RasterYSize
			return data
		else:
			return { "error" : "ModelTiePoint not in lat/lon coordinates. Need Lat in [-80,84], Lon in [-180,180]"}
	else:
		return { "error" : "Unexpected EXIF tag setup" }

# For labeling waypoints in left widget, given image coords from a click return the USNG coordinates
#tl -> [ lat, long ], pxscale -> [ xscale, yscale ]
def pixels_to_usng( x, y, tl, pxscale ):
	# Convert the image coordinates to GPS LL
	pts = get_points
	ll = LLtoUSNG( tl[0] + pxscale[0] * y, tl[1] + pxscale[1] * x, 5 )
	return ll

# Limit gps values to 5 decimal places (1m precision) if needed
def clamp( fnum ):
	if fnum > 0:
		return math.floor( fnum * 100000 ) / 100000
	else:
		return math.ceil( fnum * 100000 ) / 100000
