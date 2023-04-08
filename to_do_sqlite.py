from flet import *
import sqlite3
import datetime


# DB 관리 클래스
class DB:

    con = None

    @staticmethod
    def connectToDatabase():
        try:
            DB.con = sqlite3.connect('todo.db',check_same_thread=False)
            c = DB.con.cursor()
            c.execute('CREATE TABLE IF NOT EXISTS tasks '
                      '(id INTEGER PRIMARY KEY AUTOINCREMENT,'
                      'task TEXT NOT NULL,'
                      'completed NUMERIC NOT NULL,'
                      'reg_date TEXT NOT NULL)')
        except Exception as e:
            print(e)

    def readDatabase(self):
        c = DB.con.cursor()
        c.execute('SELECT id, task, completed, reg_date FROM tasks')
        res = c.fetchall()
        return res

    def insertDatabase(self, values):
        c = DB.con.cursor()
        c.execute('INSERT INTO tasks (task, completed, reg_date) VALUES (?, False, ?)', values)
        DB.con.commit()
        return c.lastrowid

    def deleteDatabase(self, id):
        c = DB.con.cursor()
        c.execute(f'DELETE FROM tasks WHERE id={id}')
        DB.con.commit()

    def updateDatabase(self, values):
        c = DB.con.cursor()
        c.execute('UPDATE tasks SET task=? WHERE id=?', values)
        DB.con.commit()

    def updateTaskState(self, id, completed):
        c = DB.con.cursor()
        sql = f'UPDATE tasks SET completed={completed} WHERE id={id}'
        print(sql)
        c.execute(sql)
        DB.con.commit()


# DB 연결 및 DB 객체 생성
DB.connectToDatabase()
db = DB()


class Task(UserControl):

    def __init__(self, task_name, task_completed, task_date, task_status_change, task_delete, task_id = None):
        self.task_name = task_name
        self.task_completed = task_completed
        self.task_date = task_date
        self.task_status_change = task_status_change
        self.task_delete = task_delete
        self.task_id = task_id
        super().__init__()

    def build(self):

        self.display_task = Checkbox(
            value=self.task_completed,
            label=self.task_name,
            on_change=self.status_changed,
        )
        self.edit_name = TextField(expand=1)

        self.display_view = Row(
            alignment="spaceBetween",
            vertical_alignment="center",
            controls=[
                Column(
                    controls=[
                        self.display_task,
                        Text(
                            str(self.task_date)[:16],
                        )
                    ]),
                Row(
                    spacing=0,
                    controls=[
                        IconButton(
                            icon=icons.CREATE_OUTLINED,
                            tooltip="Edit To-Do",
                            on_click=self.edit_clicked,
                        ),
                        IconButton(
                            icons.DELETE_OUTLINE,
                            tooltip="Delete To-Do",
                            on_click=self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )

        self.edit_view = Row(
            visible=False,
            alignment="spaceBetween",
            vertical_alignment="center",
            controls=[
                self.edit_name,
                IconButton(
                    icon=icons.DONE_OUTLINE_OUTLINED,
                    icon_color=colors.GREEN,
                    tooltip="Update To-Do",
                    on_click=self.save_clicked,
                ),
            ],
        )
        return Column(controls=[self.display_view, self.edit_view])

    def edit_clicked(self, e):
        self.edit_name.value = self.display_task.label
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()

    def save_clicked(self, e):
        self.display_task.label = self.edit_name.value
        self.display_view.visible = True
        self.edit_view.visible = False

        self.task_name = self.edit_name.value
        db.updateDatabase((self.task_name, self.task_id))
        self.update()

    def status_changed(self, e):
        self.task_completed = self.display_task.value
        self.task_status_change(self)
        self.update()

    def delete_clicked(self, e):
        db.deleteDatabase(self.task_id)
        self.task_delete(self)
        self.update()


class TodoApp(UserControl):

    def build(self):

        task_list = db.readDatabase()

        self.new_task = TextField(hint_text="Whats needs to be done?", expand=True)
        self.tasks = Column()

        for t in task_list:
            task = Task(t[1], bool(t[2]), t[3], self.task_status_change, self.task_delete, t[0])
            self.tasks.controls.insert(0, task)

        self.filter = Tabs(
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[Tab(text="all"), Tab(text="active"), Tab(text="completed")],
        )

        # application's root control (i.e. "view") containing all other controls
        return Column(
            width=600,
            height=500,
            controls=[
                Row(
                    controls=[
                        self.new_task,
                        FloatingActionButton(icon=icons.ADD, on_click=self.add_clicked),
                    ],
                ),
                Column(
                    spacing=25,
                    controls=[
                        self.filter,
                        self.tasks,
                    ],
                ),
            ],

            scroll=True
        )

    def add_clicked(self, e):
        t = datetime.datetime.now()
        id = db.insertDatabase([self.new_task.value, t])
        task = Task(self.new_task.value, False, t, self.task_status_change, self.task_delete, id)
        self.tasks.controls.insert(0, task)
        self.new_task.value = ""
        self.update()

    def task_status_change(self, task):
        # task 상태 업데이트
        db.updateTaskState(task.task_id, task.task_completed)
        self.update()

    def task_delete(self, task):
        self.tasks.controls.remove(task)
        self.update()

    def update(self):
        status = self.filter.tabs[self.filter.selected_index].text
        for task in self.tasks.controls:
            task.visible = (
                status == "all"
                or (status == "active" and task.task_completed == False)
                or (status == "completed" and task.task_completed)
            )
        super().update()

    def tabs_changed(self, e):
        self.update()


def main(page: Page):
    page.title = "ToDo App"
    page.horizontal_alignment = "center"
    page.window_width = 500
    page.window_height = 600
    page.window_maximizable = False
    page.window_minimizable = False
    page.update()

    # create application instance
    app = TodoApp(db)

    # add application's root control to the page
    page.add(app)


flet.app(target=main)