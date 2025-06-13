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


class PostView(models.Model):
    id = fields.IntField(primary_key=True)
    post_id = fields.UUIDField()
    user_id = fields.IntField()
    viewed_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "post_views"
        unique_together = (("post_id", "user_id"),)


class PostLike(models.Model):
    id = fields.IntField(primary_key=True)
    post_id = fields.UUIDField()
    user_id = fields.IntField()
    liked_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "post_likes"
        unique_together = (("post_id", "user_id"),)


class PostComment(models.Model):
    id = fields.IntField(primary_key=True)
    post_id = fields.UUIDField()
    user_id = fields.IntField()
    content = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "post_comments" 