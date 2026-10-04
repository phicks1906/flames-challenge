from pathlib import Path
import base64, json, hashlib, subprocess

manifest=Path('.github/v1336.manifest.json')
raw=manifest.read_bytes()
if hashlib.sha256(raw).hexdigest()!='974b7615e3a4df5b7dbda72e7ead646f97a47d162a58a1689b45fc0ba769c280':
    raise SystemExit('manifest sha256 mismatch')
ops=json.loads(raw.decode('utf-8'))
p=Path('index.html')
data=p.read_bytes()
git_old=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
if git_old!='ffb16b853da27b2fbb5166b223516dbb997ed4b6':
    raise SystemExit('baseline git blob mismatch: '+git_old)
src=data.splitlines(keepends=True)
out=[]
cursor=1
for n,o in enumerate(ops,1):
    i1,i2=int(o['i1']),int(o['i2'])
    if i1<cursor:
        raise SystemExit(f'overlap at op {n}')
    out.extend(src[cursor-1:i1-1])
    old=base64.b64decode(o.get('old_b64',''))
    new=base64.b64decode(o.get('new_b64',''))
    if o['tag']!='insert':
        actual=b''.join(src[i1-1:i2])
        if actual!=old:
            raise SystemExit(f'baseline mismatch at op {n}')
        cursor=i2+1
    else:
        if i2!=i1-1 or old:
            raise SystemExit(f'invalid insert op {n}')
        cursor=i1
    out.append(new)
out.extend(src[cursor-1:])
newdata=b''.join(out)
if len(newdata)!=4442839:
    raise SystemExit(f'output byte length mismatch: {len(newdata)}')
if hashlib.sha256(newdata).hexdigest()!='cd51b3b76fb0c3a72391f6e3c3ac192fdfcc44a5a2530e40094a0e39f4b07c7f':
    raise SystemExit('output sha256 mismatch')
git_new=hashlib.sha1(b'blob '+str(len(newdata)).encode()+b'\0'+newdata).hexdigest()
if git_new!='ea5c1d04be39532bae23b796b3040f76db3e2206':
    raise SystemExit('output git blob mismatch: '+git_new)
p.write_bytes(newdata)
subprocess.run(['git','rm','-f','.github/v1336.manifest.json','.github/v1336_apply.py'],check=True)
print('v1336 exact manifest applied',git_new)
