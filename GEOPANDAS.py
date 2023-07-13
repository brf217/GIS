
import shapely
import matplotlib.pyplot as plt
import geopandas as gpd
hennepin = gpd.read_file('Parcels2014Hennepin.dbf')

hennepin.set_index(['PIN'], inplace = True)

# select all object type columns and change to category if meeting condition
column_list = list(hennepin.select_dtypes(include = ['object']))

def convert(df, cols):
    for col in cols:
        if df[col].nunique() / len(df[col]) <=.2:
            df[col] = df[col].astype('category')
    return df
    
column_list.remove('geometry')
hennepin = convert(hennepin, column_list)

# drop bad columns 
hennepin.drop(['AGPRE_ENRD', 'AGPRE_EXPD', 'COUNTY_ID', 'DWELL_TYPE', 
               'LANDMARK', 'MULTI_USES', 'NUM_UNITS',  'OWNER_MORE',
               'OWN_ADD_L1', 'OWN_ADD_L2', 'OWN_ADD_L3', 'PARC_CODE',
               'PREFIXTYPE', 'PREFIX_DIR', 'STREETTYPE', 'SUFFIX_DIR', 
               'ZIP4'], axis = 1, inplace = True)
    

# drop lots of nulls
def dropper(df):
    for col in df.columns:
        if df[col].isnull().sum() / len(df[col]) > .98:
            df.drop(col, axis = 1, inplace = True)
    return df   

dropper(hennepin)


# look at type
hennepin = hennepin[hennepin['geometry'].geom_type != 'POINT']

# set only to look at minneapolis
mpls = hennepin.query('CITY == "MINNEAPOLIS"')


# bring in water feature df
water_df = gpd.read_file('LakesAndRivers.dbf')

# show where all the water is
water_df.plot()

# take cedar lake out
cedar_lake = water_df.query('NAME_DNR == "Cedar"')
cedar_lake = cedar_lake.iloc[0:1, :]
 
buff_cedar_lake = cedar_lake.buffer(100)
ax = cedar_lake.plot(color = 'red')
buff_cedar_lake.plot(ax = ax, color = 'green', alpha = 0.5)
plt.show()

# start searching for overlaps - set the spatial index of what you want to search
spatial_index = mpls.sindex

# =============================================================================
# create boundary box
# =============================================================================
cedar_bb = buff_cedar_lake.bounds
cedar_bb = list(cedar_bb.itertuples(index=False, name =None))
# create a shape from the bounds and plot it
from shapely.geometry import box 
from descartes import PolygonPatch

# convert boundary box into a shape - takes tuple only as argument
cedar_bb = cedar_bb[0]
cedar_box = box(cedar_bb[0], cedar_bb[1], cedar_bb[2],cedar_bb[3])

# plot the buffered box around the lake for 4 conditions vs. checking all areas
fig = plt.figure()
ax = fig.gca()
ax.add_patch(PolygonPatch(cedar_box, alpha = 0.5))
ax.axis('scaled')
buff_cedar_lake.plot(ax = ax, alpha = 1)


# get rough matches index of parcels near the lake 
possible_matches_index = list(spatial_index.intersection(cedar_bb))
# use index of matches to locate the rows of the mpls dataframe
possible_matches_df = mpls.iloc[possible_matches_index, :]


# =============================================================================
# intersection
# =============================================================================
# create polygon object from the buff_cedar_lake dataframe by just selecting its shape
buffered_cedar_poly = buff_cedar_lake.iloc[0]
precise_matches = possible_matches_df[possible_matches_df.intersects(buffered_cedar_poly)]
precise_matches.plot() #show areas within 100 meters of the lake

#create dataframe of cedar lake parcels precise matches. Name each row by lake
cedar_lake_parcels = precise_matches.copy()
cedar_lake_parcels['LAKE_NAME'] = 'Cedar Lake'



# =============================================================================
# misc calcs
# =============================================================================
# finding centroid
cedar_lake_parcels['Parcel_Centroid'] = cedar_lake_parcels.centroid

# change data type of centroid
cedar_lake_parcels.crs # see current
# convert to lat_long
cedar_lake_parcels_lat = cedar_lake_parcels.to_crs({'init': 'epsg:4326'})

# change centroids to tuples
cedar_lake_parcels_lat['Parcel_Centroid'] = cedar_lake_parcels_lat['Parcel_Centroid'].apply(
        lambda x: tuple([x.y, x.x]))



