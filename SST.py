import streamlit as st
from numpy import roll

from misc import getsstobs, plotmap, getpsst, getsstclim

st.sidebar.header('SST ANOMALY - T42')

my_bar = st.sidebar.progress(0)

# st.sidebar.subheader('CLIMATOLOGIAS')

clim = st.sidebar.radio(
    'CLIMATOLOGY:',
    ('1989-2008', '1981-2010', '1991-2020'),
    index=2
)

# get obs e clim
anom_year = str(st.sidebar.selectbox('ANOM. YEAR:', range(2020, 2010, -1), index=0))
anom_mon = st.sidebar.selectbox('ANOM. MONTH:', list(range(1, 13)), index=0)
sst_obs, lat, lon = getsstobs(anom_year, anom_mon)
sst_clim, lat, lon = getsstclim(clim, anom_mon)

# compute anom
sst_anom = sst_obs - sst_clim

my_bar.progress(25)

# plot nom
fig_title = f'ANOM {anom_year}/{anom_mon:02d} ({clim})'
st.write(plotmap(sst_anom, lon, lat, fig_title, pal='anom'))

my_bar.progress(50)

# get psst
nc_list = []

for y in range(2020, 2010, -1):
    nc_list.append(f'obs.sst.{y}.nc')

nc_check = st.sidebar.selectbox('NC CHECK:', nc_list, index=0)

nc_mon = st.sidebar.slider('NC TIME:', 1, 12)

psst, lat, lon = getpsst(nc_check, nc_mon)

psst_clim, lat, lon = getsstclim(clim, nc_mon)

my_bar.progress(75)

fig_title = f'(CLIM {clim} MON {nc_mon:02d}) minus (SST ANOM {anom_year}/{anom_mon:02d})'

st.write(plotmap(psst - psst_clim - sst_anom, lon, lat, fig_title, pal='diff'))

my_bar.progress(100)














# r = 0

# sst_anom = roll(sst_anom, r, axis=1)

# sst_obs = roll(sst_obs, r, axis=1)

# sst_clim = roll(sst_clim, r, axis=1)

# fig_title = f'ANOMALY - {year}/{mon:02d} - CLIM {clim} - T42 GRID RESOL.'

# fig_title = 'PSST'
# st.write(plotmap(psst - 273.15, lon, lat, fig_title, pal='jet'))

# fig_title = f'OBSERVED SST  - {year}/{mon:02d} - T42 GRID RESOL.'
# st.write(plotmap(sst_obs, lon, lat, fig_title))

# fig_title = f'CLIMATOLOGY SST  - CLIM {clim} - T42 GRID RESOL.'
# st.write(plotmap(sst_clim, lon, lat, fig_title))

# st.write(plotmap(sst_obs))

# st.write(plotmap(sst_clim))

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
