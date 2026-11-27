import json,sys,os,subprocess,time,numpy as np,soundfile as sf
from kokoro import KPipeline
J,N=int(sys.argv[1]),int(sys.argv[2])
clips=json.load(open('clips.json'));keys=sorted(clips)[J::N]
VOICES={"emma":{"A":"bf_emma","B":"bm_george","C":"bf_isabella"},
        "isabella":{"A":"bf_isabella","B":"bm_fable","C":"bf_emma"},
        "george":{"A":"bm_george","B":"bf_emma","C":"bm_fable"},
        "fable":{"A":"bm_fable","B":"bf_isabella","C":"bm_george"}}
pipe=KPipeline(lang_code='b',repo_id='hexgrad/Kokoro-82M')
SR=24000;sil=lambda s:np.zeros(int(SR*s),dtype=np.float32)
os.makedirs('out',exist_ok=True);t0=time.time()
for k in keys:
  lines=clips[k]
  for preset,mp in VOICES.items():
    parts=[sil(0.35)];prev=None
    for l in lines:
      if prev is not None:parts.append(sil(0.7 if l["s"]!=prev else 0.45))
      for gs,ps,audio in pipe(l["t"],voice=mp.get(l["s"],mp["A"]),speed=0.97,split_pattern=r'(?<=[.!?])\s+'):
        a=audio.numpy() if hasattr(audio,'numpy') else np.asarray(audio)
        parts.append(a.astype(np.float32));parts.append(sil(0.22))
      prev=l["s"]
    parts.append(sil(0.5));wav=np.concatenate(parts)
    sf.write('t.wav',wav,SR)
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i','t.wav','-ac','1','-ar','24000','-b:a','40k',f'out/{k}-{preset}.mp3'],check=True)
  print('done',k,round(time.time()-t0),'s',flush=True)
