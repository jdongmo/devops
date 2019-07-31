#!/usr/bin/env python3
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
  for k,v in inputdict.items():
    if k == 'groups' or k == 'children':
      for group in v:
        if group not in groups:
          groups.update({group: {}})
    if isinstance(v, dict):
      if 'children' in v:
        if not k in newgroups:
          newgroups = { k: { 'children': [] }}
        for group in v['children']:
          newgroups[k]['children'].append(group)
        groups.update(newgroups)
      if 'groups' in v:
        if not k in newgroups:
          newgroups = { k: { 'children': [] }}
        for group in v['groups']:
          newgroups[k]['children'].append(group)
        groups.update(newgroups)
      if 'hosts' in v:
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
          if k in groups:
            if 'hosts' in groups[k]:
              groups[k]['hosts'].append(host)
            else:
              groups[k]['hosts'] = [host]
          else:
            groups.update({k: {'hosts': [host]}})
          if v['hosts'][host] is None:
            if not host in newhosts:
              newhosts[host] = {}
          elif 'vars' in v['hosts'][host]:
              newhosts.update({host: v['hosts'][host]})
          else:
            for key,val in v['hosts'][host].items():
              if host in newhosts:
                newhosts[host].update({key: val})
              else:
                newhosts[host] = {key: val}
          hosts.update(newhosts)
      if 'vars' in v:
        if position == 'group':
          if k in newgroups:
            newgroups[k].update({'vars': v['vars']})
          else:
            newgroups[k] = {'vars': v['vars']}
          groups.update(newgroups)
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
            print("Syntax error in definition of group: {}".format(k))
            print("\"{}\" is not a valid syntax key in group".format(word))
            exit(1)
      outputdict.update(static_to_dynamic_inventory(v, hosts, groups, newposition))
  outputdict['_meta']['hostvars'].update(hosts)
  outputdict.update(groups)
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
          filecontent = static_to_dynamic_inventory(filecontent)
          if 'hostvars' in filecontent['_meta']:
            for hostname in filecontent['_meta']['hostvars']:
              static_hosts.append(hostname)
          static.update(filecontent)
  static_hosts = sorted(set(static_hosts))
  return static, static_hosts

#**********************************
def main():
  static = {'_meta': {'hostvars': {}}}

  static, static_hosts = load_static_inventory(os.path.dirname(__file__), static)
  print(format(json.dumps(static, indent=2)))
  #print(format(json.dumps(static_hosts, indent=2)))

if __name__ == '__main__':
  main()

