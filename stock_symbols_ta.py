#!/usr/bin/env python3
"""
Stock Symbols - Exact same stocks as your Dart implementation
"""
# Israeli Stocks for Autodownloading (TA-125 + TA-SME60 + TA-Others + TA-Remainings + Top ETFs IL) - 228 stocks

# Official TA-125 Index - 123 Stocks Exactly (updated: 2025-01-04)
TA125_STOCKS = [
    # Banks & Financial Services (22)
    'FIBIH.TA', 'AMPA.TA', 'DSCT.TA', 'POLI.TA', 'LUMI.TA', 'MZTF.TA',
    'FIBI.TA', 'IBI.TA', 'AMOT.TA', 'EQTL.TA', 'MTAV.TA', 'ISRS.TA',
    'TASE.TA', 'KEN.TA', 'HARL.TA', 'CLIS.TA', 'MMHD.TA', 'MGDL.TA',
    'ISCD.TA', 'ISHO.TA', 'MRIN.TA', 'LAPD.TA',

    # Technology (19)
    'TEVA.TA', 'ESLT.TA', 'NVMI.TA', 'NICE.TA', 'TSEM.TA', 'CAMT.TA',
    'NYAX.TA', 'ONE.TA', 'FORTY.TA', 'MTRX.TA', 'HLAN.TA', 'MGIC.TA',
    'MLTM.TA', 'NXSN.TA', 'PRTC.TA', 'BEZQ.TA', 'PTNR.TA', 'CEL.TA',
    'GILT.TA',

    # Real Estate (24)
    'AZRG.TA', 'MLSR.TA', 'BIG.TA', 'ALHE.TA', 'ARPT.TA', 'FTAL.TA',
    'MVNE.TA', 'AURA.TA', 'AZRM.TA', 'GVYM.TA', 'GCT.TA', 'ARGO.TA',
    'SLARL.TA', 'AFRE.TA', 'RIT1.TA', 'SMT.TA', 'ISRO.TA', 'ISCN.TA',
    'MGOR.TA', 'BLSR.TA', 'CRSR.TA', 'ELCRE.TA', 'DUNI.TA', 'RMON.TA',

    # Energy (17)
    'NWMD.TA', 'ORA.TA', 'OPCE.TA', 'NVPT.TA', 'ENLT.TA', 'ENOG.TA',
    'ENRG.TA', 'PAZ.TA', 'ISRA.TA', 'RATI.TA', 'TMRP.TA', 'ORL.TA',
    'DORL.TA', 'MSKE.TA', 'SBEN.TA', 'NOFR.TA', 'DLEKG.TA',

    # Insurance (5)
    'PHOE.TA', 'IDIN.TA', 'MISH.TA', 'VRDS.TA', 'PTBL.TA',

    # Retail & Consumer (12)
    'SAE.TA', 'RMLI.TA', 'FOX.TA', 'YHNF.TA', 'RTLS.TA', 'OPK.TA',
    'CRSM.TA', 'NTML.TA', 'MAXO.TA', 'DLTI.TA', 'STRS.TA', 'DLEA.TA',

    # Construction & Industrial (18)
    'SPEN.TA', 'SKBN.TA', 'ASHG.TA', 'DIMRI.TA', 'DNYA.TA', 'AMRM.TA',
    'INRM.TA', 'DANE.TA', 'PRSK.TA', 'ELTR.TA', 'ILCO.TA', 'ISHI.TA',
    'ELCO.TA', 'ECP.TA', 'BSEN.TA', 'TRPZ.TA', 'ACRO.TA', 'DELG.TA',

    # Other Industries (5)
    'ICL.TA', 'ELAL.TA', 'ARYT.TA', 'PLRM.TA', 'ACKR.TA',
]

# Official TA-SME60 Index - 60 Stocks (updated: 2026-03-10)
SME60_STOCKS = [
    # Technology (11)
    'TLSY.TA', 'AUDC.TA', 'ALLT.TA', 'PERI.TA', 'QLTU.TA', 'ANLT.TA',
    'ARD.TA', 'ORBI.TA', 'CMDR.TA', 'MLTM.TA', 'HIPR.TA',

    # Industrial & Manufacturing (10)
    'FBRT.TA', 'PLSN.TA', 'ASHO.TA', 'TDRN.TA', 'AFHL.TA', 'TATT.TA',
    'PLRM.TA', 'ELWS.TA', 'TPGM.TA', 'RPOL.TA',

    # Financial Services (9)
    'DIFI.TA', 'ATRY.TA', 'AYAL.TA', 'ALTF.TA', 'MNIF.TA', 'MPP.TA',
    'SHVA.TA', 'GNRS.TA', 'IES.TA',

    # Real Estate (14)
    'ADGR.TA', 'CDEV.TA', 'ILDC.TA', 'KARE.TA', 'ARIN.TA', 'ROTS.TA',
    'MDTR.TA', 'HGG.TA', 'MGRT.TA', 'NTNB.TA', 'KSTN.TA', 'LAHAV.TA',
    'VTNA.TA',

    # Healthcare & Biomedical (4)
    'ILX.TA', 'KMDA.TA', 'URBC.TA',

    # Retail & Consumer (6)
    'CAST.TA', 'ISTA.TA', 'SCOP.TA', 'BLDI.TA', 'DIPL.TA', 'KRUR.TA',
    'TTAM.TA',

    # Energy & Utilities (4)
    'ECNR.TA', 'ELLO.TA', 'ZPRS.TA',

    # Other (2)
    'LUZN.TA', 'NAWI.TA', 'LEVI.TA', 'ISI.TA',
]

