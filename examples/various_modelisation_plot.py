from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
from pylab import *

file1 = 
'/ccc/scratch/cont005/legos/nivertfl/TEST_VALIDATION_TROPFLUX/MOYENNE-SAISON/grid_T_saison.nc'
file2 = 
'/ccc/scratch/cont005/legos/nivertfl/TEST_VALIDATION_TROPFLUX/MOYENNE-SAISON/grid_U_saison.nc'
file3 = 
'/ccc/scratch/cont005/legos/nivertfl/TEST_VALIDATION_TROPFLUX/MOYENNE-SAISON/grid_V_saison.nc'
file4 = 
'/ccc/scratch/cont005/legos/nivertfl/TEST_VALIDATION_TROPFLUX/MOYENNE-SAISON/MYWRF3D_regrid-saison.nc'

trop1 = 
'/ccc/scratch/cont005/legos/nivertfl/TEST_VALIDATION_TROPFLUX/MOYENNE-SAISON/sst_tropflux_1d_2000-regrid-saison.nc'
trop2 = 
'/ccc/scratch/cont005/legos/nivertfl/TEST_VALIDATION_TROPFLUX/MOYENNE-SAISON/taux_tropflux_1d_2000-regrid-saison.nc'
trop3 = 
'/ccc/scratch/cont005/legos/nivertfl/TEST_VALIDATION_TROPFLUX/MOYENNE-SAISON/tauy_tropflux_1d_2000-regrid-saison.nc'
trop4 = 
'/ccc/scratch/cont005/legos/nivertfl/TEST_VALIDATION_TROPFLUX/MOYENNE-SAISON/swr_tropflux_1d_2000-regrid-saison.nc'
trop5 = 
'/ccc/scratch/cont005/legos/nivertfl/TEST_VALIDATION_TROPFLUX/MOYENNE-SAISON/lwr_tropflux_1d_2000-regrid-saison.nc'

pluie1 = 
'/ccc/scratch/cont005/legos/nivertfl/TEST_VALIDATION_TROPFLUX/MOYENNE-SAISON/precip-2000-regrid-saison.nc'

meshmask = 
'/ccc/scratch/cont005/legos/nivertfl/TEST_VALIDATION_TROPFLUX/MOYENNE-SAISON/mesh_mask.nc'

mask = Dataset(file1, mode='r')
masku = Dataset(file2, mode='r')
maskv = Dataset(file3, mode='r')
wrf = Dataset(file4, mode='r')
pluie = Dataset(pluie1, mode='r')
meshmask1 = Dataset(meshmask, mode='r')

tropsst= Dataset(trop1, mode='r')
troptaux= Dataset(trop2, mode='r')
troptauy= Dataset(trop3, mode='r')
tropswr= Dataset(trop4, mode='r')
troplwr= Dataset(trop5, mode='r')

lat = mask.variables['nav_lat'][:]
lon = mask.variables['nav_lon'][:]
lat1 = mask.variables['nav_lat'][:,0]

meshmask2 = meshmask1.variables['tmask'][:,0,:,:]

mask1 = mask.variables['votemper'][:,0,:,:]
mask11 = tropsst.variables['sst'][:,:,:]

vari2 = mask.variables['qsr'][:,:,:]
vari22 = tropswr.variables['swr'][:,:,:]

vari31 = wrf.variables['RAIN'][:,:,:]
vari3 = vari31[:,:,:] * 40 * 24
vari33 = pluie.variables['precipitation'][:,:,:]

vari4 = masku.variables['utau'][:,:,:]
vari44 = troptaux.variables['taux'][:,:,:]

vari51 = wrf.variables['GLW'][:,:,:]
vari5 = vari51[:,:,:] * meshmask2[:,:,:]
vari555 = troplwr.variables['lwr'][:,:,:]
mask112 = mask11[:,:,:] + 273.15
vari55 = vari555[:,:,:] + 
5.67e-8*(mask112[:,:,:])*(mask112[:,:,:])*(mask112[:,:,:])*(mask112[:,:,:])


vari6 = maskv.variables['vtau'][:,:,:]
vari6[vari6 == 0] = np.NaN
vari66 = troptauy.variables['tauy'][:,:,:]

list1 = ['JFM' , 'AMJ' , 'JAS' , 'OND']



