# -*- coding: utf-8 -*-
import astropy.io.fits as fits
import healpy as hp
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from astropy.io.fits import getdata
from pathlib import Path
from ga_sim.ga_sim import radec2GCdist
mpl.rcParams["legend.numpoints"] = 1
from matplotlib.colors import LogNorm
import glob

def read_final_cat(param):

    globals().update(param)

    ipix_files = glob.glob(hpx_cats_clean_path + '/*.fits')

    RA_, DEC_, MAG_G_, MAGERR_G_, MAG_R_, MAGERR_R_, GC_ = [], [], [], [], [], [], []

    for i in ipix_files:
        filepath = Path(hpx_cats_clean_path, "%s" % i)
        data = getdata(filepath)
        RA = data['ra']
        DEC = data['dec']
        MAG_G = data['mag_g_with_err']
        MAGERR_G = data['magerr_g']
        MAG_R = data['mag_r_with_err']
        MAGERR_R = data['magerr_r']
        GC = data['GC']

        RA_.append(RA)
        DEC_.append(DEC)
        MAG_G_.append(MAG_G)
        MAG_R_.append(MAG_R)
        MAGERR_G_.append(MAGERR_G)
        MAGERR_R_.append(MAGERR_R)
        GC_.append(GC)

    return RA_, DEC_, MAG_G_, MAGERR_G_, MAG_R_, MAGERR_R_, GC_


def plot_cmd_clean(ipix_clean_cats, mmin, mmax, cmin, cmax, magg_str, magr_str, GC_str, output_dir):

    tot_clus = len(ipix_clean_cats)
    
    j = 0; n_bins=100
    cmap = plt.cm.inferno    

    for i in range(tot_clus): #len_ipix):
    
        # ax[0, 1].set_yticks([])
        # ax[0, 2].set_yticks([])

        ipix = (ipix_clean_cats[i].split('/')[-1]).split('.')[0]

        data = fits.getdata(ipix_clean_cats[i])
        GC = data[GC_str]
        magg = data[magg_str]
        magr = data[magr_str]

        f, ((ax1, ax2, ax3)) = plt.subplots(1, 3, figsize=(12, 6), dpi=150)
        
        H, xedges, yedges = np.histogram2d(magg-magr, magg, bins=n_bins, range=[[cmin, cmax], [mmin, mmax]])
        ax1.set_title('CMD Ipix {}'.format(ipix))
        ax1.set_xlim([cmin, cmax])
        ax1.set_ylim([mmax, mmin])
        ax1.set_xlabel('g - r')
        ax1.set_ylabel('g')
        ax1.grid(True, lw=0.2)
        im1 = ax1.imshow(H.T, extent=[cmin, cmax, mmax, mmin], aspect='auto', interpolation='None',
                         cmap=cmap, norm=LogNorm())
        cbaxes = f.add_axes([0.355, 0.126, 0.01, 0.750])
        cbar = f.colorbar(im1, cax=cbaxes, cmap=cmap, orientation='vertical')

        bkg = (GC == 0)
        H, xedges, yedges = np.histogram2d(magg[bkg]-magr[bkg], magg[bkg], bins=n_bins, range=[[cmin, cmax], [mmin, mmax]])
        ax2.set_title('CMD Ipix {} Bkg stars'.format(ipix))
        ax2.set_xlim([cmin, cmax])
        ax2.set_ylim([mmax, mmin])
        ax2.set_xlabel('g - r')
        ax2.set_yticks([])
        ax2.grid(True, lw=0.2)
        im2 = ax2.imshow(H.T, extent=[cmin, cmax, mmax, mmin], aspect='auto', interpolation='None',
                         cmap=cmap, norm=LogNorm())
        cbaxes = f.add_axes([0.6275, 0.126, 0.01, 0.750])
        cbar = f.colorbar(im2, cax=cbaxes, cmap=cmap, orientation='vertical')


        cls = (GC == 1)
        H, xedges, yedges = np.histogram2d(magg[cls]-magr[cls], magg[cls], bins=n_bins, range=[[cmin, cmax], [mmin, mmax]])
        ax3.set_title('CMD Ipix {} Cluster stars'.format(ipix))
        ax3.set_xlim([cmin, cmax])
        ax3.set_ylim([mmax, mmin])
        ax3.set_yticks([])
        ax3.set_xlabel('g - r')
        ax3.grid(True, lw=0.2)
        im3 = ax3.imshow(H.T, extent=[cmin, cmax, mmax, mmin], aspect='auto', interpolation='None',
                         cmap=cmap)

        cbaxes = f.add_axes([0.90, 0.126, 0.01, 0.750])
        cbar = f.colorbar(im3, cax=cbaxes, cmap=cmap, orientation='vertical')
        #cbar.ax1.set_xticklabels(np.linspace(0., np.max(H), 5),rotation=0)
        # plt.tight_layout()
        plt.subplots_adjust(wspace=0.2)
        plt.show()


    #plt.savefig(output_dir + '/CMD_ipix.png')
    #plt.show()
    #plt.close()


