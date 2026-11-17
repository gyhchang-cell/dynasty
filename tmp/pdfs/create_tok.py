from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3,A4
from reportlab.lib.colors import HexColor, Color, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from pypdf import PdfReader
from pathlib import Path

OUT=Path('output/pdf'); OUT.mkdir(parents=True,exist_ok=True)
pdfmetrics.registerFont(TTFont('CJK','/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))
INK='#182C3B'; MUTED='#526574'; BG='#F6F3EC'; TEAL='#176B70'; RUST='#A95035'; BLUE='#355E90'
def txt(c,x,y,s,size=12,color=INK):
 c.setFillColor(HexColor(color)); c.setFont('CJK',size); c.drawString(x,y,s)
def para(c,s,x,top,width,size=13,leading=None,color=INK):
 st=ParagraphStyle('p',fontName='CJK',fontSize=size,leading=leading or size*1.48,textColor=HexColor(color),wordWrap='CJK',spaceAfter=0)
 p=Paragraph(s,st); w,h=p.wrap(width,1500); p.drawOn(c,x,top-h); return top-h
def box(c,x,y,w,h,color,r=10):
 c.setFillColor(HexColor(color)); c.roundRect(x,y,w,h,r,fill=1,stroke=0)
def line(c,x,y,w,color='#DADFD9'):
 c.setStrokeColor(HexColor(color));c.setLineWidth(.7);c.line(x,y,x+w,y)

p=OUT/'TOK_A3海报.pdf';c=canvas.Canvas(str(p),pagesize=A3);W,H=A3
c.setTitle('TOK｜文化背景与客观理解｜A3海报');c.setAuthor('TOK小组')
c.setFillColor(HexColor(BG));c.rect(0,0,W,H,fill=1,stroke=0)
M=36; CW=W-2*M
box(c,M,H-52,142,22,TEAL,4);txt(c,M+10,H-45,'TOK  ·  第6题',11,'#FFFFFF')
txt(c,M,H-96,'我们能否摆脱自身的文化背景，',27)
txt(c,M,H-134,'客观地理解另一种思想？',27)
para(c,'我们的回答：完全摆脱很难，但可以通过反思自己的标准、理解不同经历、比较原始材料，减少偏见。',M,H-155,CW,15,22)
box(c,M,H-222,CW,31,'#E7ECE6',5)
txt(c,M+12,H-211,'文化背景：教育、价值观、共同记忆与时代经验   ｜   客观理解：准确理解主张和理由',11.8)

cards=[
 dict(n='01',color=TEAL,title='儒法之争：我用什么标准判断？',tag='已有价值标准',lefthead='两种思想的重点 [1][2]',left='儒家重视德与礼的教化；韩非重视法令与赏罚，认为治理不能只靠人人自觉行善。两者是侧重点不同，不是儒家完全不要刑罚。',righthead='怎样影响理解？',right='习惯儒家标准的人，可能只看到法家“缺少仁义”，忽略它为何认为治理需要制度约束。先理解理由，仍然可以批评严刑与权力集中。',chain='儒家教育 → 重视道德教化 → 用同一标准看法家 → 可能忽略法家的治理理由',question='扣题：不必放弃自己的价值观，但不能把它当成理解对方的唯一标准。'),
 dict(n='02',color=BLUE,title='台湾：共同文化，为何认同不同？',tag='文化记忆与认同',lefthead='从大陆重视共同文化者看',left='共享语言、节日和经典，容易让人期待相同认同。但强调台湾独特性，也可能来自当地历史与生活经验，不一定否认共同文化。',righthead='从台湾重视地方经验者看 [3][4]',right='重视地方特色，可能让人警惕“共同文化”的表述。但重视共同性，也可能包含祖籍、亲属与文化上的亲近感，不一定否定地方差异。',chain='不同成长经历 → 不同文化认同 → 以自身经验解释对方 → 可能误读其真实理由',question='扣题：听懂不同认同如何形成，不等于必须改变自己的认同。'),
 dict(n='03',color=RUST,title='六四：时代背景与信息怎样影响理解？',tag='时代与信息环境',lefthead='事实与背景 [5][6][7][8]',left='1989年学生宣言要求对话并强调爱国；领导层强调稳定。6月3日晚至4日，部队用实弹推进，造成平民死伤。其后有拘捕，相关讨论长期受限。',righthead='怎样影响理解？',right='若先把学生诉求视为秩序威胁，可能忽略其改革理由；若主要接触一种解释，也难以比较。阅读学生与官方原文，再分别评价诉求、行动和回应。',chain='时代价值与传播环境 → 注意到的材料和问题不同 → 形成对同一思想的不同理解',question='扣题：个人愿意客观，还需要接触和比较不同解释的机会。')]
top=H-239; ch=220;gap=12
for d in cards:
 bottom=top-ch;box(c,M,bottom,CW,ch,'#FFFFFF',10)
 box(c,M+15,top-45,38,30,d['color'],5);txt(c,M+21,top-36,d['n'],17,'#FFFFFF')
 txt(c,M+65,top-36,d['title'],18.5,d['color'])
 x1=M+18;x2=M+CW/2+10;col=CW/2-33
 txt(c,x1,top-66,d['lefthead'],12,d['color']);txt(c,x2,top-66,d['righthead'],12,d['color'])
 para(c,d['left'],x1,top-76,col,12.2,17.6)
 para(c,d['right'],x2,top-76,col,12.2,17.6)
 box(c,M+15,bottom+38,CW-30,28,'#F0F3F0',4)
 txt(c,M+24,bottom+48,d['chain'],11.6)
 txt(c,M+18,bottom+17,d['question'],12.2,d['color'])
 top=bottom-gap
# Bottom argument and evidence notes
bt=top-2
txt(c,M,bt-13,'理解 ≠ 赞同',20,TEAL)
para(c,'承认背景有影响，不代表所有解释同样正确。先听懂理由，再用证据判断。',M+177,bt+3,CW-177,13,19)
para(c,'案例边界：儒法同属中国文化中的不同思想传统；两岸内部观点多样，官方讲话不代表所有人；六四的时代背景不能为向平民开枪提供正当性。',M,bt-35,CW,10.5,15,MUTED)
line(c,M,bt-79,CW)
para(c,'资料索引：[1]《论语·为政》 [2]《韩非子·显学》 [3] 2022年台湾问题白皮书 [4] 赖清德2025年双十讲话<br/>[5] 1989年5月13日学生宣言 [6] 邓小平1989年讲话 [7] 国际特赦组织六四资料 [8] 人权观察／美联社记录<br/>完整链接见配套讲稿末页。因果链为小组分析，不能据此概括所有人的动机或认知。',M,bt-88,CW,8.8,13,MUTED)
c.showPage();c.save()

speeches=[('第一位同学','开场＋儒家与法家','约2分40秒',[
'大家好，我们讨论的问题是：我们能否摆脱自身的文化背景，客观地理解另一种思想？我们的回答是：完全摆脱很难，但通过反思自己的标准、了解不同经历和比较资料，可以减少偏见。',
'我们说的文化背景，包括接受的教育、熟悉的价值观、共同记忆和时代经验。“客观理解”则是先准确说清对方主张什么、为什么这样主张，再评价它。理解不等于赞同。',
'第一个课内案例，是百家争鸣中的儒法之争。儒家与法家同属中国文化，却形成不同的思想传统，因此也能说明教育和价值背景的影响。',
'以孔子和韩非为例：孔子重视德与礼，认为人不应只是害怕惩罚，还应培养羞耻心。韩非则强调，治理不能主要指望人人自觉行善，而要通过法令与赏罚，使人难以作恶。[1][2]',
'假设一个人长期接受儒家教育，他可能习惯先问：这种治理方式能不能培养人的道德？接触法家时，就可能只看到赏罚严厉、缺少仁义，没有先问：韩非为什么不愿意把国家治理寄托在人的自觉上？',
'这里的因果关系是：原有教育形成判断标准；我们用这个标准看待另一种思想；于是容易忽略对方自己的理由。这是可能发生的理解偏差，不是说所有儒家学者都误解法家。',
'那么，我们能否摆脱自身的文化背景，客观地理解另一种思想？这个案例说明，我们不必放弃儒家的价值观，但应先承认：道德教化不是理解法家的唯一角度。先理解制度约束的理由，再讨论它是否过分依赖惩罚、是否缺少对统治者的约束。',
'所以，第一个理由是：文化背景会影响我们使用什么判断标准，但反思这个标准，可以帮助我们更客观。下面由第二位同学介绍，文化记忆与身份认同怎样影响理解。'
]),('第二位同学','台湾：共同文化与不同认同','约2分40秒',[
'第二个观点是：共同的文化，不一定带来相同的认同。不同的成长经历，也会影响我们理解另一种思想。这里讨论两岸对共同文化与地方特色的不同重视，不预设两岸每个人想法一样。',
'从大陆重视共同文化者的角度看，共享语言、节日、经典和家庭传统，可能让人产生亲近感，并期待相同的身份认同。大陆政府2022年白皮书，也强调历史文化联系，并把统一与民族复兴联系起来。这是官方表述，不能代表每个大陆人的理由。[3]',
'因此，当一个人听到强调台湾独特性的主张时，可能先想：既然文化有这么多共同点，为什么还强调不同？如果直接把这种主张理解成拒绝共同文化，就可能忽略：当地的历史、家庭记忆和生活经验，也影响着对方怎样认识自己。',
'扣回题目，我们能否摆脱自身的文化背景，客观地理解另一种思想？这里的困难是：我们容易认为，对方应该像自己一样，根据共同传统来形成认同。',
'反过来，从台湾重视地方文化者的角度看，当地经验可能使人特别重视自己的独特性。赖清德2025年双十讲话，就把台湾的民主化经历描述为共同记忆，并将其与台湾认同联系起来。这体现他表达认同的方式，不代表所有台湾人。[4]',
'如果从这种背景出发，有人可能把强调共同文化理解为否定地方特色，却忽略大陆一些人重视共同性的原因，也包括祖籍、亲属、节日和文学带来的真实感情。',
'两种情况的因果关系是：成长经历形成不同认同；人们用自己的认同解释对方；就可能误读对方的理由。这是小组提出的分析，不代表双方每个人都会这样。',
'所以，对原题的回答是：完全放下文化认同很难，但我们可以先了解对方的认同怎样形成。承认共同文化，不必抹掉地方差异；承认地方差异，也不必否定共同文化。更客观的理解，不要求我们最后变得一样。接下来由第三位同学介绍六四案例。'
]),('第三位同学','六四：时代背景、信息环境＋总结','约3分20秒',[
'第三个观点是：时代背景影响我们先看到什么，信息环境影响我们还能看到什么。这两者都会影响我们理解另一种思想。我们的案例是1989年六四事件。',
'先说事实。学生与市民参与了抗议。5月13日的学生《绝食宣言》强调爱国，要求政府承认学生运动的正当性，并开展实质性对话。这份文字让我们了解部分学生为什么行动，但不代表所有参与者。[5]',
'当时改革开放带来新的讨论空间，同时，领导层的公开论述高度重视稳定。邓小平在1989年3月强调稳定是改革发展的必要条件。也就是说，同处一个社会，人们可能先注意不同的问题：一方强调表达与对话，一方强调秩序风险。[6]',
'这怎样扣回原题？如果先把稳定作为最重要的标准，就可能先看到示威造成的秩序问题，进而把改革诉求视为威胁，没有充分理解参与者为什么认为公开表达能够改善社会。支持学生诉求的人，也不能因此认定所有具体行动都合理。',
'政府随后宣布戒严。6月3日晚至4日，解放军部队向北京市中心推进，使用实弹和装甲车辆，造成包括无武装平民在内的人员死亡和受伤。我们不引用不确定的死亡数字。6月9日，邓小平肯定军队行动，并用“暴乱”的框架解释事件。[6][7]',
'必须分清：理解领导层为何重视稳定，不等于认可向平民开枪。文化背景可以帮助解释判断，却不能自动为行为提供正当性。',
'事件之后，当局逮捕参与者，并长期限制相关讨论和纪念。这影响后来的人接触和比较不同解释的机会。[8] 因果关系就是：传播环境限制材料范围；材料范围影响我们听到哪些理由；这些理由再影响我们接受什么解释。',
'再次回答题目：我们能否摆脱自身的文化背景，客观地理解另一种思想？仅靠个人愿意客观还不够，也要接触学生宣言、官方讲话和独立记录，把诉求、行动和政府回应分开判断。',
'三个案例分别说明：儒法之争涉及判断标准，台湾案例涉及文化记忆与认同，六四案例涉及时代与信息环境。它们不能证明人永远无法客观，也不代表各种解释同样正确。',
'我们的结论是：完全摆脱背景很难，但可以减少它的影响。先理解，再评价；理解不等于赞同。不要让自己熟悉的标准、认同和有限的信息，代替对另一种思想的认真了解。谢谢大家。'
])]
refs=[
('[1] 儒家思想原文','《论语·为政》：德、礼与政、刑的比较。','https://ctext.org/text.pl?if=gb&node=1120&show=parallel'),
('[2] 法家思想原文','《韩非子·显学》：不主要依靠自觉行善，重视法与赏罚。','https://zh.wikisource.org/wiki/韓非子_(四庫全書本)/卷19'),
('[3] 大陆政府公开表述','《台湾问题与新时代中国统一事业》，2022年8月。','https://lt.china-office.gov.cn/chn/sgxw/202208/t20220810_10739960.htm'),
('[4] 台湾方面公开表述','赖清德双十讲话《变局中，奋起的新台湾》，2025年10月10日。','https://www.president.gov.tw/NEWS/39524'),
('[5] 部分学生的诉求原文','1989年5月13日《绝食宣言》，哥伦比亚大学史料选译。','https://afe.easia.columbia.edu/main_pop/ps/ps_china-tiananmen-hunger-strike.htm'),
('[6] 当时领导层的讲话','邓小平1989年3月4日、6月9日讲话英译。','https://www.marxists.org/reference/archive/deng-xiaoping/1989/178.htm'),
('[6] 续：6月9日讲话','用于研究官方如何解释事件，不将其中指控直接当作事实。','https://www.marxists.org/reference/archive/deng-xiaoping/1989/5.htm'),
('[7] 军事镇压事实记录','国际特赦组织：The 1989 Tiananmen Crackdown。','https://www.amnesty.org/en/projects/the-1989-tiananmen-crackdown/'),
('[8] 拘捕、审判与后续记录','人权观察：Tiananmen Archives, 1989–2004。','https://www.hrw.org/news/2016/06/02/tiananmen-archives-1989-2004'),
('[8] 续：相关讨论与纪念受限','美联社2025年6月4日现场报道。','https://apnews.com/article/451a7dfd09b3662791148999b6007e1e')]
q=OUT/'TOK三人演讲稿.pdf';c=canvas.Canvas(str(q),pagesize=A4);w,h=A4
c.setTitle('TOK｜三人演讲稿与资料来源');c.setAuthor('TOK小组')
for i,(who,title,timing,parts) in enumerate(speeches):
 c.setFillColor(HexColor(BG));c.rect(0,0,w,h,fill=1,stroke=0)
 txt(c,42,h-45,'TOK  ·  第6题  ·  三人演讲稿',10,TEAL)
 txt(c,42,h-80,who+'｜'+title,19)
 txt(c,42,h-104,timing+'  ·  时间为估算，排练时以实际语速为准  ·  方括号编号不用读',9.2,MUTED)
 y=h-129
 for s in parts:
  y=para(c,s,42,y,w-84,11.1,17)-10
 assert y>48,(who,y)
 line(c,42,39,w-84);txt(c,42,23,'建议总时长约8分40秒；预留停顿与交接。',9,MUTED);txt(c,w-65,23,str(i+1),9,MUTED)
 c.showPage()
# Sources page with hyperlinks
c.setFillColor(HexColor(BG));c.rect(0,0,w,h,fill=1,stroke=0)
txt(c,42,h-45,'TOK  ·  资料与排练提示',10,TEAL);txt(c,42,h-79,'资料来源与使用边界',22)
y=h-103
for title,desc,url in refs:
 y=para(c,title+'  '+desc,42,y,w-84,10.2,14)-2
 c.setFillColor(HexColor(TEAL)); c.setFont('CJK',9)
 label='点击打开原文 / 记录'; c.drawString(42,y-9,label);c.linkURL(url,(42,y-12,180,y+1),relative=0,thickness=0)
 y-=26
line(c,42,y+4,w-84)
y=para(c,'排练与答问',42,y-9,w-84,13,18)-8
for s in [
 '三人按顺序发言，总时长为估算。若接近10分钟，优先删去重复的背景句，保留案例事实、因果关系和结论。',
 '若被问“这能证明完全无法客观吗？”：不能。案例说明背景可能构成障碍，同时提出反思标准与比较材料的办法。',
 '若被问“解释政府行为是不是认可镇压？”：不是。解释原因与判断正当性是不同问题。',
 '材料边界：官方讲话只能直接证明公开表述；不能代表所有人或证明所有动机。文化影响也不是事件唯一原因，权力、利益和具体决策同样重要。']:
 y=para(c,'• '+s,42,y,w-84,10.1,14.5)-7
assert y>45,y
txt(c,w-65,23,'4',9,MUTED);c.showPage();c.save()
# plain text companion for editing (no separate authoring format assumptions)
(OUT/'TOK三人演讲稿.txt').write_text('\n\n'.join(who+'｜'+title+'（'+t+'）\n\n'+'\n\n'.join(parts) for who,title,t,parts in speeches)+'\n\n资料来源\n'+'\n'.join(a+' '+b+'\n'+u for a,b,u in refs),encoding='utf-8')
for path,count in [(p,1),(q,4)]:
 r=PdfReader(path);assert len(r.pages)==count
 print(path.resolve(), 'pages=',len(r.pages),'size_pt=',list(r.pages[0].mediabox)[2:])
