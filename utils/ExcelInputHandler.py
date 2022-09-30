import importlib
import json
import time

from utils.GetAllKeyValue import GetKeyValue


class ExcelInputHandler():
    @staticmethod
    def get_method_param(specparam):
        # 用于处理抽取Excel中pre.的方法名参数名和预期字段
        methodnameandparam = specparam.rsplit(".", maxsplit=1)[1]
        if "(" in specparam or ")" in specparam:
            mindex1 = methodnameandparam.index("(")
            mindex2 = methodnameandparam.index(")")
            mindex3 = methodnameandparam.index("[")
            mindex4 = methodnameandparam.index("]")
            meth = methodnameandparam[:mindex1]
            innerparam = methodnameandparam[mindex1 + 1:mindex2]
            param = methodnameandparam[mindex3 + 1:mindex4]
            return meth, param, innerparam
        else:
            mindex1 = methodnameandparam.index("[")
            mindex2 = methodnameandparam.index("]")
            meth = methodnameandparam[:mindex1]
            param = methodnameandparam[mindex1 + 1:mindex2]
            return meth, param

    @staticmethod
    def ExcelInputHandlerDao(localparams):
        # 用于调用pre指定的方法（无参数）
        methodinfolist = {}
        for key, value in localparams.items():
            if "pre." in str(value) and "(" not in str(value) and ")" not in str(value):
                methodinfolist.update({key: str(value)})
        if methodinfolist.get("methodinfolist"):
            methodinfolist.pop("methodinfolist")
        methodlist = []
        for key, value in methodinfolist.items():
            index = value.index("[")
            methodlist.append(value[:index])
        distinctmethod = list(set(methodlist))
        methodresponsedict = {}
        for i in distinctmethod:
            ret, cls_name, methodname = i.rsplit(".", maxsplit=2)  # rsplit()从最后边开始往前分割  #splitlines()通过换行符进行分割
            m = importlib.import_module(ret)  # 导入文件模块
            cls = getattr(m, cls_name)
            methodinvoke = getattr(cls(), methodname)
            response = methodinvoke()  # 创建类对象并执行对象函数，获取想要的结果
            methodresponse = response
            methodresponsedict.update({methodname: methodresponse})
        return methodresponsedict

    @staticmethod
    def get_function_result(targetdict, param):
        # 充方法调用结果dict-targetdict中获取方法返回的dictionary 支持被调用的方法没有参数
        func = ExcelInputHandler.get_method_param(param)[0]
        param = ExcelInputHandler.get_method_param(param)[1]
        level1 = targetdict.get(func)
        level2 = level1.get(param)
        return level2

    @staticmethod
    def ExcelInputHandlerDao_param(localparams):
        # 用于调用pre指定的方法（有参数）
        methodinfolist = {}
        for key, value in localparams.items():
            if "pre." in str(value) and "(" in str(value) and ")" in str(value):
                methodinfolist.update({key: str(value)})
        if methodinfolist.get("methodinfolist"):
            methodinfolist.pop("methodinfolist")
        methodlist = []
        for key, value in methodinfolist.items():
            index = value.index("(")
            indexend = value.index(")")
            paramvalue = value[index + 1: indexend]
            methodlist.append((value[:index], paramvalue))
        methodresponsedict = []
        for i in methodlist:
            ret, cls_name, methodname = i[0].rsplit(".", maxsplit=2)  # rsplit()从最后边开始往前分割  #splitlines()通过换行符进行分割
            m = importlib.import_module(ret)  # 导入文件模块
            cls = getattr(m, cls_name)
            methodinvoke = getattr(cls(), methodname)
            if "," not in i[1]:
                strsplit = i[1]
                response = methodinvoke(strsplit)
            else:
                strsplit = i[1].split(",")  # 逗号分割，返回列表
                response = methodinvoke(*strsplit)  # 创建类对象并执行对象函数，获取想要的结果
            methodresponse = response
            methodresponsedict.append((methodname, i[1], methodresponse))
        return methodresponsedict

    @staticmethod
    def get_function_global_with_param(targetlist, chooseparam):
        # 充方法调用结果dict-targetdict中获取方法返回的dictionary 支持被调用的方法有参数
        func = ExcelInputHandler.get_method_param(chooseparam)[0]
        requiresparam = ExcelInputHandler.get_method_param(chooseparam)[1]
        innerparam = ExcelInputHandler.get_method_param(chooseparam)[2]
        for i in targetlist:
            if i[0] == func and str(i[1]) == innerparam:
                return i[2][requiresparam]
        return None

    @staticmethod
    def handle_excel_pre_without_param(functionsr):
        # 用于调用pre指定的方法（无参数）
        starttime = time.time()
        if "pre." in functionsr and "(" not in functionsr and ")" not in functionsr and "<" not in functionsr and ">" not in functionsr:
            index = functionsr.index("[")
            index2 = functionsr.index("]")
            originalmethodname = functionsr[:index]
            expectkey = functionsr[index + 1:index2]
            ret, cls_name, methodname = originalmethodname.rsplit(".",
                                                                  maxsplit=2)  # rsplit()从最后边开始往前分割  #splitlines()通过换行符进行分割
            m = importlib.import_module(ret)  # 导入文件模块
            cls = getattr(m, cls_name)
            methodinvoke = getattr(cls(), methodname)
            response = methodinvoke()  # 创建类对象并执行对象函数，获取想要的结果
            endtime = time.time()
            if "," in expectkey:
                returndict = {}
                paramlist = expectkey.split(",")
                for i in paramlist:
                    returndict.update({i: response[i]})
                return {functionsr: returndict, "runtime": endtime - starttime}
            else:
                return {functionsr: response, "runtime": endtime - starttime}

    @staticmethod
    def handle_excel_pre_with_param(prestr, outerglobal):
        # 用于调用pre指定的方法（有参数）
        starttime = time.time()
        parambegin = prestr.index("<")
        paramend = prestr.index(">")
        expectstart = prestr.index("[")
        expectend = prestr.index("]")
        expectkey = prestr[expectstart + 1:expectend]
        paramvalue = prestr[parambegin + 1: paramend]
        method = prestr[:parambegin]
        ret, cls_name, methodname = method.rsplit(".", maxsplit=2)  # rsplit()从最后边开始往前分割  #splitlines()通过换行符进行分割
        m = importlib.import_module(ret)  # 导入文件模块
        cls = getattr(m, cls_name)
        methodinvoke = getattr(cls(), methodname)
        if "#" not in paramvalue:
            if "global_" in paramvalue:
                strsplit = outerglobal[paramvalue.split("global_")[1]]
            elif "{" in paramvalue and "}" in paramvalue:
                jsonobject = json.loads(paramvalue)
                gv = GetKeyValue(jsonobject, mode='j')
                innerwithparamlist, innerwithoutparamlist, after_json_object = gv.extract_func_name_from_str(jsonobject)
                for k, v in after_json_object.items():
                    if type(v) == str and "global_" in v:
                        if len(v.split("_")) == 2:
                            after_json_object[k] = outerglobal[v.split("_")[1]]
                        elif len(v.split("_")) == 3:
                            if v.split("_")[1].upper() == "STR":
                                after_json_object[k] = str(outerglobal[v.split("_")[2]])
                            elif v.split("_")[1].upper() == "INT":
                                after_json_object[k] = int(outerglobal[v.split("_")[2]])
                            elif v.split("_")[1].upper() == "FLOAT":
                                after_json_object[k] = float(outerglobal[v.split("_")[2]])
                strsplit = after_json_object
            else:
                strsplit = paramvalue
            response = methodinvoke(strsplit)
            endtime = time.time()
            return {prestr: response, "runtime": endtime - starttime}
        else:
            strsplit = paramvalue.split("#")  # 分好号分割，返回列表
            newstrsplit = []
            for i in strsplit:
                if "global_" in i:
                    strsplit = outerglobal[i.split("global_")[1]]
                    newstrsplit.append(strsplit)
                elif "{" in paramvalue and "}" in i:
                    jo = json.loads(i)
                    for k, v in jo.items():
                        if "pre." in str(v) and "<" in str(v) and ">" in str(v):
                            parambegin = v.index("[")
                            paramend = v.index("]")
                            expectkey = v[parambegin + 1:paramend]
                            res = ExcelInputHandler.handle_excel_pre_with_param(v, outerglobal)[v]
                            jo[k] = res[expectkey]
                        elif "pre." in str(v) and "<" not in str(v) and ">" not in str(v):
                            parambegin = v.index("[")
                            paramend = v.index("]")
                            expectkey = v[parambegin + 1:paramend]
                            res = ExcelInputHandler.handle_excel_pre_without_param(v)[v]
                            jo[k] = res[expectkey]
                    newstrsplit.append(jo)
                else:
                    strsplit = i
                    newstrsplit.append(strsplit)
            response = methodinvoke(*newstrsplit)  # 创建类对象并执行对象函数，获取想要的结果
            endtime = time.time()
            return {prestr: response, "runtime": endtime - starttime}

    @staticmethod
    def handle_normal_param(param):
        # 处理Excel中的输入
        try:
            if isinstance(param, str) and "," in param:
                type = param.split(",")[0]
                p = param.split(",", maxsplit=1)[1]
                if type == "I" or type == 'i' or type == "Int" or type == "int":
                    return int(p)
                if type == "F" or type == 'f' or type == "float" or type == "float":
                    return float(p)
                if type == "S" or type == 's' or type == "str" or type == "string":
                    return str(p)
                if type == "B" or type == 'b' or type == "Bool" or type == "bool" or type == "Bool" or type == "Boolean":
                    if p == "True" or p == "true" or p == "T" or p == "t":
                        return True
                    else:
                        return False
                if type == "A" or type == 'a' or type == "arrya" or type == "Array":
                    alist = p.strip("[").strip("]").split(",")
                    return alist
                if type == "D" or type == 'd' or type == "Dict" or type == "dict":
                    return json.loads(p)
            elif isinstance(param, str):
                return str(param)
            elif isinstance(param, float):
                return float(param)
            elif isinstance(param, int):
                return int(param)
            elif isinstance(param, bool):
                return bool(param)
            elif param == None:
                return ""
            else:
                "传入的参数类型不可识别！"
            return param
        except Exception as e:
            print(e)

    @staticmethod
    def ExcelInputHandlerDaoCombine(methoddict):
        # 用于调用pre指定的方法（无参数）
        newheader = ""
        methodinfolist = {}
        methodinfolistparam = {}
        for key, value in methoddict.items():
            if "pre." in str(value) and "(" not in str(value) and ")" not in str(value):
                methodinfolist.update({key: str(value)})
            elif "pre." in str(value) and "(" in str(value) and ")" in str(value):
                methodinfolistparam.update({key: str(value)})

        methodlist = []
        for key, value in methodinfolist.items():
            index = value.index("[")
            methodlist.append(value[:index])
        distinctmethod = list(set(methodlist))
        methodresponsedict = {}
        for i in distinctmethod:
            ret, cls_name, methodname = i.rsplit(".", maxsplit=2)  # rsplit()从最后边开始往前分割  #splitlines()通过换行符进行分割
            m = importlib.import_module(ret)  # 导入文件模块
            cls = getattr(m, cls_name)
            methodinvoke = getattr(cls(), methodname)
            response = methodinvoke()  # 创建类对象并执行对象函数，获取想要的结果
            methodresponse = response
            if "header" in methodresponse:
                newheader = methodresponse["header"]
            methodresponsedict.update({methodname: methodresponse})

        methodlistparam = []
        for key, value in methodinfolistparam.items():
            index2 = value.index("(")
            indexend2 = value.index(")")
            paramvalue2 = value[index2 + 1: indexend2]
            methodlistparam.append((value[:index2], paramvalue2))
        methodresponsedictparam = []
        for i in methodlistparam:
            ret, cls_name, methodname = i[0].rsplit(".", maxsplit=2)  # rsplit()从最后边开始往前分割  #splitlines()通过换行符进行分割
            m = importlib.import_module(ret)  # 导入文件模块
            cls = getattr(m, cls_name)
            methodinvoke = getattr(cls(), methodname)
            if "," not in i[1]:
                strsplit = i[1]
                response = methodinvoke(strsplit)
            else:
                strsplit = i[1].split(",")  # 逗号分割，返回列表
                response = methodinvoke(*strsplit)  # 创建类对象并执行对象函数，获取想要的结果
            methodresponse = response
            if "header" in methodresponse:
                newheader = methodresponse["header"]
            methodresponsedictparam.append((methodname, i[1], methodresponse))

        returndict = {}
        for key, value in methoddict.items():
            if "pre." in str(value) and "(" not in str(value) and ")" not in str(value):
                returndict.update({key: ExcelInputHandler.handle_normal_param(
                    ExcelInputHandler.get_function_result(methodresponsedict,
                                                          str(value)))})
            elif "pre." in str(value) and "(" in str(value) and ")" in str(value):
                returndict.update({key: ExcelInputHandler.handle_normal_param(
                    ExcelInputHandler.get_function_global_with_param(methodresponsedictparam,
                                                                     str(value)))})
        return returndict, newheader

    @staticmethod
    # 处理setup方法
    def handle_setup_param(localparams, param):
        if param is not None and ("setup." in param or "Setup." in param):
            method = param.split(".")[1]
            wparam = param.split(".")[2]
            for key, value in localparams.items():
                if str(key) == method:
                    jc = json.loads(json.dumps(eval(str(value))))
                    return jc.get(wparam)
        else:
            return param


if __name__ == "__main__":
    res = ExcelInputHandler.handle_excel_pre_without_param("pre.reflect_config_utils.ReflectConfig.get_two_uuid[UUID]")
    print(res)