def read_real_cat(cat_DG = "catalogs/objects_in_ref.dat", cat_GC = "catalogs/Harris_updated.dat"):

    ra_DG, dec_DG, dist_kpc_DG, Mv_DG, rhl_pc_DG, FeH_DG = np.loadtxt(
        cat_DG, usecols=(0, 1, 4, 8, 10, 11), unpack=True
    )

    name_DG = np.loadtxt(
        cat_DG, dtype=str, usecols=(2), unpack=True
    )

    #  Catalogo Harris_updated.dat
    # 0-Name 1-L 2-B 3-R_gc	4-Fe/H 5-M-M 6-Mv 7-rhl arcmin
    R_MW_GC, FeH_GC, mM_GC, Mv_GC, rhl_arcmin_GC = np.loadtxt(
        cat_GC, usecols=(3, 4, 5, 6, 7), unpack=True
    )
    
    dist_kpc_GC = 10 ** ((mM_GC / 5) - 2)
    
    rhl_pc_GC = 1000 * dist_kpc_GC * np.tan(rhl_arcmin_GC / (60 * 180 / np.pi))
    
    name_GC = np.loadtxt(
        cat_GC, dtype=str, usecols=(0), unpack=True
    )
    return name_DG, ra_DG, dec_DG, dist_kpc_DG, Mv_DG, rhl_pc_DG, FeH_DG, name_GC, R_MW_GC, FeH_GC, mM_GC, Mv_GC, rhl_pc_GC, dist_kpc_GC, rhl_arcmin_GC


