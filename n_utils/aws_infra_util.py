#!/usr/bin/env python

# Copyright 2016-2017 Nitor Creations Oy
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import collections
import json
import os
import re
import subprocess
import sys
import yaml


stacks = dict()
PARAM_REF_RE = re.compile(r'\(\(([^)]+)\)\)')
include_dirs = []
if "CF_TEMPLATE_INCLUDE" in os.environ:
    for next_dir in os.environ["CF_TEMPLATE_INCLUDE"].split(":"):
        if not next_dir.endswith("/"):
            next_dir = next_dir + "/"
        include_dirs.append(next_dir)

include_dirs.append(os.path.dirname(__file__) + "/includes/")
############################################################################
# _THE_ yaml & json deserialize/serialize functions
def yaml_load(stream):
    class OrderedLoader(yaml.SafeLoader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return collections.OrderedDict(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)

def yaml_save(data):
    class OrderedDumper(yaml.SafeDumper):
        pass
    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())
    OrderedDumper.add_representer(collections.OrderedDict, _dict_representer)
    return yaml.dump(data, None, OrderedDumper)

def json_load(stream):
    return json.loads(stream, object_pairs_hook=collections.OrderedDict)

def json_save(data):
    return json.dumps(data, indent=2)

def json_save_small(data):
    return json.dumps(data, indent=None)

############################################################################
# import_scripts
gotImportErrors = False

# the CF_ prefix is expected already to have been stripped
def decode_parameter_name(name):
    return re.sub('__', '::', name)

def import_script(filename):
    # the "var " prefix is to support javascript as well
    var_decl_re = re.compile(
        r'^(\s*var\s+)?CF_([^\s=]+)[\s="\']*([^#"\'\`]*)(?:["\'\s\`]*)(#optional)?')
    embed_decl_re = re.compile(
        r'^(.*?=\s*)?(.*?)(?:(?:\`?#|//)CF([^#\`]*))[\"\`\s]*(#optional)?')
    arr = []
    with open(filename) as f:
        for line in f:
            result = var_decl_re.match(line)
            if result:
                jsPrefix = result.group(1)
                encodedVarName = result.group(2)
                varName = decode_parameter_name(encodedVarName)
                ref = collections.OrderedDict()
                ref['Ref'] = varName
                ref['__source'] = filename
                if "#optional" == str(result.group(4)):
                    ref['__optional'] = "true"
                    ref['__default'] = str(result.group(3)).strip(" \"'")
                arr.append(line[0:result.end(2)] + "='")
                arr.append(ref)
                if jsPrefix:
                    arr.append("';\n")
                else:
                    arr.append("'\n")
            else:
                result = embed_decl_re.match(line)
                if result:
                    prefix = result.group(1)
                    if not prefix:
                        prefix = result.group(2)
                        defaultVal = ""
                    else:
                        defaultVal = str(result.group(2)).strip(" \"'")
                    arr.append(prefix + "'")
                    for entry in yaml_load("[" + result.group(3) + "]"):
                        apply_source(entry, filename, str(result.group(4)), defaultVal)
                        arr.append(entry)
                    arr.append("'\n")
                else:
                    arr.append(line)
    return arr

def find_include(basefile):
    if os.path.isfile(basefile):
        return basefile
    for search_dir in include_dirs:
        if os.path.isfile(search_dir + basefile):
            return search_dir + basefile
    return None

def resolve_file(filename, basefile):
    if filename[0] == "/":
        return filename
    if re.match(r"^(\.\./\.\./|\.\./|\./)?aws-utils/.*", filename):
        return find_include(re.sub(r"^(\.\./\.\./|\.\./|\./)?aws-utils/", "", filename))
    if re.match(r"^\(\(\s?includes\s?\)\)/.*", filename):
        return find_include(re.sub(r"^\(\(\s?includes\s?\)\)/", "", filename))
    base = os.path.dirname(basefile)
    if len(base) == 0:
        base = "."
    return base + "/" + filename

PARAM_NOT_AVAILABLE = "N/A"

def addParams(target, source, sourceProp, useValue):
    if sourceProp in source:
        for k, v in source[sourceProp].items():
            target[k] = v['Default'] if useValue else PARAM_NOT_AVAILABLE

