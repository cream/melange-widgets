import os
import json
import datetime

class Status(object):
    OPEN = 0
    DONE = 2


class Task(object):

    @staticmethod
    def from_json(obj):
        return Task(
            int(obj['id']),
            obj['title'],
            obj['description'],
            obj['tags'],
            obj['priority'],
            obj['deadline'],
            obj['status']
        )

    def __init__(self, id_, title, description, tags, priority, deadline, status=Status.OPEN):
        self.id = id_
        self.title = title
        self.description = description
        self.tags = tags
        self.priority = priority
        self.deadline = deadline
        self.status = status


    @property
    def timedelta(self):

        today = datetime.date.today()
        deadline = datetime.date.fromtimestamp(self.deadline)
        timedelta = abs((today - deadline).days)

        if today > deadline:
            if timedelta == 1:
                return'yesterday'
            else:
                return '{0} days ago'.format(str(timedelta))
        elif today < deadline and timedelta < 8:
            if timedelta == 1:
                return 'tomorrow'
            else:
                return '{0} days left'.format(str(timedelta))
        elif today == deadline:
            return 'today'
        else:
            return '{0}.{1}.{2}'.format(deadline.day, deadline.month, deadline.year)


    def to_json(self):

        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'tags': self.tags,
            'priority': self.priority,
            'deadline': self.deadline,
            'timedelta': self.timedelta,
            'status': self.status
        }


class TaskManager(object):

    def __init__(self, database_path):

        self.database_path = database_path

        self.database = {}
        if os.path.exists(database_path):
            with open(database_path) as fh:
                try:
                    for id, task in json.load(fh).iteritems():
                        self.database[int(id)] = Task.from_json(task)
                except ValueError:
                    pass

        self.next_id = 0
        for id_ in self.database.keys():
            if id_ >= self.next_id:
                self.next_id = id_ + 1

    def add_task(self, title, description, tags, priority, deadline):
        self.database[self.next_id] = Task(
            self.next_id,
            title,
            description,
            tags,
            priority,
            deadline,
        )

        self.next_id += 1
        self.save()

    def get_task(self, id):

        if id in self.database:
            return self.database[id]


    def edit_task(self, id, title, description, tags, priority, deadline):

        task = self.get_task(id)

        task.title = title
        task.description = description
        task.tags = tags
        task.priority = priority
        task.deadline = deadline

        self.save()

    def set_task_status(self, id, status):

        self.get_task(id).status = status
        self.save()


    def list_tasks(self):

        return self.database.values()

    def save(self):

        obj = {}
        for id, task in self.database.iteritems():
            obj[id] = task.to_json()

        with open(self.database_path, 'w') as fh:
            json.dump(obj, fh)
