#!/usr/bin/env python
import sys
import os
import yaml
import json


class YamlReaderError(Exception):
    pass


#**********************************
def static_to_dynamic_inventory(inputdict, hosts={}, groups={}, position='top'):
  '''{
      "_meta": {
        "hostvars": {}
      },
      "all": {
        "children": [
          "ungrouped"
        ]
      },
      "ungrouped": {
        "children": [
        ]
      }
  }
  '''

  outputdict = {'_meta': {'hostvars': {} }}
  newhosts = {}
  newgroups = {}
  tmpdict = {}
  for k,v in inputdict.items():
    if k == 'groups' or k == 'children':
      for group in v:
        newgroup = { group: { 'vars': {} }}
        groups = data_merge(groups, newgroup)
    if isinstance(v, dict):
      if 'children' in v:
        newgroups = { k: { 'children': [], 'vars': {} } }
        for group in v['children']:
          newgroups[k]['children'].append(group)
        groups = data_merge(groups, newgroups)
      if 'groups' in v:
        newgroups = { k: { 'children': [], 'vars': {} } }
        for group in v['groups']:
          newgroups[k]['children'].append(group)
        groups = data_merge(groups, newgroups)
      if 'hosts' in v:
        newgroups = { k: { 'hosts': [] } }
        if isinstance(v['hosts'], list):
          msg = """
          Hosts should not be define as a list:
          Error appear on v['hosts']
          Do this:
              hosts:
                host1:
                host2:
          Instead of this:
              hosts:
                - host1
                - host2
          Exit on Error (1)
          """
          sys.stderr.write(msg)
          exit(1)
        for host in list(v['hosts']):
          if not v['hosts'][host]:
            if host in newhosts:
              pass
            else:
              newhosts[host] = {}
          elif 'vars' in v['hosts'][host]:
            if host in newhosts:
              newhosts[host].update(v['hosts'][host]['vars'])
            else:
              newhosts[host] = v['hosts'][host]['vars']
          else:
            for key,val in v['hosts'][host].items():
              if host in newhosts:
                newhosts[host].update({key: val})
              else:
                newhosts[host] = {key: val}
          newgroups[k]['hosts'].append(host)
          hosts.update(newhosts)
          groups.update(newgroups)
      if 'vars' in v:
        if not v['vars']:
          pass
        elif position == 'group':
          newgroups = { k: { 'vars': v['vars'] } }
          groups = data_merge(groups, newgroups)
      if k == 'groups' or k == 'children':
        newposition = 'group'
      elif k == 'hosts':
        newposition = 'host'
      else:
        newposition = 'data'
      valid_group_syntax = ['children', 'groups', 'hosts', 'vars', '', None]
      if position == 'group':
        for word in v:
          if not word in valid_group_syntax:
           # print("Syntax error in definition of group: {}".format(k), file=sys.stderr)
           # print("\"{}\" is not a valid syntax key in group".format(word), file=sys.stderr)
           # print("Exit on Error (1)", file=sys.stderr)
           # exit(1)
            pass
      tmpdict = static_to_dynamic_inventory(v, hosts, groups, newposition)
  outputdict['_meta']['hostvars'].update(hosts)
  outputdict.update(groups)
  outputdict.update(tmpdict)
  return outputdict

#**********************************
def data_merge(inst1, inst2):

  try:
    if (inst1 is None or isinstance(inst1, str)
      or isinstance(inst1, int)
      or isinstance(inst1, float)
      ):
      inst1 = inst2
    elif isinstance(inst1, list):
      if isinstance(inst2, list):
        inst1 = inst1 + inst2
      else:
        inst1.append(inst2)
    elif isinstance(inst1, dict):
      if isinstance(inst2, dict):
        inst1.update(inst2)
      else:
        raise YamlReaderError('Cannot merge non-dict "%s" into dict "%s"' % (inst2, inst1))
  except TypeError as e:
    raise YamlReaderError('TypeError "%s" when merging "%s" into "%s"' %
    (e, inst1, inst2))
  return inst1

#**********************************
def load_static_inventory(path, static):

  ##- load static
  #add filename to dir
  files = {}
  files['static'] = {}
  files['static']['dir'] = path + '/static'
  files['static']['files'] = []

  static_hosts = []
  #get all *.yml files
  for root, directory, filename in os.walk(path):
    for file in filename:
      if file.endswith(('.yml', '.yaml')):
        files['static']['files'].append(os.path.join(root, file))
        filecontent = None
        filecontent = yaml.load(
         open(os.path.join(root, file), "rb").read()
        )
        if type(filecontent) == dict:
#          print(root, file)
          filecontent = static_to_dynamic_inventory(filecontent)
#          print(filecontent)
          if 'hostvars' in filecontent['_meta']:
            for hostname in filecontent['_meta']['hostvars']:
              static_hosts.append(hostname)
          static.update(filecontent)
        else:
          pass
  static_hosts = sorted(set(static_hosts))
  return static, static_hosts

#**********************************
def main():
  static = {'_meta': {'hostvars': {}}}

  static, static_hosts = load_static_inventory('/home/jdongmo/work/devops/inventory/',static)
  static.update({'static': static_hosts})
  print(format(json.dumps(static, indent=2)))

if __name__ == '__main__':
  main()

