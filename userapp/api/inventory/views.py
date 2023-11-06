from django.shortcuts import render
import traceback
from urllib import response
from django.shortcuts import render
from rest_framework import viewsets
from userapp.models import Notifications
from . import serializers
from coreapp.helper import *
from django.contrib.auth.models import Group, Permission
from userapp.models import GroupTime
from coreapp.models import Role, User
from rest_framework.authtoken.models import Token
import datetime
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..filters import UserFilterInventory
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins


class GroupView(views.APIView):
    permission_classes = (CustomDjangoModelPermissions, IsAuthenticated)

    def get_queryset(self):
        return Group.objects.all()

    @extend_schema(request=serializers.GroupSerializer, responses={201: serializers.GroupSerializer})
    def get(self, request, format=None):
        try:
            pk = request.GET.get("id")
            if (pk is None):
                queryset = Group.objects.all()
            else:
                queryset = Group.objects.filter(id=pk)
            data = []
            for group in queryset:
                group_time = GroupTime.objects.filter(
                    group_id=group.id).first()
                if group_time is not None:

                    permissions_data = []
                    current_data = {
                        'id': group.id,
                        'name': group.name,
                        'permissions': [],
                        'created_at': group_time.created_at,
                        'updated_at': group_time.updated_at,
                    }
                    for permissions in group.permissions.all():
                        permissions_data.append({
                            'id': permissions.id,
                            "name": permissions.name,
                            "content_type": permissions.content_type.name,
                            "codename": permissions.codename,
                        })
                        current_data["permissions"] = permissions_data
                    data.append(current_data)

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            data = {
                "msg": "Data Doesn't Exists",
                'error': str(e)
            }
            return Response(data, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(request=serializers.AddGroupWithPermissionSerializer, responses={201: serializers.AddGroupWithPermissionSerializer})
    def post(self, request, format=None):
        try:
            GROUPS = request.data
            print(GROUPS)

            for group_name in GROUPS:
                print("group_name", group_name)

                new_group = Group.objects.filter(name=group_name).first()

                if new_group is None:
                    new_group = Group.objects.create(name=group_name)
                    group_time = GroupTime.objects.create(
                        group_id=new_group.id)
                else:
                    data = {
                        "error": "Group with this same name already exists."
                    }
                    return Response(data, status=status.HTTP_404_NOT_FOUND)
                for app_model in GROUPS[group_name]:
                    for permission_name in GROUPS[group_name][app_model]:
                        name = f"Can {permission_name} {app_model.lower()}"
                        try:
                            model_add_perm = Permission.objects.get(name=name)
                        except Permission.DoesNotExist:
                            continue
                        new_group.permissions.add(model_add_perm)
            data = {
                "id": new_group.id,
                "group": new_group.name,
            }
            return Response(data, status=status.HTTP_201_CREATED)

        except Exception as e:
            traceback.print_exc()
            data = {
                "msg": "Something went wrong.",
                "error": str(e)
            }
            return Response(data, status=status.HTTP_404_NOT_FOUND)


class GroupUpdateView(views.APIView):
    @extend_schema(request=serializers.AddGroupWithPermissionSerializer, responses={201: serializers.AddGroupWithPermissionSerializer})
    def patch(self, request, pk, format=None):
        try:
            GROUPS = request.data
            for group_name in GROUPS:
                foundGroup = Group.objects.filter(id=pk).first()
                foundGroup.name = group_name
                foundGroup.permissions.clear()
                grouped_users = foundGroup.user_set.all()
                for userss in grouped_users:
                    userToken = Token.objects.filter(user_id=userss.id).first()
                    if userToken is not None:
                        userToken.delete()
                if foundGroup is not None:
                    for app_model in GROUPS[group_name]:
                        for permission_name in GROUPS[group_name][app_model]:
                            name = f"Can {permission_name} {app_model.lower()}"
                            try:
                                model_add_perm = Permission.objects.get(
                                    name=name)
                            except Permission.DoesNotExist:
                                continue

                            foundGroup.permissions.add(model_add_perm)
                foundGroup.save()
                return Response({"data": "updated"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            traceback.print_exc()
            data = {
                "msg": "Something went wrong.",
                "error": str(e)
            }
            return Response(data, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(request=serializers.AddGroupWithPermissionSerializer, responses={201: serializers.AddGroupWithPermissionSerializer})
    def delete(self, request, pk, format=None):
        try:
            foundGroup = Group.objects.filter(id=pk).first()

            if foundGroup is not None:
                foundGroup.permissions.clear()
                grouped_users = foundGroup.user_set.all()
                for userss in grouped_users:
                    userToken = Token.objects.filter(user_id=userss.id).first()
                    if userToken is not None:
                        userToken.delete()
                foundGroup.delete()
                return Response({"data": "deleted"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"data": "deleted", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Can view products
# can view Products -->wrong
class ModelView(views.APIView):
    permission_classes = (CustomDjangoModelPermissions, IsAuthenticated)

    def get_queryset(self):
        return Permission.objects.all()

    def get(self, request, format=None):
        try:
            from django.apps import apps
            app_models = [model.__name__ for model in apps.get_models()]
            return Response(app_models, status=status.HTTP_200_OK)

        except:
            traceback.print_exc()
            data = {
                "msg": "Data Doesn't Exists"
            }
            return Response(data, status=status.HTTP_404_NOT_FOUND)



class AddRoleView(views.APIView):

    permission_classes = (CustomDjangoModelPermissions, IsAuthenticated)

    def get_queryset(self):
        return Role.objects.all()

    @extend_schema(request=serializers.ViewRoleSerializer, responses={201: serializers.ViewRoleSerializer})
    def get(self, request):
        roles = Role.objects.all()
        serializer = serializers.ViewRoleSerializer(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=serializers.AddRoleSerializer, responses={201: serializers.AddRoleSerializer})
    def post(self, request,):
        try:
            roles_data = request.data
            if not Role.objects.filter(name=roles_data['name']).exists():
                role = Role.objects.create(name=roles_data['name'])

                for group in roles_data['roles']:
                    group_obj = Group.objects.get(id=group)
                    role.groups.add(group_obj)
                role.save()
                data = {
                    "id": role.id,
                    "role": role.name,
                    "created_at": role.created_at,
                    "updated_at": role.updated_at,

                }
                return Response(data, status=status.HTTP_201_CREATED)
            return Response({"msg": "Already exists a role with this same name."}, status=status.HTTP_400_BAD_REQUEST)
        except:
            traceback.print_exc()
            data = {
                "msg": "Something went wrong."
            }
            return Response(data, status=status.HTTP_404_NOT_FOUND)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filterset_class = UserFilterInventory
    lookup_field = 'slug'

    def perform_create(self, serializer):
        instance = serializer.save()
        user_role = serializer.validated_data.get('role')
        user_pass = serializer.validated_data.get('password')

        user = User.objects.get(id=instance.id)
        user.set_password(user_pass)
        user.save()
        if user_role is not None:
            role = Role.objects.get(id=user_role.id)
            for group in role.groups.all():
                my_group = Group.objects.get(name=group.name)
                my_group.user_set.add(user)

    def perform_update(self, serializer):
        instance = serializer.save()
        new_password = self.request.data.get("password")
        user_role = serializer.validated_data.get('role')
        user = User.objects.get(id=instance.id)
        if new_password:
            user.set_password(new_password)
            user.save()

        if user_role is not None:
            user.user_permissions.clear()
            user.groups.clear()
            role = Role.objects.get(id=user_role.id)
            for group in role.groups.all():
                my_group = Group.objects.get(name=group.name)
                my_group.user_set.add(user)
                my_group.save()

        user_token = Token.objects.filter(user_id=instance.id).first()
        if user_token:
            user_token.delete()


class DeleteRoleView(viewsets.ModelViewSet):
    permission_classes = (CustomDjangoModelPermissions, IsAuthenticated)
    queryset = Role.objects.all()
    serializer_class = serializers.ViewRoleSerializer
    http_method_names = ['delete']

    def destroy(self, request, *args, **kwargs):
        try:
            role = self.get_object()
            connectedUsers = User.objects.filter(role_id=role.id)
            for user in connectedUsers:
                userToken = Token.objects.filter(user_id=user.id).first()
                if userToken is not None:
                    userToken.delete()
            role.delete()
            return Response("Deleted", status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_200_OK)


# GROUPS = {
#     "Administration": {
#         # general permissions
#         "log entry": ["add", "delete", "change", "view"],
#         "group": ["add", "delete", "change", "view"],
#         "permission": ["add", "delete", "change", "view"],
#         "user": ["add", "delete", "change", "view"],
#         "content type": ["add", "delete", "change", "view"],
#         "session": ["add", "delete", "change", "view"],

#         # django app model specific permissions
#         "project": ["add", "delete", "change", "view"],
#         "order": ["add", "delete", "change", "view"],
#         "staff time sheet": ["add", "delete", "change", "view"],
#         "staff": ["add", "delete", "change", "view"],
#         "client": ["add", "delete", "change", "view"],
#     }, }

# class PermissionAddToGroupView(views.APIView):
#     permission_classes = [IsAuthenticated]


class NotificationsViewSet(viewsets.ModelViewSet):

    permission_classes = (IsAuthenticated,)
    queryset = Notifications.objects.all()
    serializer_class = serializers.NotificationSerializer
    http_method_names = ['get']

    def list(self, request, *args, **kwargs):
        from utility.utils import notification_utils
        notification_utils.update_dashboard_notification("notification", 0)
        return super().list(request, *args, **kwargs)
