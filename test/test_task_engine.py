import os
import pytest
import hero
from hero.lib.errors import MissingRequiredAttribute
from requests.exceptions import HTTPError


@pytest.fixture(scope="module")
def task_engine():
    """Create a TaskEngine instance for all tests in this module."""
    hero_client = hero.HeroClient()
    return hero_client.TaskEngine()


@pytest.fixture
def cleanup(task_engine):
    """Fixture to track and cleanup tasks and queues after each test.

    Usage:
        def test_example(self, task_engine, cleanup):
            queue = task_engine.add_queue(name="test_queue", metadata={})
            cleanup.queue(queue["id"])
            task = task_engine.add_task(queue_id=queue["id"], name="test_task", metadata={})
            cleanup.task(task["id"])
            # Test logic here - cleanup happens automatically even if test fails
    """
    task_ids = []
    queue_ids = []

    class Cleanup:
        def task(self, task_id):
            task_ids.append(task_id)

        def queue(self, queue_id):
            queue_ids.append(queue_id)

    yield Cleanup()

    # Cleanup tasks first (tasks belong to queues)
    # Note: Task Engine API soft-deletes are idempotent, so re-deleting is safe
    for task_id in task_ids:
        task_engine.delete_task(task_id)

    # Then cleanup queues
    for queue_id in queue_ids:
        task_engine.delete_queue(queue_id)


class TestQueue:
    """Tests for queue operations."""

    def test_read_queues(self, task_engine):
        """Test listing all queues."""
        queues = task_engine.read_queues()
        assert queues is not None
        assert isinstance(queues, list)

    def test_read_queues_with_state(self, task_engine):
        """Test listing queues with specific state."""
        queues = task_engine.read_queues(state="active")
        assert queues is not None
        assert isinstance(queues, list)
        # Check that all queues have state 'active'
        for queue in queues:
            assert queue["state"] == "active"

    def test_add_queue(self, task_engine, cleanup):
        """Test creating a new queue."""
        queue = task_engine.add_queue(name="example_queue", metadata={})
        cleanup.queue(queue["id"])
        assert queue is not None
        assert queue["name"] == "example_queue"
        assert "id" in queue

    def test_read_queue(self, task_engine, cleanup):
        """Test reading a specific queue by ID."""
        # Create a queue
        queue = task_engine.add_queue(name="test_read_queue", metadata={})
        queue_id = queue["id"]
        cleanup.queue(queue_id)

        # Read the queue
        read_queue = task_engine.read_queue(queue_id)
        assert read_queue is not None
        assert read_queue["id"] == queue_id

    def test_delete_queue(self, task_engine, cleanup):
        """Test deleting a queue."""
        # Create a queue to delete
        queue = task_engine.add_queue(name="queue_to_delete", metadata={})
        cleanup.queue(queue["id"])

        # Delete the queue
        deleted_queue = task_engine.delete_queue(queue["id"])
        assert deleted_queue is not None
        assert deleted_queue["GSI1SK"] == "METATYPE#Queue|deleted"

    def test_read_queue_by_name(self, task_engine, cleanup):
        """Test reading a queue by name."""
        # Create a queue first
        queue = task_engine.add_queue(
            name="test_queue_by_name", metadata={"description": "test description"}
        )
        queue_id = queue["id"]
        cleanup.queue(queue_id)

        # Read by name
        read_queue = task_engine.read_queue_by_name(
            name="test_queue_by_name", metatype="Queue"
        )
        assert read_queue is not None
        assert read_queue["name"] == "test_queue_by_name"

    def test_update_queue(self, task_engine, cleanup):
        """Test updating a queue."""
        # Create a queue first
        queue = task_engine.add_queue(
            name="test_update_queue", metadata={"description": "original description"}
        )
        queue_id = queue["id"]
        cleanup.queue(queue_id)

        # Update the queue
        updated_queue = task_engine.update_queue(
            queue_id=queue_id, name="updated_test_queue", metadata={"updated": True}
        )
        assert updated_queue is not None
        assert updated_queue["name"] == "updated_test_queue"

    # TODO: Skipped until server-side permissions are fixed for SQS visibility timeout updates
    @pytest.mark.skip(
        reason="Server-side permission issue prevents updating SQS visibility timeout"
    )
    def test_update_queue_visibility_timeout(self, task_engine, cleanup):
        """Test updating a queue with visibility timeout."""
        # Create a queue first
        queue = task_engine.add_queue(
            name="test_update_queue", metadata={"description": "original description"}
        )
        queue_id = queue["id"]
        cleanup.queue(queue_id)

        # Update the queue with visibility timeout
        updated_queue = task_engine.update_queue(
            queue_id=queue_id,
            name="updated_test_queue_visibility",
            metadata={"updated": True, "sqs": {"visibility_timeout": "120"}},
        )
        assert updated_queue is not None
        assert updated_queue["name"] == "updated_test_queue_visibility"

    def test_add_queue_missing_name(self, task_engine):
        """Test that adding a queue without a name raises an error."""
        with pytest.raises(MissingRequiredAttribute):
            task_engine.add_queue(name=None, metadata={})

    def test_read_queue_missing_id(self, task_engine):
        """Test that reading a queue without an ID raises an error."""
        with pytest.raises(MissingRequiredAttribute):
            task_engine.read_queue(None)

    def test_read_queue_by_name_missing_name(self, task_engine):
        """Test that reading a queue by name without a name raises an error."""
        with pytest.raises(MissingRequiredAttribute):
            task_engine.read_queue_by_name(name=None)

    def test_delete_queue_missing_id(self, task_engine):
        """Test that deleting a queue without an ID raises an error."""
        with pytest.raises(MissingRequiredAttribute):
            task_engine.delete_queue(None)


