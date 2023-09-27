from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import json
import os
import requests
import base64
from .permission import IsAdmin


class LibcalTokenView(APIView):
    permission_classes = (IsAuthenticated, IsAdmin)
    http_method_names = ['post']

    def post(self, request):
        libcal_client_id = os.getenv('LIBCAL_CLIENT_ID', None)
        libcal_client_secret = os.getenv('LIBCAL_CLIENT_SECRET', None)
        url = 'https://colorado.libcal.com/1.1/oauth/token'
        body = {
            'client_id': libcal_client_id,
            'client_secret': libcal_client_secret,
            'grant_type': 'client_credentials'
        }
        r = requests.post(url, body)
        return Response(r.json())

class FolioSearchView(APIView):
    """
      returns Response with following items:
         patronType: number 1|2
           where 1 = Student affiliation 
                 2 = Faculty or Staff affiliation
                 0 = Other affiliation
         email: string
         firstName: string
         lastName: string
    """
    permission_classes = (IsAuthenticated, IsAdmin)
    http_method_names = ['get']

    def get(self, request):
        # information to connect to Folio API
        folio_api_url = os.getenv('ROOM_BOOKING_FOLIO_API_URL', None)
        folio_tenant = os.getenv('ROOM_BOOKING_FOLIO_TENANT', None)
        folio_username = os.getenv('ROOM_BOOKING_FOLIO_USERNAME', None)
        folio_password = os.getenv('ROOM_BOOKING_FOLIO_PASSWORD', None)
        patron_groups_student = os.getenv(
            'ROOM_BOOKING_FOLIO_GROUPS_STUDENT', '').split(",") 
        patron_groups_faculty_staff = os.getenv(
            'ROOM_BOOKING_FOLIO_GROUPS_FACULTY_STAFF', '').split(",")

        # Default response
        responseInfo = {
            'patronType': 0,
            'firstName': '', 
            'lastName': '', 
            'email': '' 
        }

        # Check we have parameters
        if ('barcode' in request.GET):
            query = '((barcode="{0}") and (active=="true"))'.format(request.GET.get('barcode'))
        elif ('externalSystemId' in request.GET):
            query = '((externalSystemId="{0}") and (active=="true"))'.format(request.GET.get('externalSystemId'))
        else:
            return Response(responseInfo)

        # Set headers and post data to get the Folio token
        headers = {
            'x-okapi-tenant': folio_tenant,  
            'x-okapi-token': '' 
        }

        body = {
            'username': folio_username, 
            'password': folio_password
        }

        #r = requests.post("{0}/authn/login".format(folio_api_url), json=body, headers=headers)
        # Get Folio Token that will expire after set time
        r = requests.post("{0}/authn/login".format(folio_api_url),
                          data=json.dumps(body), headers=headers)

        if (r.status_code == 201):
            headers['x-okapi-token'] = r.json()['okapiToken']
            headers['Accept'] = 'application/json'

            queryItems = {
                'limit': 1,
                'query': query 
            }

            response = requests.get("{0}/users".format(folio_api_url),
                                    params=queryItems, headers=headers)

            # We got exactly one patron that matched
            if (response.status_code == 200 and 
                len(response.json()['users']) == 1):
                patron = response.json()['users'][0]

                # determine the patron type given the Folio Patron Groups 
                if (patron['patronGroup'] in patron_groups_student):
                    responseInfo['patronType'] = 1
                elif (patron['patronGroup'] in patron_groups_faculty_staff): 
                    responseInfo['patronType'] = 2
                else:
                    responseInfo['patronType'] = 0

                responseInfo['firstName'] = patron['personal']['firstName']
                responseInfo['lastName'] = patron['personal']['lastName']
                responseInfo['email'] = patron['personal']['email']

                return Response(responseInfo)
            # Unable to get patron info based on parameters
            else:
                return Response(responseInfo)
        # Unable to get Folio Token
        else:
            print("Unable to get Folio Token")
            print(r.text)
            return Response(responseInfo)

class SierraSearchView(APIView):
    permission_classes = (IsAuthenticated, IsAdmin)
    http_method_names = ['get']

    def get(self, request):
        api_url = 'https://libraries-old.colorado.edu/iii/sierra-api/v5'
        sierra_client_id = os.getenv('ROOM_BOOKING_SIERRA_API_KEY', None)
        sierra_client_secret = os.getenv(
            'ROOM_BOOKING_SIERRA_CLIENT_SECRET', None)
        preStr = "{0}:{1}".format(sierra_client_id, sierra_client_secret)
        preByte = preStr.encode("utf-8")
        encoded = base64.b64encode(preByte)
        headers = {"Content-Type": "application/json",
                   "Authorization": "Basic {0}".format(encoded.decode('utf-8'))}

        url = 'https://libraries-old.colorado.edu/iii/sierra-api/v5/token'
        body = {
            'grant_type': 'client_credentials'
        }

        r = requests.post("{0}/token".format(api_url), body, headers=headers)
        varFieldContent = request.GET.get('key')
        varFieldTag = request.GET.get('tag')
        newHeaders = {"Content-Type": "application/json",
                      "Authorization": "Bearer {0}".format(r.json()['access_token'])}
        req = requests.get("{0}/patrons/find?varFieldTag={1}&varFieldContent={2}&fields=patronType,varFields".format(
            api_url, varFieldTag, varFieldContent), headers=newHeaders)
        return Response(req.json())
