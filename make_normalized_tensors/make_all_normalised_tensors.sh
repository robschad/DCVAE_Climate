#!/usr/bin/bash

# Make all the normalized tensors
# Requires pre-made normalization parameters.

(cd ERA5 && ./make_all_tensors.py --variable=tas)
(cd ERA5 && ./make_all_tensors.py --variable=ts)
(cd ERA5 && ./make_all_tensors.py --variable=psl)
(cd ERA5 && ./make_all_tensors.py --variable=pr)
