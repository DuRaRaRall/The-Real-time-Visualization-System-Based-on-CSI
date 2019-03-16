import numpy as np

def usig2sig(b):
    if b > 127:
        return b
    else:
        return ~(b-128) + 1

def read_bfee(Bytes):
    timestamp_low = int.from_bytes(Bytes[0:4], 'little')
    bfee_count = int.from_bytes(Bytes[4:6], 'little')
    Nrx = Bytes[8]
    Ntx = Bytes[9]
    rssi_a = Bytes[10]
    rssi_b = Bytes[11]
    rssi_c = Bytes[12]
    noise = usig2sig(Bytes[13])
    agc = Bytes[14]
    antenna_sel = Bytes[15]
    len = int.from_bytes(Bytes[16:18], 'little')
    fake_rate_n_flags = int.from_bytes(Bytes[18:20], 'little')
    calc_len = int((30 * (Nrx * Ntx * 8 * 2 + 3) + 7) / 8)
    index = 0
    payload = Bytes[20:]
    csi = np.empty((Ntx, Nrx, 30), dtype=complex, order = 'C')
    perm = [((antenna_sel) & 0x3) + 1, ((antenna_sel >> 2) & 0x3) + 1, ((
            antenna_sel >> 4) & 0x3) + 1]
    if len != calc_len:
        print('Error: Wrong beamforming matrix size.')
        return
    
    for i in range(0, 30):
        index += 3
        remainder = index % 8;
        for j in range(0, Ntx):
            for k in range(0, Nrx):
                re = (payload[(int)(index/8)] >> remainder) | (payload[(int)(index/8)+1] << (8-remainder))
			       #printf("%d\n", tmp);
                im = (payload[(int)(index/8)+1] >> remainder) | (payload[(int)(index/8)+2] << (8-remainder))
                csi[j,k,i] = complex(re, im)
                index += 16
                   
 
    structure =[timestamp_low, bfee_count, Nrx, Ntx, rssi_a, rssi_b, rssi_c, 
                noise, agc, perm, fake_rate_n_flags, csi]
    return structure

'''                  
    st = np.dtype([('timestamp_low', 'I'), ('bfee_count', 'H'),
                   ('Nrx', 'B'), ('Ntx', 'B'), 
                   ('rssi_a', 'B'), ('rssi_b', 'B'), ('rssi_c', 'B'),
                   ('noise', 'B'), ('agc', 'B'),
                   ('perm', 'B'), ('rate', 'H'),
                   ('csi', 'complex64')])
    structure = np.array([(timestamp_low, bfee_count,
                           Nrx, Ntx, rssi_a, rssi_b, rssi_c,
                           noise, agc, perm, fake_rate_n_flags, csi)], dtype = st)
'''