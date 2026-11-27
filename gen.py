import json,urllib.request,urllib.error,time,sys
J,N=int(sys.argv[1]),int(sys.argv[2])
items=[x for i,x in enumerate(json.load(open('s4items.json'))) if i%N==J]
out={}
def ask(prompt):
  for attempt in range(8):
    body={"model":"openai","messages":[{"role":"user","content":prompt}],"temperature":0.4,"referrer":"mamunbracu.github.io","private":True}
    try:
      d=json.load(urllib.request.urlopen(urllib.request.Request("https://text.pollinations.ai/openai",data=json.dumps(body).encode(),headers={"content-type":"application/json"}),timeout=120))
      c=d["choices"][0]["message"].get("content") or ""
      return json.loads(c[c.find("{"):c.rfind("}")+1])
    except urllib.error.HTTPError as e:
      ra=int(e.headers.get("retry-after") or 45);print("http",e.code,"wait",ra,flush=True);time.sleep(ra+2)
    except Exception as e:
      print("err",e,flush=True);time.sleep(47)
  return None
for it in items:
  short=all(len(k.split())<9 for q,k in it["qs"])
  qpart=("\n\nThen rewrite each reference answer below as a complete, natural spoken sentence a Level 4+ candidate would say (keep every fact, add no new facts, 8 to 25 words each):\n"+"\n".join(f"{i+1}. Q: {q} | Reference: {k}" for i,(q,k) in enumerate(it["qs"]))) if short else ""
  fmt='{"summary":"...","answers":["...","..."]}' if short else '{"summary":"..."}'
  kind="passage" if it["kind"]=="reading" else "recording"
  p=f"""You are an expert ISLPR examiner in Australia. Write a model SPOKEN SUMMARY of the {kind} below, exactly as a strong ISLPR Level 4+ candidate (a pre-service secondary teacher) would say it to the examiner.
Rules: 75 to 100 words; start with a clear topic sentence ("This {kind} is about..." or similar); cover ALL these key points: {"; ".join(it["points"])}; use your own words and paraphrase (never copy 5 or more words in a row from the source); use linking words (firstly, in addition, however, as a result, overall); natural Australian English; no bullet points; no new facts.

{kind.upper()}:
{it["src"]}{qpart}

Reply with ONLY this JSON: {fmt}"""
  r=ask(p)
  if r and r.get("summary"):out[it["id"]]=r;print("ok",it["id"],len(r["summary"].split()),"words",flush=True)
  else:print("FAILED",it["id"],flush=True)
import base64
json.dump(out,open(f"out{J}.json","w"),ensure_ascii=False)
print("B64OUT",base64.b64encode(json.dumps(out).encode()).decode(),flush=True)
