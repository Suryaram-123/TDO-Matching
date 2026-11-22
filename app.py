import os, json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from db import init_db, save_report, history
from services.verifier import StoreVerifier
load_dotenv(); init_db()
st.set_page_config(page_title='Store Verification AI',layout='wide')
st.title('Store Verification AI')
st.caption('Evidence-first verification of current, future, closed, replaced and historical store locations.')
with st.sidebar:
    st.header('Services')
    st.write('Google Places:', '✅' if os.getenv('GOOGLE_MAPS_API_KEY') else '❌')
    st.write('Web search:', '✅' if os.getenv('TAVILY_API_KEY') else '⚠️ optional')
    st.write('AI classifier:', '✅' if os.getenv('OPENAI_API_KEY') else '⚠️ rules fallback')

def show(r):
    a,b,c=st.columns(3); a.metric('Status',r['final_status']); b.metric('Confidence',r['confidence']); c.metric('Sources',len(r.get('evidence',[])))
    st.subheader('Explanation'); st.write(r['explanation'])
    if r.get('opening_date'): st.write('**Opening date:**',r['opening_date'])
    if r.get('reopening_date'): st.write('**Reopening date:**',r['reopening_date'])
    if r.get('replacement_business'): st.write('**Replacement:**',r['replacement_business'])
    if r.get('google_place'):
        st.subheader('Google Places match'); st.json(r['google_place'])
    st.subheader('Verified evidence / source links')
    for i,e in enumerate(r.get('evidence',[]),1):
        with st.expander(f"{i}. {e.get('title') or e.get('url')}"):
            st.write('**Published:**',e.get('published_date') or 'Unknown')
            st.write('**URL:**',e.get('url'))
            st.write(e.get('snippet',''))
            if e.get('url'): st.markdown(f"[Open verified source]({e['url']})")
    with st.expander('Raw report'): st.json(r)

t1,t2,t3=st.tabs(['Single store','Batch CSV','History'])
with t1:
    with st.form('verify'):
        name=st.text_input('Store name'); address=st.text_input('Street address'); city=st.text_input('City'); state=st.text_input('State'); zipc=st.text_input('ZIP'); country=st.text_input('Country','US'); go=st.form_submit_button('Verify store',type='primary')
    if go:
        if not all([name,address,city]): st.error('Store name, address and city are required.')
        elif not os.getenv('GOOGLE_MAPS_API_KEY'): st.error('Add GOOGLE_MAPS_API_KEY to .env.')
        else:
            with st.spinner('Searching Google Places and the web...'):
                r=StoreVerifier().verify({'store_name':name,'address':address,'city':city,'state':state,'postal_code':zipc,'country':country})
            save_report(r); show(r)
with t2:
    up=st.file_uploader('CSV: store_name,address,city,state,postal_code,country',type='csv')
    if up:
        df=pd.read_csv(up); st.dataframe(df.head(20),use_container_width=True)
        if st.button('Verify batch',type='primary'):
            if not os.getenv('GOOGLE_MAPS_API_KEY'): st.error('Add GOOGLE_MAPS_API_KEY to .env.')
            else:
                out=[]; bar=st.progress(0)
                for i,row in df.iterrows():
                    d={k:str(row.get(k,'') or '') for k in ['store_name','address','city','state','postal_code','country']}
                    try:
                        r=StoreVerifier().verify(d); save_report(r); out.append({'store_name':d['store_name'],'address':d['address'],'status':r['final_status'],'confidence':r['confidence'],'explanation':r['explanation'],'source_count':len(r['evidence'])})
                    except Exception as e: out.append({'store_name':d['store_name'],'address':d['address'],'status':'ERROR','confidence':'LOW','explanation':str(e),'source_count':0})
                    bar.progress((i+1)/len(df))
                result=pd.DataFrame(out); st.dataframe(result,use_container_width=True); st.download_button('Download results CSV',result.to_csv(index=False).encode(),'store_verification_results.csv','text/csv')
with t3:
    rows=history(); st.dataframe(pd.DataFrame(rows),use_container_width=True) if rows else st.info('No verification history yet.')
