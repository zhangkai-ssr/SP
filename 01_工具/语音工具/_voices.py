import pyttsx3
e = pyttsx3.init()
vs = e.getProperty('voices')
print('voice count:', len(vs))
for v in vs:
    print('-', v.name, '|', getattr(v, 'languages', None))
