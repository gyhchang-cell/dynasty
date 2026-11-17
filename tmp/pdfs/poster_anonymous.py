from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3,landscape
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
from pypdf import PdfReader
from math import atan2,cos,sin,pi
pdfmetrics.registerFont(TTFont('Sans','/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))
pdfmetrics.registerFont(TTFont('Serif','/System/Library/Fonts/Supplemental/Songti.ttc',subfontIndex=1))
pdfmetrics.registerFont(TTFont('TC','/System/Library/Fonts/Supplemental/Songti.ttc',subfontIndex=2))
W,H=landscape(A3);P=Path('output/pdf/TOK_A3横版海报_匿名版.pdf');c=canvas.Canvas(str(P),pagesize=(W,H))
c.setTitle('文化背景与思想理解');BG='#FAFBF8';INK='#203D43';GREEN='#536949';GOLD='#B78943';MUTED='#62706D';LIGHT='#E9EEE6';LINE='#BFCBC3'
def t(x,y,s,n=14,f='Sans',col=INK):
 c.setFillColor(HexColor(col));c.setFont(f,n);c.drawString(x,y,s)
def r(x,y,w,h,col):
 c.setFillColor(HexColor(col));c.rect(x,y,w,h,stroke=0,fill=1)
def ln(x,y,x2,y2,col=LINE,lw=.8):
 c.setStrokeColor(HexColor(col));c.setLineWidth(lw);c.line(x,y,x2,y2)
def arrow(x,y,x2,y2,col=GREEN):
 ln(x,y,x2,y2,col,1)
 a=atan2(y2-y,x2-x)
 for d in [-.5,.5]:ln(x2,y2,x2-6*cos(a+d),y2-6*sin(a+d),col,1)
def p(s,x,top,w,n=14,lead=21,f='Sans',col=INK):
 lines=[];cur=''
 for ch in s:
  if cur and pdfmetrics.stringWidth(cur+ch,f,n)>w-7 and ch not in '，。；：？！、）》」』':lines.append(cur);cur=ch
  else:cur+=ch
 if cur:lines.append(cur)
 for i,ss in enumerate(lines):t(x,top-n-i*lead,ss,n,f,col)
 return top-len(lines)*lead
def center(x,y,s,n=15,f='Sans',col=INK):
 t(x-pdfmetrics.stringWidth(s,f,n)/2,y,s,n,f,col)
def node(x,y,w,h,lines,col=LIGHT,f='Sans',n=15):
 r(x,y,w,h,col)
 if isinstance(lines,str):lines=[lines]
 start=y+h/2+(len(lines)-1)*11-5
 for i,ss in enumerate(lines):center(x+w/2,start-i*22,ss,n,f)
r(0,0,W,H,BG)
# A firm title, a single reply, and open space replace footnotes and slogans.
r(47,782,34,5,GOLD)
t(47,733,'我们能否摆脱自身的文化背景，',34,'Serif')
t(47,687,'客观地理解另一种思想？',34,'Serif')
r(861,673,282,113,INK)
t(881,751,'很难完全摆脱。',23,'Serif','#FFFFFF')
p('文化背景会影响我们用什么标准、赋予什么意义。',881,735,240,15,23,col='#E1E9DF')
ln(47,642,1143,642,INK,1.1)
x1=47;x2=423;x3=799;cw=344
# Subtle column separation leaves diagrams room to breathe.
ln(399,146,399,614);ln(775,146,775,614)
t(x1,606,'01',13,col=GREEN);t(x1+40,600,'儒家与法家',31,'Serif')
p('儒家重视德与礼的教化；韩非强调法令与赏罚，认为治理不能只靠自觉行善。',x1,575,cw,14.5,22)
# One vertical causal chain, followed by the two sides of selective attention.
node(x1+26,438,292,55,'长期接受儒家教育',n=17)
arrow(x1+172,430,x1+172,407)
node(x1+26,340,292,63,['容易先问：','治理能否培养人的道德？'],n=16)
arrow(x1+172,334,x1+172,310)
ln(x1+79,307,x1+265,307,GREEN,1)
arrow(x1+79,307,x1+79,286);arrow(x1+265,307,x1+265,286)
t(x1+4,261,'可能先看到',14,col=GREEN)
t(x1+188,261,'可能忽略',14,col=GREEN)
p('法家的严厉赏罚',x1+4,249,162,16,23,f='Serif')
p('制度约束的理由',x1+188,249,156,16,23,f='Serif')
ln(x1,208,x1+cw,208,LINE,.8)
p('文化背景影响评价标准，理解因此可能偏向一面。',x1,187,cw,19.5,29,f='Serif')
# The middle section is traditional throughout, with parallel tracks instead of vague circles.
t(x2,606,'02',13,col=GREEN);t(x2+40,600,'A國與B地區',29,'TC')
p('共享語言與習俗，不代表對文化認同有相同理解。兩種可能的理解路徑：',x2,575,cw,14.5,22)
center(x2+81,487,'A國一些人',16,'TC',GREEN)
center(x2+263,487,'B地區一些人',16,'TC',GREEN)
node(x2,409,163,61,['更重視共同傳統','節日、語言與親緣'],f='Sans',n=13.4)
node(x2+181,409,163,61,['更重視當地經驗','生活、歷史與記憶'],f='Sans',n=13.4)
arrow(x2+81,402,x2+81,375);arrow(x2+263,402,x2+263,375)
p('可能把強調B地區特色，理解為否定共同文化。',x2+3,363,158,14.5,22)
p('可能把強調共同文化，理解為否定當地特色。',x2+184,363,158,14.5,22)
p('同樣談文化聯繫，有人先感到親近，有人先擔心自己的獨特經歷被忽略。',x2,278,cw,13.5,20,col=MUTED)
ln(x2,208,x2+cw,208,LINE,.8)
p('文化記憶影響認同，也影響我們怎樣解釋對方。',x2,187,cw,19.5,29,f='TC')
# Only the year identifies the third case; the analysis remains cultural.
t(x3,606,'03',13,col=GREEN);t(x3+40,590,'某国',43,'Serif')
p('有一个国家，在一次公共讨论中，一些参与者要求对话；管理者则更强调稳定与秩序。',x3,575,cw,14.5,22)
center(x3+172,488,'如何理解“公共责任”？',18,'Serif')
ln(x3+79,469,x3+265,469,GREEN,1)
arrow(x3+79,469,x3+79,445);arrow(x3+265,469,x3+265,445)
node(x3,379,163,62,['若更重视','稳定与秩序'],n=16)
node(x3+181,379,163,62,['若更重视','参与和公开讨论'],n=15)
arrow(x3+81,373,x3+81,346);arrow(x3+263,373,x3+263,346)
p('可能先把不同意见看作秩序的干扰。',x3+3,333,158,14.5,22)
p('可能先把不同意见看作改进的机会。',x3+184,333,158,14.5,22)
p('对权威、责任与表达方式的看法，也是文化背景的一部分。',x3,259,cw,13.5,20,col=MUTED)
ln(x3,208,x3+cw,208,LINE,.8)
p('文化中的价值偏好，影响同一种意见被怎样理解。',x3,187,cw,19.5,29,f='Serif')
# Only a supported conclusion remains; no unargued promise of removing bias.
r(47,43,1096,65,INK)
t(67,66,'我们往往带着自己的文化标准，理解另一种思想。',24,'Serif','#FFFFFF')
c.showPage();c.save()
rdr=PdfReader(P);s=rdr.pages[0].extract_text()
assert len(rdr.pages)==1
for bad in ['减少偏见','反思自己的标准','六四','06 / 04','6月','4日','时代']:assert bad not in s,bad
assert 'A國與B地區' in s and '某国' in s
for bad in ['1989','2025','台湾','臺灣','两岸','兩岸','赖清德','賴清德','双十','雙十']:assert bad not in s,bad
print(P.resolve(),list(rdr.pages[0].mediabox))
