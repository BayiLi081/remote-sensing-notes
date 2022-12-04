
import glob
import numpy as np
import re
import pandas as pd
import geopandas as gpd
import rioxarray as rxr
import earthpy.plot as ep
import matplotlib.pyplot as plt
from shapely.geometry import mapping, box
from rasterio.plot import plotting_extent

list_of_hdf = glob.glob('../h08v04/*.hdf')

desired_bands = ["sur_refl_b01_1",
                 "sur_refl_b02_1",
                 "sur_refl_b03_1",
                 "sur_refl_b04_1",
                 "sur_refl_b05_1",
                 "sur_refl_b06_1",
                 "sur_refl_b07_1"]


fire_boundary_path = "../boundary/boundary.shp"
fire_boundary = gpd.read_file(fire_boundary_path)
# Check CRS

modis_pre_bands = rxr.open_rasterio('../h08v04/MOD09GA.A2020202.h08v04.061.2020339163109.hdf', masked=True, variable=desired_bands).squeeze()

if not fire_boundary.crs == modis_pre_bands.rio.crs:
    # If the crs is not equal reproject the data
    fire_bound_sin = fire_boundary.to_crs(modis_pre_bands.rio.crs)
# Notice this is a box - representing the spatial extent
# of your study area
crop_bound_box = [box(*fire_boundary.total_bounds)]
# fire_bound_sin.crs
    # fire_boundary.crs
    # <Derived Projected CRS: EPSG:3857>
    # Name: WGS 84 / Pseudo-Mercator
    # Axis Info [cartesian]:
    # - X[east]: Easting (metre)
    # - Y[north]: Northing (metre)
    # Area of Use:
    # - name: World between 85.06°S and 85.06°N.
    # - bounds: (-180.0, -85.06, 180.0, 85.06)
    # Coordinate Operation:
    # - name: Popular Visualisation Pseudo-Mercator
    # - method: Popular Visualisation Pseudo Mercator
    # Datum: World Geodetic System 1984 ensemble
    # - Ellipsoid: WGS 84
    # - Prime Meridian: Greenwich

for mod_path in list_of_hdf:
    modis_path = mod_path
    file_name = re.search(r'(?<=h08v04/).*(?=.hdf)', modis_path).group(0)
    newline = file_name.split(".")
    date = newline[1].replace('A', '')
    date = pd.to_datetime(date[:4]) + pd.to_timedelta(int(date[4:]) - 1, unit='D')
    date = str(date.date())
    modis_pre_clip = rxr.open_rasterio(modis_path, masked=True, variable=desired_bands).squeeze()
    modis_NBR = 0.0001*((modis_pre_clip['sur_refl_b05_1'] - modis_pre_clip['sur_refl_b07_1'])/(modis_pre_clip['sur_refl_b05_1'] + modis_pre_clip['sur_refl_b07_1']))
    modis_NDVI = 0.0001*((modis_pre_clip['sur_refl_b05_1'] - modis_pre_clip['sur_refl_b01_1'])/(modis_pre_clip['sur_refl_b05_1'] + modis_pre_clip['sur_refl_b01_1']))
    modis_NDWI = 0.0001*((modis_pre_clip['sur_refl_b03_1'] - modis_pre_clip['sur_refl_b05_1'])/(modis_pre_clip['sur_refl_b03_1'] + modis_pre_clip['sur_refl_b05_1']))
    modis_NBR = modis_NBR.rio.reproject(fire_boundary.crs)
    modis_NDVI = modis_NDVI.rio.reproject(fire_boundary.crs)
    modis_NDWI = modis_NDWI.rio.reproject(fire_boundary.crs)
    modis_NBR_clip = modis_NBR.rio.clip(crop_bound_box, crs=fire_boundary.crs, all_touched=True, from_disk=True)
    modis_NDVI_clip = modis_NDVI.rio.clip(crop_bound_box, crs=fire_boundary.crs, all_touched=True, from_disk=True)
    modis_NDWI_clip = modis_NDWI.rio.clip(crop_bound_box, crs=fire_boundary.crs, all_touched=True, from_disk=True)
    year = date[:4]
    modis_NBR.rio.to_raster(f'../NBR/{year}/NBR_{date}.tif')
    modis_NDVI.rio.to_raster(f'../NDVI/{year}/NDVI_{date}.tif')
    modis_NDWI.rio.to_raster(f'../NDWI/{year}/NDWI_{date}.tif')
    modis_NBR_clip.rio.to_raster(f'../NBR/{year}/NBR_clip_{date}.tif')
    modis_NDVI_clip.rio.to_raster(f'../NDVI/{year}/NDVI_clip_{date}.tif')
    modis_NDWI_clip.rio.to_raster(f'../NDWI/{year}/NDWI_clip_{date}.tif')

#%%
# # Plot band one of the data
# ep.plot_bands(modis_pre_bands.sur_refl_b01_1)
# plt.show()

#%%
# mypath = "../h08v04"
# onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

# files_dict = convert_juliandate(onlyfiles)
# files_dict.to_csv("../files_dict.csv")

# The final clipped data
modis_pre_clip
# %%
modis_ext = plotting_extent(modis_pre_clip.to_array().values[0],
                            modis_pre_clip.rio.transform())
# View cropped data
f, ax = plt.subplots()
ep.plot_bands(modis_pre_clip.to_array().values[0],
              ax=ax,
              extent=modis_ext,
              title="Plot of data clipped to the crop box (extent)")
# fire_bound_sin.plot(ax=ax, color="green")
plt.show()
# %%

modis_pre_clip = rxr.open_rasterio(modis_path, masked=True, variable=desired_bands).rio.clip(crop_bound_box, crs=fire_boundary.crs, all_touched=True, from_disk=True)

# Create a list of titles
titles = ["Red Band", "Near Infrared (NIR) Band", "Blue/Green Band", "Green Band",
          "Near Infrared (NIR) Band", "Mid-infrared Band", "Mid-infrared Band"]

# Plot all bands individually
ep.plot_bands(modis_pre_clip,
              cols=3,
              title=titles,
              figsize=(10, 6))
plt.show()
# %%
# Plot band one of the data
ep.plot_bands(modis_pre_clip['sur_refl_b01_1'])
plt.show()
# %%
ep.plot_bands(modis_pre_clip.to_array().values, figsize= (20, 6))
plt.show()
# %%
ep.plot_bands(modis_pre_bands.to_array().values, figsize= (10, 6))
plt.show()
# %%
# Select the rgb bands only
rgb_bands = ['sur_refl_b01_1',
             'sur_refl_b03_1',
             'sur_refl_b04_1']
# Turn the data into a DataArray
modis_rgb_xr = modis_pre_clip[rgb_bands].to_array().values
modis_rgb_xr = np.squeeze(modis_rgb_xr, axis=(1,))
#%%
# Plot MODIS RGB numpy image array
ep.plot_rgb(modis_rgb_xr,
            rgb=[0, 2, 1],
            title='RGB Image of MODIS Data')