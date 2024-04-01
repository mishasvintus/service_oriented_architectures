from tortoise import fields, models
import uuid

class Post(models.Model):
    id = fields.UUIDField(primary_key=True, default=uuid.uuid4)
    title = fields.CharField(max_length=255)
    description = fields.TextField()
    author_id = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    is_private = fields.BooleanField(default=False)
    tags = fields.JSONField(null=True) 

    class Meta:
        table = "posts"

    def __str__(self):
        return self.title 