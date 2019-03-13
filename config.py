import toml

# some examples:
# https://www.programcreek.com/python/example/93872/toml.load
cfg = toml.load('cruise.toml')

print(cfg['global']['author'])

for key in cfg['cruise'].keys():
    print(cfg['cruise'][key])
    print(cfg['cruise'].get(key))

ctd = cfg['ctd']
s = ctd['split']
for key in s.keys():
    print("{}: {}".format(key, s[key]))
s = ctd['splitAll']
for key in s.keys():
    print("{}: {}".format(key, s[key]))
