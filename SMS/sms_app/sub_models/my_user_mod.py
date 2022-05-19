from django.contrib.auth.models import User
class MyUser(User):
    class Meta:
        proxy = True

    def __str__(self):
        return self.get_full_name()