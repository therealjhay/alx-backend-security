from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login
from ratelimit.decorators import ratelimit
from drf_yasg.utils import swagger_auto_schema
from .serializers import LoginSerializer

@swagger_auto_schema(
    method='post',
    request_body=LoginSerializer,
    operation_description="Login with rate limiting protection"
)
@api_view(['POST']) # <--- Crucial: Makes it visible to Swagger
@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def login_view(request):
    # In DRF, we use request.data instead of request.POST
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        assert serializer.validated_data is not None
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)