# Other TA stocks - 4 Stocks (updated: 2026-03-10)
TA_OTHERS_STOCKS = [
    # Other non TA-125 Stocks of interest (4)
    'AGRD.TA', 'IMCO.TA', 'ARDM.TA', 'ALAR.TA',
]

# Official TA-Remainings (Yeter) Index - 84 Stocks (updated: 2026-03-10)
TA_REMAINING_STOCKS = [
    # Energy (1)
    'PTCH.TA',

    # Financial (9)
    'LBRA.TA', 'MLRN.TA', 'MTRD.TA', 'PEN.TA', 'SRAC.TA', 'JCFN.TA',
    'ZUR.TA', 'WESR.TA', 'EXPO.TA',

    # Healthcare (4)
    'BONS.TA', 'BWAY.TA', 'CGEN.TA', 'MTLF.TA',

    # Industrial (16)
    'ELMR.TA', 'ALUMA.TA', 'ARAN.TA', 'BRAN.TA', 'BRND.TA', 'GOLD.TA',
    'PNRG.TA', 'TIGBUR.TA', 'TURB.TA', 'ELSPC.TA', 'SANO1.TA', 'THES.TA',
    'CNGL.TA', 'RGAS.TA', 'SHAN.TA', 'AXN.TA',

    # Real Estate (16)
    'ALMA.TA', 'ALRPR.TA', 'CPPL.TA', 'ASGR.TA', 'ILDR.TA', 'HGGE.TA',
    'KRDI.TA', 'LURO.TA', 'NSTR.TA', 'AZRT.TA', 'RLRE.TA', 'RANI.TA',
    'BLGO.TA', 'BOTI.TA', 'MGDO.TA', 'OMCN.TA',

    # Retail (13)
    'RVL.TA', 'WLFD.TA', 'WILC.TA', 'STG.TA', 'AMAN.TA', 'GLRS.TA',
    'GSFI.TA', 'DRAL.TA', 'VCTR.TA', 'GAD.TA', 'ALBA.TA', 'PRDM.TA',
    'NTO.TA',

    # Technology (17)
    'APLP.TA', 'MIA.TA', 'ELAD.TA', 'JEEN.TA', 'CMER.TA', 'PMNT.TA',
    'PCBT.TA', 'RZR.TA', 'UNIT.TA', 'RSEL.TA', 'BLRN.TA', 'GIX.TA',
    'TSG.TA', 'SOLR.TA', 'SLRM.TA', 'SOFW.TA', 'RPAC.TA', 'CISY.TA',

    # Telecom (3)
    'GLTL.TA', 'SCC.TA', 'GLDE.TA',

    # Utilities (3)
    'PRIM.TA', 'SNFL.TA', 'TRLT.TA',
]

# Selected top ETF IL - 17 Stocks (updated: 2026-03-10)
TOP_ETFS_IL = [
    # Harel ETFs (5)
    'HRL-F16.TA', 'HRL-F7.TA', 'HRL-FK43.TA', 'HRL-F14.TA', 'HRL-F12.TA',

    # MTF (Migdal) ETFs (6)
    'MTF-F74.TA', 'MTF-F42.TA', 'MTF-F18.TA', 'MTF-F66.TA', 'MTF-F71.TA',
    'MTF-F84.TA',

    # Meitav Tachlit ETFs (3)
    'TCH-F171.TA', 'TCH-F172.TA', 'TCH-F83.TA',

    # KSM ETFs (3)
    'KSM-F103.TA', 'KSM-F21.TA', 'KSM-F192.TA',
]


def get_all_symbols():
    """Get all symbols for download"""
    return {
        'TA125': TA125_STOCKS,
        'TA-SME60': SME60_STOCKS,
        'TA-Others': TA_OTHERS_STOCKS,
        'TA-Remainings': TA_REMAINING_STOCKS,
        'Top ETFs IL': TOP_ETFS_IL,
    }