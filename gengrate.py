import os

from re import sub
from re import compile
from sympy  import  *
from sympy import re, im, I, E
from sympy import diff,expand
from sympy.parsing import sympy_parser
from sympy.parsing.sympy_parser import standard_transformations

from excel2txt import excel2txt
# 参数的类型取值
paraValue = ['internalFV','internalGV','stateV','algebV','constC','otherV']

class codeGenerate:
    def __init__(self,name,className,data_path):

        # 状态变量列表,储存对象均为类
        self.stateVList =[]
        # 代数变量列表
        self.algebVList =[]
        # 常数列表
        self.constCList =[]
        # 内部变量
        self.internalFVList = []
        self.internalGVList = []
        # 状态方程列表
        self.stateFList =[]
        # 代数方程列表
        self.algebFList =[]
        # 内部变量方程
        self.internalFFList = []
        self.internalGFList = []
        #其他变量方程
        self.otherVList=[]
        self.initialVList=[]
        self.initialFList=[]
        self.excelpath = data_path
        self.txtpath = 'excel2txt.txt'
        self.templatepath ='template.txt'
        self.name = name
        self.className =className
        self.alter('name',self.name)
        self.alter('className',self.className)
        #用于测试的代码列表
        self.codeList=[]
    def dataRead(self):
        excel2txt(self.excelpath, self.txtpath)
        case = open(self.txtpath)
        for each_line in case:
            data = each_line.split()
            if data[0] == 'State':
                self.stateVList.append(data[1])
                self.stateFList.append(data[2])

            elif data[0] == 'Algeb':
                self.algebVList.append(data[1])
                self.algebFList.append(data[2])

            elif data[0] == 'Internal_f':
                self.internalFVList.append(data[1])
                self.internalFFList.append(data[2])

            elif data[0] == 'Internal_g':
                self.internalGVList.append(data[1])
                self.internalGFList.append(data[2])

            elif data[0] == 'Constant':
                self.constCList.append(data[1])

            elif data[0] == 'Initial':
                self.initialVList.append(data[1])
                self.initialFList.append(data[2])


    # 用于替换模板里的内容
    def alter(self, old_str, new_str):
        file = self.templatepath
        with open(file, "r", encoding="utf-8") as f1, open("%s.bak" % file, "w", encoding="utf-8") as f2:
            for line in f1:
                f2.write(sub('%\('+old_str+'\)', new_str, line))
        os.remove(file)
        os.rename("%s.bak" % file, file)
    # 返回表达式中的所有参数
    def variableGet(self,expression):
        local_dict = {}
        global_dict = {}
        transformations = standard_transformations
        code = sympy_parser.stringify_expr(expression, local_dict, global_dict, transformations)
        code = sub(' ', '', code)
        pattern = compile(r'(?<=Symbol\(\').*?(?=\'\))')
        variableList = pattern.findall(code)
        pattern = compile(r'(?<=Function\(\').*?(?=\'\))')
        functionList = pattern.findall(code)
        return [variableList,functionList]
    #返回幅角表达式
    def angleCal(self,expression):
        str = 'cmplx.Phase('+expression+')'
        return str
    # 返回共轭表达式
    def conjCal(self,expression):
        str = 'cmplx.Conj('+expression+')'
        return str
    def expCal(self,expression):
        str = 'cmplx.Exp('+expression+')'
        return str
    def reCal(self,expression):
        str = 'real('+expression+')'
        return str
    def imCal(self,expression):
        str = 'imag('+expression+')'
        return str
    def sinCal(self,expression):
        str = 'math.Sin(' + expression + ')'
        return str
    def cosCal(self,expression):
        str = 'math.Cos(' + expression + ')'
        return str
    #返回复数表达式
    # if 'I' in variableList
    def complexCal(self,variableList,expression):
        tempCode = ''
        self.complex = ''
        for item in variableList:
            if item != 'I':
                tempCode+= item+'=symbols(\"'+item+'\",integer=True)\n'
        tempCode+='comp=('+expression+').as_real_imag()\n'
        tempCode+="self.complex+='complex('+str(comp[0])+','+str(comp[1])+')'\n"
        exec(tempCode)
        return self.complex
    def structGenerate(self):
        variableList=[self.constCList,self.stateVList,self.algebVList,self.internalFVList,self.internalGVList]
        variableCodeList = ['constListCode', 'stateVListCode','algebVListCode','internalFVListCode','internalGVListCode']
        # 此处应该可以用for循环代替
        for v_list in variableList:
            tempCode =''
            for variable in v_list:
                tempCode += variable+','
            tempCode = tempCode[:-1]
            self.alter(variableCodeList[variableList.index(v_list)], tempCode)
    def initalGenerate(self):
        variableList=[self.stateVList,self.algebVList]
        variableCodeList = ['stOrderCode','alOrderCode']
        tempCode = ''
        for v_list in variableList:
            tempCode =''
            for variable in v_list:
                tempCode += '\"'+variable+'\",'
            tempCode = tempCode[:-1]
            self.alter(variableCodeList[variableList.index(v_list)], tempCode)

        tempCode=""
        for item in self.constCList:
            tempCode+='\t'+self.name+'.pVarF[\"'+item+'\"]=&'+self.name+'.'+item+'\n'
        tempCode = tempCode[1:]
        tempCode += '\n'

        for item in self.stateVList:
            tempCode+='\t'+self.name+'.pVarSt[\"'+item+'\"]=&'+self.name+'.'+item+'\n'
        tempCode += '\n'

        for item in self.algebVList:
            tempCode+='\t'+self.name+'.pVarAl[\"'+item+'\"]=&'+self.name+'.'+item+'\n'
        tempCode += '\n'
        self.alter('initalCode', tempCode)

    def setX0Generate(self):
        # 依次处理语句,可化简
        tempCode = ''
        for equation in self.initialFList:
            if equation[0].islower() == True:
                tempCode+=self.setX0FunctionHandle(equation)
        for equation in self.initialFList:
            if equation[0].isupper() == True:
                tempCode += self.setX0FunctionHandle(equation)
        self.alter('setX0Code', tempCode)

    def setX0FunctionHandle(self,equation):
            linkSymbol = '='
            expression=equation.split('=')
            # 不知道为什么，正则头尾没有字符式匹配不到东西
            expression[1]=' '+expression[1]+' '
            if expression[0] in self.stateVList:
                expression[0]=self.name+'.pDae.X['+self.name+'.'+expression[0]+'[i]]'
            elif expression[0] in self.algebVList:
                expression[0]=self.name+'.pDae.Y['+self.name+'.'+expression[0]+'[i]]'
            else:
                linkSymbol=':='
            [variableList,functionList]= self.variableGet(expression[1])
            # 如果存在复数或者指数，则预处理
            for function in functionList:
                expression[1]=self.functionHandle(function,expression[1],variableList)
            if 'I' in variableList and functionList==[]:
                expression[1]=self.complexCal(variableList,expression[1])
            for variable in variableList:
                if variable =='pi':
                    pattern = '(?<=[^.])' + variable + '(?=[^a-zA-Z0-9])'
                    expression[1] = sub(pattern, 'math.Pi', expression[1])
                if variable in self.constCList:
                    pattern = '(?<=[^.])' + variable + '(?=[^a-zA-Z0-9])'
                    expression[1] = sub(pattern,self.name + '.' + variable +'[i]', expression[1])
                if variable in self.stateVList:
                    pattern = '(?<=[^.])' + variable + '(?=[^a-zA-Z0-9])'
                    subs = self.name + '.pDae.X[' + self.name + '.' + variable + '[i]]'
                    expression[1]=sub(pattern, subs, expression[1])
                if variable in self.algebVList:
                    pattern = '(?<=[^.])' + variable + '(?=[^a-zA-Z0-9])'
                    subs = self.name + '.pDae.Y[' + self.name + '.' + variable + '[i]]'
                    expression[1] =sub(pattern, subs, expression[1])
            tempCode = '\t'+linkSymbol.join(expression)+'\n'
            return tempCode

    def calFFunctionHandle(self,equation):
        linkSymbol = '='
        expression = equation.split('=')
        if expression[0].endswith('_f')==True:
            name=sub('_f','',expression[0])
            expression[0] = self.name + '.pDae.X[' + self.name + '.' + name + '[i]]'
        else :
            linkSymbol=':='

        expression[1] = ' ' + expression[1] + ' '
        [variableList, functionList] = self.variableGet(expression[1])
        for function in functionList:
            expression[1] = self.functionHandle(function, expression[1], variableList)
        initial = ''

        for variable in variableList:
            if variable =='pi':
                pattern = '(?<=[^.])' + variable + '(?=[^a-zA-Z0-9])'
                expression[1] = sub(pattern, 'math.Pi', expression[1])
            # 替换常数项
            if variable in self.constCList:
                pattern = '(?<=[^.])' + variable + '(?=[^a-zA-Z0-9])'
                expression[1] = sub(pattern,self.name + '.' + variable +'[i]', expression[1])
            if variable in self.variableHandledList:
                continue
            else:
                self.variableHandledList.append(variable)
                if variable in self.stateVList:
                    pattern = '(?<=[^.])' + variable + '(?=[^a-zA-Z0-9])'
                    initial +='\t'+variable+':='+ self.name + '.pDae.X[' + self.name + '.' + variable + '[i]]'+'\n'
                elif variable in self.algebVList:
                    pattern = '(?<=[^.])' + variable + '(?=[^a-zA-Z0-9])'
                    initial +='\t'+variable+':='+ self.name + '.pDae.Y[' + self.name + '.' + variable + '[i]]'+'\n'
        tempCode = '\t'+linkSymbol.join(expression)+'\n'
        return tempCode,initial

    def calGFunctionHandle(self, equation,spliltSymbol):
        linkSymbol = '='
        expression = equation.split(spliltSymbol)
        if expression[0].endswith('_g') == True:
            name = sub('_g', '', expression[0])
            expression[0] = self.name + '.pDae.G[' + self.name + '.' + name + '[i]]'
            linkSymbol = '+='
        else :
            linkSymbol=":="
        expression[1] = ' ' + expression[1] + ' '
        [variableList, functionList] = self.variableGet(expression[1])
        for function in functionList:
            expression[1] = self.functionHandle(function, expression[1], variableList)
        initial = ''

        for variable in variableList:
            if variable == 'pi':
                pattern = '(?<=[^.])' + variable + '(?=[^a-zA-Z0-9])'
                expression[1] = sub(pattern, 'math.Pi', expression[1])
            # 替换常数项
            if variable in self.constCList:
                pattern = '(?<=[^.])' + variable + '(?=[^a-zA-Z0-9])'
                expression[1] = sub(pattern, self.name + '.' + variable + '[i]', expression[1])
            if variable.endswith('_g'):
                pattern = '(?<=[^.])' + variable + '(?=[^a-zA-Z0-9])'
                name = sub('_g', '', variable)
                subs = self.name + '.pDae.Y[' + self.name + '.' + name + '[i]]'
                expression[1]=sub(pattern, subs, expression[1])

            if variable in self.variableHandledList:
                continue
            else:
                self.variableHandledList.append(variable)
                if variable in self.stateVList:
                    initial += '\t' + variable + ':=' + self.name + '.pDae.X[' + self.name + '.' + variable + '[i]]' + '\n'
                elif variable in self.algebVList:
                    initial += '\t' + variable + ':=' + self.name + '.pDae.Y[' + self.name + '.' + variable + '[i]]' + '\n'
        tempCode = '\t' + linkSymbol.join(expression) + '\n'
        return tempCode, initial

    def addGenerate(self):
        tempCode = ''
        for item in self.constCList:
            tempCode+='\t'+self.name+'.'+item+'=append('+self.name+'.'+item+',0)\n'
        tempCode = tempCode[1:]
        self.alter('addCode', tempCode)
        pass
    def calGGenerate(self):
        initial_all = ''
        equation_all = ''
        self.variableHandledList = []
        for item in code.internalGFList:
            equation, initial = self.calGFunctionHandle(item,'=')
            initial_all += initial
            equation_all += equation
        self.variableHandledList = []
        for item in code.algebFList:
            equation, initial = self.calGFunctionHandle(item,'+=')
            initial_all += initial
            equation_all += equation
        tempCode = initial_all + '\n' + equation_all
        self.alter('calGCode1', tempCode[1:])
    def calFGenerate(self):
        initial_all = ''
        equation_all = ''
        self.variableHandledList = []
        for item in code.internalFFList:
            equation,initial = self.calFFunctionHandle(item)
            initial_all += initial
            equation_all += equation
        self.variableHandledList = []
        for item in code.stateFList:
            equation,initial = self.calFFunctionHandle(item)
            initial_all += initial
            equation_all += equation
        tempCode = initial_all +'\n'+ equation_all
        self.alter('calFCode1', tempCode[1:])
    def calGyGenerate(self):
        calGyCode1 = ''
        # 第一步，读取函数
        initial_all = ''
        equation_all = ''

        for equation in self.algebFList:
            # 右边为需要偏导的部分，在左边，分别在代数变量里轮询
            # 如果函数中有这个变量，就将等式左侧的数对等式右边求偏导
            # 自己偏自己都是-1
            equation=sub('_g', '', equation)
            expression = equation.split('+=')
            tempCode = ''
            initial = ''
            [variableList, functionList] = self.variableGet(expression[1])
            # 将化简式展开
            for item in variableList:
                if item in self.internalFVList:
                    tempCode = self.internalFFList[self.internalFVList.index(item)].split('=')
                    expression[1]=sub(item,'('+tempCode[1]+')',expression[1])

                if item  in self.internalGVList:
                    tempCode=self.internalGFList[self.internalGVList.index(item)].split('=')[1]
                    expression[1]=sub(item,'('+tempCode+')',expression[1])

            # 利用展开后的式子进一步求偏导
            tempCode=''
            [variableList, functionList] = self.variableGet(expression[1])
            for item in variableList:
                tempCode += item + '=Symbol(\"' + item + '\")\n'
            exec(tempCode)
            self.variableHandledList=[]

            for item in variableList:
                if item in self.algebVList or item  in self.stateVList:
                    equation=str(expand(diff(expression[1], item)))
                    equation,initial=self.calGyFunctionHandle(equation)
                    print(equation)
                    code=self.name+'.DenseAdd('+self.name+'.pDae.Gy,'+self.name+'.'+expression[0]+'[i],'\
                          +self.name+'.'+item+'[i],'+equation+')\n'
                    equation_all+=code
                    initial_all+=initial


        self.alter('calGyCode1',initial_all+equation_all)
        calGyCode2 = ''
        calGyCode3 = ''
        pass

    def calGyFunctionHandle(self,equation):
        initial = ''
        [variableList, functionList] = self.variableGet(equation)
        for variable in variableList:
            if variable =='pi':
                pattern = '(?<=[^.])' + variable + '(?=[^a-zA-Z0-9])'
                equation = sub(pattern, 'math.Pi', equation)
            # 替换常数项
            if variable in self.constCList:
                pattern = '(?<=[^.])' + variable + '(?=[^a-zA-Z0-9])'
                equation = sub(pattern,self.name + '.' + variable +'[i]',equation)
            if variable in self.variableHandledList:
                continue
            else:
                self.variableHandledList.append(variable)
                if variable in self.stateVList:
                    initial +='\t'+variable+':='+ self.name + '.pDae.X[' + self.name + '.' + variable + '[i]]'+'\n'
                elif variable in self.algebVList:
                    initial +='\t'+variable+':='+ self.name + '.pDae.Y[' + self.name + '.' + variable + '[i]]'+'\n'
        print(initial)
        return equation,initial
    def calGyGenerate(self):
        calGyCode1 = ''
        # 第一步，读取函数
        initial_all = ''
        equation_all = ''

        for equation in self.algebFList:
            # 右边为需要偏导的部分，在左边，分别在代数变量里轮询
            # 如果函数中有这个变量，就将等式左侧的数对等式右边求偏导
            # 自己偏自己都是-1
            equation=sub('_g', '', equation)
            expression = equation.split('+=')
            tempCode = ''
            initial = ''
            [variableList, functionList] = self.variableGet(expression[1])
            # 将化简式展开
            for item in variableList:
                if item in self.internalFVList:
                    tempCode = self.internalFFList[self.internalFVList.index(item)].split('=')
                    expression[1]=sub(item,'('+tempCode[1]+')',expression[1])

                if item  in self.internalGVList:
                    tempCode=self.internalGFList[self.internalGVList.index(item)].split('=')[1]
                    expression[1]=sub(item,'('+tempCode+')',expression[1])

            # 利用展开后的式子进一步求偏导
            tempCode=''
            [variableList, functionList] = self.variableGet(expression[1])
            for item in variableList:
                tempCode += item + '=Symbol(\"' + item + '\")\n'
            exec(tempCode)
            self.variableHandledList=[]

            for item in variableList:
                if item in self.algebVList or item  in self.stateVList:
                    equation=str(expand(diff(expression[1], item)))
                    equation,initial=self.calGyFunctionHandle(equation)
                    print(equation)
                    code=self.name+'.DenseAdd('+self.name+'.pDae.Gy,'+self.name+'.'+expression[0]+'[i],'\
                          +self.name+'.'+item+'[i],'+equation+')\n'
                    equation_all+=code
                    initial_all+=initial

    def functionHandle(self,function,expression,variableList):
        funcDict={'exp':self.expCal,'angle':self.angleCal,
                    'conj':self.conjCal,'re':self.reCal,'im':self.imCal,
                  'sin':self.sinCal,'cos':self.cosCal}
        # pattern = compile(r'(?<=Function\(\').*?(?=\'\))')
        # functionList = pattern.findall(code)
        tempCode = sub(function, '', expression)
        # 若存在复数，则用复数计算
        if 'I' in variableList:
            tempCode = self.complexCal(variableList, tempCode)
        return funcDict[function](tempCode)



if __name__ == '__main__':
    code=codeGenerate('syn6','Syn6','testData.xlsx')
    code.dataRead()
    # for item in code.initialFList:
    #     code.variableGet(item)
    code.structGenerate()
    code.initalGenerate()
    code.setX0Generate()
    code.calFGenerate()
    code.addGenerate()
    code.calGGenerate()
    code.calGyGenerate()
    # code.voltageCal()
    # 先处理内部变量


