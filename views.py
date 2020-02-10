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


class SierraSearchView(APIView):
    permission_classes = (IsAuthenticated, IsAdmin)
    http_method_names = ['get']

    def get(self, request):
        api_url = 'https://libraries.colorado.edu/iii/sierra-api/v5'
        sierra_client_id = os.getenv('ROOM_BOOKING_SIERRA_API_KEY', None)
        sierra_client_secret = os.getenv(
            'ROOM_BOOKING_SIERRA_CLIENT_SECRET', None)
        preStr = "{0}:{1}".format(sierra_client_id, sierra_client_secret)
        preByte = preStr.encode("utf-8")
        encoded = base64.b64encode(preByte)
        headers = {"Content-Type": "application/json",
                   "Authorization": "Basic {0}".format(encoded.decode('utf-8'))}

        url = 'https://libraries.colorado.edu/iii/sierra-api/v5/token'
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
