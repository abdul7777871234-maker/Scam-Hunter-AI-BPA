from __future__ import annotations

from .models import Task, new_id


class TaskManager:
    def __init__(self) -> None:
        self.tasks: dict[str, Task] = {}

    def create_for_case(self, case_id: str, definitions: list[dict[str, str]]) -> list[Task]:
        created = []
        for definition in definitions:
            task = Task(
                task_id=new_id("task"),
                case_id=case_id,
                title=definition.get("title", "Review case"),
                priority=definition.get("priority", "normal"),
            )
            self.tasks[task.task_id] = task
            created.append(task)
        return created

    def for_case(self, case_id: str) -> list[dict]:
        return [task.to_dict() for task in self.tasks.values() if task.case_id == case_id]
