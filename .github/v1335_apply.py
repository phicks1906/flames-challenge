from pathlib import Path
import base64, json, hashlib, subprocess

manifest=Path('.github/v1335.final.manifest.json')
raw=manifest.read_bytes()
if hashlib.sha256(raw).hexdigest()!='086b86a576e8f0ca195906dbe59c5e781bc58b6d87d51779b2bb1703468dce36':
    raise SystemExit('manifest sha256 mismatch')
ops=json.loads(raw.decode('utf-8'))
p=Path('index.html')
src=p.read_bytes().splitlines(keepends=True)
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
data=b''.join(out)
if len(data)!=4442583:
    raise SystemExit(f'output byte length mismatch: {len(data)}')
if hashlib.sha256(data).hexdigest()!='f35ae49930c0895e4c61cb8178f5ff74c86094184e7faec921aad8521ef1faf2':
    raise SystemExit('output sha256 mismatch')
git_blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
if git_blob!='ffb16b853da27b2fbb5166b223516dbb997ed4b6':
    raise SystemExit('output git blob mismatch: '+git_blob)
p.write_bytes(data)
subprocess.run(['git','rm','-f','.github/v1335.final.manifest.json','.github/v1335_apply.py'],check=True)
print('v1335 exact manifest applied',git_blob)
