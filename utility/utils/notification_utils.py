from userapp.models import Notifications


def makeNotificationFormat(created_by, notification_info, created_who):
    return f'<span class="fw-bold">{created_by}</span> {notification_info} <span class="fw-bold">{created_who}</span>'


def createNotifications(title, notification_info, created_by, created_who):
    created_by_generate = created_by.get_full_name() if created_by else "From Website"
    html_text_info = makeNotificationFormat(created_by_generate, notification_info, created_who)
    notification = Notifications.objects.create(title=title, info=html_text_info, created_by=created_by)
    notification.save()
    return notification


def getCurrentUser():
    import inspect
    for frame_record in inspect.stack():
        if frame_record[3] == 'get_response':
            request = frame_record[0].f_locals['request']
            return request.user
            break
    else:
        request = None


def update_dashboard_notification(name, value,created=False,client_user=None):
    from utility.models import DashboardNotification
    user = getCurrentUser()
    if user!=None:
        try:
            if user.is_anonymous:
                return None
        except:
            return None
    if created:
      print("on update dashboard notification")
      update_admin_notification = DashboardNotification.objects.filter(user__is_superuser=True).update(**{name: value})
      if client_user!=None:
        try:
          update_seen_dashboard_notification = DashboardNotification.objects.filter(user=client_user).update(**{name: value})
        except:
           create_user_obj = DashboardNotification.objects.create(user=client_user)
    else:
      update_seen_dashboard_notification = DashboardNotification.objects.filter(user=getCurrentUser()).update(**{name: value})



def ProductNotification(Product_name):
    user = getCurrentUser()
    title = f"Product Created ({Product_name})"
    notification_info = " added a new product,"
    createNotifications(title=title, notification_info=notification_info,
                        created_by=user, created_who=Product_name)


def CustomerNotifications_OnCreate(name):
    user = getCurrentUser()
    title = f"Customer Created ({name})"
    notification_info = " Created a new customer "
    createNotifications(title=title, notification_info=notification_info,
                        created_by=user, created_who=name)


def CustomerNotifications_OnUpdate(name):
    user = getCurrentUser()
    title = f"Customer Updated ({name})"
    notification_info = " Updated information for"
    createNotifications(title=title, notification_info=notification_info,
                        created_by=user, created_who=name)

def create_dashboard_notifications_for_superusers():
    from coreapp.models import  User
    from utility.models import DashboardNotification

    superusers = User.objects.filter(is_superuser=True)

    for user in superusers:
        # Check if a dashboard notification already exists for the user
        if not DashboardNotification.objects.filter(user=user).exists():
            dashboard_notification = DashboardNotification(
                user=user,
                # Set default values for review, invoice, contact_us, work_us, or any other fields you want
            )
            dashboard_notification.save()