import numpy as np
from PIL import Image
from scipy import ndimage as ndi
R=lambda n: np.array(Image.open(f'colg/m_{n}.png')).astype(np.float32)/255
ring,inner,let=R('ring'),R('inner'),R('lfill')
N=ring.shape[0]; pad=int(round((50/42.1-1)/2*N)); M=N+2*pad
P=lambda a: np.pad(a,pad)
ring,inner,let=P(ring),P(inner),P(let)
relief=np.clip(ring+let,0,1)
# rounded bevel: distance-based profile
d=ndi.distance_transform_edt(relief>0.5)
prof=np.clip(d/7.0,0,1); prof=np.sin(prof*np.pi/2)
h=ndi.gaussian_filter(prof,1.2)
Image.fromarray((h*65535).astype(np.uint16)).save('colg/medal_height.png')
inner_only=np.clip(inner-let,0,1)
mask=np.stack([relief, inner_only, np.clip(1-relief-inner,0,1)],-1)
Image.fromarray((mask*255).astype(np.uint8)).save('colg/medal_mask.png')
print(M, pad)
Image.fromarray((h*255).astype(np.uint8)).resize((800,800)).save('colg/prev_height.png')
