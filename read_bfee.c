void read_bfee(unsigned char *inBytes, mxArray *outCell)
{
	unsigned int timestamp_low = inBytes[0] + (inBytes[1] << 8) +
		(inBytes[2] << 16) + (inBytes[3] << 24);
	unsigned short bfee_count = inBytes[4] + (inBytes[5] << 8);
	unsigned int Nrx = inBytes[8];
	unsigned int Ntx = inBytes[9];
	unsigned int rssi_a = inBytes[10];
	unsigned int rssi_b = inBytes[11];
	unsigned int rssi_c = inBytes[12];
	char noise = inBytes[13];
	unsigned int agc = inBytes[14];
	unsigned int antenna_sel = inBytes[15];
	unsigned int len = inBytes[16] + (inBytes[17] << 8);
	unsigned int fake_rate_n_flags = inBytes[18] + (inBytes[19] << 8);
	unsigned int calc_len = (30 * (Nrx * Ntx * 8 * 2 + 3) + 7) / 8;
	unsigned int i, j;
	unsigned int index = 0, remainder;
	unsigned char *payload = &inBytes[20];
	char tmp;
	mwSize size[] = {Ntx, Nrx, 30};
	mxArray *csi = mxCreateNumericArray(3, size, mxDOUBLE_CLASS, mxCOMPLEX);
	mwSize perm_size[] = {1, 3};
	mxArray *perm = mxCreateNumericArray(2, perm_size, mxDOUBLE_CLASS, mxREAL);
	double* ptrR = (double *)mxGetPr(csi);
	double* ptrI = (double *)mxGetPi(csi);

	/* Check that length matches what it should */
	if (len != calc_len)
		mexErrMsgIdAndTxt("MIMOToolbox:read_bfee_new:size","Wrong beamforming matrix size.");

	/* Compute CSI from all this crap :) */
	for (i = 0; i < 30; ++i)
	{
		index += 3;
		remainder = index % 8;
		for (j = 0; j < Nrx * Ntx; ++j)
		{
			tmp = (payload[index / 8] >> remainder) |
				(payload[index/8+1] << (8-remainder));
			//printf("%d\n", tmp);
			*ptrR = (double) tmp;
			++ptrR;
			tmp = (payload[index / 8+1] >> remainder) |
				(payload[index/8+2] << (8-remainder));
			*ptrI = (double) tmp;
			++ptrI;
			index += 16;
		}
	}

	/* Compute the permutation array */
	ptrR = (double *)mxGetPr(perm);
	ptrR[0] = ((antenna_sel) & 0x3) + 1;
	ptrR[1] = ((antenna_sel >> 2) & 0x3) + 1;
	ptrR[2] = ((antenna_sel >> 4) & 0x3) + 1;
}
