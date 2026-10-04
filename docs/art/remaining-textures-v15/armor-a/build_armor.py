#!/usr/bin/env python3
"""Original native-grid armor A candidates. NEVER writes src or other sets.

32x32 inventory silhouettes and 64x32 worn UVs are authored independently.
Shared pixel tools do not imply a shared/recolored design; each material has
its own silhouette, seam topology, core and surface organization.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import argparse,hashlib,json,shutil

D=Path(__file__).resolve().parent
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
S=ROOT/'src/main/resources/assets/dynasty'
A=D/'candidate/assets/dynasty/textures'
SETS=['cloth','bamboo','leather','brocade','silver','cinnabar','dragon_scale','sea_silk','phoenix','qilin','draco_king']
PIECES=['helmet','chestplate','leggings','boots']
PROTECTED=['general','jade','sky','bronze','xuantian']
# a outline; b shadow; c base; d light; e restrained edge; f/g/h binding;
# i/j/k ornament dark/base/light. Every RGB swatch is deliberately chosen.
HEX={
'cloth':['353e41','596368','7b8588','a1aaa5','c0c5b5','504b3e','81765c','afa185','505c61','737e80','a1aaa5'],
'bamboo':['2f3d29','53613a','778a4c','a0ad65','c1c782','53432d','89704c','b69b68','485431','76874b','a6b575'],
'leather':['352a24','634333','91634a','b58a63','d1ae7a','403b32','82745d','b1a17b','583b31','805344','b4865e'],
'brocade':['322735','594051','865767','ad7a86','c99e9f','60482f','ad8751','d4b577','4b3345','85566b','be8595'],
'silver':['29333d','465867','708693','a1b3b8','ced4c7','35484d','68828a','a2b9b3','315856','5d8d82','a0c7ad'],
'cinnabar':['38282a','683b38','a35643','c78160','dcac83','595241','a29160','cbb880','55272d','8c4145','b86358'],
'dragon_scale':['223a37','34524a','4a7565','75a082','9db89b','574733','9a7b48','c2a467','24494f','427d82','87b6b1'],
'sea_silk':['273e49','426773','648c97','92b6b8','bed1c6','45564f','7d9481','bac4a2','315566','568d9a','9dc5c4'],
'phoenix':['482e2c','794637','aa6948','cc9560','e0be80','63472b','af8b48','d4b973','732f32','ac5050','d88366'],
'qilin':['293e3a','466858','6a9277','9cb797','c3ceb0','655738','a99460','d0c18c','324e52','54858a','9fc0b0'],
'draco_king':['2c2d3e','4a4565','6c6287','9586aa','b5a6be','594a37','aa8952','d1b776','234b4e','458487','95c1b3'],
}
PALETTES={k:{chr(97+i):tuple(bytes.fromhex(v))+(255,) for i,v in enumerate(vals)} for k,vals in HEX.items()}
DESIGN={
'cloth':'交领布衫、软帽与缠布靴；宽布褶、短缝线，不使用金属宝石。',
'bamboo':'纵向竹片和两道横扎绳；方肩护条、分节护膝，与布甲结构不同。',
'leather':'短皮坎肩、斜背带与三枚扣结；厚护膝、折口皮靴。',
'brocade':'交领锦衣、窄金线包边、两组团花；帽沿与裤腿刺绣留出布面。',
'silver':'中脊白银板甲、分段肩片、冷青小扣；大面积中灰，边缘才使用银亮色。',
'cinnabar':'朱砂漆甲、竖向符纸护带和横叠护片；明亮符纸只占局部。',
'dragon_scale':'青绿错层龙鳞、铜护边、短翼肩片；鳞片成簇而非随机细点。',
'sea_silk':'鲛绡折领、弧形襟线、横向波褶；小贝扣与柔软分叉下摆。',
'phoenix':'斜向羽片与V形覆胸、三阶冠沿、扇形肩羽；赭金、暗红与受控羽梢亮色。',
'qilin':'玉绿菱形大鳞、浅角色中脊与肩片；少量青玉铆接区别龙鳞甲。',
'draco_king':'紫灰厚甲、倒V胸肋与三阶冠、铜边和小型海玉核；较宽护肩与分层腰甲。',
}

class Pix:
    def __init__(self,style,size=(32,32)):
        self.p=PALETTES[style];self.im=Image.new('RGBA',size);self.d=ImageDraw.Draw(self.im)
    def r(self,box,c): self.d.rectangle(box,fill=self.p[c] if c else (0,0,0,0))
    def poy(self,pts,c): self.d.polygon(pts,fill=self.p[c] if c else (0,0,0,0))
    def l(self,pts,c,width=1): self.d.line(pts,fill=self.p[c],width=width)
    def pt(self,x,y,c): self.d.point((x,y),fill=self.p[c])
    def tile(self,x,y,rows):
        assert len(set(map(len,rows)))==1
        im=Image.new('RGBA',(len(rows[0]),len(rows)))
        im.putdata([self.p[c] if c!='.' else (0,0,0,0) for r in rows for c in r])
        self.im.paste(im,(x,y))

def scale_cluster(p,x,y,w=4):
    p.l([(x,y),(x+w-1,y)],'a')
    p.l([(x,y+1),(x,y+2),(x+1,y+3),(x+w-2,y+3),(x+w-1,y+2),(x+w-1,y+1)],'b')
    p.l([(x+1,y+1),(x+w-2,y+1)],'d')
    p.l([(x+1,y+2),(x+w-2,y+2)],'c')

def gem(p,x,y):
    p.poy([(x,y-2),(x+2,y),(x,y+2),(x-2,y)],'f')
    p.poy([(x,y-1),(x+1,y),(x,y+1),(x-1,y)],'j');p.pt(x,y-1,'k')

def dragon_icon(piece):
    p=Pix('dragon_scale')
    if piece=='chestplate':
        p.poy([(3,6),(7,4),(11,5),(12,8),(14,10),(17,10),(19,8),(20,5),(24,4),(28,6),(29,10),(27,15),(24,16),(24,25),(22,29),(9,29),(7,25),(7,16),(4,15),(2,10)],'a')
        p.poy([(9,10),(12,11),(19,11),(22,10),(23,23),(21,28),(10,28),(8,23)],'c')
        p.l([(10,6),(12,9),(14,11),(17,11),(19,9),(21,6)],'g')
        p.l([(11,6),(12,8),(14,10),(17,10),(19,8),(20,6)],'h')
        for flip in [False,True]:
            def pts(q):return [(31-x if flip else x,y) for x,y in q]
            p.poy(pts([(3,7),(7,5),(10,6),(10,10),(8,13),(4,12)]),'g')
            p.poy(pts([(4,7),(7,6),(9,7),(8,10),(5,11)]),'d' if not flip else 'c')
            p.l(pts([(4,13),(7,15),(10,13)]),'g')
            p.l(pts([(5,13),(7,14),(9,12)]),'d')
        for y,xs in [(12,[10,17]),(16,[9,14,19]),(20,[11,16])]:
            for x in xs: scale_cluster(p,x,y,4)
        gem(p,15,12)
        p.l([(9,24),(22,24)],'a');p.l([(10,25),(21,25)],'g')
        p.l([(11,26),(14,27),(15,26)],'d');p.l([(16,26),(18,27),(20,26)],'c')
        p.l([(10,28),(13,28)],'g');p.l([(18,28),(21,28)],'g')
    elif piece=='helmet':
        p.poy([(6,9),(9,6),(12,5),(13,3),(18,3),(19,5),(22,6),(25,9),(26,16),(24,25),(20,27),(19,19),(12,19),(11,27),(7,25),(5,16)],'a')
        p.poy([(7,10),(10,7),(14,6),(17,6),(22,8),(24,11),(24,17),(7,17)],'c')
        for x,y in [(9,9),(16,9),(12,13)]:scale_cluster(p,x,y,5)
        p.poy([(6,6),(6,3),(8,4),(10,8),(9,10),(7,9)],'g');p.pt(6,3,'h')
        p.poy([(25,6),(25,3),(23,4),(21,8),(22,10),(24,9)],'g');p.pt(25,3,'h')
        p.l([(7,17),(12,16),(19,16),(24,17)],'g');p.l([(8,17),(12,17),(19,17),(23,17)],'h')
        p.r((12,18,19,23),None)
        p.poy([(7,18),(10,19),(10,24),(8,24)],'d');p.poy([(21,19),(24,18),(23,24),(21,24)],'c')
        p.l([(8,25),(10,26)],'g');p.l([(21,26),(23,25)],'g');gem(p,15,9)
    elif piece=='leggings':
        p.poy([(7,4),(24,4),(25,11),(23,16),(23,28),(17,29),(16,17),(15,17),(14,29),(8,28),(8,16),(6,11)],'a')
        p.r((8,5,23,9),'g');p.l([(9,6),(22,6)],'h');gem(p,15,7)
        p.poy([(8,10),(23,10),(21,16),(17,15),(15,13),(12,16),(9,15)],'c')
        for x in (9,18):
            p.r((x,14,x+4,27),'c');scale_cluster(p,x,14,5);scale_cluster(p,x,19,5)
            p.l([(x,25),(x+4,25)],'g');p.l([(x+1,26),(x+3,26)],'d');p.l([(x,28),(x+4,28)],'g')
        p.l([(15,10),(15,13)],'a')
    else:
        for flip in [False,True]:
            def pts(q):return [(31-x if flip else x,y) for x,y in q]
            p.poy(pts([(6,5),(13,5),(14,20),(14,27),(3,27),(3,23),(5,21)]),'a')
            p.poy(pts([(7,7),(12,7),(12,24),(5,24),(6,21)]),'c')
            p.l(pts([(6,6),(12,6)]),'h');p.l(pts([(6,8),(12,8)]),'g')
            p.l(pts([(7,10),(11,10),(12,12),(10,14),(8,14),(7,12)]),'d')
            p.l(pts([(7,15),(11,15),(12,17),(10,19),(8,19),(7,17)]),'b')
            p.l(pts([(8,16),(10,16)]),'d')
            p.l(pts([(5,23),(12,23)]),'g');p.l(pts([(4,25),(12,25)]),'b')
    return p.im

CHEST_SHAPES={
'cloth':[(5,7),(10,5),(12,7),(15,10),(18,7),(20,5),(26,7),(29,13),(25,16),(23,14),(23,27),(8,27),(8,14),(6,16),(2,13)],
'bamboo':[(3,7),(8,5),(11,5),(12,9),(19,9),(20,5),(24,5),(28,7),(28,14),(24,15),(24,28),(7,28),(7,15),(3,14)],
'leather':[(4,8),(10,5),(12,6),(13,9),(18,9),(19,6),(21,5),(27,8),(29,13),(24,16),(23,27),(21,29),(10,29),(8,27),(7,16),(2,13)],
'brocade':[(3,8),(9,4),(11,5),(13,9),(16,11),(19,7),(21,4),(27,8),(30,15),(25,18),(23,15),(24,28),(8,28),(8,15),(6,18),(1,15)],
'silver':[(2,7),(6,4),(10,4),(12,8),(14,9),(17,9),(19,8),(21,4),(25,4),(29,7),(28,13),(25,15),(24,24),(22,28),(9,28),(7,24),(6,15),(3,13)],
'cinnabar':[(3,6),(10,5),(12,7),(13,10),(18,10),(20,6),(22,5),(28,6),(29,14),(24,16),(24,28),(7,28),(7,16),(2,14)],
'sea_silk':[(5,7),(10,4),(12,5),(14,9),(17,9),(20,5),(22,4),(26,7),(29,14),(25,16),(23,14),(24,26),(21,29),(17,28),(15,29),(10,28),(7,26),(8,14),(6,16),(2,14)],
'phoenix':[(1,5),(7,7),(10,4),(12,7),(13,10),(18,10),(20,6),(22,4),(25,7),(30,5),(28,13),(24,17),(24,24),(21,29),(16,27),(11,29),(7,24),(7,17),(3,13)],
'qilin':[(2,8),(5,4),(10,4),(12,7),(12,9),(19,9),(20,6),(22,4),(26,4),(29,8),(28,14),(24,16),(24,26),(21,29),(10,29),(7,26),(7,16),(3,14)],
'draco_king':[(1,7),(5,3),(10,4),(12,6),(12,9),(14,11),(17,11),(19,9),(19,6),(22,4),(26,3),(30,7),(29,14),(25,16),(25,24),(22,29),(9,29),(6,24),(6,16),(2,14)],
}

def icon(style,piece):
    p=Pix(style)
    if piece=='chestplate':
        p.poy(CHEST_SHAPES[style],'a')
        p.poy([(9,9),(13,11),(18,11),(22,9),(23,25),(21,27),(10,27),(8,25)],'c')
        if style=='cloth':
            p.poy([(5,8),(9,7),(11,10),(9,13),(6,14),(4,12)],'c');p.poy([(21,7),(26,8),(28,12),(25,14),(22,11)],'b')
            p.l([(10,7),(14,12),(19,16)],'e');p.l([(20,7),(18,11),(11,20)],'b',2)
            p.l([(20,8),(18,12),(12,19)],'d');p.r((9,21,22,23),'f');p.r((14,21,17,23),'g')
            p.l([(10,13),(10,18)],'d');p.l([(21,16),(21,20)],'b');p.l([(10,25),(14,25)],'d');p.l([(18,25),(21,25)],'b')
            for x in (9,12,19,22):p.pt(x,26,'b')
        elif style=='bamboo':
            p.r((4,7,10,13),'b');p.r((21,7,27,13),'b')
            for x in [5,8,22,25]:p.r((x,7,x+1,12),'d');p.pt(x,8,'e')
            for x in [9,12,15,18,21]:
                p.r((x,11,x+1,25),'d');p.l([(x+1,11),(x+1,25)],'c');p.pt(x,12,'e')
            p.l([(8,14),(23,14)],'f');p.l([(8,15),(23,15)],'h');p.l([(8,21),(23,21)],'f');p.l([(8,22),(23,22)],'g')
            p.l([(8,27),(23,27)],'g');p.r((14,20,17,23),'f');p.l([(15,21),(16,22)],'h')
        elif style=='leather':
            p.poy([(5,9),(9,7),(11,10),(9,14),(5,13)],'d');p.poy([(21,7),(26,9),(27,13),(23,14),(20,10)],'b')
            p.l([(11,7),(13,10),(16,12),(19,10),(20,7)],'d')
            p.poy([(9,11),(11,11),(22,20),(22,23),(20,22),(9,14)],'f')
            p.l([(10,12),(21,21)],'g');p.r((15,15,18,18),'a');p.r((16,16,17,17),'h')
            p.r((9,23,22,25),'f');p.r((13,23,16,25),'g');p.pt(14,24,'h')
            for x,y in [(9,17),(10,20),(22,12)]:p.pt(x,y,'h')
            p.l([(10,27),(14,27)],'d');p.l([(18,26),(21,26)],'b')
        elif style=='brocade':
            p.poy([(4,9),(8,7),(11,10),(9,14),(6,16),(3,14)],'c');p.poy([(23,7),(27,9),(29,14),(26,16),(23,14),(20,10)],'b')
            p.l([(10,6),(14,12),(20,17)],'g',2);p.l([(11,6),(15,12),(21,17)],'h')
            p.l([(20,7),(18,12),(11,21)],'f',2);p.l([(21,7),(19,12),(12,21)],'g')
            for x,y in [(10,13),(20,20)]:
                p.l([(x,y-1),(x+2,y+1),(x,y+3),(x-2,y+1),(x,y-1)],'d');p.pt(x,y+1,'g')
            p.r((9,23,22,24),'g');p.r((14,23,17,25),'h');p.l([(16,25),(16,27)],'f')
            p.l([(4,14),(6,16),(8,14)],'g');p.l([(24,14),(26,16),(28,14)],'g')
        elif style=='silver':
            for flip in [False,True]:
                tx=lambda pts:[(31-x if flip else x,y) for x,y in pts]
                p.poy(tx([(3,8),(6,5),(9,5),(11,9),(9,13),(5,13)]),'b')
                p.poy(tx([(4,8),(7,6),(9,7),(9,10),(6,12),(4,11)]),'d')
                p.l(tx([(5,7),(8,6)]),'e');p.l(tx([(5,14),(8,15),(10,13)]),'c')
            p.poy([(10,12),(14,11),(15,13),(15,20),(11,18),(9,16)],'d');p.poy([(17,11),(21,12),(22,16),(20,18),(16,20),(16,13)],'c')
            p.l([(10,12),(13,12)],'e');p.l([(16,12),(16,20)],'b')
            gem(p,16,12)
            for y in [21,24]:p.l([(9,y),(15,y+1),(22,y)],'b');p.l([(10,y+1),(15,y+2),(21,y+1)],'d')
            p.l([(10,27),(21,27)],'g')
        elif style=='cinnabar':
            p.r((4,7,10,13),'b');p.r((21,7,27,13),'b');p.l([(4,7),(10,7)],'d');p.l([(21,7),(27,7)],'c')
            for y in (13,17,21):p.l([(9,y),(22,y)],'a');p.l([(10,y+1),(21,y+1)],'d')
            for x in [10,20]:
                p.r((x,9,x+2,21),'f');p.r((x,10,x+1,20),'h');p.l([(x,12),(x+1,13),(x,14),(x+1,16),(x,18)],'i')
            p.r((13,24,18,25),'g');p.r((15,23,16,26),'h');p.l([(9,27),(12,27)],'d');p.l([(19,27),(22,27)],'c')
        elif style=='sea_silk':
            p.poy([(5,8),(9,6),(12,10),(10,14),(7,14),(4,12)],'d');p.poy([(22,6),(26,8),(28,12),(25,14),(22,14),(19,10)],'c')
            p.l([(11,6),(13,9),(15,11),(17,11),(20,8)],'e');p.l([(11,8),(14,12),(18,12),(21,9)],'g')
            for y in [15,20]:
                p.l([(9,y),(12,y+2),(18,y+2),(22,y)],'b');p.l([(10,y),(13,y+1),(17,y+1),(20,y)],'d')
            p.poy([(10,24),(14,25),(14,27),(11,26)],'d');p.poy([(17,25),(21,24),(20,27),(17,27)],'b')
            gem(p,16,14);p.l([(23,11),(25,13)],'e');p.l([(7,11),(9,13)],'e')
        elif style=='phoenix':
            for flip in [False,True]:
                tx=lambda pts:[(31-x if flip else x,y) for x,y in pts]
                p.poy(tx([(2,7),(7,9),(9,6),(11,10),(8,15),(4,12)]),'g')
                p.l(tx([(3,8),(7,11),(9,8)]),'h');p.l(tx([(5,11),(8,13),(10,11)]),'d')
                p.l(tx([(5,14),(8,16),(10,13)]),'c')
            for y in [12,16,20]:
                p.poy([(9,y),(15,y+3),(22,y),(20,y+4),(16,y+6),(11,y+4)],'b')
                p.l([(10,y),(15,y+3),(21,y)],'d');p.l([(11,y+2),(15,y+4),(20,y+2)],'g')
            gem(p,16,13);p.l([(11,27),(15,25),(20,27)],'h')
        elif style=='qilin':
            p.poy([(3,9),(6,5),(10,6),(11,10),(8,14),(4,13)],'g');p.poy([(21,6),(25,5),(28,9),(27,13),(23,14),(20,10)],'g')
            p.poy([(5,9),(7,7),(9,9),(7,12)],'e');p.poy([(22,9),(24,7),(26,9),(24,12)],'d')
            for x,y in [(12,13),(19,13),(15,18)]:
                p.poy([(x,y-2),(x+3,y),(x,y+3),(x-3,y)],'b');p.l([(x-2,y),(x,y-1),(x+2,y)],'d');p.l([(x,y),(x,y+2)],'c')
            p.l([(15,10),(15,16)],'h');gem(p,16,11)
            p.l([(9,22),(14,24),(17,24),(22,22)],'g');p.l([(10,23),(14,25),(17,25),(21,23)],'h')
            p.l([(10,27),(13,28)],'d');p.l([(18,28),(21,27)],'c')
        elif style=='draco_king':
            for flip in [False,True]:
                tx=lambda pts:[(31-x if flip else x,y) for x,y in pts]
                p.poy(tx([(2,8),(6,4),(9,5),(11,8),(10,13),(7,15),(3,12)]),'g')
                p.poy(tx([(4,8),(6,6),(9,7),(9,11),(6,13),(4,11)]),'d' if not flip else 'c')
                p.l(tx([(4,8),(6,6),(8,7)]),'h');p.l(tx([(4,14),(7,16),(10,14)]),'b')
            for y in [13,18,23]:
                p.l([(9,y+2),(15,y),(22,y+2)],'a',2);p.l([(10,y+2),(15,y+1),(21,y+2)],'d')
            p.l([(9,12),(9,23)],'g');p.l([(22,12),(22,23)],'g');gem(p,16,14)
            p.r((13,25,18,27),'f');p.r((14,25,17,26),'h');p.pt(16,26,'j')
            p.l([(10,28),(13,28)],'g');p.l([(18,28),(21,28)],'g')
    elif piece=='helmet':
        # Per-material silhouettes: soft caps, slat casques, folded crown,
        # plate helm, feather crest and ceremonial crown are distinct.
        shapes={
        'cloth':[(7,12),(8,8),(12,6),(20,6),(24,9),(25,15),(23,19),(22,24),(19,25),(19,17),(12,17),(12,25),(8,24),(7,19)],
        'bamboo':[(6,9),(9,5),(22,5),(25,9),(26,18),(24,25),(20,25),(20,18),(11,18),(11,25),(7,25),(5,18)],
        'leather':[(7,9),(11,6),(20,6),(24,9),(25,18),(24,24),(20,26),(19,19),(12,19),(11,26),(7,24),(6,18)],
        'brocade':[(7,10),(9,6),(13,5),(14,3),(18,3),(19,5),(23,6),(25,10),(24,16),(22,19),(20,23),(19,18),(12,18),(11,23),(9,19),(7,16)],
        'silver':[(6,10),(9,6),(13,4),(18,4),(22,6),(25,10),(26,18),(23,26),(19,27),(19,19),(12,19),(12,27),(8,26),(5,18)],
        'cinnabar':[(6,10),(9,7),(13,6),(13,3),(18,3),(18,6),(22,7),(25,10),(25,19),(23,27),(19,27),(19,18),(12,18),(12,27),(8,27),(6,19)],
        'sea_silk':[(7,9),(11,5),(19,5),(24,9),(26,15),(24,21),(21,26),(19,24),(19,18),(12,18),(12,24),(10,26),(7,22),(5,16)],
        'phoenix':[(4,10),(7,7),(8,3),(12,7),(15,2),(19,7),(24,3),(24,8),(27,11),(25,19),(22,25),(19,24),(19,18),(12,18),(12,24),(9,25),(6,19)],
        'qilin':[(6,10),(9,7),(13,6),(14,2),(17,2),(19,6),(23,7),(25,10),(26,18),(24,25),(20,27),(19,19),(12,19),(11,27),(7,25),(5,18)],
        'draco_king':[(4,9),(4,3),(7,4),(10,8),(13,6),(14,2),(17,2),(19,6),(21,8),(24,4),(27,3),(27,9),(26,20),(23,27),(19,28),(19,19),(12,19),(12,28),(8,27),(5,20)],
        }
        p.poy(shapes[style],'a');p.poy([(8,10),(11,7),(20,7),(23,10),(24,16),(7,16)],'c')
        # Central face remains alpha clear; cheek pieces frame the opening.
        p.r((12,17,19,25),None)
        p.poy([(7,17),(10,18),(10,23),(8,23)],'d');p.poy([(21,18),(24,17),(23,23),(21,23)],'b')
        if style=='cloth':
            p.poy([(9,9),(12,7),(20,7),(23,10),(22,13),(9,13)],'d');p.l([(8,14),(23,14)],'b');p.l([(9,15),(22,15)],'c')
            p.l([(14,8),(14,12)],'c');p.l([(20,9),(21,11)],'e');p.l([(9,19),(9,22)],'b')
        elif style=='bamboo':
            for x in [8,11,14,17,20,23]:p.r((x,9,x+1,15),'d');p.l([(x+1,10),(x+1,15)],'c')
            p.l([(8,8),(23,8)],'g');p.l([(7,16),(24,16)],'h');p.l([(8,18),(9,23)],'g');p.l([(22,18),(23,23)],'g')
        elif style=='leather':
            p.poy([(10,9),(14,7),(18,7),(21,9),(22,14),(9,14)],'d');p.l([(15,7),(15,15)],'b');p.l([(7,16),(24,16)],'f');p.l([(8,17),(23,17)],'g')
            for x in [9,13,18,22]:p.pt(x,16,'h')
            p.r((7,20,9,24),'b');p.r((22,20,24,24),'b');p.pt(8,21,'h');p.pt(23,21,'h')
        elif style=='brocade':
            p.poy([(10,8),(14,6),(19,6),(22,8),(22,12),(9,12)],'d');p.r((14,4,17,7),'b');p.l([(8,14),(23,14)],'g');p.l([(9,15),(22,15)],'h')
            p.l([(12,9),(15,12),(19,9)],'g');gem(p,16,14);p.l([(9,18),(10,21)],'g');p.l([(22,18),(21,21)],'g')
        elif style=='silver':
            p.poy([(9,10),(13,6),(15,6),(15,15),(8,15)],'d');p.poy([(17,6),(20,7),(23,10),(23,15),(17,15)],'c')
            p.l([(15,5),(16,6),(16,15)],'e');p.l([(7,16),(24,16)],'b');p.l([(8,17),(23,17)],'d');gem(p,16,13)
            p.l([(8,19),(8,24),(10,25)],'e');p.l([(23,19),(23,24),(21,25)],'d')
        elif style=='cinnabar':
            p.r((14,4,17,10),'h');p.l([(15,5),(16,6),(15,8)],'i');p.l([(8,11),(23,11)],'d');p.l([(7,16),(24,16)],'g')
            p.r((8,18,10,25),'h');p.r((21,18,23,25),'g');p.l([(9,19),(9,20),(8,21),(9,23)],'i');p.l([(22,19),(22,22),(21,23)],'i')
        elif style=='sea_silk':
            p.l([(9,10),(12,7),(18,7),(22,10)],'e');p.l([(8,13),(12,11),(19,11),(23,13)],'d');p.l([(7,16),(12,14),(19,14),(24,16)],'g');gem(p,16,13)
            p.l([(8,19),(10,21),(10,23)],'e');p.l([(23,19),(21,21),(21,23)],'d')
        elif style=='phoenix':
            p.poy([(8,5),(12,10),(15,4),(19,10),(23,5),(21,13),(10,13)],'g');p.l([(9,8),(12,11),(15,6),(19,11),(22,8)],'h');p.l([(8,16),(15,14),(23,16)],'d');gem(p,16,12)
            p.l([(7,18),(10,20),(9,23)],'g');p.l([(24,18),(21,20),(22,23)],'g')
        elif style=='qilin':
            p.poy([(14,4),(16,3),(17,6),(16,12),(14,10)],'h');p.l([(9,10),(12,8),(13,11),(10,13)],'d');p.l([(18,10),(21,8),(23,11),(20,13)],'d')
            p.l([(7,16),(12,15),(19,15),(24,16)],'g');gem(p,16,14);p.l([(8,18),(10,21),(9,24)],'h');p.l([(23,18),(21,21),(22,24)],'g')
        elif style=='draco_king':
            p.poy([(5,5),(7,6),(10,10),(13,9),(15,4),(17,9),(21,10),(24,6),(26,5),(24,12),(7,12)],'g');p.l([(6,7),(9,11),(13,10),(15,6),(18,10),(22,11),(25,7)],'h')
            p.l([(7,15),(12,14),(19,14),(24,15)],'g');gem(p,16,13)
            p.l([(7,18),(9,21),(9,25),(11,26)],'g');p.l([(24,18),(22,21),(22,25),(20,26)],'g')
    elif piece=='leggings':
        outlines={
        'cloth':[(7,5),(24,5),(24,13),(22,28),(17,28),(16,17),(15,17),(14,28),(9,28),(7,13)],
        'bamboo':[(7,4),(24,4),(25,12),(23,16),(23,28),(17,28),(16,17),(15,17),(14,28),(8,28),(8,16),(6,12)],
        'leather':[(7,5),(24,5),(25,13),(23,18),(22,28),(17,28),(16,16),(15,16),(14,28),(9,28),(8,18),(6,13)],
        'brocade':[(7,4),(24,4),(25,14),(23,29),(17,29),(16,17),(15,17),(14,29),(8,29),(6,14)],
        'silver':[(7,4),(24,4),(25,10),(23,17),(24,22),(22,28),(17,28),(16,17),(15,17),(14,28),(9,28),(7,22),(8,17),(6,10)],
        'cinnabar':[(7,4),(24,4),(25,12),(23,17),(23,28),(17,28),(16,17),(15,17),(14,28),(8,28),(8,17),(6,12)],
        'sea_silk':[(8,5),(23,5),(25,11),(23,21),(22,28),(17,29),(16,18),(15,18),(14,29),(9,28),(8,21),(6,11)],
        'phoenix':[(7,4),(24,4),(26,12),(23,17),(24,21),(22,29),(17,28),(16,18),(15,18),(14,28),(9,29),(7,21),(8,17),(5,12)],
        'qilin':[(7,4),(24,4),(25,11),(23,16),(24,22),(22,29),(17,29),(16,17),(15,17),(14,29),(9,29),(7,22),(8,16),(6,11)],
        'draco_king':[(6,4),(25,4),(26,12),(23,17),(24,23),(22,29),(17,29),(16,17),(15,17),(14,29),(9,29),(7,23),(8,17),(5,12)]}
        p.poy(outlines[style],'a');p.r((8,6,23,12),'c')
        for x in [9,18]:p.poy([(x,13),(x+4,14),(x+4,27),(x,27)],'c')
        if style=='cloth':
            p.r((8,6,23,8),'f');p.l([(15,7),(16,9),(14,12)],'h')
            p.l([(10,11),(10,18),(11,24)],'d');p.l([(21,12),(20,19),(20,25)],'b');p.l([(10,26),(13,26)],'d');p.l([(18,26),(21,26)],'b')
        elif style=='bamboo':
            p.r((8,5,23,7),'g');p.l([(9,6),(22,6)],'h')
            for x in [9,12,18,21]:p.r((x,9,x+1,16),'d');p.r((x,20,x+1,26),'d')
            for y in [12,17,24]:
                for x in [9,18]:p.l([(x,y),(x+4,y)],'f');p.l([(x,y+1),(x+4,y+1)],'g')
        elif style=='leather':
            p.r((8,6,23,8),'f');p.r((14,5,17,9),'g');p.r((15,6,16,7),'h')
            for x in [9,18]:p.poy([(x,18),(x+2,17),(x+4,18),(x+4,22),(x+2,24),(x,22)],'b');p.l([(x+1,18),(x+3,18)],'d');p.pt(x+1,20,'h');p.l([(x,26),(x+4,26)],'f')
        elif style=='brocade':
            p.r((8,5,23,8),'g');p.r((14,6,17,10),'h')
            for x in [9,18]:p.l([(x,11),(x,26)],'b');p.l([(x+4,12),(x+4,26)],'g');p.l([(x+1,18),(x+3,20),(x+1,22)],'d');p.pt(x+2,20,'g');p.l([(x,27),(x+4,27)],'g')
        elif style=='silver':
            p.l([(8,6),(23,6)],'e');p.l([(8,9),(14,11),(17,11),(23,9)],'b');gem(p,16,8)
            for x in [9,18]:p.l([(x,13),(x+3,13)],'d');p.poy([(x+2,18),(x+4,20),(x+3,23),(x,23),(x-1,20)],'b');p.l([(x,20),(x+2,19),(x+3,20)],'e');p.l([(x+1,24),(x+1,26)],'d')
        elif style=='cinnabar':
            p.r((8,6,23,8),'g');p.r((14,6,17,8),'h')
            for x in [9,20]:p.r((x,10,x+2,17),'h');p.l([(x+1,11),(x,13),(x+1,15)],'i')
            for x in [9,18]:
                for y in [19,23]:p.l([(x,y),(x+4,y)],'b');p.l([(x,y+1),(x+3,y+1)],'d')
        elif style=='sea_silk':
            p.l([(8,7),(12,9),(19,9),(23,7)],'g');p.l([(8,10),(12,12),(19,12),(23,10)],'d')
            for x in [9,18]:p.l([(x,14),(x+2,16),(x+3,23)],'d');p.l([(x+1,22),(x+3,24)],'b');p.l([(x,27),(x+4,26)],'g')
        elif style=='phoenix':
            p.l([(8,6),(14,8),(17,8),(23,6)],'h');gem(p,16,8)
            for x in [9,18]:
                for y in [12,17,22]:p.poy([(x,y),(x+4,y),(x+2,y+5)],'b');p.l([(x,y),(x+2,y+3),(x+4,y)],'d');p.pt(x+2,y+4,'g')
        elif style=='qilin':
            p.l([(8,6),(23,6)],'h');p.l([(8,9),(12,12),(15,10),(19,12),(23,9)],'b');gem(p,16,8)
            for x in [11,20]:p.poy([(x,17),(x+3,20),(x,24),(x-3,20)],'b');p.l([(x-2,20),(x,18),(x+2,20)],'h');p.l([(x,20),(x,22)],'d');p.l([(x-2,26),(x+2,26)],'g')
        elif style=='draco_king':
            p.r((8,5,23,7),'g');gem(p,16,7)
            p.l([(7,11),(11,9),(15,12)],'d');p.l([(17,12),(21,9),(24,11)],'c')
            for x in [9,18]:
                for y in [15,20,25]:p.l([(x,y+1),(x+2,y),(x+4,y+1)],'d');p.l([(x,y+2),(x+4,y+2)],'b')
                p.l([(x,27),(x+4,27)],'g')
    else:
        # Boots use pair silhouettes, material-specific cuffs and shin shapes.
        for flip in [False,True]:
            tx=lambda pts:[(31-x if flip else x,y) for x,y in pts]
            high=style in ['silver','phoenix','qilin','draco_king','cinnabar']
            top=4 if high else (8 if style=='cloth' else 6)
            toe=2 if style in ['leather','brocade','draco_king'] else 3
            p.poy(tx([(6,top),(13,top),(14,21),(14,27),(toe,27),(toe,23),(5,21)]),'a')
            p.poy(tx([(7,top+2),(12,top+2),(12,24),(toe+2,24),(6,21)]),'c')
            if style=='cloth':
                for y in [11,16,21]:p.l(tx([(6,y),(12,y+2)]),'b');p.l(tx([(7,y),(12,y+1)]),'d')
                p.l(tx([(4,25),(12,25)]),'f');p.pt(*tx([(8,10)])[0],'e')
            elif style=='bamboo':
                for x in [7,10]:p.l(tx([(x,8),(x,21)]),'d');p.l(tx([(x+1,9),(x+1,21)]),'b')
                for y in [10,17,23]:p.l(tx([(6,y),(12,y)]),'g');p.l(tx([(6,y+1),(12,y+1)]),'f')
            elif style=='leather':
                p.poy(tx([(5,7),(13,7),(13,11),(6,10)]),'d');p.l(tx([(6,11),(12,12)]),'f');p.l(tx([(8,13),(8,21)]),'b')
                for y in [15,19]:p.l(tx([(8,y),(10,y+1)]),'h')
                p.l(tx([(4,24),(11,24)]),'d');p.l(tx([(3,26),(13,26)]),'f')
            elif style=='brocade':
                p.l(tx([(6,7),(12,7)]),'h');p.l(tx([(6,9),(12,9)]),'g');p.l(tx([(11,11),(11,21)]),'g');p.l(tx([(8,14),(10,16),(8,18)]),'d');p.pt(*tx([(9,16)])[0],'h');p.l(tx([(3,24),(12,24)]),'g')
            elif style=='silver':
                p.poy(tx([(7,6),(12,6),(12,20),(10,23),(7,20)]),'b');p.poy(tx([(8,7),(10,6),(11,9),(11,20),(9,21),(8,18)]),'d');p.l(tx([(9,8),(9,18)]),'e');p.l(tx([(4,23),(12,23)]),'d');p.l(tx([(4,25),(12,25)]),'b')
            elif style=='cinnabar':
                p.l(tx([(6,5),(12,5)]),'g');p.r((19 if flip else 9,8,20 if flip else 10,16),'h')
                for y in [18,22]:p.l(tx([(6,y),(12,y)]),'b');p.l(tx([(7,y+1),(11,y+1)]),'d')
                p.l(tx([(9,9),(10,11),(9,13),(10,15)]),'i')
            elif style=='sea_silk':
                p.l(tx([(6,7),(9,9),(12,7)]),'e');p.l(tx([(6,12),(9,14),(12,12)]),'d');p.l(tx([(7,17),(10,19),(12,17)]),'b');p.l(tx([(5,23),(8,24),(12,23)]),'g')
            elif style=='phoenix':
                p.poy(tx([(6,6),(9,8),(12,5),(11,14),(8,12)]),'g');p.l(tx([(7,7),(9,10),(11,7)]),'h')
                for y in [14,19]:p.l(tx([(7,y),(9,y+3),(12,y)]),'d');p.l(tx([(8,y+2),(9,y+4),(11,y+2)]),'b')
                p.l(tx([(4,24),(12,24)]),'g')
            elif style=='qilin':
                p.l(tx([(6,5),(12,5)]),'g');p.poy(tx([(9,9),(12,13),(9,18),(6,13)]),'b');p.l(tx([(7,13),(9,10),(11,13)]),'h');p.l(tx([(9,13),(9,16)]),'d');p.l(tx([(6,21),(9,23),(12,21)]),'g')
            elif style=='draco_king':
                p.l(tx([(6,5),(12,5)]),'h');p.l(tx([(6,7),(12,7)]),'g')
                for y in [10,15,20]:p.l(tx([(6,y+2),(9,y),(12,y+2)]),'d');p.l(tx([(7,y+3),(11,y+3)]),'b')
                p.l(tx([(3,24),(12,24)]),'g');p.pt(*tx([(9,12)])[0],'j')
    return p.im

# Native worn UV patterns: each row is exactly one texture pixel high.
DRAGON={
'body_front':['gb....bg','hccjjcch','cdddcccb','bcbbbcbb','cddcddcc','bcbbbcbb','ddccddcc','bcbbbcbb','cddcddcc','bcbbbcbb','ghhjjhhg','abbbbbba'],
'body_back':['gbccccbg','bccddccb','cddcddcc','bcbbbcbb','ddccddcc','bcbbbcbb','cddcddcc','bcbbbcbb','ddccddcc','bcbbbcbb','ghhhhhhg','abbbbbba'],
'body_side':['gcbh','dccb','bbcb','dccb','bbcb','cdcb','bbcb','dccb','bbcb','cdcb','ghhg','abba'],
'body_top':['gb....bg','bccccccb','cdcccccb','gbccccbg'],
'arm_front':['ghhg','hddg','cddc','bcbb','cddc','bcbb','ddcc','bcbb','cddc','bcbb','ghhg','abba'],
'arm_back':['ghhg','hccg','ddcc','bcbb','cddc','bcbb','ddcc','bcbb','cddc','bcbb','ghhg','abba'],
'arm_side':['ghhg','hcdg','dccb','bbcb','dccb','bbcb','dccb','bbcb','dccb','bbcb','ghhg','abba'],
'arm_top':['ghhg','hddh','hdch','ghhg'],
'head_front':['ggghhggg','cdckjcdc','hb....bh','bc....cb','bc....cb','dc....cd','gb....bg','ab....ba'],
'head_back':['bccddccb','cdccccdc','cddcddcc','bcbbbcbb','ddccddcc','bcbbbcbb','ghhhhhhg','abbbbbba'],
'head_side':['gbccccbg','cdcccccb','bccddccb','bcbbbcbb','cddcddcc','bcbbbcbb','gbbbbbbg','abbbbbba'],
'head_top':['abbbbbba','bccddccb','cddcddcc','bcbbbcbb','ddccddcc','bcbbbcbb','bccddccb','abbbbbba'],
'leg_front':['ghhg','cddc','bcbb','ddcc','bcbb','cddc','ghhg','cddc','bcbb','ddcc','bcbb','abba'],
'leg_back':['ghhg','bccb','bccb','abba','bccb','bccb','ghhg','bccb','abba','bccb','bccb','abba'],
'leg_side':['ghhg','dccb','bbcb','dccb','bbcb','dccb','ghhg','dccb','bbcb','dccb','bbcb','abba'],
'boot_front':['....','....','....','....','....','....','ghhg','cddc','bcbb','cddc','ghhg','abba'],
'boot_back':['....','....','....','....','....','....','ghhg','bccb','abba','bccb','ghhg','abba'],
'boot_side':['....','....','....','....','....','....','ghhg','dccb','bbcb','dccb','ghhg','abba'],
}

def R(s):return s.split('/')

# These are hand-authored anatomical texel patterns, not scaled inventory art.
# Front/back distinctions and soft-cloth/plate structures are intentional.
WORN={
'cloth':{
'body_front':'bc....cb/ccdecbcc/cbcdecbc/cbccdebc/cbcbdebc/ccbdcbcc/ccdcbcbc/ccbcbbcc/ffffffff/gggghggg/ccbdcbcc/bbbcbbcb',
'body_back':'bbccccbb/bccddccb/bccccccb/bccccccb/ccbccbcc/ccbccbcc/ccbccbcc/bccccccb/ffffffff/gggggggg/ccbccbcc/bbbbbbbb',
'arm_front':'bccb/ccdc/bcdc/bcdc/bccc/bccc/bbcc/cbdc/ccbc/bbbb/..../....',
'arm_back':'bccb/cccc/bccc/bccc/bccc/bccc/bbcc/cccc/cccc/bbbb/..../....',
'leg_front':'fggf/cbdc/cbdc/cbdc/cbdc/ccdc/cbdc/cbcc/cbcc/cbcc/bbbb/bbbb',
'leg_back':'fggf/ccbc/ccbc/ccbc/ccbc/cbbc/ccbc/ccbc/cbcc/cbcc/bbbb/bbbb',
'head_front':'bbddddbb/bcdddccb/cc....cc/bc....cb/bc....cb/bc....cb/.b....b./........',
'head_back':'bbddddbb/bcddddcb/ccddddcc/bccccccb/bccbcbcb/bccccccb/.bbbbbb./........',
'head_top':'..bbbb../.bccdcb./bccdddcb/bccdddcb/bccbdccb/bccbdccb/.bccccb./..bbbb..',
'boot_front':'..../..../..../..../..../..../..../..../bbbc/cddc/fggf/ffff',
},
'bamboo':{
'body_front':'gc....cg/hhccccgh/cdbcdcbc/cdbcdcbc/ffffffff/hhhhhhhh/cdbcdcbc/cdbcdcbc/cdbcdcbc/ffffffff/ggghhggg/bbbbbbbb',
'body_back':'gccccccg/hccccccg/cdbcdcbc/cdbcdcbc/ffffffff/hhhhhhhh/cdbcdcbc/cdbcdcbc/cdbcdcbc/ffffffff/gggggggg/bbbbbbbb',
'arm_front':'ghhg/cddc/cdbc/cdbc/ffff/hhhh/cdbc/cdbc/ffff/ghhg/..../....',
'arm_back':'ghhg/ccdc/cdbc/cdbc/ffff/gggg/cdbc/cdbc/ffff/gggg/..../....',
'leg_front':'ghhg/cdbc/cdbc/ffff/hhhh/cdbc/cdbc/ffff/ghhg/cdbc/cdbc/bbbb',
'leg_back':'gggg/cdbc/cdbc/ffff/gggg/cdbc/cdbc/ffff/gggg/cdbc/cdbc/bbbb',
'head_front':'gggggggg/cddcddcc/cb....bc/hh....hh/cb....bc/cb....bc/gb....bg/........',
'head_back':'gggggggg/cddcddcc/cdbcdbcc/cdbcdbcc/hhhhhhhh/cdbcdbcc/cdbcdbcc/gggggggg',
'head_top':'gbbbbbbg/cddcddcc/cdbcdbcc/cdbcdbcc/ffffffff/hhhhhhhh/cdbcdbcc/gbbbbbbg',
'boot_front':'..../..../..../..../..../..../ffff/hhhh/cdbc/cdbc/gggg/bbbb',
},
'leather':{
'body_front':'bc....cb/cddccddc/cffcdccb/ccgfcccb/cccgfccb/cccchfcb/cccccgfc/cccbccgf/ffffffff/gggfhggg/cccbcccb/bbbbbbbb',
'body_back':'bcddddcb/cddccddc/bccbbccb/bccbbccb/bccccccb/bccccccb/bccccccb/bccccccb/ffffffff/gggggggg/bccbbccb/bbbbbbbb',
'arm_front':'bccb/cddc/ccdc/fhgf/bccc/bccc/ccbc/ccbc/ffgf/gggg/bbbb/....',
'arm_back':'bccb/cddc/cccc/fgff/bccc/bccc/ccbc/ccbc/ffgf/gggg/bbbb/....',
'leg_front':'fggf/cdcc/cdcc/cbcc/cbcc/bbbb/bddb/bccb/bbbb/cbcc/cbcc/bbbb',
'leg_back':'fggf/ccbc/ccbc/ccbc/bbbc/cccc/bccc/bccc/bccc/cccc/cccc/bbbb',
'head_front':'bbddddbb/bcdcbccb/hg....gh/bc....cb/bc....cb/bc....cb/gh....hg/ab....ba',
'head_back':'bbddddbb/bcdcbccb/ccdcbdcc/bcdcbdcb/ffffffff/gggggggg/bccccccb/abbbbbba',
'head_top':'..bbbb../.bcddcb./bcdcbccb/bcdcbccb/bcdcbdcb/bcdcbdcb/.bccccb./..bbbb..',
'boot_front':'..../..../..../..../..../..../cddc/fggf/cghc/cbhc/cddc/ffff',
},
'brocade':{
'body_front':'gc....cg/cghccccb/ccghcccb/cbcghccb/cdccghcb/ccdcghcb/cbcdgccb/cbdgcbcc/gggggggg/hhhhghhh/cdcggcdc/bbbfgbbb',
'body_back':'gbddddbg/bccddccb/bccccccb/bcdcbdcb/bcghdgcb/bcdcbdcb/bccccccb/bccccccb/gggggggg/hhhhhhhh/bcdcbdcb/bbbbbbbb',
'arm_front':'gccg/cddc/cbdc/cdcc/cghc/cdcc/cbdc/ccdc/cbdc/ghhg/bbbb/....',
'arm_back':'gccg/ccdc/cbcc/cdcc/cggc/cdcc/cbcc/ccdc/cbcc/ghhg/bbbb/....',
'leg_front':'ghhg/cdcg/cdcg/cbcg/cbcg/cdcg/cghg/cdcg/cbcg/cdcg/ghhg/bbbb',
'leg_back':'ghhg/cbcg/cbcg/cbcg/cbcg/cbcg/cggg/cbcg/cbcg/cbcg/ghhg/bbbb',
'head_front':'bbddddbb/bcddgccb/ggghhggg/hg....gh/bc....cb/.b....b./......../........',
'head_back':'bbddddbb/bcddbccb/ccddbdcc/bccccccb/gggggggg/hhhhhhhh/bccccccb/........',
'head_top':'..bbgb../.bcggcb./bccggccb/bccccccb/bccccccb/bccccccb/.bccccb./..bbbb..',
'boot_front':'..../..../..../..../..../..../ghhg/cdcg/cghg/cdcg/ghhg/bbbb',
},
'silver':{
'body_front':'gb....bg/cddeedcc/cdcbbdcc/cddjjdcc/cddkjdcc/bcccbbcc/bcdbbdcb/abbbbbba/cddbbddc/bcdbbdcb/ggghhggg/abbbbbba',
'body_back':'gbccccbg/bcddddcb/cddddddc/bccbbccb/bccbbccb/bccbbccb/bcdbbdcb/abbbbbba/bcddddcb/bccbbccb/gggggggg/abbbbbba',
'arm_front':'gddg/deed/cddc/bccb/bccb/cddc/abba/cddc/bccb/cddc/ghhg/abba',
'arm_back':'gddg/cddc/cbcc/bbcc/bbcc/bccb/abba/bccb/bbcc/bccb/ghhg/abba',
'leg_front':'ghhg/cddc/cddc/bccb/abba/bddb/deed/cddc/abba/bcdb/bcdb/abba',
'leg_back':'ghhg/bccb/bccb/bccb/abba/bccb/bddb/bccb/abba/bccb/bccb/abba',
'head_front':'bccedccb/cddeedcc/bddjjddb/hd....dh/bc....cb/dc....cd/gb....bg/ab....ba',
'head_back':'bccedccb/cddeedcc/cddeedcc/bcdccdcb/bccccccb/bccbbccb/gggggggg/abbbbbba',
'head_top':'abbeebba/bcdeedcb/cddeeddc/cddeeddc/bcdeedcb/bcdeedcb/bcdeedcb/abbeebba',
'boot_front':'..../..../..../..../..../ghhg/bddb/cdec/cdec/bddb/ghhg/abba',
},
'cinnabar':{
'body_front':'gc....cg/chccccgc/chddccgc/ciabcbhc/chccdbic/ciaacbhc/chccdbic/ciabcbhc/chddccgc/bcbbbbcb/gghhhggg/abbbbbba',
'body_back':'gbccccbg/bccddccb/bccbbccb/abbbbbba/bccccccb/cddddddc/abbbbbba/bccccccb/bccbbccb/bcddddcb/gggggggg/abbbbbba',
'arm_front':'ghhg/cddc/bccb/chic/chhc/chic/bccb/abba/cddc/abba/ghhg/abba',
'arm_back':'ghhg/ccdc/bccb/bccb/cddc/abba/bccb/abba/cddc/abba/ghhg/abba',
'leg_front':'ghhg/chic/chhc/chic/chhc/bbbb/cddc/abba/bccb/cddc/ghhg/abba',
'leg_back':'ghhg/bccb/bccb/abba/bccb/bbbb/cddc/abba/bccb/cddc/ghhg/abba',
'head_front':'gbchhcbg/cdchicdc/ghhhhhhg/hh....hh/hi....ih/hh....hh/hi....ih/ab....ba',
'head_back':'gbchhcbg/bcchhccb/bccccccb/bcddddcb/abbbbbba/bccccccb/gggggggg/abbbbbba',
'head_top':'abchhcba/bcchhccb/bcchiccb/cddddddc/abbbbbba/bccccccb/bccccccb/abbbbbba',
'boot_front':'..../..../..../..../..../ghhg/chhc/chic/chhc/cddc/ghhg/abba',
},
'sea_silk':{
'body_front':'gc....cg/cdeeeddc/cdgccgdc/bcgjjgcb/bcckkccb/bccccccb/cbddddbc/ccbddbcc/cdccccdc/ccbddbcc/ggchhcgg/bbccbcbb',
'body_back':'gbccccbg/cddddddc/bccddccb/bccccccb/bccccccb/bccccccb/cbddddbc/ccbddbcc/cdccccdc/ccbddbcc/gggggggg/bbccbcbb',
'arm_front':'gddg/deed/cddc/cbbc/bccb/cddc/cbbc/bccb/cddc/gggg/..../....',
'arm_back':'gddg/cddc/ccdc/cbbc/bccb/cddc/cbbc/bccb/cddc/gggg/..../....',
'leg_front':'ghhg/cddc/bcdb/bcdb/ccdc/ccdc/cbcc/bcdb/cddc/cbbc/gggg/bbbb',
'leg_back':'ghhg/bccb/cbcc/cbcc/ccbc/ccbc/cbcc/bccb/cbcc/cbbc/gggg/bbbb',
'head_front':'bccddccb/cddeeddc/hdckkcdh/bc....cb/dc....cd/bc....cb/.b....b./........',
'head_back':'bccddccb/cddeeddc/bcddddcb/bccccccb/cbddddbc/ccbddbcc/gbccccbg/........',
'head_top':'..bbbb../.bcddcb./bcdeedcb/cddeeddc/bcddddcb/cbddddbc/.cbddbc./..bbbb..',
'boot_front':'..../..../..../..../..../..../gddg/cbbc/bcdb/cddc/gggg/bbbb',
},
'phoenix':{
'body_front':'gc....cg/cdhccgdc/bcdkkdcb/gccdcccc/cgdccdbc/bcgddgcb/cbcggcbc/dcbccbdc/cddbbddc/bcddddcb/ggchhcgg/abbbbbba',
'body_back':'gbccccbg/cddccddc/bcddddcb/cbcddcbc/dcbccbdc/cddbbddc/bcddddcb/cbcddcbc/dcbccbdc/cddbbddc/gggggggg/abbbbbba',
'arm_front':'ghhg/hddh/cgdc/bcdg/cbcg/dcbc/cdbc/bcdg/cbcg/dcbc/ghhg/abba',
'arm_back':'ghhg/gddg/ccdc/bcdg/cbcg/dcbc/cdbc/bcdg/cbcg/dcbc/ghhg/abba',
'leg_front':'ghhg/cddc/bddc/cbcg/dcbc/cddc/bddc/cbcg/dcbc/cddc/ghhg/abba',
'leg_back':'ghhg/bccb/ccdc/cbcg/dcbc/bccb/ccdc/cbcg/dcbc/bccb/ghhg/abba',
'head_front':'gbchhcbg/cghghghc/bchgghcb/hg....gh/dc....cd/gc....cg/.b....b./........',
'head_back':'gbchhcbg/cddccddc/bcddddcb/cbcddcbc/dcbccbdc/cddbbddc/ghhhhhhg/abbbbbba',
'head_top':'gbchhcbg/cddccddc/bcddddcb/cbcddcbc/dcbccbdc/cddbbddc/bcddddcb/abbbbbba',
'boot_front':'..../..../..../..../..../ghhg/cddg/bcdg/cbcg/dcbc/ghhg/abba',
},
'qilin':{
'body_front':'gc....cg/cdhhhcdc/bcdkkdcb/bdchhcdb/dcbcdbcd/bddcddcb/cbcddcbc/bcdccdbb/cddhhddc/bcghhgcb/ggchhcgg/abbbbbba',
'body_back':'gbccccbg/bcdhhcdb/dcbcdbcd/bddcddcb/cbcddcbc/bcdccdcb/dcbcdbcd/bddcddcb/cbcddcbc/bcdccdcb/gggggggg/abbbbbba',
'arm_front':'ghhg/gddh/cdhc/bcdb/cbdc/bcdb/cdhc/bcdb/cbdc/bcdb/ghhg/abba',
'arm_back':'ghhg/gccg/cddc/bcdb/cbdc/bcdb/cddc/bcdb/cbdc/bcdb/ghhg/abba',
'leg_front':'ghhg/cddc/bcdb/cbdc/bcdb/bhhb/hddh/bcdb/cbdc/bcdb/ghhg/abba',
'leg_back':'ghhg/bccb/bcdb/cbdc/bcdb/bccb/bddb/bcdb/cbdc/bcdb/ghhg/abba',
'head_front':'gbchhcbg/bcdhhcdb/cdhkjhdc/hg....gh/dc....cd/hc....ch/gb....bg/ab....ba',
'head_back':'gbccccbg/bcdccdcb/dcbcdbcd/bddcddcb/cbcddcbc/bcdccdcb/ghhhhhhg/abbbbbba',
'head_top':'abchhcba/bcdhhcdb/dcbhhbcd/bddhhddb/cbchhcbc/bcdhhcdb/bccddccb/abbbbbba',
'boot_front':'..../..../..../..../..../ghhg/bhhb/hddh/bcdb/cbdc/ghhg/abba',
},
'draco_king':{
'body_front':'gc....cg/cdhhhcdc/gcdkkdcg/gcbjjbcg/cdbccbdc/bccddccb/abccccba/cdbccbdc/bccddccb/abccccba/ggchhcgg/abbbbbba',
'body_back':'gbccccbg/gcdccdcg/gcbccbcg/cdbccbdc/bccddccb/abccccba/cdbccbdc/bccddccb/abccccba/bcddddcb/gggggggg/abbbbbba',
'arm_front':'ghhg/hddh/cddc/bcdb/cdcc/abba/cddc/bcdb/cdcc/abba/ghhg/abba',
'arm_back':'ghhg/gccg/cddc/bcdb/cbcc/abba/cddc/bcdb/cbcc/abba/ghhg/abba',
'leg_front':'ghhg/cddc/bcdb/cdcc/abba/cddc/bcdb/cdcc/abba/cddc/ghhg/abba',
'leg_back':'ghhg/bccb/bcdb/cbcc/abba/bccb/bcdb/cbcc/abba/bccb/ghhg/abba',
'head_front':'gbghhgbg/chghhghc/gggkkggg/hg....gh/gc....cg/gc....cg/hb....bh/ab....ba',
'head_back':'gbghhgbg/cdgccgdc/bcgccgcb/bccccccb/cdbccbdc/bccddccb/ghhhhhhg/abbbbbba',
'head_top':'gbghhgbg/cdgccgdc/bcgccgcb/bcghhgcb/cdbccbdc/bccddccb/bccbbccb/abbbbbba',
'boot_front':'..../..../..../..../..../ghhg/cddc/bcdb/cdcc/abba/ghhg/abba',
},
}

def pattern(style):
    out={k:R(v) for k,v in WORN[style].items()}
    # Side material bands align to their own front/back seam heights.
    # This is UV-face construction, not reuse of an inventory graphic.
    side=[]
    for front,back in zip(out['body_front'],out['body_back']):
        side.append(back[:2]+front[-2:])
    out['body_side']=side
    out['body_top']=['gb....bg','bccddccb','bccccccb','gbccccbg']
    out['arm_side']=[b[:2]+a[-2:] for a,b in zip(out['arm_front'],out['arm_back'])]
    out['arm_top']={
      'cloth':['bccb','cddc','ccdc','bccb'],'bamboo':['ghhg','cddc','cdbc','ghhg'],
      'leather':['bccb','cddc','ccdc','fggf'],'brocade':['gccg','cddc','cggc','gccg'],
      'silver':['ghhg','deed','cddc','ghhg'],'cinnabar':['ghhg','cddc','bccc','ghhg'],
      'sea_silk':['gddg','deed','cddc','gddg'],'phoenix':['ghhg','hddh','cgdg','ghhg'],
      'qilin':['ghhg','hddh','cdhc','ghhg'],'draco_king':['ghhg','hddh','cddc','ghhg'],
    }[style]
    out['head_side']=[r[::-1] for r in out['head_back']]
    out['leg_side']=[b[:2]+a[-2:] for a,b in zip(out['leg_front'],out['leg_back'])]
    out['boot_back']=[r.replace('e','c').replace('d','c').replace('h','g') for r in out['boot_front']]
    out['boot_side']=[b[:2]+a[-2:] for a,b in zip(out['boot_front'],out['boot_back'])]
    # A two/three-pixel waist band belongs to leggings, not the chest texture.
    out['hip_front']=['........']*8+[out['body_front'][r] for r in [8,9,10,11]]
    out['hip_back']=['........']*8+[out['body_back'][r] for r in [8,9,10,11]]
    out['hip_side']=['....']*8+[out['body_side'][r] for r in [8,9,10,11]]
    return out

def atlases(style,patterns):
    p=Pix(style,(64,32));q=Pix(style,(64,32))
    def cube_tiles(canvas,root,w,h,depth,front,back,side,top=None,bottom=None):
        x,y=root
        assert len(front)==len(back)==len(side)==h
        assert all(len(r)==w for r in front+back)
        assert all(len(r)==depth for r in side)
        canvas.tile(x+depth,y+depth,front);canvas.tile(x+2*depth+w,y+depth,back)
        canvas.tile(x,y+depth,side);canvas.tile(x+depth+w,y+depth,[r[::-1] for r in side])
        canvas.tile(x+depth,y,top or ['c'*w]*depth)
        canvas.tile(x+depth+w,y,bottom or ['b'*w]*depth)
    pat=patterns
    cube_tiles(p,(0,0),8,8,8,pat['head_front'],pat['head_back'],pat['head_side'],pat['head_top'],['.'*8]*8)
    # Hat island (32,0) remains transparent: no invented outer hat geometry.
    cube_tiles(p,(16,16),8,12,4,pat['body_front'],pat['body_back'],pat['body_side'],pat['body_top'])
    cube_tiles(p,(40,16),4,12,4,pat['arm_front'],pat['arm_back'],pat['arm_side'],pat['arm_top'])
    cube_tiles(p,(0,16),4,12,4,pat['boot_front'],pat['boot_back'],pat['boot_side'],['....']*4,['abba','bccb','bccb','abba'])
    # LEGS uses inner model/body+legs. Waist only; chest itself belongs to CHEST.
    hip=pat.get('hip_front',['........']*8+['abbbbbba','bccddccb','ghhhhhhg','abbbbbba'])
    hipback=pat.get('hip_back',hip)
    hipside=pat.get('hip_side',['....']*8+['abba','bccb','ghhg','abba'])
    cube_tiles(q,(16,16),8,12,4,hip,hipback,hipside,['........']*4,['abbbbbba']*4)
    cube_tiles(q,(0,16),4,12,4,pat['leg_front'],pat['leg_back'],pat['leg_side'],['ghhg','bccb','bccb','ghhg'])
    return p.im,q.im

def backups(style):
    records=[]
    for rel in [f'textures/item/{style}_{piece}.png' for piece in PIECES]+[f'textures/models/armor/{style}_layer_{n}.png' for n in [1,2]]+[f'models/item/{style}_{piece}.json' for piece in PIECES]:
        src=S/rel;dst=D/'before'/rel
        dst.parent.mkdir(parents=True,exist_ok=True)
        if not dst.exists():shutil.copy2(src,dst)
        assert dst.read_bytes()==src.read_bytes(),f'Concurrent source edit: {rel}'
        records.append({'target':str(src.relative_to(ROOT)),'backup':str(dst.relative_to(D)),'sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
    return records

def icon_page(style):
    f=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',18)
    sf=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',12)
    page=Image.new('RGB',(1080,655),'#e9e9df');d=ImageDraw.Draw(page)
    d.text((18,14),f'{style.upper()} | 32x32 ORIGINAL PIXEL ICONS',font=f,fill='#293c38')
    d.text((18,43),'New native-grid designs. BEFORE above / CANDIDATE below. No resize-generated artwork.',font=sf,fill='#52645c')
    for col,piece in enumerate(PIECES):
        x=20+col*264
        d.text((x,74),piece,font=f,fill='#293c38')
        for row,root in enumerate([D/'before/textures',A]):
            tex=Image.open(root/f'item/{style}_{piece}.png').convert('RGBA')
            y=102+row*255
            panel=Image.new('RGB',(192,192),'#c5cec1')
            pd=ImageDraw.Draw(panel)
            for yy in range(0,192,16):
                for xx in range(0,192,16):
                    if (xx//16+yy//16)%2:pd.rectangle((xx,yy,xx+15,yy+15),fill='#d8ddcf')
            big=tex.resize((192,192),Image.Resampling.NEAREST);panel.paste(big,(0,0),big);page.paste(panel,(x,y))
            page.paste(tex,(x+207,y+30),tex);d.text((x+207,y+68),'1x',font=sf,fill='#52645c')
            small=tex.resize((16,16),Image.Resampling.NEAREST);page.paste(small,(x+216,y+105),small)
            d.text((x+200,y+130),'16px',font=sf,fill='#52645c')
    d.text((20,625),'Icons are flat sprites. Worn 64x32 layer atlases are independently authored on actual humanoid UVs.',font=sf,fill='#52645c')
    page.save(D/'previews'/f'{style}-icons.png')

def run(selected):
    records=[];out=[]
    for style in selected:
        assert style in SETS and style not in PROTECTED
        records+=backups(style)
        for piece in PIECES:
            tex=dragon_icon(piece) if style=='dragon_scale' else icon(style,piece)
            tex.save(A/f'item/{style}_{piece}.png')
        pat=DRAGON if style=='dragon_scale' else pattern(style)
        for n,tex in enumerate(atlases(style,pat),1):tex.save(A/f'models/armor/{style}_layer_{n}.png')
        icon_page(style)
        for rel in [f'item/{style}_{part}.png' for part in PIECES]+[f'models/armor/{style}_layer_{n}.png' for n in [1,2]]:
            path=A/rel;im=Image.open(path).convert('RGBA')
            alphas=sorted(set(im.getchannel('A').getdata()));assert set(alphas)<={0,255}
            expected=(32,32) if rel.startswith('item/') else (64,32);assert im.size==expected
            out.append({'set':style,'candidate':str(path.relative_to(D)),'target':'src/main/resources/assets/dynasty/textures/'+rel,'size':list(im.size),'alpha':alphas,'visible_colors':len({p[:3] for p in im.getdata() if p[3]}),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    manifest={'status':'candidate_only_not_installed','sets':selected,'protected_untouched':PROTECTED,'designs':{k:DESIGN[k] for k in selected},'baseline':records,'files':out,'game_tested':False,'animation':False,'emissive':False,'native_authorship':'Direct integer coordinates at 32x32 / 64x32; no high-resolution generation/resampling. Artwork is new; source PNGs used only for comparison and backup.','history_evidence':['tools/art/gen_armor.py: sea_silk copies dragon_scale icons','tools/art/gen_armor2.py: bamboo/leather/brocade/silver/cinnabar/phoenix/qilin/draco_king tint existing sets','tools/art/gen_armor_layers.py: old whole-atlas gradient, repeated lines and random damage','docs/art/build-feedback-v5/release-notes.md and visual-feedback-v6: completed general/jade/sky icons protected','docs/art/vanilla-materials-v7: bronze/xuantian completed icons protected'],'resolution_reason':'Armor items already use 32x32 resource convention; neck opening, shoulders, paired greaves and layered high-tier plates need it. Worn layers preserve actual 64x32 humanoid UV format.'}
    (D/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'sets':selected,'files':len(out),'source_files_preserved':len(records)}))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--sets',nargs='+',default=SETS);args=ap.parse_args();run(args.sets)
