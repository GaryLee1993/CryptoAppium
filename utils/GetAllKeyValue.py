import json

# 级联获取字典中指定的key
innerwithparamlist = []
innerwithoutparamlist = []


class GetKeyValue(object):
    def __init__(self, o, mode='j'):
        self.json_object = None
        if mode == 'j':
            self.json_object = o
        elif mode == 's':
            self.json_object = json.loads(o)
        else:
            raise Exception('Unexpected mode argument.Choose "j" or "s".')
        self.result_list = []

    def search_key(self, key):
        self.result_list = []
        self.__search(self.json_object, key)
        return self.result_list

    def __search(self, json_object, key):
        for k in json_object:
            if k == key:
                self.result_list.append(json_object[k])
            if isinstance(json_object[k], dict):
                self.__search(json_object[k], key)
            if isinstance(json_object[k], list):
                for item in json_object[k]:
                    if isinstance(item, dict):
                        self.__search(item, key)

    def json_get_actual_value_from_result_dict(self, new_json_object, resultdict, globaldict={}):
        for k, v in new_json_object.items():
            if type(v) == str and "pre." in v and "<" in v and ">" in v:
                indexbegin = v.index("[")
                indexend = v.index("]")
                expectkey = v[indexbegin + 1:indexend]
                new_json_object[k] = resultdict[v][expectkey]
                globaldict.update({k:resultdict[v][expectkey]})
            elif type(v) == str and "pre." in v and "<" not in v and ">" not in v:
                indexbegin = v.index("[")
                indexend = v.index("]")
                expectkey = v[indexbegin + 1:indexend]
                new_json_object[k] = resultdict[v][expectkey]
                globaldict.update({k: resultdict[v][expectkey]})
            elif type(v) == str and "global_" in v:
                if len(v.split("_")) == 2 and v.split("_")[1] in globaldict.keys():
                    new_json_object[k] = globaldict[v.split("_")[1]]
                    globaldict.update({k: globaldict[v.split("_")[1]]})
                elif len(v.split("_")) == 3 and v.split("_")[2] in globaldict.keys():
                    if v.split("_")[1].upper() == "STR":
                        new_json_object[k] = str(globaldict[v.split("_")[2]])
                        globaldict.update({k: str(globaldict[v.split("_")[2]])})
                    elif v.split("_")[1].upper() == "INT":
                        new_json_object[k] = int(globaldict[v.split("_")[2]])
                        globaldict.update({k: int(globaldict[v.split("_")[2]])})
                    elif v.split("_")[1].upper() == "FLOAT":
                        new_json_object[k] = float(globaldict[v.split("_")[2]])
                        globaldict.update({k: float(globaldict[v.split("_")[2]])})
            elif isinstance(v, dict):
                self.json_get_actual_value_from_result_dict(v, resultdict, globaldict)
            elif isinstance(v, list):
                for item in new_json_object[k]:
                    if isinstance(item, dict):
                        self.json_get_actual_value_from_result_dict(item, resultdict)
                    if isinstance(item, str) and "pre." in item and "<" in item and ">" in item:
                        indexbegin = item.index("[")
                        indexend = item.index("]")
                        expectkey = item[indexbegin + 1:indexend]
                        itemindex = new_json_object[k].index(item)
                        new_json_object[k][itemindex] = resultdict[item][expectkey]
                    elif isinstance(item, str) and "pre." in item and "<" not in item and ">" not in item:
                        indexbegin = item.index("[")
                        indexend = item.index("]")
                        expectkey = item[indexbegin + 1:indexend]
                        itemindex = new_json_object[k].index(item)
                        new_json_object[k][itemindex] = resultdict[item][expectkey]

    def extract_func_name_from_str(self, json_object, globaldict={}):
        for k, v in json_object.items():
            if type(v) == str and "pre." in v and "<" in v and ">" in v:
                innerwithparamlist.append(v)
            elif type(v) == str and "pre." in v and "<" not in v and ">" not in v:
                innerwithoutparamlist.append(v)
            elif type(v) == str and "global." in v:
                if len(v.split(".")) == 2:
                    json_object[k] = globaldict[v.split(".")[1]]
                elif len(v.split(".")) == 3:
                    if v.split(".")[1].upper() == "STR":
                        json_object[k] = str(globaldict[v.split(".")[2]])
                    elif v.split(".")[1].upper() == "INT":
                        json_object[k] = int(globaldict[v.split(".")[2]])
                    elif v.split(".")[1].upper() == "FLOAT":
                        json_object[k] = float(globaldict[v.split(".")[2]])
            elif isinstance(v, dict):
                self.extract_func_name_from_str(v, globaldict)
            elif isinstance(v, list):
                finallist = []
                for item in json_object[k]:
                    if type(item) == str and "pre." in item and "<" in item and ">" in item:
                        innerwithparamlist.append(item)
                        finallist.append(item)
                    elif type(item) == str and "pre." in item and "<" not in item and ">" not in item:
                        innerwithoutparamlist.append(item)
                        finallist.append(item)
                    elif type(item) == str and "global." in item:
                        if len(item.split(".")) == 2:
                            finallist.append(globaldict[item.split(".")[1]])
                        elif len(item.split(".")) == 3:
                            if item.split(".")[1].upper() == "STR":
                                finallist.append(str(globaldict[item.split(".")[2]]))
                            elif item.split(".")[1].upper() == "INT":
                                finallist.append(int(globaldict[item.split(".")[2]]))
                            elif item.split(".")[1].upper() == "FLOAT":
                                finallist.append(float(globaldict[item.split(".")[2]]))
                    elif isinstance(item, dict) and (
                            True not in [str(i).startswith("pre.") for i in item.values()]) and (
                            True not in [str(i).startswith("global.") for i in item.values()]):
                        finallist.append(item)
                    elif isinstance(item, dict) and (True in [str(i).startswith("pre.") for i in item.values()] or
                                                     True in [str(i).startswith("global.") for i in item.values()]):
                        innerwithparamlistinner, innerwithoutparamlistinner, json_objectinner = self.extract_func_name_from_str(
                            item, globaldict)
                        finallist.append(json_objectinner)
                    else:
                        finallist.append(item)
                json_object[k] = finallist
        return innerwithparamlist, innerwithoutparamlist, json_object