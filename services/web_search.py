import os, requests
class WebSearch:
    def __init__(self): self.key=os.getenv('TAVILY_API_KEY')
    def search(self,q,max_results=5):
        if not self.key: return []
        r=requests.post('https://api.tavily.com/search',json={'api_key':self.key,'query':q,'search_depth':'advanced','max_results':max_results,'include_answer':False},timeout=45)
        r.raise_for_status(); d=r.json()
        return [{'title':x.get('title'),'url':x.get('url'),'snippet':x.get('content',''),'published_date':x.get('published_date')} for x in d.get('results',[])]
