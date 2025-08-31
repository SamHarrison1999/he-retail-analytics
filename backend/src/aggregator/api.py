from fastapi import FastAPI
app=FastAPI(title='HE API')
@app.get('/healthz')
def health(): return {'ok': True}
