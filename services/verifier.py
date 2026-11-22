from datetime import datetime, timezone
from .google_places import GooglePlaces
from .web_search import WebSearch
from .classifier import classify
class StoreVerifier:
    def __init__(self): self.places=GooglePlaces(); self.web=WebSearch()
    def verify(self,data):
        query=', '.join(str(data.get(k,'')) for k in ['store_name','address','city','state','postal_code','country'] if data.get(k,''))
        places=self.places.search(query); place=self._best(places,data)
        # Search both normal/current evidence and the special edge cases the user requested.
        qs=[
          f'"{data["store_name"]}" "{data["address"]}" {data["city"]}',
          f'"{data["store_name"]}" "{data["address"]}" opening',
          f'"{data["store_name"]}" "{data["address"]}" closed',
          f'"{data["store_name"]}" "{data["address"]}" reopening',
          f'"{data["store_name"]}" "{data["address"]}" replacement',
          f'"{data["store_name"]}" "{data["city"]}" "coming soon"',
          f'"{data["address"]}" "{data["city"]}" "new business"',
          f'"{data["store_name"]}" "{data["city"]}" "permanently closed"',
          f'"{data["store_name"]}" "{data["city"]}" "temporarily closed"']
        evidence=[]; seen=set()
        for q in qs:
            for item in self.web.search(q):
                if item.get('url') and item['url'] not in seen:
                    seen.add(item['url']); item['query']=q; evidence.append(item)
        cp=self._compact(place); result=classify(data,cp,evidence)
        return {'checked_at':datetime.now(timezone.utc).isoformat(),'input':data,'google_place':cp,'evidence':evidence,'final_status':result['status'],'confidence':result['confidence'],'explanation':result['explanation'],'opening_date':result.get('opening_date'),'reopening_date':result.get('reopening_date'),'replacement_business':result.get('replacement_business'),'evidence_ids':result.get('evidence_ids',[])}
    def _best(self,places,data):
        if not places:return None
        target=' '.join(str(data.get(k,'')) for k in ['store_name','address','city']).lower()
        def score(p):
            text=(p.get('displayName',{}).get('text','')+' '+p.get('formattedAddress','')).lower()
            return sum(1 for t in target.split() if len(t)>2 and t in text)
        return max(places,key=score)
    def _compact(self,p):
        if not p:return None
        return {k:p.get(k) for k in ['id','formattedAddress','businessStatus','openingDate','googleMapsUri','websiteUri','rating','userRatingCount','reviews','photos']} | {'name':p.get('displayName',{}).get('text')}
