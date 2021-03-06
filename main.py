silent = False
TEMP_VARS = "11" #20
EAX = "21" #return values
EBX = "22" #halt
ECX = "23" #loop counter
EDX = "24" #temp var/general purpose
ESI = "25" #goto pointer
EDI = "26" #pointer
EBP = "27" #literal loader
ESP = "28" #stack pointer
EIP = "29" #instruction pointer
INT_VARS = "30" #50
PRINT_INT = "51"
STRING_VARS = "52" #61
STRING_EBP = "62"
PRINT_STRING = "63"
FLOAT_VARS = "64" #73
PRINT_FLOAT = "74"
PRINT_ACTIVATE = "75"
INC = "77"
DEC = "75"
CMP = "331" #585
STACK = "586" #624
MAX = 625

'''
TODO: get call & return instruction working
TODO: change to absolute goto for return instruction (or do some magic to get it to work), see future

these are cool
https://www.researchgate.net/figure/Venn-Diagram-of-Complexity-Classes-in-Currently-Believed-Structure_fig10_51932027

https://enacademic.com/dic.nsf/enwiki/4317
'''

perm_vars = {}
labels = {}
strings = []

import memEdit

def runN1(al):
  nonce = 0
  a = open("rN1",'a')
  for i in al.split("\n"):
    cells = i.split(";")
    if(cells[0]=="mult"):
      location = cells[1]
      amount = cells[2]
      a.write(">"+amount+", 2, 0, EBP, 0, 0\n")
      a.write(">0, 3, 0, EBP, 0, 0\n")
      a.write(">0, 4, 0, "+location+", 0, 0\n")
      a.write("lbl;*"+str(nonce)+"Start\n")
      a.write("if;2;0\n")
      a.write("goto;:*"+str(nonce)+"End\n")
      a.write("add;"+location+";4\n")
      a.write("dec;2\n")
      a.write("goto;:*"+str(nonce)+"Start\n")
      a.write("lbl;*"+str(nonce)+"End\n")
      nonce += 1
    else:
      a.write(i+"\n")


def run0(al):
  nonce = 0
  a = open("r0",'a')
  for i in al.split("\n"):
    cells = i.split(";")
    if(cells[0]=="add"):
      lin = i.split(";")
      location = str(lin[1])
      amount = str(lin[2])
      a.write(">"+amount+", 1, 0, "+EBP+", 0, 0\n")
      a.write("lbl;+"+str(nonce)+"Start\n")
      a.write(">0, "+TEMP_VARS+", 0, "+EBP+", 0, 0\n")
      a.write("if;1;"+TEMP_VARS+"\n")
      a.write("goto;:+"+str(nonce)+"Mid\n")
      a.write("goto;:+"+str(nonce)+"End\n")
      a.write("lbl;+"+str(nonce)+"Mid\n")
      a.write(">0, 1, 0, "+DEC+", [1], 0\n")#dec ecx
      a.write(">0, "+location+", 0, "+INC+", ["+location+"], 0\n")#inc location
      a.write("goto;:+"+str(nonce)+"Start\n")
      a.write("lbl;+"+str(nonce)+"End\n")
      nonce +=1

    elif(cells[0]=="sub"):
      lin = i.split(";")
      location = str(lin[1])
      amount = str(lin[2])
      a.write(">"+amount+", 1, 0, "+EBP+", 0, 0\n")
      a.write("lbl;+"+str(nonce)+"Start\n")
      a.write(">0, "+TEMP_VARS+", 0, "+EBP+", 0, 0\n")
      a.write("if;1;"+TEMP_VARS+"\n")
      a.write("goto;:+"+str(nonce)+"Mid\n")
      a.write("goto;:+"+str(nonce)+"End\n")
      a.write("lbl;+"+str(nonce)+"Mid\n")
      a.write(">0, 1, 0, "+DEC+", [1], 0\n")#dec ecx
      a.write(">0, "+location+", 0, "+DEC+", ["+location+"], 0\n")#dec location
      a.write("goto;:+"+str(nonce)+"Start\n")
      a.write("lbl;+"+str(nonce)+"End\n")
      nonce +=1
    else:
      a.write(i+"\n")
  a.close()

