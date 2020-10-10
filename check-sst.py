import matplotlib as mpl
import streamlit as st
import xarray as xr
import cartopy as cart
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from cartopy.util import add_cyclic_point

sst_obs_t42 = 'SST.ER.LAND.50-81.and.OIV2.82-0820.T42.nc'

st.sidebar.subheader('CLIMATOLOGIA')

idate = str(st.sidebar.selectbox('Ano inicial:', list(range(1981, 2020)), index=0))
fdate = str(st.sidebar.selectbox('Ano final:', list(range(1981, 2020)), index=29))
# mon = st.sidebar.selectbox('Mês:', list(range(1, 13)), index=0)
mon = st.sidebar.slider('Mês:', 1, 12)

def is_mon(month, n: int):
    """
    Se n = 1, seleciona somente os jan do período
    Se n = 2, seleciona somente os fev do período
    Se n = 12, seleciona somente os dez do período
    """
    return (month == n)


with xr.open_dataset(sst_obs_t42) as dset:

    # lon 0:360 -> -180:180

    # https://stackoverflow.com/a/53471670

    dset['_longitude'] = xr.where(dset['longitude'] > 180,
                                  dset['longitude'] - 360,
                                  dset['longitude'])

    dset = (
        dset
        .swap_dims({'longitude': '_longitude'})
        .sel(**{'_longitude': sorted(dset._longitude)})
        .drop('longitude')
    )

    dset = dset.rename({'_longitude': 'longitude'})

    # st.info(dset)

    sst = dset.sst \
        .sel(time=is_mon(dset.sst['time.month'], mon)) \
        .sel(time=slice(idate, fdate)).mean(dim='time')

    fig_map = plt.figure(figsize=(7, 7))

    proj = cart.crs.PlateCarree(central_longitude=-160)

    ax = plt.axes(projection=proj)

    # add cyclic point lon

    lat = sst.coords['latitude'].values

    lon = sst.coords['longitude']

    lon_idx = sst.dims.index('longitude')

    sst, lon = add_cyclic_point(
        sst.values, coord=lon, axis=lon_idx
    )

    # ax.set_extent([-400, 20, -88, 88], proj)

    img = ax.contourf(
        lon,
        lat,
        sst,
        cmap=mpl.cm.get_cmap('jet'),
        norm=None,
        transform=proj
    )

    ax.add_feature(
        cart.feature.LAND,
        zorder=50,
        edgecolor='k',
        facecolor='#D3D3D3'
    )

    bar = fig_map.colorbar(
                img,
                pad=0.02,
                spacing='uniform',
                orientation='horizontal',
                ax=ax,
                extendfrac='auto'
            )

    st.write(fig_map)


# print(r)

# fig_map = plt.figure(figsize=(12, 8))
# ax_map = fig_map.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
# ax_map.set_global()
# if st.checkbox('land'): ax_map.add_feature(cfeature.LAND)
# if st.checkbox('ocean'): ax_map.add_feature(cfeature.OCEAN)
# if st.checkbox('coastline'): ax_map.add_feature(cfeature.COASTLINE)
# if st.checkbox('borders'): ax_map.add_feature(cfeature.BORDERS, linestyle=':')
# if st.checkbox('lakes'): ax_map.add_feature(cfeature.LAKES, alpha=0.5)
# if st.checkbox('rivers'): ax_map.add_feature(cfeature.RIVERS)
# st.write(fig_map)

#