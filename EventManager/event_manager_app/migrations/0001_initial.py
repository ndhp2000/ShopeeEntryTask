# Generated by Django 2.2.15 on 2021-08-26 05:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CategoriesModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.CharField(max_length=64)),
            ],
            options={
                'db_table': 'categories_tb',
            },
        ),
        migrations.CreateModel(
            name='UsersModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(db_index=True, max_length=64, unique=True)),
                ('password', models.CharField(max_length=512)),
                ('name', models.CharField(max_length=64)),
                ('avatar_url', models.CharField(blank=True, max_length=512)),
                ('is_admin', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'users_tb',
            },
        ),
        migrations.CreateModel(
            name='SessionsModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_token', models.CharField(max_length=255, unique=True)),
                ('refresh_token', models.CharField(max_length=255, unique=True)),
                ('expired_time', models.BigIntegerField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='event_manager_app.UsersModel')),
            ],
            options={
                'db_table': 'sessions_tb',
            },
        ),
        migrations.CreateModel(
            name='EventsModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64)),
                ('description', models.CharField(blank=True, max_length=1024)),
                ('location', models.CharField(blank=True, max_length=1024)),
                ('date', models.BigIntegerField(blank=True, db_index=True)),
                ('image_url', models.CharField(blank=True, max_length=512)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='event_manager_app.CategoriesModel')),
                ('likes', models.ManyToManyField(related_name='like_relation', to='event_manager_app.UsersModel')),
                ('participants', models.ManyToManyField(related_name='participate_relation', to='event_manager_app.UsersModel')),
            ],
            options={
                'db_table': 'events_tb',
            },
        ),
        migrations.CreateModel(
            name='CommentsModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment_content', models.CharField(max_length=1024)),
                ('comment_time', models.BigIntegerField(blank=True, db_index=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='event_manager_app.EventsModel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='event_manager_app.UsersModel')),
            ],
            options={
                'db_table': 'comments_tb',
                'unique_together': {('user', 'event', 'comment_time')},
            },
        ),
    ]