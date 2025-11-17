#!/usr/bin/env python3
"""
Stock Symbols - Exact same stocks as your Dart implementation
"""

# TA-125 Stocks (exact same as your Dart code)
TA125_STOCKS = [
    # Banks & Financial Services
#    'DSCT.TA',
#    'POLI.TA', 'LUMI.TA', 'MZTF.TA', 'FIBI.TA', 'IBI.TA',
#    'AMOT.TA', 'EQTL.TA', 'MTAV.TA', 'ISRS.TA', 'MNIF.TA', 'TASE.TA',
#    'KEN.TA', 'HARL.TA', 'CLIS.TA', 'MMHD.TA', 'MGDL.TA', 'ISCD.TA',
    
    ## Technology & Healthcare
#    'TEVA.TA', 'ESLT.TA', 'NVMI.TA', 'NICE.TA', 'TSEM.TA', 'CAMT.TA',
#    'NYAX.TA', 'ONE.TA', 'SPNS.TA', 'FORTY.TA', 'MTRX.TA', 'HLAN.TA',
#    'MGIC.TA', 'TLSY.TA', 'MLTM.TA', 'NXSN.TA', 'PRTC.TA',
    
    # Telecommunications
#    'BEZQ.TA', 'PTNR.TA', 'CEL.TA',
    
    # Real Estate & Construction
#    'AZRG.TA', 'MLSR.TA', 'BIG.TA', 'ALHE.TA', 'AFHD.TA', 'CHCG.TA',
#    'CITYB.TA', 'GMUL.TA', 'ILCO.TA', 'BATM.TA', 'SHOM.TA', 'EMCO.TA',
#    'BRAM.TA', 'FTAL.TA', 'ISCO.TA', 'GREN.TA', 'MNRV.TA', 'LIND.TA',
#    'BLSR.TA', 'PTCH.TA', 'KTEN.TA', 'SNTG.TA', 'ADCN.TA',
    
    # Energy
#    'DLKM.TA', 'DLEKG.TA', 'OPCE.TA', 'NVPT.TA', 'ENLT.TA', 'ENOG.TA',
#    'ENRG.TA', 'PAZ.TA', 'ISRA.TA', 'RATI.TA', 'TMRP.TA', 'ORL.TA',
#    'DORL.TA', 'DRAL.TA', 'MSKE.TA', 'BEZN.TA', 'SBEN.TA', 'NOFR.TA',
#    'DUNI.TA',
    
    # Insurance
#    'PHOE.TA', 'IDIN.TA', 'MISH.TA', 'BCOM.TA', 'VRDS.TA', 'TDRN.TA',
#    'PTBL.TA', 'WLFD.TA',
    
    # Retail & Consumer
#    'SAE.TA', 'RMLI.TA', 'FOX.TA', 'YHNF.TA', 'RTLS.TA', 'OPK.TA',
#    'MCDL.TA', 'NVCR.TA', 'DRSD.TA', 'BLRX.TA', 'INTV.TA', 'OPKO.TA',
    
    # Manufacturing & Industrial
#    'ELRN.TA', 'GILT.TA', 'MRHL.TA', 'DNMR.TA', 'RLCO.TA', 'PLSN.TA',
#    'SODA.TA', 'VTLS.TA', 'BONS.TA', 'MZTF.TA', 'INRM.TA', 'ELCO.TA',
#    'DELT.TA', 'HRON.TA', 'AVGL.TA', 'NECL.TA', 'LPSN.TA', 'RDGS.TA',
#    'ORMP.TA', 'KAMN.TA', 
]