def plot_clusters_clean(ipix_cats, ipix_clean_cats, nside, ra_str, dec_str, half_size_plot, output_dir, st_line_arcsec=10.):
    """_summary_

    Parameters
    ----------
    ipix_cats : list
        List of catalogs with all stars.
    ipix_clean_cats : list
        List of catalogs with stars filtered.
    nside : int
        Nside of pixelizations.
    half_size_plot : float, optional
        Size to be seen on plots. Usually twice the angular size of exponential
        profiles of clusters. Units: degrees.
    output_dir : str
        Folder where the plots will be saved.
    st_line_arcsec : float
        Size of a ruler shown in the plots. Unit: arcsec

    """
    len_ipix = len(ipix_clean_cats)

    ipix = [int((i.split('/')[-1]).split('.')[0]) for i in ipix_cats]

    ra_cen, dec_cen = hp.pix2ang(nside, ipix, nest=True, lonlat=True)

    tot_clus = len(ipix)
    '''
    tot_clus = 0
    for i in range(len_ipix):
        data = fits.getdata(ipix_cats[i])
        RA_orig = data[ra_str]
        DEC_orig = data[dec_str]
        half_size_plot_dec = half_size_plot
        half_size_plot_ra = half_size_plot / np.cos(np.deg2rad(dec_cen[i]))

        if len(RA_orig[(RA_orig < ra_cen[i] + half_size_plot_ra) & (RA_orig > ra_cen[i] - half_size_plot_ra) &
                       (DEC_orig < dec_cen[i] + half_size_plot_dec) & (DEC_orig > dec_cen[i] - half_size_plot_dec)]) > 10.:
            tot_clus += 1
    '''

    for i in range(len_ipix):
        
        data = fits.getdata(ipix_cats[i])
        RA_orig = data[ra_str]
        DEC_orig = data[dec_str]
        GC_orig = data['GC']
        
        half_size_plot_dec = half_size_plot
        half_size_plot_ra = half_size_plot / np.cos(np.deg2rad(dec_cen[i]))

        if len(RA_orig[(RA_orig < ra_cen[i] + half_size_plot_ra) & (RA_orig > ra_cen[i] - half_size_plot_ra) &
                       (DEC_orig < dec_cen[i] + half_size_plot_dec) & (DEC_orig > dec_cen[i] - half_size_plot_dec)]) > 10.:
            
            fig, ax = plt.subplots(1, 3, figsize=(18, 6), dpi=150)
  
            ax[1].set_yticks([])
            ax[2].set_yticks([])

            data = fits.getdata(ipix_clean_cats[i])
            RA = data[ra_str]
            DEC = data[dec_str]
            GC = data['GC']
            col = 0
            ax[col].scatter(
                RA_orig[(GC_orig == 0)], DEC_orig[(GC_orig == 0)], edgecolor='b', color='None', s=20, label='MW stars')
            ax[col].scatter(
                RA_orig[(GC_orig == 1)], DEC_orig[(GC_orig == 1)], edgecolor='k', color='None', s=20, label='Cl stars')
            ax[col].set_xlim(
                [ra_cen[i] + half_size_plot_ra, ra_cen[i] - half_size_plot_ra])
            ax[col].set_ylim(
                [dec_cen[i] - half_size_plot_dec, dec_cen[i] + half_size_plot_dec])
            ax[col].set_title('Ipix {:d} before filter'.format(ipix[i]), y= 0.9, pad=8, backgroundcolor='w') #{x=ra_cen[i], y=dec_cen[i], pad=8)
            ax[col].legend(loc=3)
            ax[col].scatter(
                ra_cen[i], dec_cen[i], color='k', s=100, marker='+', label='Cluster center')
            ax[col].set_xlabel('RA (deg)')
            ax[col].set_ylabel('DEC (deg)')

            col = 1
            ax[col].scatter(RA[GC == 0], DEC[GC == 0], edgecolor='b', color='None', s=20, label='Filt MW stars')
            ax[col].scatter(RA[GC == 1], DEC[GC == 1], edgecolor='k', color='None', s=20, label='Filt cl stars')
            ax[col].set_xlim(
                [ra_cen[i] + half_size_plot_ra, ra_cen[i] - half_size_plot_ra])
            ax[col].set_ylim(
                [dec_cen[i] - half_size_plot_dec, dec_cen[i] + half_size_plot_dec])
            ax[col].set_title('Ipix {:d} after filter'.format(ipix[i]), y= 0.9, pad=8, backgroundcolor='w') #{x=ra_cen[i], y=dec_cen[i], pad=8)
            ax[col].legend(loc=3)
            ax[col].scatter(
                ra_cen[i], dec_cen[i], color='k', s=100, marker='+', label='Cluster center')
            ax[col].text(
                ra_cen[i] - half_size_plot_ra + 2. * st_line_arcsec / (np.cos(np.deg2rad(dec_cen[i]))*3600), dec_cen[i] - 0.96 * half_size_plot_dec, '{:d} arcsec'.format(int(st_line_arcsec)), fontsize=8.)
            ax[col].set_xlabel('RA (deg)')
            ax[col].plot(
                [ra_cen[i] - half_size_plot_ra + st_line_arcsec / (np.cos(np.deg2rad(dec_cen[i]))*3600),
                 ra_cen[i] - half_size_plot_ra + 2. * st_line_arcsec / (np.cos(np.deg2rad(dec_cen[i]))*3600)],
                [dec_cen[i] - 0.9 * half_size_plot_dec, dec_cen[i] - 0.9 * half_size_plot_dec], color='k', lw=1)
            
            col = 2
            ax[col].set_xlabel('RA (deg)')
            ax[col].scatter(
                RA_orig[GC_orig == 0], DEC_orig[GC_orig == 0], edgecolor='b', color='None', s=20, label='MW stars')
            ax[col].scatter(
                RA_orig[GC_orig == 1], DEC_orig[GC_orig == 1], edgecolor='k', color='None', s=20, label='Cl stars')
            ax[col].set_xlim(
                [ra_cen[i] + half_size_plot, ra_cen[i] - half_size_plot])
            ax[col].set_ylim(
                [dec_cen[i] - half_size_plot, dec_cen[i] + half_size_plot])
            ax[col].scatter(RA, DEC, color='r', s=2, label='Filt stars (MW+cl)')
            ax[col].set_xlim(
                [ra_cen[i] + half_size_plot_ra, ra_cen[i] - half_size_plot_ra])
            ax[col].set_ylim(
                [dec_cen[i] - half_size_plot, dec_cen[i] + half_size_plot])
            ax[col].set_title('Ipix='+str(ipix[i]), y= 0.9, pad=8, backgroundcolor='w') #{x=ra_cen[i], y=dec_cen[i], pad=8)
            ax[col].legend(loc=3)
            ax[col].scatter(
                ra_cen[i], dec_cen[i], color='k', s=100, marker='+', label='Cluster center')

            plt.subplots_adjust(wspace=0, hspace=0)
            # plt.savefig(output_dir + '/clusters_with_and_without_crowded_stars.png')
            plt.show()
            # plt.close()

    