def run1(al):
  global labels
  a = open("r1","a")
  ids = 0
  for i in al.split("\n"):
    cells = i.split(";")
    if(cells[0]=="if"):
      ids+=1
      a.write(">0, "+CMP+", ["+cells[2]+"], "+EBP+", 0, 0\n") #cmp loc 1
      a.write(">1, "+CMP+", ["+cells[1]+"], "+EBP+", 0, 0\n") #w/ loc 2
      a.write(">0, "+EAX+", 0, "+CMP+", ["+cells[2]+"], 0\n") #return to eax
      a.write("goto;["+EAX+"]\n") #decider
    elif(cells[0]=="call"):
      a.write("push;EIP\n")
      a.write("goto;:"+cells[1]+"\n")
    elif(cells[0]=="return"):
      a.write("pop;\n")
      a.write(">0, EIP, 0, EAX, 0, 0\n")
    else:
      a.write(i+"\n")

def run2(al):
  a = open("r2","a")
  for i in al.split("\n"):
    cells = i.split(";")
    if(cells[0]=="print"):
      if(cells[1]=="int"):
        a.write(">"+cells[2]+", "+PRINT_INT+", 0, "+EBP+", 0, 0\n")
        a.write(">1, "+PRINT_ACTIVATE+", 0, "+EBP+", 0, 0\n")
      elif(cells[1]=="string"):
        a.write('>"'+cells[2]+'", '+PRINT_STRING+", 0, "+STRING_EBP+", 0, 0\n")
        a.write(">2, "+PRINT_ACTIVATE+", 0, "+EBP+", 0, 0\n")
    elif(cells[0]=="nop"):
      a.write(">0, "+EAX+", 0, "+EAX+", 0, 0\n")
    elif(cells[0]=="goto"):
      a.write(">0, "+EAX+", 0, "+EAX+", 0, "+cells[1]+"\n")
    elif(cells[0]=="halt"):
      a.write(">0, 0, 0, "+EBP+", 0, 0\n")
    elif(cells[0]=="dec"):
      a.write(">0, "+cells[1]+", 0, "+DEC+", ["+cells[1]+"], 0\n")
    elif(cells[0]=="inc"):
      a.write(">0, "+cells[1]+", 0, "+INC+", ["+cells[1]+"], 0\n")      
    elif(cells[0]=="push"):
      a.write(">"+cells[1]+", "+STACK+", ["+ESP+"], "+EBP+", 0, 0\n")#put in on the stack
      a.write(">0, "+ESP+", 0, "+INC+", ["+ESP+"], 0\n")#inc stack pointer
    elif(cells[0]=="pop"):
      a.write(">0, "+ESP+", 0, "+DEC+", ["+ESP+"], 0\n")#dec stack pointer
      a.write(">0, "+EAX+", 0, "+STACK+", ["+ESP+"], 0\n")#put top of stack into eax

    else:
      a.write(i+"\n")
  a.close()

def run3(al):
  a = open("r3","a")
  global perm_vars, labels
  c = 0
  varC = 0
  for i in al.split("\n"):
    c+=1
    cells = i.split(";")
    if(cells[0]=="lbl"):
      labels[cells[1]]=c
      a.write(">0, "+EAX+", 0, "+EAX+", 0, 0\n") #nop
    elif(cells[0]=="var"):
      if(cells[2]=="int"):
        perm_vars[cells[1]]=int(INT_VARS)+varC
        a.write(">"+cells[3]+", "+INT_VARS+", "+str(varC)+", "+EBP+", 0, 0\n")
        varC+=1
    else:
      a.write(i+"\n")

