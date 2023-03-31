from flet import *


def main(page: Page):

    def add_clicked(e):
        tasks.controls.append(
            Checkbox(label=new_task.value)
        )
        new_task.value = ""
        view.update()

    new_task = TextField(hint_text="할 일이 무엇인가요?", expand=True)
    tasks = Column()
    view = Column(
        width=600,
        controls=[
            Row(
                controls=[
                    new_task,
                    FloatingActionButton(
                        icon=icons.ADD,
                        on_click=add_clicked
                    ),
                ],
            ),
            tasks,
        ],
    )

    page.window_width = 400
    page.window_height = 600
    page.horizontal_alignment = "center"
    page.add(view)


flet.app(target=main)