def general_plots(star_clusters_simulated, output_dir):
    
    output_plots = Path(output_dir)
    output_plots.mkdir(parents=True, exist_ok=True)
    
    name_DG, ra_DG, dec_DG, dist_kpc_DG, Mv_DG, rhl_pc_DG, FeH_DG, name_GC, R_MW_GC, FeH_GC, mM_GC, Mv_GC, rhl_pc_GC, dist_kpc_GC, rhl_arcmin_GC = read_real_cat()

    PIX_sim, NSTARS, MAG_ABS_V, NSTARS_CLEAN, MAG_ABS_V_CLEAN, RA, DEC, R_EXP, ELL, PA, MASS, DIST = np.loadtxt(
        star_clusters_simulated,
        usecols=(0, 1, 2, 4, 5, 9, 10, 11, 12, 13, 14, 15),
        unpack=True,
    )
    f, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(22, 5))
    ax1.scatter(1.7 * R_EXP[MAG_ABS_V < 0.0], MAG_ABS_V[MAG_ABS_V < 0.0], color='r', label='Sim')
    ax1.scatter(1.7 * R_EXP[MAG_ABS_V < 0.0], MAG_ABS_V_CLEAN[MAG_ABS_V < 0.0], color='darkred', label='Sim filt')
    ax1.scatter(rhl_pc_DG, Mv_DG, color='b', marker='x', label='DG')
    ax1.scatter(rhl_pc_GC, Mv_GC, color='k', marker='x', label='GC')
    for i, j in enumerate(R_EXP):
        if MAG_ABS_V[i] < 0.0:
            ax1.plot([1.7 * R_EXP[i], 1.7 * R_EXP[i]],
                     [MAG_ABS_V[i], MAG_ABS_V_CLEAN[i]], color='darkred', lw=0.1)
    for i, j in enumerate(rhl_pc_DG):
        ax1.annotate(name_DG[i], (rhl_pc_DG[i], Mv_DG[i]))
    for i, j in enumerate(rhl_pc_GC):
        ax1.annotate(name_GC[i], (rhl_pc_GC[i], Mv_GC[i]))
    ax1.set_ylabel("M(V)")
    ax1.set_xlabel(r"$r_{1/2}$ (pc))")
    ax1.set_xlim([np.min(1.7 * R_EXP[MAG_ABS_V < 0.0]) - 0.1, np.max(1.7 * R_EXP[MAG_ABS_V < 0.0]) + 0.1])
    ax1.set_ylim([np.max(MAG_ABS_V_CLEAN[MAG_ABS_V < 0.0]) + 0.1, np.min(MAG_ABS_V[MAG_ABS_V < 0.0]) - 0.1])
    ax1.set_xscale("log")
    ax1.legend()

    ax2.scatter(1.7 * R_EXP[MAG_ABS_V < 0.0], MAG_ABS_V[MAG_ABS_V < 0.0], color='r', label='Sim')
    ax2.scatter(1.7 * R_EXP[MAG_ABS_V < 0.0], MAG_ABS_V_CLEAN[MAG_ABS_V < 0.0], color='darkred', label='Sim filt')
    ax2.scatter(rhl_pc_DG, Mv_DG, color='b', marker='x', label='DG')
    ax2.scatter(rhl_pc_GC, Mv_GC, color='k', marker='x', label='GC')
    #for i, j in enumerate(rhl_pc_DG):
    #    ax2.annotate(name_DG[i], (np.log10(rhl_pc_DG[i]), Mv_DG[i]))
    #for i, j in enumerate(rhl_pc_GC):
    #    ax2.annotate(name_GC[i], (np.log10(rhl_pc_GC[i]), Mv_GC[i]))
    ax2.set_xlabel(r"$r_{1/2}$ (pc))")
    ax2.legend()
    ax2.plot(np.logspace(np.log10(1.8), np.log10(1800), 10, endpoint=True),
        np.linspace(1, -14, 10, endpoint=True), color="b", ls=":")
    ax2.plot(np.logspace(np.log10(4.2), np.log10(4200), 10, endpoint=True),
        np.linspace(1, -14, 10, endpoint=True), color="b", ls=":")
    ax2.plot(np.logspace(np.log10(11), np.log10(11000), 10, endpoint=True),
        np.linspace(1, -14, 10, endpoint=True), color="b", ls=":")
    ax2.plot(np.logspace(np.log10(28), np.log10(28000), 10, endpoint=True),
        np.linspace(1, -14, 10, endpoint=True), color="b", ls=":")
    ax2.text(300, -7.9, r"$\mu_V=27\ mag/arcsec$", rotation=45)
    ax2.text(400, -4.2, r"$\mu_V=31\ mag/arcsec$", rotation=45)
    ax2.set_xscale("log")
    ax2.set_xlim([0.4, 4000])
    ax2.set_ylim([1, -14])

    ax3.scatter(MASS, MAG_ABS_V, label='Sim', color='r')
    ax3.scatter(MASS, MAG_ABS_V_CLEAN, label='Sim filt', color='darkred')
    for i, j in enumerate(MASS):
        if MAG_ABS_V[i] < 0.0:
            ax3.plot([MASS[i], MASS[i]],
                     [MAG_ABS_V[i], MAG_ABS_V_CLEAN[i]], color='darkred', lw=0.2)
    ax3.set_xlabel("mass(Msun)")
    ax3.set_ylim([np.max(MAG_ABS_V_CLEAN[MAG_ABS_V < 0.0]) + 0.1, np.min(MAG_ABS_V[MAG_ABS_V < 0.0]) - 0.1])
    ax3.legend()
    plt.savefig(output_dir + '/hist_MV.png')
    plt.show()
    plt.close()


