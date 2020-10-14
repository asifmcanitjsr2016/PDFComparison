from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
class Upload(APIView):
    def post(self, request, *args, **kwargs):
        filename = request.headers['filename']
        with open(settings.INPUT_FILE_PATH + filename, 'wb') as output:
            output.write(request.read())
        return Response("success")                        
