"""An in-memory to-do list app.

Tasks are stored as a list of dicts, each with an id, title and a
done flag. A simple menu loop lets you add, list, complete and delete
tasks. Nothing is saved to disk; the list lives only while the program runs.
"""


def add_task(tasks, title):
    """Add a new task and return it.

    The id is one more than the largest existing id (or 1 if empty).
    """
    next_id = max((task["id"] for task in tasks), default=0) + 1
    task = {"id": next_id, "title": title, "done": False}
    tasks.append(task)
    return task


def find_task(tasks, task_id):
    """Return the task with the given id, or None."""
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


def complete_task(tasks, task_id):
    task = find_task(tasks, task_id)
    if task is None:
        return False
    task["done"] = True
    return True


def delete_task(tasks, task_id):
    task = find_task(tasks, task_id)
    if task is None:
        return False
    tasks.remove(task)
    return True


def list_tasks(tasks):
    if not tasks:
        print("No tasks yet.")
        return
    for task in tasks:
        mark = "x" if task["done"] else " "
        print(f"  [{mark}] {task['id']}. {task['title']}")


def read_task_id(prompt):
    """Read an integer task id from the user, or None if invalid."""
    raw = input(prompt).strip()
    try:
        return int(raw)
    except ValueError:
        print("Please enter a valid task number.")
        return None


def print_menu():
    print("\n=== To-Do List ===")
    print("1. Add task")
    print("2. List tasks")
    print("3. Complete task")
    print("4. Delete task")
    print("5. Quit")


def main():
    tasks = []  # the in-memory store, a list of dicts

    while True:
        print_menu()
        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            title = input("Task title: ").strip()
            if title:
                add_task(tasks, title)
                print("Task added.")
            else:
                print("Title cannot be empty.")

        elif choice == "2":
            list_tasks(tasks)

        elif choice == "3":
            task_id = read_task_id("Task number to complete: ")
            if task_id is not None:
                if complete_task(tasks, task_id):
                    print("Task completed.")
                else:
                    print("No task with that number.")

        elif choice == "4":
            task_id = read_task_id("Task number to delete: ")
            if task_id is not None:
                if delete_task(tasks, task_id):
                    print("Task deleted.")
                else:
                    print("No task with that number.")

        elif choice == "5":
            print("Goodbye!")
            break

        else:
            print("Unknown option, please choose 1-5.")


if __name__ == "__main__":
    main()
