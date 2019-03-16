#import struct
import read_bfee, get_scaled_csi
import socket               # 导入 socket 模块
import numpy as np
#import matplotlib.pyplot as plt
#import matplotlib.animation as animation
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
            #print('fuze')
            #print(data)
            #fl = data[current_index : current_index+2]
            fl = fd.read(2)
            #print(type(fl),len(fl))            
            field_len = int.from_bytes(fl, 'big')
            if field_len == 0:
                break
            #current_index += 2
        except:
            print('Timeout, please restart the client and connect again.');
            break
        #print(field_len)
        #co = data[current_index]
        co = fd.read(1)
        #print(type(co))
        if not isinstance(co, int):
            code = int.from_bytes(co, 'big')
        else:
            code = co
      
        #print(code)
        #current_index += 1
        # If unhandled code, skip (seek over) the record and continue
        
        if code == 187:           # get beamforming or phy data
            
            #bytes = data[3:3+field_len-1]
            #fread(t, field_len-1, 'uint8');
            #Bytes = data[current_index: current_index+field_len-1]
            #current_index += field_len - 1
            #print(current_index)
            Bytes = fd.read(field_len-1)
            if len(Bytes) != field_len-1:
                c.close()
                exit()
             
        elif field_len <= 1024: # skip all other info
            fd.read(field_len-1)
            #current_index += field_len - 1
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

#            index = (index + 1) % 10
            
            csi = get_scaled_csi.get_scaled_csi(csi_entry)
            
#            p[index*3] = get_scaled_csi.db(abs(csi[1,1,:].flatten()));
#            p[index*3+1] = get_scaled_csi.db(abs(csi[1,2,:].flatten()));
#            p[index*3+2] = get_scaled_csi.db(abs(csi[1,3,:].flatten()));
            
            x = np.arange(30)
            p1.setData(x, get_scaled_csi.db(abs(csi[0,0,:].flatten())));
            p2.setData(x, get_scaled_csi.db(abs(csi[0,1,:].flatten())));
            p3.setData(x, get_scaled_csi.db(abs(csi[0,2,:].flatten())));

#            plt.close('all')
#            for i in range(0,10):
#                plt.plot(p[i*3], 'r')
#                plt.plot(p[i*3+1], 'b')
#                plt.plot(p[i*3+2], 'g')\
            
            pg.QtGui.QApplication.processEvents()

            csi_entry = []
        
    c.close()                # 关闭连接
    pg.QtGui.QApplication.closeAllWindows()
    
    
    
    
    
    
    '''
        if code == 187: # (tips: 187 = hex2dec('bb')) Beamforming matrix -- output a record
            ll = ctypes.cdll.LoadLibrary   
            lib = ll("./read_bfee.so")
            csi_entry = read_bfee(bytes);
        
            perm = csi_entry.perm
            Nrx = csi_entry.Nrx
            
            if Nrx > 1: # No permuting needed for only 1 antenna
                if sum(perm) != triangle(Nrx): # matrix does not contain default values
                    if broken_perm == 0:
                        broken_perm = 1
                        print('WARN ONCE: Found CSI (%s) with Nrx=%d and invalid perm=[%s]\n', filename, Nrx, int2str(perm))
                else:
                    csi_entry.csi(:,perm(1:Nrx),:) = csi_entry.csi(:,1:Nrx,:)
    
        index = mod(index+1, 10);
        
        csi = get_scaled_csi(csi_entry) #CSI data
	#You can use the CSI data here.

	#This plot will show graphics about recent 10 csi packets
    
        set(p(index*3 + 1),'XData', [1:30], 'YData', db(abs(squeeze(csi(1,1,:)).')), 'color', 'b', 'linestyle', '-');
        if Nrx > 1
            set(p(index*3 + 2),'XData', [1:30], 'YData', db(abs(squeeze(csi(1,2,:)).')), 'color', 'g', 'linestyle', '-');
        end
        if Nrx > 2
            set(p(index*3 + 3),'XData', [1:30], 'YData', db(abs(squeeze(csi(1,3,:)).')), 'color', 'r', 'linestyle', '-');
        end
        axis([1,30,-10,40]);
        drawnow;
 
        csi_entry = [];
    end
%% Close file
    fclose(t);
    delete(t);
end 
    '''
    
    

    