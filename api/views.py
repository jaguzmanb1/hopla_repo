import cloudinary.uploader
import hashlib
from datetime import datetime
from collections import defaultdict
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions, mixins, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

from .models import Ticket, User, Image
from .serializer import TicketSerializer, UserSerializer, ImageSerializer


class TicketViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def post(self, request, format=None):
        try:
            user = request.user
            ticket = Ticket.objects.create(id_user=user)
            images_count = request.data.get('images_count')
            if images_count:
                ticket.images_count = images_count
                ticket.save()
            else:
                return Response({"error": "El campo images_count es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({"response": "Ticket creado exitosamente"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        state = self.request.query_params.get('completed')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        queryset = queryset.filter(id_user=user)

        if state:
            queryset = queryset.filter(completed=state == 'true')

        if start_date or end_date:
            filters = Q()
            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                filters &= Q(created_at__gte=start_date)
            if end_date:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                filters &= Q(created_at__lte=end_date)
            queryset = queryset.filter(filters)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        grouped_tickets = defaultdict(list)

        for ticket in queryset:
            grouped_tickets[ticket.id_user].append(ticket)

        serialized_data = {}
        for user, tickets in grouped_tickets.items():
            serializer = self.get_serializer(tickets, many=True)
            serialized_data[user.email] = serializer.data

        return Response(serialized_data)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        images = instance.image_set.all() 

        image_serializer = ImageSerializer(images, many=True)

        data = serializer.data
        data['images'] = image_serializer.data

        return Response(data)

class ImagesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, ticket_id=None):
        try:
            ticket = get_object_or_404(Ticket, pk=ticket_id)

            user = request.user
            if user.id != ticket.id_user.id:
                return Response({"error": "No tienes permiso para agregar imágenes a este ticket."}, status=status.HTTP_403_FORBIDDEN)

            if ticket.completed:
                return Response({"msg": "Ticket con todas las imagenes"}, status=status.HTTP_200_OK) 
            
            hash_filename = hashlib.sha1().hexdigest()[:10]
            path = f"tickets/{ticket_id}/{hash_filename}"

            img_model = Image.objects.create(id_ticket=ticket, url=path)
            img_model.save()

            img = request.FILES.get('image')
            cloudinary.uploader.upload(img, public_id=path)

            image_count = Image.objects.filter(id_ticket=ticket_id).count()
            if image_count >= ticket.images_count:
                ticket.completed = True
                ticket.save()
                return Response({"msg": "El ticket se ha marcado como completado"}, status=status.HTTP_200_OK)

            return Response({"msg": "Ok"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AuthView(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        try:
            user_data = request.data
            user = User.objects.get(email=user_data["email"])

            if not user.check_password(request.data['password']):
                return Response({"error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)
            
            token, created = Token.objects.get_or_create(user=user)

            return Response({"token": token.key}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)