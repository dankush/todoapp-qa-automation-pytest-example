import pytest
import sys
import os
from typing import Generator
from playwright.sync_api import Page, expect

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pages.todo_page import CoolTodoPage
from pages.add_task_page import AddTaskPage


@pytest.fixture
def todo_page(page: Page) -> Generator[CoolTodoPage, None, None]:
    """Fixture that returns a configured CoolTodoPage instance."""
    page_object = CoolTodoPage(page)
    # Navigate to the app
    page_object.goto("https://react-cool-todo-app.netlify.app/")
    
    # Navigate done, yield for test
    yield page_object
    
    # Reset app state by clearing storage and reloading
    page_object.page.evaluate("() => window.localStorage.clear()")
    page_object.page.reload()

@pytest.fixture
def add_task_page(page: Page) -> Generator[AddTaskPage, None, None]:
    """Fixture that returns a configured AddTaskPage instance."""
    page_object = AddTaskPage(page)
    # Navigate to the add task page
    page_object.goto("https://react-cool-todo-app.netlify.app/")
    
    yield page_object


class TestTodoApp:
    """Tests for the React Cool Todo App."""
    
    def test_add_task(self, todo_page: CoolTodoPage) -> None:
        """Test adding a new task."""
        task_title = "Test Task"
        task_description = "This is a test task description"
        # Add and verify the task
        todo_page.add_task(task_title, task_description)
        # todo_page.expect_task_visible(task_title, task_description)
        # todo_page.expect_task_count(1)
    
    # def test_complete_task(self, todo_page: CoolTodoPage) -> None:
        """Test marking a task as complete."""
        # Add a task
        task_title = "Complete Me"
        todo_page.add_task(task_title)
        
        # Mark it as complete
        todo_page.complete_task(task_title)
        
        # Verify it's marked as complete
        todo_page.expect_task_completed(task_title, is_completed=True)
    
    # def test_edit_task(self, todo_page: CoolTodoPage) -> None:
        """Test editing a task."""
        # Add a task
        original_title = "Original Task"
        original_description = "Original description"
        todo_page.add_task(original_title, original_description)
        
        # Edit the task
        new_title = "Updated Task"
        new_description = "Updated description"
        todo_page.edit_task(original_title, new_title, new_description)
        
        # Verify the task was updated
        todo_page.expect_task_hidden(original_title)
        todo_page.expect_task_visible(new_title, new_description)
    
    # def test_delete_task(self, todo_page: CoolTodoPage) -> None:
        """Test deleting a task."""
        # Add a task
        task_title = "Delete Me"
        todo_page.add_task(task_title)
        
        # Delete the task
        todo_page.delete_task(task_title)
        
        # Verify task is gone
        todo_page.expect_task_hidden(task_title)
        todo_page.expect_task_count(0)
    
    # def test_search_tasks(self, todo_page: CoolTodoPage) -> None:
        """Test searching for tasks."""
        # Add multiple tasks
        tasks = [
            {"title": "First Task", "description": "Description 1"},
            {"title": "Second Task", "description": "Description 2"},
            {"title": "Another Task", "description": "Description 3"}
        ]
        todo_page.add_tasks(tasks)
        
        # Search for a specific task
        todo_page.search_tasks("First")
        
        # Verify only matching tasks are visible
        todo_page.expect_task_visible("First Task")
        todo_page.expect_task_hidden("Second Task")
        todo_page.expect_task_hidden("Another Task")
        
        # Clear search and verify all tasks are visible again
        todo_page.clear_search()
        todo_page.expect_total_task_cards(3)
    
    # def test_purge_all_tasks(self, todo_page: CoolTodoPage) -> None:
        """Test purging all tasks."""
        # Add multiple tasks
        tasks = [
            {"title": "Task 1", "description": "Description 1"},
            {"title": "Task 2", "description": "Description 2"}
        ]
        todo_page.add_tasks(tasks)
        
        # Verify tasks were added
        todo_page.expect_total_task_cards(2)
        
        # Purge all tasks
        todo_page.purge_all_tasks()
        
        # Verify no tasks remain
        todo_page.expect_no_tasks()
