import configparser
import datetime
import json
import jwt
import os
import requests
from requests import Session

class InvalidData(Exception):
    """Raised if JWT data is not sufficient"""

class AuthError(Exception):
    """Raised for auth errors"""
    def __init__(self, error_description, error):
        self.error_description = error_description
        self.error = error
        super(AuthError, self).__init__()

    def __str__(self):
        return """
        --- Authentication failed --->
        Error description: {}
        Error: {}
        --- Authentication failed ---!
        """.format(self.error_description, self.error)

class JWTAuth(object):
    """Implementation of the JWT Service Account Flow

    Arguments:
        keyPath(str): Path to the private key for the service account
        -------------------------------------------------------------
        See how to create a key here:
        https://www.adobe.io/authentication/auth-methods.html#!AdobeDocs/adobeio-auth/master/AuthenticationOverview/ServiceAccountIntegration.md
        -------------------------------------------------------------
        endpoint(str, optional): JWT exchange endpoint, defaults to EXCHANGE_ENDPOINT

    Raises:
        FileNotFoundError: Private key path is not valid

    Attributes:
        jwtPayload(object): The JWT payload
        endpoint(str): JWT exchange endpoint
    """
    EXCHANGE_ENDPOINT = "https://ims-na1.adobelogin.com/ims/exchange/jwt"
    
    def __init__(self, keyPath, endpoint = EXCHANGE_ENDPOINT):
        self.jwtPayload = {}
        self.endpoint = endpoint
        try:
            with open(keyPath, "r") as fd:
                self.privateKey = fd.read()
        except FileNotFoundError:
            raise FileNotFoundError("Private Key File Path could not be resolved")

    def setIss(self, iss):
        self.jwtPayload["iss"] = iss
        return self

    def setSub(self, sub):
        self.jwtPayload["sub"] = sub
        return self
    
    def setMetascopes(self, *args):
        for arg in args:
            self.jwtPayload[arg] = True
        return self

    def setClientId(self, clientId):
        self.clientId = clientId
        return self

    def setClientSecret(self, clientSecret):
        self.clientSecret = clientSecret
        return self

    def setCompanyId(self, companyId):
        self.companyId = companyId
        return self

    @classmethod
    def fromConfig(cls, path = None):
        if not os.path.isfile(path):
            raise FileNotFoundError("Config could not be found")
        parser = configparser.ConfigParser()
        parser.read(path)
        jwt = cls(parser["adobeio.privatekey"]["Path"])
        jwt.setIss(parser["adobeio.credentials"]["OrganizationId"])
        jwt.setSub(parser["adobeio.credentials"]["TechnicalAccountId"])
        jwt.setClientId(parser["adobeio.credentials"]["ClientId"])
        jwt.setClientSecret(parser["adobeio.credentials"]["ClientSecret"])
        for scope in parser["adobeio.metascopes"]["Scopes"].split(","):
            jwt.setMetascopes(scope)  
        jwt.setCompanyId("dhlcom1")
        return jwt
    
    def authenticate(self, con):
        """Authenticates the request session with the JWT headers

        Attributes:
            con(requests.Session): A valid requests session object

        Raises:
            TypeError: Session object of wrong type
            InvalidData: jwtPayload is not valid

        """
        if not isinstance(con, Session):
            raise TypeError("con object must be a requests session object")
        if not all([True if arg in self.jwtPayload else False for arg in ["iss", "sub"]]):
            raise InvalidData("Missing payload data in jwt payload")
        self.jwtPayload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(seconds=60)
        self.jwtPayload["aud"] = "https://ims-na1.adobelogin.com/c/{}".format(self.clientId)
        jwttoken = jwt.encode(self.jwtPayload, self.privateKey, algorithm="RS256")
        
        accessTokenPayload = {
            "client_id": self.clientId,
            "client_secret": self.clientSecret,
            "jwt_token": jwttoken
        }

        result = requests.post(self.endpoint, data = accessTokenPayload)
        resultJSON = json.loads(result.text)
        if result.status_code != 200:
            raise AuthError(
                resultJSON["error_descripion"],
                resultJSON["error"]
            )
        
        con.headers.update({
            "x-api-key": self.clientId,
            "x-proxy-global-company-id": self.companyId,
            "Authorization": "Bearer {}".format(resultJSON["access_token"]),
            "Accept": "application/json",
            "Content-Type": "application/json"
        })