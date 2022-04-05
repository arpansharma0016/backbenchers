from django.contrib import admin
from .models import Confirm, Password, Post, Me, Comment, Bookmark, Post_report, Comment_report

admin.site.register(Confirm)
admin.site.register(Password)
admin.site.register(Post)
admin.site.register(Me)
admin.site.register(Comment)
admin.site.register(Bookmark)
admin.site.register(Post_report)
admin.site.register(Comment_report)
