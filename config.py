import toml

# some examples:
# https://www.programcreek.com/python/example/93872/toml.load
cfg = toml.load('tests/test.toml')

print(cfg['global']['author'])

d = cfg['global']
print(d, end='\n')
print(end='\n')

d = cfg['cruise']
print(d, end='\n')
print(end='\n')

d = cfg['ctd']
print(d, end='\n')
print(end='\n')

d = cfg['ctd']['header']
print(d, end='\n')
for key in d.keys():
    print("{}: {}".format(key, d[key]))
print(end='\n')

for key in cfg['cruise'].keys():
    print(cfg['cruise'][key])
    # print(cfg['cruise'].get(key))
print(end='\n')

d = cfg['split']['ctd']
print(d, end='\n')
for key in d.keys():
    print("{}: {}".format(key, d[key]))
print(end='\n')

d = cfg['split']['ctdAll']
print(d, end='\n')
for key in d.keys():
    print("{}: {}".format(key, d[key]))
print(end='\n')

d = cfg['split']['btl']
print(d, end='\n')
for key in d.keys():
    print("{}: {}".format(key, d[key]))
print(end='\n')
