from pathlib import Path
root=Path('output/speeches')
a=root/'第二位同学_两岸文化认同.txt';s=a.read_text()
s=s.replace('第二位同学：两岸文化认同','第二位同学：A国与B地区的文化认同').replace('第二个例子，是两岸文化认同。','第二个例子，我们用A国和B地区作为代称，讨论文化认同。').replace('两岸','A国和B地区').replace('大陆','A国').replace('台湾','B地区')
start=s.index('赖清德');end=s.index('\n\n',start)
s=s[:start]+'同样是在谈文化联系，有人先感受到亲近，有人却先担心自己的独特经历被忽略。因此，双方听到相近的话，也可能理解出不同的意思。'+s[end:]
b=root/'第二位同学_A国与B地区.txt';b.write_text(s);a.unlink()
a=root/'第三位同学_1989与总结.txt';s=a.read_text().replace('第三位同学：1989＋总结','第三位同学：某国的公共讨论＋总结').replace('第三个例子，是海报上的1989。','第三个例子，我们隐去国名和时间，只讨论其中的文化观念。\n\n有一个国家，曾发生过这样一场公共讨论。').replace('当年的公共讨论中','在这场讨论中').replace('两岸文化认同的例子','A国与B地区文化认同的例子').replace('1989的例子','某国公共讨论的例子')
b=root/'第三位同学_某国公共讨论与总结.txt';b.write_text(s);a.unlink()
s=Path('tmp/pdfs/poster_diagram.py').read_text()
s=s.replace('TOK_A3横版海报_图解版.pdf','TOK_A3横版海报_匿名版.pdf')
s=s.replace('兩岸文化認同','A國與B地區').replace('大陸一些人','A國一些人').replace('臺灣一些人','B地區一些人').replace('強調臺灣特色','強調B地區特色')
s=s.replace('賴清德2025年雙十講話強調民主化記憶，呈現以共同經歷建構認同的方式。','同樣談文化聯繫，有人先感到親近，有人先擔心自己的獨特經歷被忽略。')
s=s.replace("'1989',51","'某国',43")
s=s.replace('一些学生要求对话，将表达诉求视为关心国家；领导层更强调稳定与秩序。','有一个国家，在一次公共讨论中，一些参与者要求对话；管理者则更强调稳定与秩序。')
s=s.replace("assert 'A國與B地區' in s and '1989' in s","assert 'A國與B地區' in s and '某国' in s\nfor bad in ['1989','2025','台湾','臺灣','两岸','兩岸','赖清德','賴清德','双十','雙十']:assert bad not in s,bad")
Path('tmp/pdfs/poster_anonymous.py').write_text(s)
for path in root.glob('*.txt'):
 text=path.read_text()
 if path.name.startswith(('第二','第三')):
  for bad in ['1989','2025','台湾','两岸','赖清德','双十']:assert bad not in text,(path,bad)
print('Updated scripts:',*[p.name for p in root.glob('*.txt')],sep='\n')
