from pathlib import Path
import onnxruntime as ort,numpy as np,soundfile as sf
from scipy.signal import stft,istft,get_window
R=Path('/workspace/seminuevos-01-v4/music-reference');sr=44100;nfft=6144;hop=1024;N=hop*255;step=N//2;win=get_window('hann',nfft,fftbins=True);norm=win.sum()
x,sr=sf.read(R/'reference.wav',dtype='float32');original=len(x);x=x.T;pad=N//2;x=np.pad(x,((0,0),(pad,pad+N)));out=np.zeros_like(x);weight=np.zeros(x.shape[1]);opts=ort.SessionOptions();opts.intra_op_num_threads=3;opts.inter_op_num_threads=1;s=ort.InferenceSession(str(R/'model.onnx'),sess_options=opts,providers=['CPUExecutionProvider']);env=np.hanning(N).astype(np.float32)
for start in range(0,x.shape[1]-N+1,step):
 chunk=x[:,start:start+N];_,_,z=stft(chunk,fs=sr,window=win,nperseg=nfft,noverlap=nfft-hop,nfft=nfft,boundary='zeros',padded=False);z=z*norm
 spec=np.stack((z.real,z.imag),axis=1).reshape(1,4,nfft//2+1,256)[:,:,:3072,:].astype(np.float32)
 pred=s.run(None,{'input':spec})[0].reshape(2,2,3072,256);p=pred[:,0]+1j*pred[:,1];p=np.pad(p,((0,0),(0,1),(0,0)))
 _,y=istft(p/norm,fs=sr,window=win,nperseg=nfft,noverlap=nfft-hop,nfft=nfft,input_onesided=True,boundary=True)
 out[:,start:start+N]+=y[:,:N]*env;weight[start:start+N]+=env;print(start/sr,flush=True)
y=out/np.maximum(weight,1e-8);y=y[:,pad:pad+original].T;sf.write(R/'instrumental.wav',y,sr,subtype='FLOAT');sf.write(R/'removed.wav',x[:,pad:pad+original].T-y,sr,subtype='FLOAT');print('DONE',flush=True)
