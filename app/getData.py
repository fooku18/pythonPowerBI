import requests
import os
from auth.client import JWTAuth
from report.client import ReportClient
from datetime import datetime, timedelta

# path to the adobe analytics service account private key
jwt = JWTAuth("C:/users/jschlons/keys/adobe_io_private.key")
jwt.setIss("9D88879D5579828F7F000101@AdobeOrg")
jwt.setSub("473A0AFF5C498D430A495E7C@techacct.adobe.com")
jwt.setClientId("45ec3245e84d4d40978fd8da5eeefc3d")
# client secret is sensitive, better store it as an evnironment variable 
jwt.setClientSecret(os.environ.get("ADOBE_CLIENT_SECRET"))
jwt.setMetascopes("https://ims-na1.adobelogin.com/s/ent_analytics_bulk_ingest_sdk")
jwt.setCompanyId("dhlcom1")

# setup connection and authenticate
con = requests.Session()
jwt.authenticate(con)

# report client configuration
client = ReportClient(con, "dhlcom1")

# select report from adobe analytics internal json request format
# the respective json can be retrieved as described here:
# https://helpx.adobe.com/analytics/kt/using/build-api2-requests-analysis-workspace-feature-video-use.html
client.fromJSON("C:/pythonprojects/powerbi/testjson.json")

# set date range here
# use python datetime syntax for setting the start and end date
# refer to: https://docs.python.org/3.7/library/datetime.html
client.setDateRange(datetime.now() - timedelta(days=5), datetime.now())

# execute and retrieve pandas dataframe
df = client.execute()
print(df)