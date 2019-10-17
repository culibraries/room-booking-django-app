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


class SierraTokenView(APIView):
    permission_classes = (IsAuthenticated, IsAdmin)
    http_method_names = ['post']
    api_url = 'https://libraries.colorado.edu/iii/sierra-api/v5/'

    def post(self, request):
        sierra_client_id = os.getenv('ROOM_BOOKING_SIERRA_API_KEY', None)
        sierra_client_secret = os.getenv(
            'ROOM_BOOKING_SIERRA_CLIENT_SECRET', None)
        preStr = sierra_client_secret + ':' + sierra_client_id
        encoded = base64.b64encode(str.encode(preStr))
        headers = {"Content-Type": "application/json",
                   "Authorization": "Basic {0}".format(encoded.decode("utf-8"))}

        url = 'https://libraries.colorado.edu/iii/sierra-api/v5/token'
        body = {
            'grant_type': 'client_credentials'
        }

        r = requests.post("{0}/token".format(api_url), body, headers=headers)
        return Response(r.json())