# S&P 500 Stocks (exact same as your Dart code) 
SP500_STOCKS = [
  'AAL', 'FI', 'META', 'MRK', 'RHI', 'IBKR', 'EME', 'WSM', 'TKO', 'TTD',
'WDAY', 'AMCR', 'MO', 'COF', 'CPT', 'CPB', 'EG', 'EVRG', 'FISV', 'KDP',
'MLM', 'VLTO', 'MMM', 'AOS', 'ABT', 'ABBV', 'ACN', 'ADBE', 'AMD', 'AES',
'AFL', 'A', 'APD', 'ABNB', 'AKAM', 'ALB', 'ARE', 'ALGN', 'ALLE', 'LNT',
'ALL', 'GOOGL', 'GOOG', 'AMZN', 'AEE', 'AEP', 'AXP', 'AIG', 'AMT', 'AWK',
'AMP', 'AME', 'AMGN', 'APH', 'ADI', 'AON', 'APA', 'AAPL', 'AMAT', 'APTV',
'ACGL', 'ADM', 'ANET', 'AJG', 'AIZ', 'T', 'ATO', 'ADSK', 'ADP', 'AZO',
'AVB', 'AVY', 'AXON', 'BKR', 'BALL', 'BAC', 'BAX', 'BDX', 'BRK.B', 'BBY',
'TECH', 'BIIB', 'BLK', 'BX', 'XYZ', 'BK', 'BA', 'BKNG', 'BSX', 'BMY',
'AVGO', 'BR', 'BRO', 'BF.B', 'BLDR', 'BG', 'BXP', 'CHRW', 'CDNS', 'CAH',
'CCL', 'CARR', 'CAT', 'CBOE', 'CBRE', 'CDW', 'COR', 'CNC', 'CNP', 'CF',
'CRL', 'SCHW', 'CHTR', 'CVX', 'CMG', 'CB', 'CHD', 'CI', 'CINF', 'CTAS',
'CSCO', 'C', 'CFG', 'CLX', 'CME', 'CMS', 'KO', 'CTSH', 'COIN', 'CL',
'CMCSA', 'CAG', 'COP', 'ED', 'STZ', 'CEG', 'COO', 'CPRT', 'GLW', 'CTVA',
'SOLS', 'CSGP', 'COST', 'CTRA', 'CRWD', 'CCI', 'CSX', 'CMI', 'CVS', 'DHR',
'DRI', 'DVA', 'DAY', 'DECK', 'DE', 'DELL', 'DAL', 'DVN', 'DXCM', 'FANG',
'DLR', 'DG', 'DLTR', 'D', 'DPZ', 'DASH', 'DOV', 'DOW', 'DHI', 'DTE',
'DUK', 'DD', 'ETN', 'EBAY', 'ECL', 'EIX', 'EW', 'EA', 'ELV', 'EMR',
'ETR', 'EOG', 'EPAM', 'EQT', 'EFX', 'EQIX', 'EQR', 'ERIE', 'ESS', 'EL',
'ES', 'EXC', 'EXPE', 'EXPD', 'EXR', 'XOM', 'FFIV', 'FDS', 'FICO', 'FAST',
'FRT', 'FDX', 'FIS', 'FITB', 'FSLR', 'FE', 'CPAY', 'F', 'FTNT', 'FTV',
'FOXA', 'FOX', 'BEN', 'FCX', 'GRMN', 'IT', 'GE', 'GEV', 'GEHC', 'GEN',
'GNRC', 'GD', 'GIS', 'GM', 'GPC', 'GILD', 'GPN', 'GL', 'GDDY', 'GS',
'HAL', 'HIG', 'HAS', 'HCA', 'DOC', 'HSIC', 'HSY', 'HPE', 'HLT', 'HOLX',
'HD', 'HON', 'HRL', 'HST', 'HWM', 'HPQ', 'HUBB', 'HUM', 'HBAN', 'HII',
'IBM', 'IEX', 'IDXX', 'ITW', 'INCY', 'IR', 'PODD', 'INTC', 'ICE', 'IFF',
'IP', 'IPG', 'INTU', 'ISRG', 'IVZ', 'INVH', 'IQV', 'IRM', 'JBHT', 'JBL',
'JKHY', 'J', 'JNJ', 'JCI', 'JPM', 'DDOG', 'K', 'KVUE', 'KEY', 'KEYS',
'KMB', 'KIM', 'KMI', 'KKR', 'KLAC', 'KHC', 'KR', 'LHX', 'LH', 'LRCX',
'LW', 'LVS', 'LDOS', 'LEN', 'LLY', 'LIN', 'LYV', 'LKQ', 'LMT', 'LII',
'L', 'LOW', 'LULU', 'LYB', 'MTB', 'TPL', 'MPC', 'MAR', 'MMC', 'MAS',
'MA', 'MTCH', 'MKC', 'MCD', 'MCK', 'MDT', 'MET', 'MTD', 'MGM', 'MCHP',
'MU', 'MSFT', 'MAA', 'MRNA', 'MHK', 'MOH', 'TAP', 'MDLZ', 'MPWR', 'MNST',
'MCO', 'MS', 'MOS', 'MSI', 'MSCI', 'NDAQ', 'NTAP', 'NFLX', 'NEM', 'NWSA',
'NWS', 'NEE', 'NKE', 'NI', 'NDSN', 'NSC', 'NTRS', 'NOC', 'NCLH', 'NRG',
'NUE', 'NVDA', 'NVR', 'NXPI', 'ORLY', 'OXY', 'ODFL', 'OMC', 'ON', 'OKE',
'ORCL', 'OTIS', 'PCAR', 'PKG', 'PLTR', 'PANW', 'Q', 'PSKY', 'PH', 'PAYX',
'PAYC', 'PYPL', 'PNR', 'PEP', 'PFE', 'PCG', 'PM', 'PSX', 'PNW', 'PNC',
'POOL', 'PPG', 'PPL', 'PFG', 'PG', 'PGR', 'PLD', 'PRU', 'PEG', 'PTC',
'PSA', 'PHM', 'APO', 'PWR', 'QCOM', 'DGX', 'RL', 'RJF', 'RTX', 'O',
'REG', 'REGN', 'RF', 'RSG', 'RMD', 'RVTY', 'ROK', 'ROL', 'ROP', 'ROST',
'RCL', 'SPGI', 'CRM', 'SBAC', 'SLB', 'STX', 'SRE', 'NOW', 'SHW', 'SPG',
'SWKS', 'SJM', 'SW', 'SNA', 'SOLV', 'SO', 'LUV', 'SWK', 'SBUX', 'STT',
'STLD', 'STE', 'SYK', 'SMCI', 'SYF', 'SNPS', 'SYY', 'TMUS', 'TROW', 'TTWO',
'TPR', 'TRGP', 'TGT', 'TEL', 'TDY', 'TER', 'TSLA', 'TXN', 'TXT', 'TMO',
'TJX', 'TSCO', 'TT', 'TDG', 'TRV', 'TRMB', 'TFC', 'TYL', 'TSN', 'USB',
'UBER', 'UDR', 'ULTA', 'UNP', 'UAL', 'UPS', 'URI', 'UNH', 'UHS', 'VLO',
'VTR', 'VRSN', 'VRSK', 'VZ', 'VRTX', 'VTRS', 'VICI', 'V', 'VST', 'VMC',
'WRB', 'GWW', 'WAB', 'WMT', 'DIS', 'WBD', 'WM', 'WAT', 'WEC', 'WFC',
'WELL', 'WST', 'WDC', 'WY', 'WMB', 'EXE', 'WTW', 'WYNN', 'XEL', 'XYL',
'YUM', 'ZBRA', 'ZBH', 'ZTS', 'APP', 'HOOD',
#
'AZN', 'ARM', 'CCEP', 'MELI', 'PDD', 'TEAM', 'MSTR', 'MDB', 'ZS', 'MRVL',
'SIRI',
#
'CSIQ', 'AA', 'IIPR', 'MP', 'BE', 'RDDT', 'SMR', 'RGTI', 'QBTS', 'OKLO',
'IONQ', 'NXE', 'CLS', 'ASML', 'GES', 'ILMN',
]

