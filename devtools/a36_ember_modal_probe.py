from pathlib import Path
s=Path('index.html').read_text('utf8').splitlines()
for a,b in [(51355,51460),(51460,51515),(44838,44866),(45595,45612)]:
 print('A36_EMBER_SOURCE_RANGE',a,b)
 for i in range(a-1,b):print(f'{i+1}: {s[i][:450]}')
