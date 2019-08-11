from .serializers import ProfileSerializer
from .models import PhoneNumber
from django.utils import timezone
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
import pyotp
from twilio.rest import Client as TwilioClient
from decouple import config

account_sid = config('TWILIO_ACCOUNT_SID')
auth_token = config("TWILIO_AUTH_TOKEN")
twilio_phone = config("TWILIO_PHONE")
client = TwilioClient(account_sid, auth_token)



class PhoneViewset(viewsets.ModelViewSet):
    queryset = PhoneNumber.objects.all()
    serializer_class = PhoneSerializer
    permission_classes = (permissions.IsAuthenticated,)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_phone(request, format=None):
    code = int(request.data['sms_code'])
    if request.user.authenticate(code):
        phone = request.user.phone
        phone.verified=True
        phone.save()
        return Response(status=201)
    return Response(dict(detail='The provided code did not match or has expired'),status=200)
    

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def send_sms_code(request, format=None):
    
    #Time based otp
    time_otp = pyotp.TOTP(request.user.key, interval=60)
    time_otp = time_otp.now()
    user_phone_number = request.user.profile.phone_number #Must start with a plus '+'
    client.messages.create(
                     body="Your verification code is "+time_otp,
                     from_=twilio_phone,
                     to=user_phone_number
                 )
    return Response(status=200)
