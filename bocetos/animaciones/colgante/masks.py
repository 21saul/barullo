import re, resvg_py, io, numpy as np
from PIL import Image
svg=open('/home/ddev/www/barullo/public/media/brand/emblema.svg').read()
paths=re.findall(r'<path[^>]*/>', svg)
head=svg.split('<path')[0]
N=3000
def ras(body):
    s=head+body+'</svg>'
    png=bytes(resvg_py.svg_to_bytes(svg_string=s, width=N, height=N))
    a=np.array(Image.open(io.BytesIO(png)).convert('RGBA'))[...,3]
    return a
ring=ras(paths[1].replace('#E63B2E','#fff'))
inner=ras(paths[0].replace('#0B0B0B','#fff'))
d=re.search(r'd="([^"]*)"',paths[2]).group(1)
letters_line=ras(f'<path d="{d}" fill="none" stroke="#fff" stroke-width="6.21" stroke-linejoin="round"/>')
letters_fill=ras(f'<path d="{d}" fill="#fff" fill-rule="evenodd" stroke="#fff" stroke-width="6.21" stroke-linejoin="round"/>')
letters_nz=ras(f'<path d="{d}" fill="#fff" fill-rule="nonzero" stroke="#fff" stroke-width="6.21" stroke-linejoin="round"/>')
for n,a in [('ring',ring),('inner',inner),('lline',letters_line),('lfill',letters_fill),('lnz',letters_nz)]:
    Image.fromarray(a).save(f'colg/m_{n}.png')
prev=np.concatenate([letters_fill,letters_nz],1)[900:2200, 1000:5000:1]
Image.fromarray(np.concatenate([letters_fill[700:2100,500:1600],letters_nz[700:2100,500:1600]],1)).resize((1100,700)).save('colg/prev_letters.png')
