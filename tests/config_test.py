from genericore import Configurable

def test_loadConstructor():
  class cl(Configurable): pass
  conf = {'a' : 'b'}
  a = cl(conf)
  assert a.config['a'] == 'b'

def test_load_conf():
  a = Configurable({'a' : 'b'})
  assert a.config['a'] == 'b'

  a.load_conf({'a' : { 'x' : 'y'}})
  assert a.config['a']['x'] == 'y'

  a.load_conf({'b' : 'd'})
  assert a.config['a']['x'] == 'y'
  assert a.config['b'] == 'd'

def test_load_conf_file():
  a = Configurable({'a' : {'x' : 'y'}})
  a.load_conf_file('configurable.json')
  assert a.config['a']['x'] == 'z'
  assert a.config['b'] == 'd'
  
