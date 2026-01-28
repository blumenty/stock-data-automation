#!/usr/bin/env python3
"""
Stock Symbols - Exact same TA stocks as your Dart implementation
"""

# TA-125 Stocks (exact same as your Dart code)
TA125_STOCKS = [
    # Banks & Financial Services
    'DSCT.TA',
    'POLI.TA', 'LUMI.TA', 'MZTF.TA', 'FIBI.TA', 'IBI.TA',
    'AMOT.TA', 'EQTL.TA', 'MTAV.TA', 'ISRS.TA', 'MNIF.TA', 'TASE.TA',
    'KEN.TA', 'HARL.TA', 'CLIS.TA', 'MMHD.TA', 'MGDL.TA', 'ISCD.TA',

    # Technology & Healthcare
    'TEVA.TA', 'ESLT.TA', 'NVMI.TA', 'NICE.TA', 'TSEM.TA', 'CAMT.TA',
    'NYAX.TA', 'ONE.TA', 'SPNS.TA', 'FORTY.TA', 'MTRX.TA', 'HLAN.TA',
    'MGIC.TA', 'TLSY.TA', 'MLTM.TA', 'NXSN.TA', 'PRTC.TA',

    # Telecommunications
    'BEZQ.TA', 'PTNR.TA', 'CEL.TA',

    # Real Estate & Construction
    'AZRG.TA', 'MLSR.TA', 'BIG.TA', 'ALHE.TA', 'AFHD.TA', 'CHCG.TA',
    'CITYB.TA', 'GMUL.TA', 'ILCO.TA', 'BATM.TA', 'SHOM.TA', 'EMCO.TA',
    'BRAM.TA', 'FTAL.TA', 'ISCO.TA', 'GREN.TA', 'MNRV.TA', 'LIND.TA',
    'BLSR.TA', 'PTCH.TA', 'KTEN.TA', 'SNTG.TA', 'ADCN.TA',

    # Energy
    'DLKM.TA', 'DLEKG.TA', 'OPCE.TA', 'NVPT.TA', 'ENLT.TA', 'ENOG.TA',
    'ENRG.TA', 'PAZ.TA', 'ISRA.TA', 'RATI.TA', 'TMRP.TA', 'ORL.TA',
    'DORL.TA', 'DRAL.TA', 'MSKE.TA', 'BEZN.TA', 'SBEN.TA', 'NOFR.TA',
    'DUNI.TA',

    # Insurance
    'PHOE.TA', 'IDIN.TA', 'MISH.TA', 'BCOM.TA', 'VRDS.TA', 'TDRN.TA',
    'PTBL.TA', 'WLFD.TA',

    # Retail & Consumer
    'SAE.TA', 'RMLI.TA', 'FOX.TA', 'YHNF.TA', 'RTLS.TA', 'OPK.TA',
    'MCDL.TA', 'NVCR.TA', 'DRSD.TA', 'BLRX.TA', 'INTV.TA', 'OPKO.TA',

    # Manufacturing & Industrial
    'ELRN.TA', 'GILT.TA', 'MRHL.TA', 'DNMR.TA', 'RLCO.TA', 'PLSN.TA',
    'SODA.TA', 'VTLS.TA', 'BONS.TA', 'INRM.TA', 'ELCO.TA',
    'DELT.TA', 'HRON.TA', 'AVGL.TA', 'NECL.TA', 'LPSN.TA', 'RDGS.TA',
    'ORMP.TA', 'KAMN.TA',
]

def get_all_symbols():
    """Get all symbols for download"""
    return {
        'TA125': TA125_STOCKS,
    }















