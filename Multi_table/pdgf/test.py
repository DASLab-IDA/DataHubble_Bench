f = open("dicts/desc.dict", "r", encoding='utf-8')
o = open("new.dict", "w", encoding='utf-8')
line = f.readline()
while line:
    print(line)
    o.write(line)
    line = f.readline()