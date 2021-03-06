# Default and past lists of DAQ failures and disconnections
DAQFAIL_PAST_NAME = 'daqfail_past.txt'
DISCONN_PAST_NAME = 'disconn_past.txt'

# FREQUENCY RANGES FOR PSD SEGMENTS
SEGMENT_FREQS = [
    (0.03, 0.1),
    (0.1, 0.3),
    (0.3, 1),
    (1, 3),
    (3, 10),
    (10, 30),
    (30, 100),
    (100, 300),
    (300, 1000),
    (1000, 3000)
]

# NUMBER OF SEGMENTS BY PSD LENGTH
NUM_SEGMENTS = {
    8: 5,
    16: 6,
    32: 7,
    64: 7,
    128: 8,
    256: 8,
    512: 9,
    1024: 10,
    2048: 10,
    4096: 11
}

# SEGMENT EDGES
SEGMENT_EDGES = [0, 36, 138, 174, 277, 313, 416, 452, 555, 591, 694, 730]

# SEGMENT END INDICES
SEGMENT_END_IDX = {
    8: 303,
    16: 344,
    32: 418,
    64: 434,
    128: 467,
    256: 532,
    512: 566,
    1024: 593,
    2048: 645,
    4096: 700,
    8192: 721
}

# ALPHA VALUE FOR EXPONENTIAL AVERAGING
ALPHA = 2 / (1+12)