def get_params(data, template):
    params = dict()

    # first load defaults for all parameters in "Parameters"
    addParams(params, data, 'Parameters', True)
    params['REGION'] = PARAM_NOT_AVAILABLE
    params['ACCOUNT_ID'] = PARAM_NOT_AVAILABLE
    params['STACK_NAME'] = PARAM_NOT_AVAILABLE

    # then override them with values from infra
    template_dir = os.path.dirname(os.path.abspath(template))
    image_dir = os.path.dirname(template_dir)

    imageName = os.path.basename(image_dir)
    stackName = os.path.basename(template_dir)
    stackName = re.sub('^stack-', '', stackName)

    get_vars_command = ['env', '-i', 'bash', '-c',
                        'source source_infra_properties.sh "' + \
                        imageName + '" "' + stackName + '" ; set']

    if 'GIT_BRANCH' in os.environ:
        get_vars_command.insert(2, 'GIT_BRANCH=' + os.environ['GIT_BRANCH'])
    if 'REGION' in os.environ:
        get_vars_command.insert(2, 'REGION=' + os.environ['REGION'])
    if 'ACCOUNT_ID' in os.environ:
        get_vars_command.insert(2, 'ACCOUNT_ID=' + os.environ['ACCOUNT_ID'])

    p = subprocess.Popen(get_vars_command, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, universal_newlines=True)
    output = p.communicate()
    if p.returncode:
        sys.exit("Failed to retrieve infra*.properties")

    for line in output[0].split('\n'):
        line = line.strip()
        if line:
            k, v = line.split('=', 1)
            if k in params:
                v = v.strip("'").strip('"')
                params[k] = v

    # source_infra_properties.sh always resolves a region, account id and stack
    # name
    params["AWS::Region"] = params['REGION']
    params["AWS::AccountId"] = params['ACCOUNT_ID']
    params["AWS::StackName"] = params['STACK_NAME']

    # finally load AWS-provided and "Resources"
    params["AWS::NotificationARNs"] = PARAM_NOT_AVAILABLE
    params["AWS::NoValue"] = PARAM_NOT_AVAILABLE
    params["AWS::StackId"] = PARAM_NOT_AVAILABLE
    addParams(params, data, 'Resources', False)

    return params

# replaces "((param))" references in `data` with values from `params` argument.
# Param references with no association in `params` are left as-is.
def apply_params(data, params):
    if isinstance(data, collections.OrderedDict):
        for k, v in data.items():
            k2 = apply_params(k, params)
            v2 = apply_params(v, params)
            if k != k2:
                del data[k]
            data[k2] = v2
    elif isinstance(data, list):
        for i in range(0, len(data)):
            data[i] = apply_params(data[i], params)
    elif isinstance(data, str):
        prevEnd = None
        res = ''
        for m in PARAM_REF_RE.finditer(data):
            k = m.group(1)
            if k in params:
                span = m.span()
                # support non-string values only when value contains nothing but
                # the reference
                if span[0] == 0 and span[1] == len(data):
                    return params[k]
                res += data[prevEnd:span[0]]
                res += params[k]
                prevEnd = span[1]
        data = res + data[prevEnd:]
    return data

# Applies recursively source to script inline expression
def apply_source(data, filename, optional, default):
    if isinstance(data, collections.OrderedDict):
        if 'Ref' in data:
            data['__source'] = filename
            if "#optional" == optional:
                data['__optional'] = "true"
                data['__default'] = default
        for k, v in data.items():
            apply_source(k, filename, optional, default)
            apply_source(v, filename, optional, default)

