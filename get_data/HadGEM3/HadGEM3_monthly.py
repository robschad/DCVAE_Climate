# Functions to load HadGEM3 monthly data

import os
import iris
import iris.util
import iris.coord_systems
import numpy as np
import cube_helper as ch
import glob
import iris.coord_categorisation
import cf_units as unit
from iris.time import PartialDateTime

def guesslatlonbounds(cube):

    cube.coord('longitude').circular = True

    cs = iris.coord_systems.GeogCS(6371229)
    for coord in ['latitude','longitude']:
        if cube.coord(coord).bounds is None:
            cube.coord(coord).guess_bounds()
        if cube.coord(coord).coord_system is None:
            cube.coord(coord).coord_system = cs

    return cube

def precip_to_mmpday(cube):
    if (cube.units == unit.Unit('kg m-2 s-1')):
        rho = iris.coords.AuxCoord(1000.0, long_name='ref density', units='kg m-3')
        outcube = cube / rho
        outcube.convert_units('mm day-1')
        outcube.standard_name = cube.standard_name
    if (cube.units == unit.Unit('m s-1')):
        outcube = cube
        outcube.convert_units('mm day-1')
        outcube.standard_name = cube.standard_name
    if (cube.units == unit.Unit('mm day-1')):
        outcube = cube
    if (cube.units != unit.Unit('kg m-2 s-1') and cube.units != unit.Unit('mm day-1') and cube.units != unit.Unit(
            'm s-1')):
        raise ValueError('cube not in mm/day, kg/m2/s or m/s ', cube.units)
    return outcube

# Don't really understand this, but it gets rid of the error messages.
iris.FUTURE.datum_support = True

# ERA5 data does not have explicit coodinate systems
# Specify one to add on load so the cubes work properly with iris.
#cs_ERA5 = iris.coord_systems.RotatedGeogCS(90, 180, 0)

# And a function to add the coord system to a cube (in-place)
#def add_coord_system(cbe):
#    cbe.coord("latitude").coord_system = cs_ERA5
#    cbe.coord("longitude").coord_system = cs_ERA5

def load(
    variable="pr", year=None, month=None, constraint=None, grid=None
):
    if variable == "land_mask":
        filename = "/data/users/hadrk/VAE-HG3/data/sftlf*"
        varC = ch.load(filename)
        # Get rid of unnecessary height dimensions
        if len(varC.data.shape) == 3:
            varC = varC.extract(iris.Constraint(expver=1))
        #add_coord_system(varC)
        varC= guesslatlonbounds(varC)

        #varC.long_name = variable
        if grid is not None:
            varC = varC.regrid(grid, iris.analysis.Nearest())
            if constraint is not None:
                varC = varC.extract(constraint)        
        varC.data.data[np.where(varC.data >= 50.0)] = 0
        varC.data.data[np.where(varC.data < 50.0)] = 1
        return varC

    if year is None or month is None:
        raise Exception("Year and month must be specified")

    filenames = glob.glob("/data/users/hadrk/VAE-HG3/data/%s*" % (
        variable,
    ))
    if not os.path.isfile(filenames[0]):
        raise Exception("No data file %s" % filenames[0])

    cube = ch.load(filenames)
    varC = cube.extract(iris.Constraint(time=lambda cell: cell.point == PartialDateTime(year=year, month=month)))
    #iris.coord_categorisation.add_year(cube, 'time', name='year')
    #iris.coord_categorisation.add_month(cube, 'time', name='month')
    #monthcon = iris.Constraint(time=lambda cell: cell.point.month == month)
    #yearcon = iris.Constraint(time=lambda cell: cell.point.year == year)
    #varC = cube.extract(monthcon & yearcon)
    if variable == 'pr':
        varC = precip_to_mmpday(varC)

    # Get rid of unnecessary height dimensions
    if len(varC.data.shape) == 3:
        varC = varC.extract(iris.Constraint(expver=1))
    #add_coord_system(varC)
    varC= guesslatlonbounds(varC)

    #varC.long_name = variable
    if grid is not None:
        varC = varC.regrid(grid, iris.analysis.Nearest())
    if constraint is not None:
        varC = varC.extract(constraint)
    return varC


