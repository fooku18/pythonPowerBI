import json
import requests
import pandas as pd
from datetime import datetime, timedelta

class ReportError(Exception):
    """General Error returned from the Adobe Analytics Report API response"""
    def __init__(self, errorCode, errorDescription):
        self.errorCode = errorCode
        self.errorDescription = errorDescription
        super(ReportError, self).__init__()
    
    def __str__(self):
        return """
        ---Report failed--->
        Error Code: {}
        Error Description: {}
        ---Report failed---!
        """.format(self.errorCode, self.errorDescription)
    
class BodyEmptyError(Exception):
    """Raised if the ReportClient has no body set"""

class ProxyGlobalCompanyIdHeaderNotSetError(Exception):
    """Raised if x-proxy-global-company-id header not set in con session"""

class ReportClient(object):
    """
    This object serves as a client for the Adobe Analytics Report API

    Args:
        con (requests.session.Session): A valid requests session object for the request
        endpoint (str, optional): Adobe Analytics Report API endpoint, defaults to ENDPOINT_URL

    Raises:
        (ProxyGlobalCompanyIdHeaderNotSetError): x-proxy-global-company-id is not set in con session object

    """
    ENDPOINT_URL = "https://analytics.adobe.io/api/{}/reports"

    def __init__(self, con, endpoint = ENDPOINT_URL):
        self.con = con
        if not con.headers.get("x-proxy-global-company-id"):
            raise ProxyGlobalCompanyIdHeaderNotSetError()
        self.endpoint = endpoint.format(con.headers.get("x-proxy-global-company-id"))

    def setDateRange(self, start, end):
        """Sets the start and end date for the report
        
        Args:
            start (datetime.datetime): A python datetime object for the start of the reporting period
            end (datetime.datetime): A python datetime object for the end of the reporting period

        Raises:
            BodyEmptyError: No body set for the report

        Returns:
            (ReportClient): The current object
        """
        if not hasattr(self, "body"):
            raise BodyEmptyError()
        for entry in self.body["globalFilters"]:
            if entry["type"] == "dateRange":
                entry["dateRange"] = "{}/{}".format(start.isoformat(), end.isoformat())
        return self

    def fromJSON(self, jsonPath):
        """Loads a json text file from the path and updates the objects body

        Args:
            jsonPath(str): Path to the json text file

        Returns:
            (ReportClient): The current object

        """
        with open(jsonPath, "r", encoding="UTF-8") as fd:
            f = fd.read()
        self.body = json.loads(f)
        return self

    def execute(self):
        """Executes the Adobe Analytics Report request and returns the request as a 
        pandas DataFrame object

        Raises:
            ReportError: The Adobe Analytics Report returns a erroneous response

        Returns:
            (pandas.DataFrame): The response as a pandas DataFrame object
        """
        lastPage = False
        data = {
            "dimension": []
        }
        while not lastPage:
            res = self.con.post(self.endpoint, data = json.dumps(self.body))
            resJSON = json.loads(res.text)
            if res.status_code != 200:
                raise ReportError(
                    resJSON["errorCode"],
                    resJSON["errorDescription"]
                )
            data["dimension"] += [r["value"] for r in resJSON["rows"]]
            for i in range(len(resJSON["columns"]["columnIds"])):
                if not str(i) in data:
                    data[str(i)] = []
                data[str(i)] += [r["data"][i] for r in resJSON["rows"]]
            lastPage = resJSON["lastPage"]
            if not lastPage:
                if not "settings" in self.body:
                    self.body["settings"] = {}
                self.body["settings"]["page"] = resJSON["number"]+1
        df = pd.DataFrame(data)
        return df