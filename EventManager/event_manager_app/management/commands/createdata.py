import random
import time
import numpy

import faker.providers
from django.core.management.base import BaseCommand
from faker import Faker

from ...models import CategoriesModel, EventsModel, UsersModel, CommentsModel

N_CATEGORIES = 1000
N_EVENTS = 1000000
N_USERS = 1000000
BATCH_SIZE = 50000


class Provider(faker.providers.BaseProvider):
    def gen_image(self):
        n_images = 1000
        return 'img_' + str(random.randint(1, n_images)) + '.png'

    def gen_time(self):
        return int(time.time() + 100000000 - random.randint(1, 200000000))


class Command(BaseCommand):
    help = "Command Information"

    def gen_categories_table(self, n_lines):
        fake = Faker()
        fake.add_provider(Provider)
        L = []
        for i in range(n_lines):
            category_name = (fake.company() + " " + str(i + 1))[:64]
            L.append(CategoriesModel(category_name=category_name))
            if (i + 1) % BATCH_SIZE == 0:
                print("BATCH SIZE = ", (i + 1) / BATCH_SIZE)
                CategoriesModel.objects.bulk_create(L)
                L.clear()
        if len(L) != 0:
            CategoriesModel.objects.bulk_create(L)

    def gen_events_table(self, n_lines, n_categories):
        fake = Faker()
        fake.add_provider(Provider)
        L = []
        for i in range(n_lines):
            titles = (fake.job() + " " + str(i + 1))[:64]
            description = (fake.text(1024))
            location = (fake.address() + " " + str(i + 1))[:1024]
            date = fake.gen_time()
            image_url = fake.gen_image()
            category_id = random.randint(1, n_categories)
            # print(titles, "\n", description, "\n", location, "\n", date, "\n", image_url, "\n", category_id)
            L.append(EventsModel(title=titles, description=description,
                                 location=location, image_url=image_url,
                                 date=date,
                                 category_id=category_id))
            if (i + 1) % BATCH_SIZE == 0:
                print("BATCH SIZE = ", (i + 1) / BATCH_SIZE)
                EventsModel.objects.bulk_create(L)
                L.clear()
        if len(L) != 0:
            EventsModel.objects.bulk_create(L)

    def gen_users_table(self, n_lines):
        fake = Faker()
        fake.add_provider(Provider)
        L = []
        for i in range(n_lines):
            username = "admin" + str(i + 1)
            password = '$2b$04$aKktvZPVkH8PmrmOYJ488OSYUGim20Z9eFfCjwI1jekx2dk0Cnpf.'
            name = (fake.name() + " " + str(i + 1))[:64]
            avatar_url = fake.gen_image()
            is_admin = random.randint(0, 1)
            # print(username, "\n", password, "\n", name, "\n", avatar_url, "\n", is_admin)
            L.append(UsersModel(username=username, password=password, name=name, avatar_url=avatar_url,
                                is_admin=is_admin))
            if (i + 1) % BATCH_SIZE == 0:
                print("BATCH SIZE = ", (i + 1) / BATCH_SIZE)
                UsersModel.objects.bulk_create(L)
                L.clear()
        if len(L) != 0:
            UsersModel.objects.bulk_create(L)

    def gen_likes_table(self, n_lines, n_users, n_events):
        fake = Faker()
        fake.add_provider(Provider)
        L = []
        i = 0
        for event_id in range(1, n_events + 1):
            users_id = numpy.random.choice(n_users, min(int(n_lines / n_events), n_users), replace=False)
            for user_id in users_id:
                L.append(EventsModel.likes.through(eventsmodel_id=event_id, usersmodel_id=user_id + 1))
                i += 1
                if i == BATCH_SIZE:
                    print("BATCH SIZE = ", (i + 1) / BATCH_SIZE)
                    EventsModel.likes.through.objects.bulk_create(L)
                    L.clear()
                    i = 0
        if len(L) != 0:
            EventsModel.likes.through.objects.bulk_create(L)

    def gen_participants_table(self, n_lines, n_users, n_events):
        fake = Faker()
        fake.add_provider(Provider)
        L = []
        i = 0
        for event_id in range(1, n_events + 1):
            users_id = numpy.random.choice(n_users, min(int(n_lines / n_events), n_users), replace=False)
            for user_id in users_id:
                L.append(EventsModel.participants.through(eventsmodel_id=event_id, usersmodel_id=user_id + 1))
                i += 1
                if i == BATCH_SIZE:
                    print("BATCH SIZE = ", (i + 1) / BATCH_SIZE)
                    EventsModel.participants.through.objects.bulk_create(L)
                    L.clear()
                    i = 0
        if len(L) != 0:
            EventsModel.participants.through.objects.bulk_create(L)

    def gen_comments_table(self, n_lines, n_users, n_events):
        fake = Faker()
        fake.add_provider(Provider)
        L = []
        for i in range(n_lines):
            event_id = random.randint(1, n_events)
            user_id = random.randint(1, n_users)
            comment_content = fake.text(1024)
            L.append(CommentsModel(event_id=event_id, user_id=user_id,
                                   comment_content=comment_content, comment_time=int(time.time() * 1000000)))
            if (i + 1) % BATCH_SIZE == 0:
                print("BATCH SIZE = ", (i + 1) / BATCH_SIZE)
                CommentsModel.objects.bulk_create(L)
                L.clear()
        if len(L) != 0:
            CommentsModel.objects.bulk_create(L)

    def handle(self, *args, **options):
        print("HELLO CREATE-DATA")
        Faker.seed(0)
        print("GEN CATEGORIES")
        self.gen_categories_table(N_CATEGORIES)
        print("GEN EVENTS")
        self.gen_events_table(N_EVENTS, N_CATEGORIES)
        print("GEN USERS")
        self.gen_users_table(N_USERS)
        print("GEN LIKES")
        self.gen_likes_table(2 * N_EVENTS, N_USERS, int(N_EVENTS / 100))
        print("GEN COMMENTS")
        self.gen_participants_table(2 * N_EVENTS, N_USERS, int(N_EVENTS / 100))
        print("GEN COMMENTS")
        self.gen_comments_table(2 * N_EVENTS, N_USERS, int(N_EVENTS / 100))