class TestTask:
    """Tests for task operations."""

    def test_read_tasks(self, task_engine, cleanup):
        """Test listing tasks in a queue."""
        # Create a queue
        queue = task_engine.add_queue(name="test_read_tasks_queue", metadata={})
        queue_id = queue["id"]
        cleanup.queue(queue_id)

        # Add a task to the queue
        task = task_engine.add_task(queue_id=queue_id, name="test_task", metadata={})
        task_id = task["id"]
        cleanup.task(task_id)

        # Read tasks in the queue
        tasks = task_engine.read_tasks(queue_id=queue_id)
        assert tasks is not None
        assert isinstance(tasks, list)

    def test_count_tasks(self, task_engine, cleanup):
        """Test counting tasks in a queue."""
        # Create a queue
        queue = task_engine.add_queue(name="test_count_tasks_queue", metadata={})
        queue_id = queue["id"]
        cleanup.queue(queue_id)

        # Add a task to the queue
        task = task_engine.add_task(
            queue_id=queue_id, name="test_task_count", metadata={}
        )
        task_id = task["id"]
        cleanup.task(task_id)

        # Count tasks in the queue
        resp = task_engine.count_tasks(queue_id=queue_id)
        count = resp["count"]
        assert count is not None
        assert isinstance(count, int)

    def test_pull_tasks(self, task_engine, cleanup):
        """Test pulling tasks from a queue."""
        # Create a queue
        queue = task_engine.add_queue(name="test_pull_tasks_queue", metadata={})
        queue_id = queue["id"]
        cleanup.queue(queue_id)

        # Add a task to the queue
        task = task_engine.add_task(
            queue_id=queue_id, name="test_pull_task", metadata={}
        )
        task_id = task["id"]
        cleanup.task(task_id)

        # Pull tasks (claim)
        pulled = task_engine.pull_tasks(queue_id=queue_id, receive=5)
        assert isinstance(pulled, list)
        assert pulled[0]["id"] == task_id

    def test_read_task(self, task_engine, cleanup):
        """Test reading a specific task by ID."""
        # Create a queue
        queue = task_engine.add_queue(name="test_read_task_queue", metadata={})
        queue_id = queue["id"]
        cleanup.queue(queue_id)

        # Add a task
        task = task_engine.add_task(
            queue_id=queue_id, name="test_read_task", metadata={}
        )
        task_id = task["id"]
        cleanup.task(task_id)

        # Read the task
        read_task = task_engine.read_task(task_id)
        assert read_task is not None
        assert read_task["id"] == task_id

    def test_read_task_by_name(self, task_engine, cleanup):
        """Test reading a task by name."""
        # Create a queue
        queue = task_engine.add_queue(name="test_read_task_by_name_queue", metadata={})
        queue_id = queue["id"]
        cleanup.queue(queue_id)

        # Add a task
        task = task_engine.add_task(
            queue_id=queue_id, name="test_read_task_by_name", metadata={}
        )
        task_id = task["id"]
        cleanup.task(task_id)

        # Read the task by name
        read_task = task_engine.read_task_by_name(
            name="test_read_task_by_name", metatype="Task"
        )
        assert read_task is not None
        assert read_task["name"] == "test_read_task_by_name"

    def test_delete_task(self, task_engine, cleanup):
        """Test deleting a task."""
        # Create a queue
        queue = task_engine.add_queue(name="test_delete_task_queue", metadata={})
        queue_id = queue["id"]
        cleanup.queue(queue_id)

        # Add a task
        task = task_engine.add_task(
            queue_id=queue_id, name="test_delete_task", metadata={}
        )
        task_id = task["id"]
        cleanup.task(task_id)

        # Delete the task
        deleted_task = task_engine.delete_task(task_id)
        assert deleted_task is not None

    def test_add_task(self, task_engine, cleanup):
        """Test creating a new task."""
        # Create a queue
        queue = task_engine.add_queue(name="test_add_task_queue", metadata={})
        queue_id = queue["id"]
        cleanup.queue(queue_id)

        # Add a task
        task = task_engine.add_task(
            queue_id=queue_id, name="test_add_task", metadata={"test": True}
        )
        assert task is not None
        assert task["name"] == "test_add_task"
        task_id = task["id"]
        cleanup.task(task_id)

    def test_update_task(self, task_engine, cleanup):
        """Test updating a task."""
        # Create a queue
        queue = task_engine.add_queue(name="test_update_task_queue", metadata={})
        queue_id = queue["id"]
        cleanup.queue(queue_id)

        # Add a task
        task = task_engine.add_task(
            queue_id=queue_id, name="test_update_task", metadata={}
        )
        task_id = task["id"]
        cleanup.task(task_id)

        # Update the task
        updated_task = task_engine.update_task(
            task_id=task_id,
            name="updated_test_task",
            state="completed",
            metadata={"updated": True},
        )
        assert updated_task is not None
        assert updated_task["name"] == "updated_test_task"

    def test_update_task_without_name(self, task_engine, cleanup):
        """Test updating a task without changing the name."""
        # Create a queue
        queue = task_engine.add_queue(name="test_update_task_queue", metadata={})
        queue_id = queue["id"]
        cleanup.queue(queue_id)

        # Add a task
        task = task_engine.add_task(
            queue_id=queue_id, name="test_update_task", metadata={}
        )
        task_id = task["id"]
        cleanup.task(task_id)

        # Update the task without changing the name
        updated_task = task_engine.update_task(
            task_id=task_id,
            name="test_update_task",
            state="completed",
            metadata={"updated": True},
        )
        assert updated_task is not None
        assert updated_task["name"] == "test_update_task"

    def test_restart_task(self, task_engine, cleanup):
        """Test restarting a task."""
        # Create a queue
        queue = task_engine.add_queue(name="test_restart_task_queue", metadata={})
        queue_id = queue["id"]
        cleanup.queue(queue_id)

        # Add a task
        task = task_engine.add_task(
            queue_id=queue_id, name="test_restart_task", metadata={}
        )
        task_id = task["id"]
        cleanup.task(task_id)

        # Set task to done state first
        task_engine.update_task(
            task_id=task_id, name="test_restart_task", state="done", metadata={}
        )

        # Restart the task
        restarted_task = task_engine.restart_task(task_id)
        assert restarted_task is not None

    def test_add_task_missing_queue_id(self, task_engine):
        """Test that adding a task without a queue_id raises an error."""
        with pytest.raises(MissingRequiredAttribute):
            task_engine.add_task(queue_id=None, name="test", metadata={})

    def test_add_task_missing_name(self, task_engine, cleanup):
        """Test that adding a task without a name raises an error."""
        # Create a queue for testing
        queue = task_engine.add_queue(name="test_missing_name_queue", metadata={})
        queue_id = queue["id"]
        cleanup.queue(queue_id)

        with pytest.raises(MissingRequiredAttribute):
            task_engine.add_task(queue_id=queue_id, name=None, metadata={})

    def test_read_task_missing_id(self, task_engine):
        """Test that reading a task without an ID raises an error."""
        with pytest.raises(MissingRequiredAttribute):
            task_engine.read_task(None)

    def test_read_task_by_name_missing_name(self, task_engine):
        """Test that reading a task by name without a name raises an error."""
        with pytest.raises(MissingRequiredAttribute):
            task_engine.read_task_by_name(name=None)

    def test_restart_task_missing_id(self, task_engine):
        """Test that restarting a task without an ID raises an error."""
        with pytest.raises(MissingRequiredAttribute):
            task_engine.restart_task(None)

    def test_delete_task_missing_id(self, task_engine):
        """Test that deleting a task without an ID raises an error."""
        with pytest.raises(MissingRequiredAttribute):
            task_engine.delete_task(None)


