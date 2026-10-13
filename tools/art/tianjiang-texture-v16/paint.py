"""Original, hand-arranged pixel clusters for the approved V15 surfaces.

No geometry, UV, external image, RNG, blur, PBR or baked studio reflection.
Material placement follows garment/armour roles; crescent tiles share a world
coordinate field so their joining faces do not become separate framed boxes.
"""
from PIL import Image, ImageDraw

PAL = {k:tuple(bytes.fromhex(v)) for k,v in {
 'ink':'1d2934', 'navy':'253848', 'cloth':'344c60', 'cloth_hi':'4a6375',
 'cloth_fold':'2b4053', 'iron_dark':'334957', 'iron':'637f8c',
 'iron_mid':'4c6575', 'iron_hi':'99b5bd', 'edge':'d6e2dc',
 'gold_dark':'715237', 'gold':'b18a50', 'gold_hi':'dec391',
 'gold_mid':'94713f', 'skin_dark':'785546', 'skin':'b08b6e',
 'skin_hi':'d0ae8b', 'skin_mid':'97725b', 'jade_dark':'285355',
 'jade':'4f9793', 'jade_hi':'a1c9b7', 'leather':'493c36',
 'leather_hi':'77604b', 'leather_dark':'322e30',
}.items()}

def paint(role,face,w,h,context=None):
 im=Image.new('RGB',(w,h),PAL['ink']);d=ImageDraw.Draw(im)
 def rect(x0,y0,x1,y1,c):
  if x1>=x0 and y1>=y0:d.rectangle((x0,y0,x1,y1),fill=PAL[c])
 def line(points,c,width=1):d.line(points,fill=PAL[c],width=width)
 def poly(points,c):d.polygon(points,fill=PAL[c])
 def point(x,y,c):d.point((x,y),fill=PAL[c])
 def fill(c):rect(0,0,w-1,h-1,c)
 front=face=='north';back=face=='south';side=face in ['east','west']
 cap=face in ['up','down']
 if role=='head':
  fill('iron_dark')
  if cap:
   if face=='up':
    rect(3,2,w-4,h-3,'iron_mid');line([(3,2),(w//2,1),(w-4,2)],'iron')
    line([(w//2,3),(w//2,h-4)],'gold_dark')
   return im
  # Brow, cheek guards and the unchanged exposed face. No added mask geometry.
  rect(1,0,w-2,4,'iron_mid');rect(3,1,w-4,3,'iron')
  line([(2,0),(5,0)],'iron_hi');line([(w-5,0),(w-3,0)],'iron_hi')
  line([(1,4),(5,4),(7,5),(8,5),(10,4),(w-2,4)],'gold')
  if front:
   rect(7,1,8,3,'gold');point(7,1,'gold_hi');point(8,3,'gold_dark')
   rect(7,2,8,2,'jade');point(7,2,'jade_hi')
   poly([(3,6),(5,5),(10,5),(12,6),(12,12),(10,14),(5,14),(3,12)],'skin_dark')
   poly([(5,7),(10,7),(11,9),(10,12),(9,13),(5,12)],'skin')
   rect(6,10,9,11,'skin_mid');line([(6,13),(9,13)],'skin_hi')
   # Angled brow shapes determine attention; tiny pale pixels stay non-emissive.
   line([(3,6),(5,6),(6,7)],'ink');line([(9,7),(10,6),(12,6)],'ink')
   rect(4,7,5,8,'skin_dark');rect(10,7,11,8,'skin_dark')
   point(5,7,'gold_hi');point(10,7,'gold_hi')
   line([(7,8),(7,10)],'skin_hi');point(8,10,'skin_dark')
   line([(6,12),(9,12)],'skin_dark')
   poly([(0,5),(2,6),(2,12),(4,14),(4,15),(0,15)],'iron_mid')
   poly([(15,5),(13,6),(13,12),(11,14),(11,15),(15,15)],'iron_mid')
   line([(1,6),(1,10),(3,13)],'iron');line([(14,6),(14,10),(12,13)],'iron')
   point(2,6,'iron_hi');point(13,6,'iron_hi')
  elif back:
   rect(3,5,w-4,h-3,'iron_mid');line([(w//2,5),(w//2,h-3)],'iron_dark')
   line([(4,6),(6,6)],'iron');line([(w-7,6),(w-5,6)],'iron')
   rect(0,h-3,w-1,h-1,'cloth_fold');line([(3,h-3),(3,h-1)],'cloth')
  else:
   poly([(2,5),(w-4,5),(w-3,10),(w-5,13),(3,13)],'iron_mid')
   poly([(3,6),(w-5,6),(w-6,10),(4,10)],'iron')
   line([(3,6),(6,6)],'iron_hi');rect(3,12,w-4,13,'iron_dark')
   line([(4,12),(6,12)],'gold_dark');rect(0,h-2,w-1,h-1,'cloth_fold')
 elif role=='torso':
  fill('cloth_fold')
  if cap:
   if face=='up':rect(3,1,w-4,h-2,'iron_dark')
   return im
  # Cloth is only in the neck, side panels and waist, not grey metal everywhere.
  rect(0,1,w-1,3,'cloth');line([(2,0),(4,3)],'cloth_hi')
  if front:
   poly([(1,5),(4,4),(11,4),(14,5),(14,13),(11,17),(4,17),(1,13)],'iron_dark')
   poly([(2,6),(5,5),(10,5),(13,6),(13,12),(10,16),(5,16),(2,12)],'iron_mid')
   poly([(3,6),(6,6),(6,15),(5,15),(3,12)],'iron')
   poly([(9,6),(12,6),(12,11),(10,14),(9,14)],'iron')
   line([(2,5),(5,4),(6,4)],'iron_hi');line([(10,4),(13,5)],'iron')
   # One identity centre: original thunder mark, worked into a broad cuirass.
   poly([(9,6),(6,10),(8,10),(6,14),(10,9),(8,9)],'gold_dark')
   poly([(8,6),(6,9),(8,9),(7,12),(10,8),(8,8)],'gold')
   line([(8,6),(7,7)],'gold_hi');line([(8,10),(7,12)],'gold_hi')
   # Subordinate cloud clasps and one scar are deliberately sparse.
   line([(3,9),(4,8),(5,8)],'iron_dark');line([(10,12),(11,12),(12,11)],'iron_mid')
   line([(3,13),(4,14)],'iron_hi');point(4,15,'iron_dark')
   line([(4,1),(7,3),(8,3),(11,1)],'gold_dark',2)
   line([(4,1),(7,2),(8,2),(11,1)],'gold');point(6,2,'gold_hi')
  elif back:
   poly([(2,4),(w-3,4),(w-3,13),(11,17),(4,17),(2,13)],'iron_dark')
   poly([(3,5),(12,5),(12,12),(10,15),(5,15),(3,12)],'iron_mid')
   line([(4,5),(7,4),(11,5)],'iron')
   line([(7,7),(5,9),(7,9),(9,7),(11,9)],'gold_dark')
   line([(5,11),(10,11)],'iron');line([(4,14),(6,15)],'iron_dark')
  elif side:
   rect(2,4,w-3,16,'cloth');line([(3,5),(3,14),(4,16)],'cloth_hi')
   line([(w-3,4),(w-4,8),(w-4,15)],'cloth_fold')
   rect(0,4,1,15,'iron_dark');line([(1,5),(1,11)],'iron_mid')
  rect(0,18,w-1,20,'leather');line([(0,18),(w-1,18)],'gold_dark')
  line([(1,20),(w-2,20)],'leather_dark')
  if front:
   rect(6,18,9,20,'gold_dark');rect(6,18,8,19,'gold');point(6,18,'gold_hi')
   point(3,19,'leather_hi');point(12,19,'leather_hi')
  rect(0,21,w-1,h-1,'navy');line([(3,21),(3,h-1)],'cloth_fold')
 elif role=='arm':
  fill('cloth_fold')
  if cap:
   if face=='up':
    fill('iron_mid');rect(1,1,w-2,h-2,'iron');line([(1,1),(w-3,1)],'iron_hi')
   else:fill('skin_dark')
   return im
  # Top shoulder plate has a sloped painted fold, not a rectangular white frame.
  rect(0,0,w-1,7,'iron_dark')
  poly([(1,1),(w-2,1),(w-1,3),(w-2,5),(1,6),(0,3)],'iron_mid')
  poly([(2,1),(w-3,1),(w-2,3),(w-3,4),(2,4)],'iron')
  line([(1,1),(3,0),(5,1)],'iron_hi')
  line([(0,6),(3,7),(w-1,6)],'gold_dark')
  if front or side:line([(1,5),(3,6),(5,6)],'gold');point(2,2,'iron_hi')
  rect(0,8,w-1,12,'cloth');line([(1,8),(2,10),(2,12)],'cloth_hi')
  line([(w-2,8),(w-3,11),(w-3,12)],'cloth_fold')
  poly([(1,13),(w-2,13),(w-1,15),(w-2,18),(1,18)],'iron_dark')
  poly([(2,14),(w-3,14),(w-2,15),(w-3,17),(2,17)],'iron_mid')
  line([(2,14),(4,14)],'iron');point(2,15,'iron_hi')
  line([(1,18),(w-2,18)],'gold_dark');line([(1,19),(w-2,19)],'gold')
  rect(0,20,w-1,h-1,'skin_dark')
  if front or side:
   rect(1,20,w-2,h-2,'skin');line([(2,20),(4,20)],'skin_hi');point(w-3,h-2,'skin_mid')
 elif role=='leg':
  fill('navy')
  if cap:
   if face=='down':fill('leather_dark')
   return im
  rect(1,1,w-2,10,'cloth_fold')
  line([(2,2),(2,7),(3,9)],'cloth');line([(w-3,3),(w-3,8)],'cloth')
  line([(0,11),(w-1,11)],'gold_dark')
  poly([(1,12),(w-2,12),(w-1,16),(w-2,20),(1,20),(0,16)],'iron_dark')
  poly([(2,13),(w-3,13),(w-2,16),(w-3,19),(2,19)],'iron_mid')
  line([(2,13),(3,13),(3,17)],'iron');point(2,13,'iron_hi')
  rect(0,21,w-1,h-1,'leather_dark');line([(1,21),(w-2,21)],'leather')
 elif role=='thigh':
  fill('iron_dark')
  if not cap:
   poly([(1,0),(w-2,0),(w-2,h-2),(w//2,h-1),(1,h-2)],'iron_mid')
   line([(1,0),(w-2,0)],'gold_dark');line([(2,1),(4,1)],'iron')
  else:fill('iron_mid')
 elif role in ['crown','socket','crossbar']:
  fill('gold_dark')
  if h>1:
   rect(0,0,w-1,max(0,h//2),'gold');line([(0,0),(max(0,w//2-1),0)],'gold_hi')
   if w>4 and h>3:
    line([(1,h-2),(w-2,h-2)],'gold_mid');point(w-2,1,'gold_dark')
  else:
   rect(0,0,w-1,0,'gold');rect(w//2,0,w-1,0,'gold_mid')
  if role=='socket' and front and w>=4 and h>=4:
   rect(w//2-1,2,w//2,h-3,'jade_dark');rect(w//2-1,2,w//2-1,h-4,'jade')
   point(w//2-1,2,'jade_hi')
 elif role=='crest':
  fill('iron_dark');rect(0,0,w-1,max(0,h//3),'iron_mid')
  line([(0,0),(w-1,0)],'gold');line([(0,2),(0,h-2)],'iron')
 elif role=='shaft':
  fill('iron_dark');line([(0,0),(0,h-1)],'iron_mid')
  for y in [4,h-9]:
   line([(0,y),(w-1,y)],'gold');line([(0,y+1),(w-1,y+1)],'gold_dark')
 elif role=='grip':
  fill('leather_dark')
  for y in range(1,h,3):
   line([(0,y+1),(w-1,y)],'leather');point(0,y+1,'leather_hi')
 else:
  fill('iron_dark')
  if front or back:
   origin=context['origin'];sz=context['size']
   # One field across the entire assembled moon blade, evaluated in model space.
   for y in range(h):
    for x in range(w):
     xx=origin[0]+((x+.5)/w if front else 1-(x+.5)/w)*sz[0]
     yy=origin[1]+(1-(y+.5)/h)*sz[1]
     c='iron_mid'
     if xx<-14.8:c='edge'
     elif xx<-14.2:c='iron_hi'
     elif xx<-12.6:c='iron'
     elif xx<-10.4:c='iron_mid'
     else:c='iron_dark'
     # The two hooks are folded steel, not black attachments. Their broad
     # stepped planes continue the blade field without framing each tile.
     if yy>43.3 and xx>-9:
      c='iron_mid' if yy<44.5+(xx+9)*.6 else 'iron'
     if yy<35.7 and xx>-9:
      c='iron_mid' if yy>34.5-(xx+9)*.5 else 'iron'
     # Broad facet bands join across tile borders, not repeated per-cube stripes.
     if xx<-11.5 and 40.5<yy<42.5:c='iron_hi' if xx<-13 else 'iron'
     if role in ['blade_tip_end','blade_hook_end']:
      end=y<1 if role=='blade_tip_end' else y>=h-1
      if end:c='edge'
     # A few purposeful chips on the real outer cutting edge.
     if xx<-14.8 and (37.4<yy<38.1 or 42.0<yy<42.4):c='iron_mid'
     # Recessed original command strokes, confined to the thick blade centre.
     if -11.8<xx<-11.1 and 36.5<yy<41:c='jade_dark'
     if -11.1<xx<-10.7 and 38.6<yy<40:c='jade'
     if -11.8<xx<-9.8 and 39.8<yy<40.3:c='jade'
     point(x,y,c)
   if role=='rear_tine':line([(0,0),(0,h-1)],'iron')
  elif face=='up':fill('iron')
  elif role=='blade_edge' and side:fill('iron_hi')
 return im
