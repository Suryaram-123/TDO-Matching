import json, os
from openai import OpenAI
STATUSES=['OPEN','FUTURE_OPENING','TEMPORARILY_CLOSED','PERMANENTLY_CLOSED','REPLACED','HISTORICAL','NOT_FOUND','UNCERTAIN']
SYSTEM='''You are a conservative business-location verification analyst. Use ONLY supplied evidence. Never invent facts, dates, URLs, reviews, or sources. A Google place existing does not automatically prove it operates today. Recent reviews/photos are supporting evidence, not absolute proof. Prefer recent, direct, official, or reputable local evidence. If evidence conflicts or is weak, use UNCERTAIN. Allowed statuses: OPEN, FUTURE_OPENING, TEMPORARILY_CLOSED, PERMANENTLY_CLOSED, REPLACED, HISTORICAL, NOT_FOUND, UNCERTAIN. Return JSON with status, confidence (HIGH/MEDIUM/LOW), explanation, opening_date, reopening_date, replacement_business, evidence_ids.'''

def rule_classify(place,evidence):
    if not place:
        return {'status':'UNCERTAIN' if evidence else 'NOT_FOUND','confidence':'LOW','explanation':'No matching Google Place was found; web evidence requires review.' if evidence else 'No matching Google Place or web evidence was found.','opening_date':None,'reopening_date':None,'replacement_business':None,'evidence_ids':[str(i) for i in range(len(evidence))]}
    s=place.get('businessStatus')
    mapping={'OPERATIONAL':'OPEN','CLOSED_TEMPORARILY':'TEMPORARILY_CLOSED','CLOSED_PERMANENTLY':'PERMANENTLY_CLOSED','FUTURE_OPENING':'FUTURE_OPENING'}
    if s in mapping:
        return {'status':mapping[s],'confidence':'HIGH' if s!='OPERATIONAL' else 'MEDIUM','explanation':f'Google Places reports the matched location as {s}.','opening_date':place.get('openingDate'),'reopening_date':None,'replacement_business':None,'evidence_ids':[str(i) for i in range(len(evidence))]}
    return {'status':'UNCERTAIN','confidence':'LOW','explanation':'Place status is insufficient for a confident classification.','opening_date':None,'reopening_date':None,'replacement_business':None,'evidence_ids':[str(i) for i in range(len(evidence))]}

def classify(inp,place,evidence):
    if not os.getenv('OPENAI_API_KEY'): return rule_classify(place,evidence)
    client=OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    r=client.responses.create(model=os.getenv('OPENAI_MODEL','gpt-5-mini'),instructions=SYSTEM,input=json.dumps({'input':inp,'google_place':place,'evidence':evidence},ensure_ascii=False))
    out=json.loads(r.output_text)
    if out.get('status') not in STATUSES: raise ValueError('Invalid model status')
    return out
