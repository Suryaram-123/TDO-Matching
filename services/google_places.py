import os, requests
BASE='https://places.googleapis.com/v1'
class GooglePlaces:
    def __init__(self):
        self.key=os.getenv('GOOGLE_MAPS_API_KEY')
        if not self.key: raise RuntimeError('GOOGLE_MAPS_API_KEY is missing')
    def search(self, query):
        headers={'Content-Type':'application/json','X-Goog-Api-Key':self.key,'X-Goog-FieldMask':','.join([
          'places.id','places.displayName','places.formattedAddress','places.businessStatus',
          'places.openingDate','places.googleMapsUri','places.websiteUri','places.location',
          'places.rating','places.userRatingCount','places.reviews','places.photos'])}
        payload={'textQuery':query,'includeFutureOpeningBusinesses':True,'pageSize':10}
        r=requests.post(f'{BASE}/places:searchText',headers=headers,json=payload,timeout=30); r.raise_for_status()
        return r.json().get('places',[])