class TestEventSource:
    """Tests for event source operations."""

    def test_create_event_source(self, task_engine, cleanup):
        """Test creating an event source."""
        # Create a queue
        queue = task_engine.add_queue(name="test_event_source_queue", metadata={})
        queue_id = queue["id"]
        cleanup.queue(queue_id)

        lambda_name = os.environ.get("TEST_TASK_ENGINE_LAMBDA", "test-lambda-function")
        lambda_missing = False

        try:
            event_source = task_engine.create_event_source(
                queue_id=queue_id, lambda_name=lambda_name
            )
            assert event_source is not None
            assert isinstance(event_source, dict)

            # Cleanup - delete event source if created
            if event_source.get("metadata", {}).get("events"):
                event_id = event_source["metadata"]["events"][0]["id"]
                task_engine.delete_event_source(queue_id=queue_id, event_id=event_id)
        except HTTPError as e:
            # Acceptable path when lambda doesn't exist in local/dev
            if "Function does not exist" in str(e.response.text):
                lambda_missing = True
            else:
                raise e

        if lambda_missing:
            pytest.skip("Lambda function not present - skipping event source test")

    def test_delete_event_source(self, task_engine, cleanup):
        """Test deleting an event source."""
        # Create a queue
        queue = task_engine.add_queue(name="test_delete_event_queue", metadata={})
        queue_id = queue["id"]
        cleanup.queue(queue_id)

        lambda_name = os.environ.get("TEST_TASK_ENGINE_LAMBDA", "test-lambda-function")
        lambda_missing = False

        try:
            # First create an event source
            event_source = task_engine.create_event_source(
                queue_id=queue_id, lambda_name=lambda_name
            )
            assert event_source is not None

            # Get the event ID
            event_id = event_source["metadata"]["events"][0]["id"]

            # Delete the event source
            deleted_event = task_engine.delete_event_source(
                queue_id=queue_id, event_id=event_id
            )
            assert deleted_event is not None
        except HTTPError as e:
            # Acceptable path when lambda doesn't exist in local/dev
            if "Function does not exist" in str(e.response.text):
                lambda_missing = True
            else:
                raise e

        if lambda_missing:
            pytest.skip("Lambda function not present - skipping event source test")