# returns new data
def import_scripts_pass1(data, basefile, path):
    global gotImportErrors
    if isinstance(data, collections.OrderedDict):
        if 'Fn::ImportFile' in data:
            v = data['Fn::ImportFile']
            script_import = resolve_file(v, basefile)
            if script_import:
                data.clear()
                contents = import_script(script_import)
                data['Fn::Join'] = ["", contents]
            else:
                print "ERROR: " + v + ": Can't import file \"" + v + \
                      "\" - file not found on include paths or relative to " + \
                      basefile
                gotImportErrors = True
        elif 'Fn::ImportYaml' in data:
            v = data['Fn::ImportYaml']
            del data['Fn::ImportYaml']
            yaml_file = resolve_file(v, basefile)
            if yaml_file:
                contents = yaml_load(open(yaml_file))
                contents = apply_params(contents, data)
                data.clear()
                if isinstance(contents, collections.OrderedDict):
                    for k, v in contents.items():
                        data[k] = import_scripts_pass1(v, yaml_file, path + k +\
                                                       "_")
                elif isinstance(contents, list):
                    data = contents
                    for i in range(0, len(data)):
                        data[i] = import_scripts_pass1(data[i], yaml_file,
                                                       path + str(i) + "_")
                else:
                    print "ERROR: " + path + ": Can't import yaml file \"" + \
                          yaml_file + "\" that isn't an associative array or" +\
                          " a list in file " + basefile
                    gotImportErrors = True
            else:
                print "ERROR: " + v + ": Can't import file \"" + v + \
                      "\" - file not found on include paths or relative to " + \
                      basefile
                gotImportErrors = True
        elif 'Fn::Merge' in data:
            mergeList = data['Fn::Merge']
            if not isinstance(mergeList, list):
                print "ERROR: " + path + ": Fn::Merge must associate to a list in file " + basefile
                gotImportErrors = True
                return data
            data = import_scripts_pass1(mergeList[0], basefile, path + "0_")
            for i in range(1, len(mergeList)):
                merge = import_scripts_pass1(mergeList[i], basefile, path + str(i) + "_")
                if isinstance(data, collections.OrderedDict):
                    if not isinstance(merge, collections.OrderedDict):
                        print "ERROR: " + path + ": First Fn::Merge entry " +\
                              "was an object, but entry " + str(i) + " was " + \
                              "not an object: " + str(merge) + " in file " +\
                              basefile
                        gotImportErrors = True
                    else:
                        for k, v in merge.items():
                            data[k] = v
                elif isinstance(data, list):
                    if not isinstance(merge, list):
                        print "ERROR: " + path + ": First Fn::Merge entry " +\
                              "was a list, but entry " + str(i) + " was not" +\
                              " a list: " + str(merge)
                        gotImportErrors = True
                    else:
                        for k in range(0, len(merge)):
                            data.append(merge[k])
                else:
                    print "ERROR: " + path + ": Unsupported " + str(type(data))
                    gotImportErrors = True
                    break
        elif 'Ref' in data:
            data['__source'] = basefile
        else:
            for k, v in data.items():
                data[k] = import_scripts_pass1(v, basefile, path + k + "_")
    elif isinstance(data, list):
        for i in range(0, len(data)):
            data[i] = import_scripts_pass1(data[i], basefile, path + str(i) + "_")
    return data

# returns new data
def import_scripts_pass2(data, templateFile, path, templateParams, resolveRefs):
    global gotImportErrors
    if isinstance(data, collections.OrderedDict):
        if 'Ref' in data:
            varName = data['Ref']
            if '__source' in data:
                filename = data['__source']
                del data['__source']
            else:
                filename = "unknown"
            if not varName in templateParams:
                if '__optional' in data:
                    data = data['__default']
                else:
                    print "ERROR: " + path + ": Referenced parameter \"" + \
                          varName + "\" in file " + filename + \
                          " not declared in template parameters in " + \
                          templateFile
                    gotImportErrors = True
            else:
                if resolveRefs:
                    data = templateParams[varName]
                    if data == PARAM_NOT_AVAILABLE:
                        print "ERROR: " + path + ": Referenced parameter \"" +\
                              varName + "\" in file " + filename +\
                              " is resolved later by AWS; cannot resolve its" +\
                              " value now"
                        gotImportErrors = True
            if '__optional' in data:
                del data['__optional']
            if '__default' in data:
                del data['__default']
        elif 'StackRef' in data:
            stack_var = import_scripts_pass2(data['StackRef'], templateFile,
                                             path + "StackRef_", templateParams,
                                             True)
            data.clear()
            region = stack_var['region']
            stack_name = stack_var['stackName']
            stack_param = stack_var['paramName']
            stack_key = region + "." + stack_name
            if stack_key in stacks:
                stack_params = stacks[stack_key]
            else:
                describe_stack_command = ['show-stack-params-and-outputs.sh',
                                          region, stack_name]
                try:
                    p = subprocess.Popen(describe_stack_command,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         universal_newlines=True)
                    output = p.communicate()
                    if p.returncode:
                        sys.exit("Describe stack failed: " + output[1])
                    stack_params = json_load(output[0])
                    stacks[stack_key] = stack_params
                except OSError as e:
                    sys.exit("Describe stack failed: " + e.strerror +\
                             "\nIs show-stack-params-and-outputs.sh " +\
                             "available on your $PATH?")
            if not stack_param in stack_params:
                sys.exit("Did not find value for: " + stack_param +\
                         " in stack " + stack_name)
            data = stack_params[stack_param]
        else:
            for k, v in data.items():
                data[k] = import_scripts_pass2(v, templateFile, path + k +\
                                               "_", templateParams, resolveRefs)
    elif isinstance(data, list):
        for i in range(0, len(data)):
            data[i] = import_scripts_pass2(data[i], templateFile, path + \
                                           str(i) + "_", templateParams,
                                           resolveRefs)
    return data

def import_scripts(data, basefile):
    global gotImportErrors
    gotImportErrors = False

    data = import_scripts_pass1(data, basefile, "")
    data = import_scripts_pass2(data, basefile, "", get_params(data, basefile),
                                False)
    if gotImportErrors:
        sys.exit(1)
    return data