'''Difference modele'''
for x in range(0,4):
    print "We're on time %d" % (x)
    plt.clf()
    result1 = mask1[x,:,:] - mask11[x,:,:]
    result2 = vari2[x,:,:] - vari22[x,:,:]
    result3 = vari3[x,:,:] - vari33[x,:,:]
    result4 = vari4[x,:,:] - vari44[x,:,:]
    result5 = vari5[x,:,:] - vari55[x,:,:]
    result6 = vari6[x,:,:] - vari66[x,:,:]
    fig, cs = plt.subplots(3, 2, figsize=(9, 6))
    fig.subplots_adjust(left=0.125, bottom=0.1, right=0.9, top=0.9, 
wspace=0.3, hspace=0.3)
    im1 = cs[0, 0].contourf(lon,lat,result1, np.linspace(-2.5,2.5,21), 
extend='both', cmap=cm.RdBu_r)
    cs[0, 0].set_title('Difference VOTEMPER MODELE - OBS  Saison ' + 
list1[x],fontsize=10)
    fig.colorbar(im1, ax=cs[0, 0], orientation='horizontal')
    im2 = cs[0, 1].contourf(lon,lat,result2, np.linspace(-100,100,21), 
extend='both', cmap=cm.RdBu_r)
    cs[0, 1].set_title('Difference QSR MODELE - OBS  Saison ' + 
list1[x],fontsize=10)
    fig.colorbar(im2, ax=cs[0, 1], orientation='horizontal')
    im3 = cs[1, 0].contourf(lon,lat,result3, np.linspace(-16,16,21), 
extend='both', cmap=cm.RdBu_r)
    cs[1, 0].set_title('Difference PRECIP MODELE - OBS  Saison ' + 
list1[x],fontsize=10)
    fig.colorbar(im3, ax=cs[1, 0], orientation='horizontal')
    im4 = cs[1, 1].contourf(lon,lat,result4, np.linspace(-0.1,0.1,21), 
extend='both', cmap=cm.RdBu_r)
    cs[1, 1].set_title('Difference U TAU MODELE - OBS  Saison ' + 
list1[x],fontsize=10)
    fig.colorbar(im4, ax=cs[1, 1], orientation='horizontal', format='%.0e')
    im5 = cs[2, 0].contourf(lon,lat,result5, np.linspace(-50,50,21), 
extend='both', cmap=cm.RdBu_r)
    cs[2, 0].set_title('Difference LW MODELE - OBS  Saison ' + 
list1[x],fontsize=10)
    fig.colorbar(im5, ax=cs[2, 0], orientation='horizontal')
    im6 = cs[2, 1].contourf(lon,lat,result6, np.linspace(-0.1,0.1,21), 
extend='both', cmap=cm.RdBu_r)
    cs[2, 1].set_title('Difference V TAU MODELE - OBS  Saison ' + 
list1[x],fontsize=10)
    fig.colorbar(im6, ax=cs[2, 1], orientation='horizontal')
    plt.savefig('all_var_diff_saison_' + list1[x] + '.png')

'''plot modele'''
for x in range(0,4):
    print "We're on time %d" % (x)
    plt.clf()
    result1 = mask1[x,:,:]
    result2 = vari2[x,:,:]
    result3 = vari3[x,:,:]
    result4 = vari4[x,:,:]
    result5 = vari5[x,:,:]
    result6 = vari6[x,:,:]
    fig, cs = plt.subplots(3, 2, figsize=(9, 6))
    fig.subplots_adjust(left=0.125, bottom=0.1, right=0.9, top=0.9, 
wspace=0.3, hspace=0.3)
    im1 = cs[0, 0].contourf(lon,lat,result1, np.linspace(20,30,21), 
extend='both', cmap=cm.jet)
    cs[0, 0].set_title('VOTEMPER MODELE Saison ' + list1[x],fontsize=10)
    fig.colorbar(im1, ax=cs[0, 0], orientation='horizontal')
    im2 = cs[0, 1].contourf(lon,lat,result2, np.linspace(100,380,15), 
extend='both', cmap=cm.jet)
    cs[0, 1].set_title('QSR MODELE Saison ' + list1[x],fontsize=10)
    fig.colorbar(im2, ax=cs[0, 1], orientation='horizontal')
    im3 = cs[1, 0].contourf(lon,lat,result3, np.linspace(0,20,21), 
extend='both', cmap=cm.jet)
    cs[1, 0].set_title('PRECIP MODELE Saison ' + list1[x],fontsize=10)
    fig.colorbar(im3, ax=cs[1, 0], orientation='horizontal')
    im4 = cs[1, 1].contourf(lon,lat,result4, 
np.linspace(-0.13,0.05,21), extend='both', cmap=cm.jet)
    cs[1, 1].set_title('U TAU MODELE Saison ' + list1[x],fontsize=10)
    fig.colorbar(im4, ax=cs[1, 1], orientation='horizontal', format='%.0e')
    im5 = cs[2, 0].contourf(lon,lat,result5, np.linspace(300,460,21), 
extend='both', cmap=cm.jet)
    cs[2, 0].set_title('GLW MODELE Saison ' + list1[x],fontsize=10)
    fig.colorbar(im5, ax=cs[2, 0], orientation='horizontal')
    im6 = cs[2, 1].contourf(lon,lat,result6, 
np.linspace(-0.15,0.13,21), extend='both', cmap=cm.jet)
    cs[2, 1].set_title('V TAU MODELE Saison ' + list1[x],fontsize=10)
    fig.colorbar(im6, ax=cs[2, 1], orientation='horizontal')
    plt.savefig('all_var_modele_saison_' + list1[x] + '.png')

