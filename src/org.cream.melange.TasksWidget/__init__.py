import time
import os.path

from gi.repository import Gtk as gtk

from cream.melange import api

from taskmanager import TaskManager, Status

@api.register('org.cream.melange.TasksWidget')
class Tasks(api.API):

    def __init__(self):
        api.API.__init__(self)

        self.task_manager = TaskManager(
            os.path.join(self.context.get_user_path(), 'tasks.json')
        )

        builder = gtk.Builder()
        builder.add_from_file(
            os.path.join(self.context.working_directory, 'add-dialog.glade')
        )

        self.dialog = builder.get_object('dialog')
        self.dialog.connect('delete_event', self.dialog.hide)
        self.title = builder.get_object('title')
        self.description = builder.get_object('description').get_buffer()
        self.priority = builder.get_object('priority')
        self.deadline = builder.get_object('deadline')
        self.tags = builder.get_object('tags')
        self.calendar = builder.get_object('calendar')
        self.calendar_win = builder.get_object('calendar_win')
        self.calendar_win.connect('delete_event', lambda *args: self.calendar_win.hide())
        builder.get_object('calendar_btn').connect('clicked', self.show_calendar)

    @api.expose
    @api.in_main_thread
    def add_task(self):
        '''Add a task to the database. The data is provided by the dialog.'''
        self.reset_dialog()
        if self.dialog.run() == 1:
            data = self.get_data()
            self.task_manager.add_task(
                data['title'],
                data['description'],
                data['tags'],
                data['priority'],
                data['deadline']
            )
        self.dialog.hide()

    @api.expose
    @api.in_main_thread
    def edit_task(self, id):
        '''Edit a task with the given id.'''
        task = self.task_manager.get_task(int(id))
        self.set_dialog_entries(task)
        if self.dialog.run() == 1:
            data = self.get_data()
            self.task_manager.edit_task(
                int(id),
                data['title'],
                data['description'],
                data['tags'],
                data['priority'],
                data['deadline']
            )
        self.dialog.hide()

    @api.expose
    def set_task_status(self, id, status):
        '''Set the tasks status.'''
        self.task_manager.set_task_status(int(id), int(status))

    @api.expose
    def list_tasks(self):
        '''Get all tasks which are not marked as done.'''
        tasks = self.task_manager.list_tasks()

        return [t.to_json() for t in sorted(
            filter(lambda t: t.status != Status.DONE, tasks),
            key=lambda t: t.deadline
        )]

    def get_data(self):
        '''Retrieve the data from the dialog'''

        return {
            'title': self.title.get_text(),
            'description': self.description.get_text(
                self.description.get_start_iter(),
                self.description.get_end_iter(),
                False
            ),
            'tags': self.tags.get_text(),
            'priority': self.priority.get_active(),
            'deadline': int(time.mktime(time.strptime(
                self.deadline.get_text(),
                '%d.%m.%Y' ))
            )

        }

    def set_dialog_entries(self, task):
        '''When editing a task, set the entries to edit them'''

        self.title.set_text(task.title)
        self.description.set_text(task.description)
        self.priority.set_active(task.priority)
        timestamp = task.deadline
        today = time.localtime(timestamp)[:3]
        self.calendar.select_month(today[1] -1, today[0])
        self.calendar.select_day(today[2])
        self.deadline.set_text('{0}.{1}.{2}'.format(today[2], today[1], today[0]))

    def reset_dialog(self):
        '''When adding a task, clear the dialog'''

        self.title.set_text('')
        self.description.set_text('')
        self.priority.set_active(0)
        self.deadline.set_text('')
        today = time.localtime()
        self.calendar.select_month(today[1] -1, today[0])
        self.calendar.select_day(today[2])
        self.tags.set_text('')

    def show_calendar(self, widget, *args):
        '''Show the calendarwindow'''

        if self.calendar_win.run() == 1:
            date = self.calendar.get_date()
            self.deadline.set_text('{0}.{1}.{2}'.format(date[2], date[1] + 1, date[0]))
        self.calendar_win.hide()