# Top ETFs (exact same as your Dart code - 37 ETFs)
TOP_ETFS = [
    # Original Top Performing ETFs (37)
    'WGMI', 'EUAD', 'SHLD', 'STCE', 'PSIL', 'BKCH', 'GREK', 'ARKW', 'EWY', 'KEMQ',
    'HYDR', 'UFO', 'CNXT', 'DAPP', 'BLOK', 'EWP', 'EPOL', 'CTEC', 'FGM', 'AFK', 'DECO',
    'ARKK', 'CHAT', 'BITQ', 'KSTR', 'SLVP', 'RING', 'GDX', 'SIL', 'URA', 'DMAT', 'COPJ',
    'NLR', 'BTGD', 'PPLT', 'IBLC', 'XME',
    
    # Additional ETFs from PDF (70)
    'AIA', 'ARKF', 'ARKO', 'BKF', 'BOTZ', 'CANE', 'CGW', 'CLNE', 'COPX', 'CORN',
    'CRBN', 'DBA', 'DBB', 'DBC', 'DIA', 'EEM', 'EFA', 'FLR', 'FXI', 'GLD',
    'GRNY', 'IBB', 'IBIT', 'ILF', 'INDA', 'ITB', 'IWD', 'IWM', 'IYR', 'IYT',
    'IZRL', 'MAGS', 'MJ', 'MOO', 'MTUM', 'OEF', 'OIH', 'PBW', 'PHO', 'PPA',
    'QQQ', 'ROBT', 'RSP', 'SMH', 'SOYB', 'SPY', 'TAN', 'UNG', 'VGK', 'VGT',
    'VT', 'VTI', 'VUG', 'VWO', 'WEAT', 'WOOD', 'XLB', 'XLC', 'XLE', 'XLF',
    'XLG', 'XLI', 'XLK', 'XLV', 'XLY', 'XLU', 'XLP', 'XLRE', 'XOP', 'XRT',
]

def get_all_symbols():
    """Get all symbols for download"""
    return {
        'TA125': TA125_STOCKS,
        'SP500': SP500_STOCKS,
        'ETFs': TOP_ETFS,
    }