def plot_ftp(
    pix_ftp, star_clusters_simulated, ra_max, ra_min, dec_min, dec_max,
    output_dir
):
    """Plot footprint map to check area."""
    nside = 4096
    npix = hp.nside2npix(nside)
    
    cmap = plt.cm.inferno_r

    ra_pix_ftp, dec_pix_ftp = hp.pix2ang(nside, pix_ftp, nest=True, lonlat=True)
    map_ftp = np.zeros(hp.nside2npix(nside))
    map_ftp[pix_ftp] = 1

    test = hp.cartview(
        map_ftp,
        nest=True,
        lonra=[np.min(ra_pix_ftp), np.max(ra_pix_ftp)],
        latra=[np.min(dec_pix_ftp), np.max(dec_pix_ftp)],
        hold=True,
        cbar=False,
        title="",
        cmap=cmap,
        return_projected_map=True,
    )
    plt.clf()

    RA, DEC = np.loadtxt(star_clusters_simulated, usecols=(9, 10), unpack=True)
    #for i in range(len(RA)):
    #    hp.projtext(
    #        RA[i],
    #        DEC[i],
    #        str(PIX_sim[i]),
    #        lonlat=True,
    #        fontsize=10,
    #        c="k",
    #        horizontalalignment="center",
    #    )
    #    hp.projscatter(RA[i], DEC[i], lonlat=True, coord="C", s=1.0, color="k", lw=0.1)

    # data = getdata(mockcat)
    # RA_star, DEC_star = data["RA"], data["DEC"]
    fig, axs = plt.subplots(1, 1, figsize=(10, 10))
    axs.imshow(
        test,
        origin="lower",
        extent=(ra_max, ra_min, dec_min, dec_max),
        interpolation="none",
    )
    axs.scatter(RA, DEC, s=20., c="k", marker="s", label="Simulated clusters")
    # axs.scatter(RA_star, DEC_star, s=0.01, c="k", marker="o", label="Simulated stars")
    axs.set_xlim([ra_max, ra_min])
    axs.set_ylim([dec_min, dec_max])
    axs.set_xlabel("RA (deg)")
    axs.set_ylabel("DEC (deg)")
    axs.set_title("2D Histogram of stars of stars on Footprint Map")
    axs.grid()
    plt.legend(loc=1)
    # plt.savefig(output_dir + '/ftp.png')
    plt.show()
    # plt.close()


