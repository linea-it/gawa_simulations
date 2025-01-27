from ga_sim import (
    make_footprint,
    write_sim_clus_features,
    download_iso,
    gen_clus_file,
    read_error,
    clus_file_results,
    export_results,
    select_ipix,
    sample_ipix_cat,
    estimation_area
)

import numpy as np
import astropy.io.fits as fits
import json
import os
import glob
import parsl
from parsl.app.app import python_app
import condor
import sys
import healpy as hp

# Loading config and files, creating folders
parsl.clear()
parsl.load(condor.get_config('htcondor'))
parsl.set_stream_logger()

confg = "ga_sim.json"

with open(confg) as fstream:
    param = json.load(fstream)

try:
    os.system('rm -r results/hpx*')
    os.system('rm results/ftp/*.fits')
except:
    print('No data to clean.')

os.makedirs(param['results_path'], exist_ok=True)
os.makedirs(param['ftp_path'], exist_ok=True)
os.makedirs(param['hpx_cats_clus_field'], exist_ok=True)
os.makedirs(param['hpx_cats_path'], exist_ok=True)
os.makedirs(param['hpx_cats_clean_path'], exist_ok=True)
os.makedirs(param['hpx_cats_filt_path'], exist_ok=True)

# Downloading isochrone and printing some information
download_iso(param['padova_version_code'], param['survey'], 0.0152 * (10 ** param['MH_simulation']),
             param['age_simulation'], param['av_simulation'], param['file_iso'], 5)

iso_info = np.loadtxt(param['file_iso'], usecols=(1, 2, 3, 26), unpack=True)
FeH_iso = iso_info[0][0]
logAge_iso = iso_info[1][0]
m_ini_iso = iso_info[2]
g_iso = iso_info[3]

print('[Fe/H]={:.2f}, Age={:.2f} Gyr'.format(FeH_iso, 10**(logAge_iso-9)))

mM_mean = (param['mM_max'] + param['mM_min']) / 2.
print(np.max(m_ini_iso[g_iso + mM_mean < param['mmax']]))
mean_mass = (np.min(m_ini_iso[g_iso + mM_mean < param['mmax']]) +
             np.max(m_ini_iso[g_iso + mM_mean < param['mmax']])) / 2.

print('Mean mass (M_sun): {:.2f}'.format(mean_mass))

# Making footprint
make_footprint(param)

area_sampled = estimation_area(param)

# Selecting input files and filtering by magnitude and color ranges and
# correcting for extinction
ipix_files = select_ipix(param['nside_infile'], param['ra_min'], param['ra_max'],
                         param['dec_min'], param['dec_max'], True)

@python_app
def filter_ipix_stars_app(ipix, param):

    from ga_sim import filter_ipix_stars

    aaa = filter_ipix_stars(ipix, param)

    return aaa

res = []

for i in ipix_files:
    res.append(filter_ipix_stars_app(i, param))

outputs = [r.result() for r in res]

print('Total of {:d} pixels read and filtered.'.format(
    int(np.sum(outputs))))

# Expanding catalog depending on the case
print('Area sampled: {:.2f} square degrees'.format(area_sampled))

files_ftp = glob.glob(param['ftp_path'] + '/*.fits')
files_DP0_ftp = glob.glob(param['ftp_infile_path'] + '/' + str(int(param['nside_infile'])) + '/*.fits')

good_DP0_ftp = []

for ii in files_DP0_ftp:
    data = fits.getdata(ii)
    signal = data['SIGNAL']
    cov_fact_ipix = np.sum(signal) * hp.nside2pixarea(param['nside_ftp'], degrees=True) / hp.nside2pixarea(param['nside_infile'], degrees=True)
    if cov_fact_ipix > param['cov_factor']:
        good_DP0_ftp.extend([ii])

ipix_ftp = [i.split('/')[-1] for i in files_ftp]

