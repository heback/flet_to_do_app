import flet as ft
import sqlite3
import datetime


# DB 관리 클래스
class DB:

    # con: sqlite3.Connection
    con = None

    @staticmethod
    def connect() -> None:
        try:
            DB.con = sqlite3.connect('todo.db', check_same_thread=False)
            c = DB.con.cursor()
            c.execute('CREATE TABLE IF NOT EXISTS tasks '
                      '(id INTEGER PRIMARY KEY AUTOINCREMENT,'
                      'task TEXT NOT NULL,'
                      'completed NUMERIC NOT NULL,'
                      'reg_date TEXT NOT NULL)')
        except Exception as e:
            print(e)

    def read(self):
        c = DB.con.cursor()
        c.execute('SELECT id, task, completed, reg_date FROM tasks')
        res = c.fetchall()
        return res

    def insert(self, values: list) -> int:
        c = DB.con.cursor()
        c.execute('INSERT INTO tasks (task, completed, reg_date) VALUES (?, False, ?)', values)
        DB.con.commit()
        return c.lastrowid

    def delete(self, id: str) -> None:
        c = DB.con.cursor()
        c.execute(f'DELETE FROM tasks WHERE id={id}')
        DB.con.commit()

    def update(self, values: list) -> None:
        c = DB.con.cursor()
        c.execute('UPDATE tasks SET task=? WHERE id=?', values)
        DB.con.commit()

    def updateTaskState(self, id, completed) -> None:
        c = DB.con.cursor()
        sql = f'UPDATE tasks SET completed={completed} WHERE id={id}'
        c.execute(sql)
        DB.con.commit()


# DB 연결 및 DB 객체 생성
DB.connect()
db = DB()


class Task(ft.UserControl):

    def __init__(
            self,
            task_name: str,
            task_completed: int,
            task_date: str,
            task_status_change,
            task_delete,
            task_id: str = None):
        self.edit_view = None
        self.display_view = None
        self.edit_name = None
        self.display_task = None
        self.task_name = task_name
        self.task_completed = task_completed
        self.task_date = task_date
        self.task_status_change = task_status_change
        self.task_delete = task_delete
        self.task_id = task_id
        super().__init__()

    def build(self):

        self.display_task = ft.Checkbox(
            value = self.task_completed,
            label = self.task_name,
            on_change = self.status_changed,
        )
        self.edit_name = ft.TextField(expand=1)

        self.display_view = ft.Row(
            alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment = ft.CrossAxisAlignment.CENTER,
            controls = [
                ft.Column(
                    controls = [
                        self.display_task,
                        ft.Text(
                            self.task_date[:16],
                        )
                    ]),
                ft.Row(
                    spacing = 0,
                    controls = [
                        ft.IconButton(
                            icon = ft.icons.CREATE_OUTLINED,
                            tooltip = "Edit To-Do",
                            on_click = self.edit_clicked,
                        ),
                        ft.IconButton(
                            ft.icons.DELETE_OUTLINE,
                            tooltip = "Delete To-Do",
                            on_click = self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )

        self.edit_view = ft.Row(
            visible = False,
            alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment = ft.CrossAxisAlignment.CENTER,
            controls = [
                self.edit_name,
                ft.IconButton(
                    icon = ft.icons.DONE_OUTLINE_OUTLINED,
                    icon_color = ft.colors.GREEN,
                    tooltip = "Update To-Do",
                    on_click = self.save_clicked,
                ),
            ],
        )
        return ft.Column(controls = [self.display_view, self.edit_view])

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
        db.delete(self.task_id)
        self.task_delete(self)
        self.update()


class TodoApp(ft.UserControl):

    def __init__(self):
        self.filter: ft.Tabs = None
        self.tasks: Task = None
        self.new_task: ft.TextField = None

    def build(self) -> ft.Column:

        task_list = db.read()

        self.new_task = ft.TextField(hint_text="무엇을 해야 합니까?", expand=True)
        self.tasks = ft.Column()

        for t in task_list:
            task = Task(
                t[1],
                bool(t[2]),
                t[3],
                self.task_status_change,
                self.task_delete,
                t[0])
            self.tasks.controls.insert(0, task)

        self.filter = ft.Tabs(
            selected_index = 0,
            on_change = self.tabs_changed,
            tabs=[ft.Tab(text = "all"), ft.Tab(text = "active"), ft.Tab(text = "completed")],
        )

        # 다른 모든 컨트롤을 포함하는 애플리케이션의 루트 컨트롤(예: "보기")
        return ft.Column(
            width = 600,
            height = 500,
            controls = [
                ft.Row(
                    controls = [
                        self.new_task,
                        ft.FloatingActionButton(
                            icon = ft.icons.ADD,
                            on_click = self.add_clicked
                        ),
                    ],
                ),
                ft.Column(
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
        id = db.insert([self.new_task.value, t])
        task = Task(
            task_name = self.new_task.value,
            task_completed = False,
            task_date = t,
            task_status_change = self.task_status_change,
            task_delete = self.task_delete,
            task_id = id
        )
        self.tasks.controls.insert(0, task)
        self.new_task.value = ""
        self.tab_update()

    def task_status_change(self, task: Task):
        # task 상태 업데이트
        db.updateTaskState(
            id = task.task_id,
            completed = task.task_completed
        )
        self.tab_update()

    def task_delete(self, task):
        self.tasks.controls.remove(task)
        self.tab_update()

    def tab_update(self):
        status = self.filter.tabs[self.filter.selected_index].text
        for task in self.tasks.controls:
            task.visible = (
                status == "all"
                or (status == "active" and task.task_completed == False)
                or (status == "completed" and task.task_completed)
            )
        super().update()

    def tabs_changed(self, e):
        self.tab_update()


def main(page: ft.Page):
    page.title = "ToDo App"
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER
    page.window_width = 500
    page.window_height = 600
    page.window_maximizable = False
    page.window_minimizable = False
    page.update()

    # TodoApp 인스턴스 생성
    app = TodoApp(db)

    # TodoApp 객체를 page에 추가
    page.add(app)


ft.app(target=main)
