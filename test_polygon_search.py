from cdshealpix import polygon_search
import astropy.units as u
lon = [0, 10, 20] * u.deg
lat = [0, 50, 10] * u.deg

print(lon.to_value(u.rad))
print(lat.to_value(u.rad))
print(polygon_search(lon, lat, 8))