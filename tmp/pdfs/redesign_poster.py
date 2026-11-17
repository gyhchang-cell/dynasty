from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3,landscape
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from pypdf import PdfReader
from pathlib import Path
pdfmetrics.registerFont(TTFont('Song','/System/Library/Fonts/Supplemental/Songti.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('Sans','/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))
# All editorial content remains vector text for A3 printing.
P=Path('output/pdf/TOK_A3横版海报.pdf');W,H=landscape(A3)
c=canvas.Canvas(str(P),pagesize=(W,H));c.setTitle('我们能否摆脱自身的文化背景，客观地理解另一种思想？');c.setAuthor('TOK小组')
BG='#F3EFE5';INK='#272721';RED='#A7372D';GRAY='#67665B';LINE='#BFB9AB'
def text(x,y,s,n=14,font='Sans',color=INK):
 c.setFillColor(HexColor(color));c.setFont(font,n);c.drawString(x,y,s)
def rule(x,y,x2,y2,color=LINE,lw=.7):
 c.setStrokeColor(HexColor(color));c.setLineWidth(lw);c.line(x,y,x2,y2)
def p(s,x,y,w,n=14.2,lead=21,color=INK,font='Sans'):
 lines=[]; current=''
 closing='，。；：？！、）》”’'
 for ch in s:
  if current and pdfmetrics.stringWidth(current+ch,font,n)>w-8 and ch not in closing:
   lines.append(current);current=ch
  else:current+=ch
 if current:lines.append(current)
 for i,line in enumerate(lines):text(x,y-n-i*lead,line,n,font,color)
 return y-len(lines)*lead

c.setFillColor(HexColor(BG));c.rect(0,0,W,H,fill=1,stroke=0)
M=43;R=W-M
text(M,H-32,'知  识  论   /   TOK',10,color=GRAY)
text(R-167,H-32,'第六题    ·    三种观看方式',10,color=GRAY)
rule(M,H-43,R,H-43,INK,1)
# Main title, unabridged assignment question.
text(M,H-104,'我们能否摆脱自身的文化背景，',38,'Song')
text(M,H-153,'客观地理解另一种思想？',38,'Song')
# Red pencil-like underline and a compact answer underneath.
rule(M+3,H-166,M+397,H-166,RED,2)
text(M,H-195,'完全摆脱很难。先看见自己的立场，才可能看清另一种思想。',15,color=GRAY)
# Two offset circles: perspective as an editorial motif, not a generic icon.
c.setStrokeColor(HexColor(RED));c.setLineWidth(1.15)
c.circle(R-150,H-120,62,stroke=1,fill=0)
c.setStrokeColor(HexColor(INK));c.circle(R-91,H-120,62,stroke=1,fill=0)
text(R-185,H-125,'背景',14,'Song',RED);text(R-91,H-125,'理解',14,'Song')
rule(R-45,H-164,R-21,H-192,INK,2)
rule(M,H-220,R,H-220,INK,1)
# Asymmetric editorial columns, separated only by fine rules.
x1=43;x2=404;x3=793;w1=318;w2=344;w3=354
rule(382,170,382,600);rule(770,170,770,600)
text(x1,598,'01   /   儒家与法家',12,color=RED)
text(x2,598,'02   /   两岸文化认同',12,color=RED)
text(x3,598,'03   /   六四事件',12,color=RED)
# 1: oversized movable type; contrasts beneath provide substance.
text(x1-4,496,'儒',86,'Song');text(x1+177,496,'法',86,'Song',RED)
rule(x1+121,506,x1+160,550,GRAY,.9)
text(x1+7,476,'德与礼的教化',12,color=GRAY)
text(x1+183,476,'法令与赏罚',12,color=GRAY)
text(x1,435,'先入为主的，是判断标准',21,'Song')
y=p('儒家重视德与礼；韩非强调，治理不能只靠人自觉行善，还要依靠法令与赏罚。',x1,415,w1)
y=p('若习惯用“能否培养道德”来评价治理，就可能只看到法家的严厉，忽略它为什么强调制度约束。',x1,y-12,w1)
p('原有教育形成标准，用同一把尺子衡量法家，理解就可能偏向一面。',x1,y-12,w1)
# 2: same cultural intersection, differing lived experiences.
c.setFillColor(HexColor('#E4DECC'));c.circle(x2+130,523,51,fill=1,stroke=0)
c.setStrokeColor(HexColor(INK));c.setLineWidth(.9);c.circle(x2+130,523,51,fill=0,stroke=1)
c.setStrokeColor(HexColor(RED));c.circle(x2+210,523,51,fill=0,stroke=1)
text(x2+94,519,'共同',15,'Song');text(x2+214,519,'地方',15,'Song',RED)
text(x2+132,458,'文化相通，经历不同',12,color=GRAY)
text(x2,424,'同一份文化，不同的认同',21,'Song')
y=p('大陆一些人重视语言、节日和亲缘联系，可能把强调台湾独特性，理解为否认共同文化。',x2,403,w2)
y=p('台湾一些人重视当地生活与历史记忆，也可能把强调共同文化，理解为抹去地方差异。',x2,y-12,w2)
y=p('赖清德2025年双十讲话将民主化经历与台湾认同联系起来。这提示我们：认同也来自共同经历。',x2,y-12,w2)
# 3: archival date typography, not a simulated historic photograph.
text(x3-4,517,'1989',83,'Song')
text(x3+4,478,'06 / 04',23,'Song',RED)
rule(x3+124,486,x3+w3,486,RED,.9)
text(x3,435,'先看到什么，也受时代影响',21,'Song')
y=p('改革讨论中，部分学生要求对话、强调爱国；领导层强调稳定。同处一个时代，人们优先关注的问题仍然不同。',x3,415,w3)
y=p('6月3日晚至4日，解放军部队使用实弹向北京市中心推进，造成平民死伤；此后有拘捕，相关讨论长期受限。',x3,y-12,w3)
p('若先把表达诉求视为秩序威胁，就可能忽略其改革理由；若只能接触一种解释，也难以比较判断。',x3,y-12,w3)
# Three concise answers share a baseline, while the content above has its own rhythm.
for x,w,s in [(x1,w1,'先听懂法家的理由，再作评价。'),(x2,w2,'先理解认同的来由，再谈分歧。'),(x3,w3,'比较学生与官方材料，再下判断。')]:
 rule(x,188,x+w,188,RED,.8)
 p(s,x,176,w,15,21,RED,'Song')
# Bottom thesis spreads across the width, like the closing line of an editorial.
rule(M,125,R,125,INK,1)
text(M,85,'理解，不等于赞同。',28,'Song')
p('客观理解，不是没有立场，而是不让自己的标准、认同和信息范围，替对方说话。',440,105,700,17,25,font='Song')
p('儒法同属中国文化中的不同思想传统；两岸内部观点多样。解释稳定观念，不能为向平民开枪辩护。',440,52,700,10.5,15,GRAY)
text(M,31,'教育与价值观   /   文化记忆   /   时代与信息环境',10,color=GRAY)
c.showPage();c.save()
r=PdfReader(P);assert len(r.pages)==1
assert abs(float(r.pages[0].mediabox.width)-1190.551)<1
print(str(P.resolve()),list(r.pages[0].mediabox))
