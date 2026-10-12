import warnings, json; warnings.filterwarnings("ignore")
from googleapiclient.discovery import build
from sheets.auth import TOKEN_PATH, SCOPES
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
c = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
if not c.valid: c.refresh(Request())
SID="1j3f5RqiGabP1-lOhSJjK-sEwMbTaqlYeHP5ZjH4gwV8"
s=build("sheets","v4",credentials=c).spreadsheets(); docs=build("docs","v1",credentials=c).documents()
v=s.values().get(spreadsheetId=SID,range="'Auto Parts'!A1:Z13").execute()["values"]; h=v[0]
out=[]
for r in v[1:]:
    if not r: continue
    row=dict(zip(h,r+[""]*(len(h)-len(r))))
    did=row["Audit/Pitch Doc"].split("/d/")[1].split("/")[0]
    d=docs.get(documentId=did).execute()
    txt="".join(e.get("textRun",{}).get("content","") for el in d["body"]["content"] if "paragraph" in el for e in el["paragraph"]["elements"])
    head=txt.split("FULL AUDIT")[0]
    pitch=txt.split("PITCH DRAFT")[-1] if "PITCH DRAFT" in txt else "NO PITCH SECTION"
    out.append({"row":row,"doc_id":did,"head":head,"pitch":pitch})
json.dump(out,open("/tmp/leads_docs.json","w"),indent=1)
for o in out:
    r=o["row"]; print("#####",r["Company"],"|",r["Reached Out"],"| search:",r["Search Provider Detected"],"| products.json:",r["Products.json Count"],"| sitemaps:",r["Product Sitemap Files"],"| shopify:",r["Shopify Confirmed"],"| contact:",r["Contact Name"])
    print(o["pitch"][:1800]); print()
