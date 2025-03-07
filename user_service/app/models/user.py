from tortoise import fields, models

class User(models.Model):
    id = fields.IntField(primary_key=True)
    login = fields.CharField(50, unique=True)
    email = fields.CharField(255, unique=True)
    first_name = fields.CharField(50, null=True)
    last_name = fields.CharField(50, null=True)
    date_of_birth = fields.DateField(null=True)
    phone = fields.CharField(20, null=True)
    password_hash = fields.CharField(128)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True) 

    class Meta:
        table = "users"
