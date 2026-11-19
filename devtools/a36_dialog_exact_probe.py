from pathlib import Path
s=Path('index.html').read_text('utf8').splitlines()
for a,b in [(44865,44948),(44965,45085),(52076,52100)]:
 print('A36_DIALOG_SNIPPET',a,b)
 for i in range(a-1,b):print(str(i+1)+': '+s[i][:420])