@python_app
def sample_ipix_cat_app(i, good_DP0_ftp, param):
    from ga_sim import sample_ipix_cat
    aaa = sample_ipix_cat(i, good_DP0_ftp, param)

res2 = []

for i in files_ftp:
    res2.append(sample_ipix_cat_app(i, good_DP0_ftp, param))

outputs = [r.result() for r in res2]

# Generating features of simulated clusters
print('Now generating cluster file.')

RA_pix, DEC_pix, r_exp, ell, pa, dist, mass, mM, hp_sample_un = gen_clus_file(
    param)

# Loading photometric errors
mag1_, err1_, err2_ = read_error(param['file_error'], 0.000, 0.000)

# Simulating stellar clusters.
print('Ready to simulate clusters.')

@python_app
def faker_app(N_stars_cmd, frac_bin, IMF_author, x0, y0, rexp, ell_, pa, dist, hpx, param, mag1_, err1_, err2_, output_path, mag_ref_comp,
              comp_mag_ref,
              comp_mag_max):

    from ga_sim import faker

    faker(N_stars_cmd, frac_bin, IMF_author, x0, y0, rexp, ell_, pa, dist, hpx, param['cmin'], param['cmax'],
          param['mmin'], param['mmax'], mag1_, err1_, err2_, param['file_iso'], output_path, mag_ref_comp,
          comp_mag_ref, comp_mag_max)

fake_clus_path = param['results_path'] + '/fake_clus'

for i in range(len(hp_sample_un)):
    N_stars_cmd = int(mass[i] / mean_mass)

    faker_app(N_stars_cmd, param['frac_bin'], param['IMF_author'], RA_pix[i], DEC_pix[i], r_exp[i], ell[i],
              pa[i], dist[i], hp_sample_un[i], param, mag1_, err1_, err2_, fake_clus_path,
              param['mag_ref_comp'], param['comp_mag_ref'], param['comp_mag_max'])

ipix_ini = glob.glob(param['hpx_cats_path'] + '/*.fits')

results_join = []

@python_app
def join_sim_field_stars_app(ipix, param):

    from ga_sim import join_sim_field_stars

    aaaa = join_sim_field_stars(ipix, param)

    return aaaa


print('Now starting to join simulations and field stars.')

for i in ipix_ini:
    results_join.append(join_sim_field_stars_app(i, param))

outputs = [r.result() for r in results_join]

print('Total of {:d} pixels were joint from clusters and fields.'.format(
    int(np.sum(outputs))))

ipix_cats = glob.glob(param['hpx_cats_clus_field'] + '/*.fits')

print('== LEN IPIX CATS == ', len(ipix_cats))
print('This is the most time consuming part: cleaning the stars from crowding.')

results_from_clear = []

@python_app
def clean_input_cat_dist_app(iiii, param):

    from ga_sim import clean_input_cat_dist

    aaaa = clean_input_cat_dist(param['hpx_cats_clean_path'], iiii, param['ra_str'],
                                param['dec_str'], param['min_dist_arcsec'], 0.01, iiii + '.log')
    return aaaa

for aa in ipix_cats:
    results_from_clear.append(clean_input_cat_dist_app(aa, param))

outputs = [r.result() for r in results_from_clear]

print('Total of {:d} pixels were cleaned from crowding fields.'.format(
    int(np.sum(outputs))))

ipix_clean_cats = [i.replace(
    param['hpx_cats_path'], param['hpx_cats_clean_path']) for i in ipix_cats]

print('Almost done.')

# Solve name of variable
sim_clus_feat = write_sim_clus_features(param, hp_sample_un, mM)

clus_file_results(param['star_clusters_simulated'],
                  sim_clus_feat, param['results_path'] + '/objects.dat')

os.system('jupyter nbconvert --execute --to html --EmbedImagesPreprocessor.embed_images=True plots_sim.ipynb')

export_results(param['export_path'], param['results_path'],
               param['copy_html_path'])
