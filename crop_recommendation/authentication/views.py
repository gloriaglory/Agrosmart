from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, get_user_model
from .nida import nida_problem, verify_nida
from .serializers import UserSerializer, UserRegistrationSerializer, UserUpdateSerializer, IdNumberUpdateSerializer

User = get_user_model()

# Create your views here.
class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": token.key
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    API endpoint for user login.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "user": UserSerializer(user).data,
                "token": token.key
            })
        return Response({"error": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving user profile.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserUpdateView(generics.UpdateAPIView):
    """
    API endpoint for updating user profile.
    """
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Return updated user data with role
        return Response(UserSerializer(instance).data)


class UpdateIdNumberView(APIView):
    """
    API endpoint to update only the user's ID number.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = IdNumberUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "ID number updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyNidaView(APIView):
    """
    Ask NIDA to confirm the logged-in user's NIDA number.
    200: verified. 400: no number, invalid, or NIDA rejected it. 503: NIDA service not connected yet.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.nida_verified:
            return Response({"verified": True, "message": "Your NIDA number is already verified.",
                             "user": UserSerializer(user).data})
        if not user.id_number:
            return Response({"verified": False, "error": "Add your NIDA number to your profile first."},
                            status=status.HTTP_400_BAD_REQUEST)
        problem = nida_problem(user.id_number)
        if problem:
            return Response({"verified": False, "error": problem}, status=status.HTTP_400_BAD_REQUEST)
        if not (user.first_name and user.last_name):
            return Response({"verified": False,
                             "error": "Add your first and last name, exactly as on your ID, before verifying."},
                            status=status.HTTP_400_BAD_REQUEST)

        result = verify_nida(user.id_number, user.first_name, user.last_name)
        if result is True:
            user.nida_verified = True
            user.save(update_fields=["nida_verified"])
            return Response({"verified": True, "message": "Your NIDA number has been verified.",
                             "user": UserSerializer(user).data})
        if result is False:
            return Response({"verified": False,
                             "error": "NIDA could not confirm these details. Check that your name matches your ID."},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({"verified": False,
                         "error": "Automatic NIDA verification is not available yet. Your number passed our "
                                  "checks and will be reviewed by our team."},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE)


class UserSearchView(APIView):
    """
    Find accounts to @tag, e.g. GET ?q=as -> users whose username or name starts with "as".
    Only logged-in users can search, and only public details are returned.
    """
    permission_classes = [permissions.IsAuthenticated]
    LIMIT = 8

    def get(self, request):
        from django.db.models import Q

        q = (request.query_params.get("q") or "").strip().lstrip("@")
        if not q:
            return Response([])
        users = (
            User.objects.filter(is_active=True)
            .filter(Q(username__istartswith=q) | Q(first_name__istartswith=q) | Q(last_name__istartswith=q))
            .order_by("username")[: self.LIMIT]
        )
        return Response([
            {
                "username": u.username,
                "name": f"{u.first_name} {u.last_name}".strip() or u.username,
                "is_seller": u.is_seller,
                "nida_verified": u.nida_verified,
            }
            for u in users
        ])