############################################################################
# extract_scripts
def bash_encode_parameter_name(name):
    return "CF_" + re.sub('::', '__', name)

def encode_script_filename(prefix, path):
    if path.find("UserData_Fn::Base64") != -1:
        return prefix + "-userdata.sh"
    CFG_PREFIX = "AWS::CloudFormation::Init_config_files_"
    idx = path.find(CFG_PREFIX)
    if idx != -1:
        soff = idx + len(CFG_PREFIX)
        eoff = path.find("_content_", soff)
        cfgPath = path[soff:eoff]
        return prefix + "-" + cfgPath[cfgPath.rfind("/") + 1:]
    return prefix + "-" + path

def extract_script(prefix, path, joinArgs):
    # print prefix, path
    # "before" and "after" code blocks, placed before and after var declarations
    code = ["", ""]
    varDecls = collections.OrderedDict()
    codeIdx = 0
    for s in joinArgs:
        if type(s) is collections.OrderedDict:
            if not 'Ref' in s:
                print "Dict with no ref"
                json_save(s)
            else:
                varName = s['Ref']
                if not len(varName) > 0:
                    raise Exception("Failed to convert reference inside " +\
                                    "script: " + str(s))
                bashVarName = bash_encode_parameter_name(varName)
                varDecl = ""
                #varDecl += "#" + varName + "\n"
                varDecl += bashVarName + "=\"\";\n"
                varDecls[varName] = varDecl
                code[codeIdx] += "${" + bashVarName + "}"
        else:
            code[codeIdx] += s
        codeIdx = 1 # switch to "after" block

    filename = encode_script_filename(prefix, path)
    sys.stderr.write(prefix + ": Exported path '" + path + \
                     "' contents to file '" + filename + "'\n")
    with open(filename, "w") as script_file: #opens file with name of "test.txt"
        script_file.write(code[0])
        script_file.write("\n")
        for varName, varDecl in varDecls.items():
            script_file.write(varDecl)
        script_file.write("\n")
        script_file.write(code[1])
    return filename

# data argument is mutated
def extract_scripts(data, prefix, path=""):
    if not isinstance(data, collections.OrderedDict):
        return
    for k, v in data.items():
        extract_scripts(v, prefix, path + k + "_")
        if k == "Fn::Join":
            if not v[0] == "":
                continue
            if isinstance(v[1][0], basestring) and (v[1][0].find("#!") != 0):
                continue
            script_file = extract_script(prefix, path, v[1])
            del data[k]
            data['Fn::ImportFile'] = script_file

############################################################################
# simple apis
def yaml_to_dict(yaml_file_to_convert):
    data = yaml_load(open(yaml_file_to_convert))
    data = import_scripts(data, yaml_file_to_convert)
    patch_launchconf_userdata_with_metadata_hash_and_params(data)
    return data

def yaml_to_json(yaml_file_to_convert):
    data = yaml_to_dict(yaml_file_to_convert)
    return json_save(data)

def json_to_yaml(json_file_to_convert):
    data = json_load(open(json_file_to_convert).read())
    extract_scripts(data, json_file_to_convert)
    return yaml_save(data)


############################################################################
# misc json
def locate_launchconf_metadata(data):
    if "Resources" in data:
        resources = data["Resources"]
        for val in resources.values():
            if val["Type"] == "AWS::AutoScaling::LaunchConfiguration" and \
                "Metadata" in val:
                return val["Metadata"]
    return None

def locate_launchconf_userdata(data):
    resources = data["Resources"]
    for val in resources.values():
        if val["Type"] == "AWS::AutoScaling::LaunchConfiguration":
            return val["Properties"]["UserData"]["Fn::Base64"]["Fn::Join"][1]
    return None

def get_refs(data, reflist=None):
    if not reflist:
        reflist = []
    if isinstance(data, collections.OrderedDict):
        if "Ref" in data:
            reflist.append(data["Ref"])
        for val in data.values():
            get_refs(val, reflist)
    elif isinstance(data, list):
        for e in data:
            get_refs(e, reflist)
    return reflist

def patch_launchconf_userdata_with_metadata_hash_and_params(data):
    lc_meta = locate_launchconf_metadata(data)
    if lc_meta is not None:
        lc_userdata = locate_launchconf_userdata(data)
        lc_userdata.append("\nexit 0\n# metadata hash: " + str(hash(json_save(lc_meta))) + "\n")
        lc_meta_refs = set(get_refs(lc_meta))
        if len(lc_meta_refs) > 0:
            first = 1
            for e in lc_meta_refs:
                lc_userdata.append("# metadata params: " if first else ", ")
                lc_userdata.append({"Ref" : e})
                first = 0
            lc_userdata.append("\n")