def plots_ang_size(
    star_clusters_simulated,
    clus_path,
    mmin,
    mmax,
    cmin,
    cmax,
    output_plots,
    FeH_iso
):
    """Plots to analyze the simulated clusters."""

    cmap = mpl.cm.get_cmap("inferno")
    cmap.set_under("dimgray")
    cmap.set_bad("black")
    
    # TODO: Variaveis Instanciadas e não usadas
    hp_sample_un, NSTARS, MAG_ABS_V, NSTARS_CLEAN, MAG_ABS_V_CLEAN, RA_pix, DEC_pix, r_exp, ell, pa, mass, dist = np.loadtxt(
        star_clusters_simulated, usecols=(0, 1, 2, 4, 5, 9, 10, 11, 12, 13, 14, 15), unpack=True
    )
    
    for i in hp_sample_un:

        # TODO: use only cats of filtered stars
        clus_filepath = Path(clus_path, "%s_clus.dat" % int(i))
        plot_filepath = Path(output_plots, "%s_cmd.png" % int(i))
        plot_filt_filepath = Path(output_plots, "%s_filt_cmd.png" % int(i))

        # Evita erro se o arquivo _clus.dat não existir.
        # Pode acontecer se o teste estiver usando uma quantidade pequena de dados.
        if not clus_filepath.exists():
            continue

        star = np.loadtxt(clus_filepath)

        plt.scatter(star[:,2]-star[:,4], star[:,2], color='r')
        plt.title('HPX ' + str(int(i)) + ', N=' + str(len(star[:,2])))
        plt.ylim([mmax, mmin])
        plt.xlim([cmin, cmax])
        plt.xlabel('mag1-mag2')
        plt.ylabel('mag1')
        # plt.savefig(str(int(i)) + '_cmd.png')
        plt.show()
        # plt.close()

        h1, xedges, yedges, im1 = plt.hist2d(
            star[:, 2] - star[:, 4],
            star[:, 2],
            bins=50,
            range=[[cmin, cmax], [mmin, mmax]],
            # norm=mpl.colors.LogNorm(),
            cmap=cmap,
        )
        plt.clf()
        plt.title("HPX " + str(int(i)) + ", N=" + str(len(star[:, 2])))
        im1 = plt.imshow(
            h1.T,
            interpolation="None",
            origin="lower",
            vmin=0.1,
            vmax=np.max(h1),
            extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]],
            aspect="auto",
            cmap=cmap,
        )
        plt.ylim([mmax, mmin])
        plt.xlim([cmin, cmax])
        plt.xlabel("mag1-mag2")
        plt.ylabel("mag1")
        plt.colorbar(im1, cmap=cmap, orientation="vertical", label="stars per bin")
        plt.savefig(plot_filepath)
        plt.show()
        plt.close()
        
    name_DG, ra_DG, dec_DG, dist_kpc_DG, Mv_DG, rhl_pc_DG, FeH_DG, name_GC, R_MW_GC, FeH_GC, mM_GC, Mv_GC, rhl_pc_GC, dist_kpc_GC, rhl_arcmin_GC = read_real_cat()
    
    hp_sample_un, NSTARS, MAG_ABS_V, NSTARS_CLEAN, MAG_ABS_V_CLEAN, RA_pix, DEC_pix, r_exp, ell, pa, mass, dist = np.loadtxt(
    star_clusters_simulated, usecols=(0, 1, 2, 4, 5, 9, 10, 11, 12, 13, 14, 15), unpack=True)
    
    ang_size_DG = 60. * (180. / np.pi) * np.arctan(rhl_pc_DG / (1000. * dist_kpc_DG))
    ang_size = 60 * np.rad2deg(np.arctan(1.7 * r_exp / dist))
    
    RHL_PC_SIM = 1.7 * r_exp

    MW_center_distance_DG_kpc = radec2GCdist(ra_DG, dec_DG, dist_kpc_DG)

    f, ((ax1, ax2), (ax3, ax4), (ax5, ax6), (ax7, ax8), (ax9, ax10)) = plt.subplots(5, 2, figsize=(15, 23))

    ax1.hist(dist_kpc_DG, bins=np.linspace(0, 2. * np.max(dist) / 1000, 20), label='DG', color='b', alpha=0.5, histtype='stepfilled')
    ax1.hist(dist_kpc_GC, bins=np.linspace(0, 2. * np.max(dist) / 1000, 20), label='GC', color='k', alpha=0.5, lw=2, histtype='step')
    ax1.hist(dist / 1000, bins=np.linspace(0, 2. * np.max(dist) / 1000, 20), label='Sim', color='r', alpha=0.5)
    ax1.legend()
    ax1.set_xlabel("Distance (kpc)")
    ax1.set_ylabel("N objects")
    ax1.set_title('Histogram of distances (linear scale)')
    ax1.set_xlim([0, 2. * np.max(dist) / 1000])

    ax2.hist(dist_kpc_DG, bins=np.linspace(0, 2. * np.max(dist) / 1000, 20), label='DG', color='b', alpha=0.5, histtype='stepfilled')
    ax2.hist(dist_kpc_GC, bins=np.linspace(0, 2. * np.max(dist) / 1000, 20), label='GC', color='k', alpha=0.5, lw=2, histtype='step')
    ax2.hist(dist / 1000, bins=np.linspace(0, 2. * np.max(dist) / 1000, 20), label='Sim', color='r', alpha=0.5)
    ax2.legend()
    ax2.set_title('Histogram of distances (log scale)')
    ax2.set_xlabel("Distance (kpc)")
    ax2.set_ylabel("N objects")
    ax2.set_yscale('log')
    ax2.set_xlim([0, 2. * np.max(dist) / 1000])
    
    ax3.hist(ang_size_DG, bins=np.linspace(np.min(ang_size) / 2, 2. * np.max(ang_size), 20), label='DG', color='b', alpha=0.5, histtype='stepfilled')
    ax3.hist(rhl_arcmin_GC, bins=np.linspace(np.min(ang_size) / 2, 2. * np.max(ang_size), 20), label='GC', color='k', alpha=0.5, lw=2, histtype='step')
    ax3.hist(ang_size, bins=np.linspace(np.min(ang_size) / 2, 2. * np.max(ang_size), 20), label='Sim', color='r', alpha=0.5)
    ax3.legend()
    ax3.set_xlim([np.min(ang_size) / 2, 2. * np.max(ang_size)])
    ax3.set_xlabel(r"$r_{1/2}$ (arcmin)")
    ax3.set_ylabel("N objects")
    ax3.set_title('Histogram of angular sizes (linear scale)')

    ax4.hist(ang_size_DG, bins=np.linspace(np.min(ang_size) / 2, 2. * np.max(ang_size), 20), label='DG', color='b', alpha=0.5, histtype='stepfilled')
    ax4.hist(rhl_arcmin_GC, bins=np.linspace(np.min(ang_size) / 2, 2. * np.max(ang_size), 20), label='GC', color='k', alpha=0.5, lw=2, histtype='step')
    ax4.hist(ang_size, bins=np.linspace(np.min(ang_size) / 2, 2. * np.max(ang_size), 20), label='Sim', color='r', alpha=0.5)
    ax4.legend()
    ax4.set_xlim([np.min(ang_size) / 2, 2. * np.max(ang_size)])
    ax4.set_yscale('log')
    ax4.set_xlabel(r"$r_{1/2}$ (arcmin)")
    ax4.set_ylabel("N objects")
    ax4.set_title('Histogram of angular sizes (log scale)')

    ax5.scatter(dist / 1000, ang_size, label='Sim', color='r')
    ax5.scatter(dist_kpc_DG, ang_size_DG, label='DG', color='b')
    ax5.scatter(dist_kpc_GC, rhl_arcmin_GC, label='GC', color='k')
    ax5.set_xlabel("Distance (kpc)")
    ax5.set_ylabel(r"$r_{1/2}$ (arcmin)")
    ax5.set_yscale('log')
    ax5.legend()
    ax5.set_title('Distances X Angular sizes')
    
    for i, j in enumerate(mass):
        if MAG_ABS_V[i] < 0.0:
            ax6.plot([mass[i], mass[i]], [NSTARS[i], NSTARS_CLEAN[i]], color='darkred', lw=0.2)
    ax6.scatter(mass, NSTARS, label='Sim', color='r')
    ax6.scatter(mass, NSTARS_CLEAN, label='Sim filt', color='darkred')
    ax6.set_xlabel("MASS(MSun)")
    ax6.set_ylabel("N stars")
    ax6.legend()
    ax6.set_title('Visible Mass X Star counts')

    ax7.hist(Mv_DG, bins=20, range=(-16, 0.0), histtype="stepfilled", label="DG", color="b", alpha=0.5)
    ax7.hist(Mv_GC, bins=20, range=(-16, 0.0), histtype="step", label="GC", color="k")
    ax7.hist(MAG_ABS_V, bins=20, range=(-16, 0.0), histtype="step", label="Sim", color="r", ls="--", alpha=0.5)
    ax7.hist(MAG_ABS_V_CLEAN, bins=20, range=(-16, 0.0), histtype="stepfilled", label="Sim filt", color="darkred", ls="--", alpha=0.5)
    ax7.set_xlabel(r"$M_V$")
    ax7.set_ylabel("N")
    ax7.legend(loc=2)
    ax7.set_title('Histogram of Absolute Magnitude (V band)')

    ax8.hist(rhl_pc_DG, bins=20, histtype="stepfilled", range=(10, 2400), label="DG", color="b", alpha=0.5)
    ax8.hist(rhl_pc_GC, bins=20, histtype="step", range=(10, 2400), label="GC", color="k")
    ax8.hist(RHL_PC_SIM, bins=20, histtype="stepfilled", range=(10, 2400), label="Sim", color="r", ls="--", alpha=0.5)
    ax8.set_xlabel(r"$r_{1/2}$[pc]")
    ax8.legend(loc=1)
    # ax8.set_xscale('log')
    ax8.set_yscale('log')
    ax8.set_title(r'Histogram of $r_{1/2}$ (parsecs)')

    ax9.hist(np.repeat(FeH_iso, len(MAG_ABS_V)), bins=20, range=(-3, 1.0), histtype="stepfilled", label="Sim", color="r", ls="--", alpha=0.5)
    ax9.hist(FeH_DG, bins=20, range=(-3, 1.0), histtype="stepfilled", label="DG", color="b", alpha=0.5)
    ax9.hist(FeH_GC, bins=20, range=(-3, 1.0), histtype="step", label="GC", color="k")
    ax9.set_xlabel("[Fe/H]")
    ax9.legend(loc=1)
    ax9.set_title('Absolute Magnitude (V band) X Metalicity')
    
    ax10.scatter(dist / 1000, np.repeat(FeH_iso, len(dist)), label="Sim", color="r", marker="x", lw=1.0)
    ax10.scatter(MW_center_distance_DG_kpc, FeH_DG, label="DG", color="b")
    ax10.scatter(R_MW_GC, FeH_GC, label="GC", color="k")
    ax10.set_xlabel("Distance to the Galactic center (kpc)")
    ax10.set_ylabel("[Fe/H]")
    ax10.set_ylim([-3.5, 0])
    ax10.legend()
    ax10.grid()
    ax10.set_title('Galactocentric distances X Metalicity')

    # plt.savefig(output_plots + '/hist_mass.png')
    plt.suptitle("Physical features of 58 Dwarf Gal + 152 GC + " + str(len(hp_sample_un)) + " Simulations", fontsize=16)
    f.tight_layout()
    plt.subplots_adjust(top=0.92)

    plt.show()


def plot_err(MAG_G, MAG_R, MAGERR_G, MAGERR_R, GC):

    """Plot the magnitude and error of the simulated clusters compared to the
    real stars, in log scale.

    """

    plt.scatter(MAG_G[GC == 0], MAGERR_G[GC == 0], label="Field stars", c="k")
    plt.scatter(
        MAG_G[GC == 1],
        MAGERR_G[GC == 1],
        label="Simulated stars",
        c="r",
        zorder=10,
    )
    plt.yscale("log")
    plt.xlabel("mag_g_with_err")
    plt.ylabel("magerr_g")
    plt.legend()

    filepath = Path(output_plots, "simulated_stars_err.png")
    plt.savefig(filepath)
    plt.show()
    plt.close()
