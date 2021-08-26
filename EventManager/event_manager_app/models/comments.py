from django.db import models


class CommentsModel(models.Model):
    comment_content = models.CharField(max_length=1024, null=False, blank=False)
    comment_time = models.BigIntegerField(null=False, blank=True, db_index=True)
    user = models.ForeignKey('UsersModel', on_delete=models.CASCADE)
    event = models.ForeignKey('EventsModel', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user) + " " + str(self.event) + " " + str(self.comment_time)

    def serialize(self):
        return {'comment_id': self.id, 'comment_content': self.comment_content,
                'comment_time': self.comment_time / 1000000}

    class Meta:
        db_table = "comments_tb"
        unique_together = ('user', 'event', 'comment_time')
