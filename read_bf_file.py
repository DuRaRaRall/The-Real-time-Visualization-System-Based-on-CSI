import read_bfee, get_scaled_csi
import socket               # 导入 socket 模块
import numpy as np
import pyqtgraph as pg

#import ctypes

while True:
    win = pg.GraphicsWindow()
    p = win.addPlot()
    p.setLabel('left', "SNR", units='dB')  
    p.setLabel('bottom', "subcarrier index") 
    p.setRange(xRange = [0, 30], yRange=[-150, 0])
    p1 = p.plot(pen = 'r')
    p2 = p.plot(pen = 'y')
    p3 = p.plot(pen = 'b')
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # 创建 socket 对象
    host = socket.gethostname() # 获取本地主机名
    port = 8095                # 设置端口
    s.bind((host, port))        # 绑定端口
    
    s.listen(5)                 # 等待客户端连接
    print('waiting for connection on port', port)
    
    c, addr = s.accept()     # 建立客户端连接。
    c.settimeout(15)
    print('连接地址：', addr)
    fd = c.makefile('rb')
    
    #while True:
    
    csi_entry = [];
    index = -1;                     # The index of the plots which need shadowing
    broken_perm = 0;                # Flag marking whether we've encountered a broken CSI yet
    triangle = [1,3,6];             # What perm should sum to for 1,2,3 antennas
    current_index = 0
    p = np.zeros((30,30), dtype='double', order = 'C')

    while True:
        # Read size and code from the received packets
        '''
        s = warning('error', 'instrument:fread:unsuccessfulRead');
        try:
            #filed_len = unpack(fmt, string)
            field_len = data[0:2];
        except IOError:
            warning(s);
            print('Timeout, please restart the client and connect again.');
            break;
        '''
        try:
            fl = fd.read(2)
            field_len = int.from_bytes(fl, 'big')
            if field_len == 0:
                break
        except:
            print('Timeout, please restart the client and connect again.');
            break
        co = fd.read(1)
        if not isinstance(co, int):
            code = int.from_bytes(co, 'big')
        else:
            code = co
      
        # If unhandled code, skip (seek over) the record and continue
        
        if code == 187:           # get beamforming or phy data
            Bytes = fd.read(field_len-1)
            if len(Bytes) != field_len-1:
                c.close()
                exit()
             
        elif field_len <= 1024: # skip all other info
            fd.read(field_len-1)
            continue;
        else:
            continue;
            
        if code == 187:
            csi_entry = read_bfee.read_bfee(Bytes);
            if not csi_entry:
                print('Error: malformed packet')
                exit()
                
            perm = csi_entry[9];
            Nrx = csi_entry[2];
            if Nrx > 1:
                if sum(perm) != triangle[Nrx-1]:
                    if broken_perm == 0:
                        broken_perm = 1
                        print('WARN ONCE: Found CSI with Nrx=', Nrx, ' and invalid perm=\n')
                    else:
                        csi_entry[11][:,perm[0:Nrx],:] = csi_entry[11][:,0:Nrx,:]
			
            csi = get_scaled_csi.get_scaled_csi(csi_entry)
            
            x = np.arange(30)
            p1.setData(x, get_scaled_csi.db(abs(csi[0,0,:].flatten())));
            p2.setData(x, get_scaled_csi.db(abs(csi[0,1,:].flatten())));
            p3.setData(x, get_scaled_csi.db(abs(csi[0,2,:].flatten())));
            
            pg.QtGui.QApplication.processEvents()

            csi_entry = []
        
    c.close()                # 关闭连接
    pg.QtGui.QApplication.closeAllWindows()