'''plot obs Trop et TRMM'''
for x in range(0,4):
    print "We're on time %d" % (x)
    plt.clf()
    result1 = mask11[x,:,:]
    result2 = vari22[x,:,:]
    result3 = vari33[x,:,:]
    result4 = vari44[x,:,:]
    result5 = vari55[x,:,:]
    result6 = vari66[x,:,:]
    fig, cs = plt.subplots(3, 2, figsize=(9, 6))
    fig.subplots_adjust(left=0.125, bottom=0.1, right=0.9, top=0.9, 
wspace=0.3, hspace=0.3)
    im1 = cs[0, 0].contourf(lon,lat,result1, np.linspace(20,30,21), 
extend='both', cmap=cm.jet)
    cs[0, 0].set_title('VOTEMPER OBS  Saison ' + list1[x],fontsize=10)
    fig.colorbar(im1, ax=cs[0, 0], orientation='horizontal')
    im2 = cs[0, 1].contourf(lon,lat,result2, np.linspace(100,380,15), 
extend='both', cmap=cm.jet)
    cs[0, 1].set_title('QSR OBS  Saison ' + list1[x],fontsize=10)
    fig.colorbar(im2, ax=cs[0, 1], orientation='horizontal')
    im3 = cs[1, 0].contourf(lon,lat,result3, np.linspace(0,20,21), 
extend='both', cmap=cm.jet)
    cs[1, 0].set_title('PRECIP OBS  Saison ' + list1[x],fontsize=10)
    fig.colorbar(im3, ax=cs[1, 0], orientation='horizontal')
    im4 = cs[1, 1].contourf(lon,lat,result4, 
np.linspace(-0.13,0.05,21), extend='both', cmap=cm.jet)
    cs[1, 1].set_title('U TAU OBS  Saison ' + list1[x],fontsize=10)
    fig.colorbar(im4, ax=cs[1, 1], orientation='horizontal', format='%.0e')
    im5 = cs[2, 0].contourf(lon,lat,result5, np.linspace(300,460,21), 
extend='both', cmap=cm.jet)
    cs[2, 0].set_title('LW OBS  Saison ' + list1[x],fontsize=10)
    fig.colorbar(im5, ax=cs[2, 0], orientation='horizontal')
    im6 = cs[2, 1].contourf(lon,lat,result6, 
np.linspace(-0.15,0.13,21), extend='both', cmap=cm.jet)
    cs[2, 1].set_title('V TAU OBS  Saison ' + list1[x],fontsize=10)
    fig.colorbar(im6, ax=cs[2, 1], orientation='horizontal')
    plt.savefig('all_var_obs_saison_' + list1[x] + '.png')


zbla=np.zeros(shape=(165,1))
zbla2=np.zeros(shape=(165,1))
zbla3=np.zeros(shape=(165,1))
zbla4=np.zeros(shape=(165,1))
zbla5=np.zeros(shape=(165,1))
zbla6=np.zeros(shape=(165,1))
zbla7=np.zeros(shape=(165,1))
zbla8=np.zeros(shape=(165,1))
zbla9=np.zeros(shape=(165,1))
zbla10=np.zeros(shape=(165,1))
zbla11=np.zeros(shape=(165,1))
zbla12=np.zeros(shape=(165,1))

