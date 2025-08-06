#!/usr/bin/env python3
"""
Stock Symbols - Exact same stocks as your Dart implementation
"""

# TA-125 Stocks (exact same as your Dart code)
TA125_STOCKS = [
    # Banks & Financial Services
    'DSCT.TA', 'POLI.TA', 'LUMI.TA', 'MZTF.TA', 'FIBI.TA', 'IBI.TA',
    'AMOT.TA', 'EQTL.TA', 'MTAV.TA', 'ISRS.TA', 'MNIF.TA', 'TASE.TA',
    'KEN.TA', 'HARL.TA', 'CLIS.TA', 'MMHD.TA', 'MGDL.TA', 'ISCD.TA',
    
    ## Technology & Healthcare
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
    'SODA.TA', 'VTLS.TA', 'BONS.TA', 'MZTF.TA', 'INRM.TA', 'ELCO.TA',
    'DELT.TA', 'HRON.TA', 'AVGL.TA', 'NECL.TA', 'LPSN.TA', 'RDGS.TA',
    'ORMP.TA', 'KAMN.TA',
]

# S&P 500 Stocks (exact same as your Dart code) 
SP500_STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA',
    'BRK-B', 'AVGO', 'LLY', 'WMT', 'JPM', 'UNH', 'XOM', 'ORCL',
    'MA', 'COST', 'HD', 'PG', 'JNJ', 'ABBV', 'NFLX', 'CRM', 'BAC',
    'CVX', 'KO', 'AMD', 'PEP', 'TMO', 'WFC', 'LIN', 'CSCO', 'ABT',
    'DIS', 'ADBE', 'VZ', 'COP', 'CMCSA', 'ACN', 'NKE', 'TXN', 'MRK',
    'QCOM', 'PM', 'INTU', 'DHR', 'IBM', 'GE', 'T', 'CAT', 'UBER',
    'RTX', 'AMGN', 'NOW', 'SPGI', 'NEE', 'LOW', 'BA', 'UNP', 'HON',
    'ELV', 'PFE', 'GS', 'BLK', 'MDT', 'LMT', 'SYK', 'AXP', 'BKNG',
    'DE', 'TJX', 'VRTX', 'ADP', 'GILD', 'ADI', 'CVS', 'MMC', 'C',
    'MO', 'SCHW', 'TMUS', 'CI', 'LRCX', 'ETN', 'REGN', 'SLB', 'FI',
    'MU', 'CB', 'BSX', 'PYPL', 'EOG', 'SO', 'WM', 'ISRG', 'ITW',
    'PLD', 'BDX', 'DUK', 'AON', 'CL', 'CMG', 'ICE', 'APH', 'FCX',
    'USB', 'NOC', 'PNC', 'HUM', 'ECL', 'MSI', 'GD', 'NSC', 'SNPS',
    'MAR', 'MCK', 'EMR', 'TGT', 'PSA', 'MPC', 'JCI', 'GM', 'AJG',
    'TFC', 'VLO', 'SHW', 'HCA', 'WELL', 'COF', 'CCI', 'AZO', 'DG',
    'WMB', 'OKE', 'CDNS', 'ORLY', 'PCAR', 'CNC', 'NXPI', 'MCO', 'TRV',
   'CMI', 'ADSK', 'AMP', 'KLAC', 'FTNT', 'AFL', 'CHTR', 'O', 'ALL',
    'PEG', 'MCHP', 'F', 'MSCI', 'TEL', 'PSX', 'AMAT', 'PAYX', 'COR',
    'AEP', 'KMI', 'SRE', 'A', 'CARR', 'FAST', 'YUM', 'CTSH', 'ROST',
    'DHI', 'PRU', 'CME', 'KMB', 'IDXX', 'GWW', 'AME', 'OTIS', 'HLT',
    'ED', 'SPG', 'FANG', 'BK', 'CTAS', 'HPQ', 'DD', 'GLW', 'EA', 'BF-B',
    'VRSK', 'XYL', 'ADM', 'EXC', 'BIIB', 'DXCM', 'KHC', 'EW', 'CPRT',
    'ACGL', 'GIS', 'DOW', 'MET', 'VMC', 'GEHC', 'ROP', 'CTVA', 'URI',
    'MLM', 'ZBH', 'WBD', 'HIG', 'FDX', 'ANSS', 'STZ', 'DAL', 'HSY',
    'ON', 'IQV', 'WEC', 'IT', 'EBAY', 'PPG', 'MTB', 'EIX', 'APTV',
    'EXR', 'MNST', 'CSGP', 'NUE', 'AVB', 'KEYS', 'FTV', 'WTW', 'SBAC',
    'ZTS', 'CDW', 'AWK', 'LH', 'VICI', 'STLD', 'HUBB', 'FSLR', 'SYF',
    'ETR', 'FITB', 'TSN', 'WY', 'HAL', 'AEE', 'MPWR', 'EQT', 'LUV',
    'NTRS', 'PPL', 'HBAN', 'STT', 'SYY', 'CAH', 'TDY', 'ARE', 'ESS',
   'LDOS', 'COG', 'RF', 'TTWO', 'NTAP', 'K', 'ALGN', 'EQR', 'EPAM',
    'SWKS', 'WAT', 'CLX', 'TROW', 'ATO', 'MAA', 'INVH', 'CINF', 'MOH',
    'INCY', 'EXPE', 'BALL', 'ZBRA', 'HOLX', 'JBHT', 'DFS', 'FE', 'CMS',
    'TYL', 'J', 'PFG', 'UDR', 'AKAM', 'KIM', 'PAYC', 'LVS', 'NI',
    'HST', 'MGM', 'AMCR', 'WAB', 'TER', 'PEAK', 'EVRG', 'CNP', 'GRMN',
    'LEN', 'UAL', 'VTRS', 'AVY', 'JKHY', 'POOL', 'AIZ', 'FFIV', 'BRO',
    'LNT', 'DTE', 'TECH', 'CTLT', 'GEN', 'L', 'DVN', 'OMC', 'KMX',
    'ULTA', 'TPG', 'NRG', 'SMCI', 'REG', 'CHRW', 'SOLV', 'ALLE', 'IEX',
    'WYNN', 'ENPH', 'AAP', 'BXP', 'NDSN', 'BBWI', 'VRSN', 'IP', 'AOS',
    'LUMN', 'PNR', 'MHK', 'QRVO', 'BEN', 'MOS', 'TAP', 'ZION', 'MKTX',
    'GL', 'HSIC', 'AIR', 'MTCH', 'PARA', 'TKR', 'ETSY', 'BWA', 'NEWS',
    'NWSA', 'HAS', 'DISH', 'CE', 'FCN', 'CZR', 'TPL', 'TRGP', 'TGT',
    'TEL', 'TDY', 'TER', 'TSLA', 'TXN', 'TPL', 'TTD', 'TSCO', 'TT',
    'TDG', 'TRV', 'TRMB', 'TFC', 'TYL', 'TSN', 'USB', 'UBER', 'UDR',
]

def get_all_symbols():
    """Get all symbols for download"""
    return {
        'TA125': TA125_STOCKS,
        'SP500': SP500_STOCKS

    }