def run4(al):
  global perm_vars, labels, strings
  lineCount = 0
  a = open("out.bc","a")
  for i in al.split("\n"):
    lineCount+=1
    splitCells = i.split(";")
    if(splitCells[0]=="pvar"):
      if(splitCells[1]=="int"):
        splitCells[2] = splitCells[2].replace("/","")
        a.write(">0, "+PRINT_INT+", 0, "+str(perm_vars[splitCells[2]])+", 0, 0\n")
        a.write(">1, "+PRINT_ACTIVATE+", 0, "+EBP+", 0, 0\n")
    else:
      for reg in ["EAX","EBX","ECX","EDX","ESI","EDI","EBP","ESP","EIP"]:
        if(reg in i):
          for cell in i.replace("/","").replace("[","").replace("]","").replace(">","").split(", "):
            if(reg in cell):
              i = i.replace(cell, eval(cell))
      if("/" in i):
        for cell in i.split(", "):
          if('/' in cell):
            cell = cell.replace("/","").replace(" ","").replace("[","").replace("]","").replace(">","")
            location = perm_vars[cell]
            i = i.replace("/"+cell, str(location))
      if("[" in i):
        for cell in i.split(", "):
          if("[" in cell):
            cell = cell.replace("/","").replace(" ","").replace("[","").replace("]","").replace(">","")
            ncell = str( int(cell)+MAX )
            i = i.replace("["+cell+"]",ncell)
      if(":" in i):
        for cell in i.split(", "):
          if(":" in cell):
            cell = cell.replace("/","").replace(" ","").replace("[","").replace("]","").replace(">","")
            targetLn = labels[cell.replace(":","")]
            delta = targetLn - lineCount - 1 #decrease 1 for goto rules
            i = i.replace(cell,str(delta))
      if('"' in i):
        for cell in i.split(", "):
          if('"' in cell):
            cell = cell.replace("/","").replace(" ","").replace("[","").replace("]","").replace(">","").replace('"',"")
            strings.append(cell)
            i = i.replace('"'+cell+'"',str(strings.index(cell)-MAX))
            #TO-DO: finish replacing strings; I/O isn't that big of a deal rn
      a.write(i+"\n")

def clear():
  files = ["out.bc","rN1","r0","r1","r2","r3"]
  for i in files:
    a = open(i,"w")
    a.write("")
    a.close()

def makeAl(f): #make 'al' variable for writing reading/writing
  a = open(f,"r")
  al = a.read()
  a.close()
  return(al)

def makeAr(al): #make array from file
  a = open("out.bc","w")
  al = al.replace("\n>",", ")
  al = al.replace(">","")
  al = al.replace("\n","")
  a.write(al)

def compile():
  clear()
  
  runN1(makeAl("in.mitc"))
  run0(makeAl("rN1"))
  run1(makeAl("r0"))
  run2(makeAl("r1"))
  run3(makeAl("r2"))
  run4(makeAl("r3"))

  print("var",perm_vars)
  print("lbl",labels)
  print("strings",strings)

howdy = '''

.88b  d88. d888888b d888888b .d8888. db    db
88'YbdP`88   `88'   `~~88~~' 88'  YP `8b  d8'
88  88  88    88       88    `8bo.    `8bd8' 
88  88  88    88       88      `Y8b.    88   
88  88  88   .88.      88    db   8D    88   
YP  YP  YP Y888888P    YP    `8888Y'    YP   

'''

def run():
  print(howdy)
  while(True):
    print("What do you want to do?")
    print('''
    1) Compile a program
    2) Edit memory
    3) Cleanup instructions
    99) Exit
    ''')
    choice = input("> ")
    if(choice == "1"):
      compile()
    elif(choice == "2"):
      memEdit.run()
    elif(choice == "3"):
      makeAr(makeAl("out.bc"))
    elif(choice == "99"):
      break
  print("Have fun")

if(silent):
  compile()
  makeAr(makeAl("out.bc"))
else:
  run()