mask1[mask1 == 0] = np.NaN
vari2[vari2 == 0] = np.NaN
vari4[vari4 == 0] = np.NaN
vari5[vari5 == 0] = np.NaN

'''Coupe zonale'''
for y in range(0,4):
    print "We're on time %d" % (y)
    for x in range(0,165):
        result1= np.nanmean(mask1[y,x,80:160])
        result2= np.nanmean(mask11[y,x,80:160])
        zbla[x,:]=result1
        zbla2[x,:]=result2

    for z in range(0,165):
        result3= np.nanmean(vari2[y,z,80:160])
        result4= np.nanmean(vari22[y,z,80:160])
        zbla3[z,:]=result3
        zbla4[z,:]=result4

    for ii in range(0,165):
        result5= np.nanmean(vari3[y,ii,80:160])
        result6= np.nanmean(vari33[y,ii,80:160])
        zbla5[ii,:]=result5
        zbla6[ii,:]=result6

    for jj in range(0,165):
        result7= np.nanmean(vari4[y,jj,80:160])
        result8= np.nanmean(vari44[y,jj,80:160])
        zbla7[jj,:]=result7
        zbla8[jj,:]=result8

    for zz in range(0,165):
        result9= np.nanmean(vari5[y,zz,80:160])
        result10= np.nanmean(vari55[y,zz,80:160])
        zbla9[zz,:]=result9
        zbla10[zz,:]=result10

    for hh in range(0,165):
        result11= np.nanmean(vari6[y,hh,80:160])
        result12= np.nanmean(vari66[y,hh,80:160])
        zbla11[hh,:]=result11
        zbla12[hh,:]=result12

    fig, cs = plt.subplots(3, 2, figsize=(9, 6))
    fig.subplots_adjust(left=0.125, bottom=0.1, right=0.9, top=0.9, 
wspace=0.3, hspace=0.3)
    im1 = cs[0, 0].plot(lat1,zbla)
    im1 = cs[0, 0].plot(lat1,zbla2)
    cs[0, 0].set_title('Comparaison SST MODELE et OBS  Saison ' + 
list1[y],fontsize=10)
    cs[0, 0].set_ylim([18,30])
    cs[0, 0].set_xlim([-20,20])
    im2 = cs[0, 1].plot(lat1,zbla3)
    im2 = cs[0, 1].plot(lat1,zbla4)
    cs[0, 1].set_title('Comparaison QSR MODELE et OBS  Saison ' + 
list1[y],fontsize=10)
    cs[0, 1].set_ylim([100,380])
    cs[0, 1].set_xlim([-20,20])
    im3 = cs[1, 0].plot(lat1,zbla5)
    im3 = cs[1, 0].plot(lat1,zbla6)
    cs[1, 0].set_title('Comparaison PRECIP MODELE et OBS  Saison ' + 
list1[y],fontsize=10)
    cs[1, 0].set_ylim([0, 20])
    cs[1, 0].set_xlim([-20,20])
    im4 = cs[1, 1].plot(lat1,zbla7)
    im4 = cs[1, 1].plot(lat1,zbla8)
    cs[1, 1].set_title('Comparaison U TAU MODELE et OBS  Saison ' + 
list1[y],fontsize=10)
    cs[1, 1].set_ylim([-0.13,0.05])
    cs[1, 1].set_xlim([-20,20])
    im5 = cs[2, 0].plot(lat1,zbla9)
    im5 = cs[2, 0].plot(lat1,zbla10)
    cs[2, 0].set_title('Comparaison LW MODELE et OBS  Saison ' + 
list1[y],fontsize=10)
    cs[2, 0].set_ylim([300,430])
    cs[2, 0].set_xlim([-20,20])
    im6 = cs[2, 1].plot(lat1,zbla11)
    im6 = cs[2, 1].plot(lat1,zbla12)
    cs[2, 1].set_title('Comparaison V TAU MODELE et OBS  Saison ' + 
list1[y],fontsize=10)
    cs[2, 1].set_ylim([-0.15,0.13])
    cs[2, 1].set_xlim([-20,20])
    plt.savefig('coupe_zonale_saison_' + list1[y] + '.png')
