import pytest
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APIClient
from mytodoapp.models import CustomUser, Todo
from mytodoapp.tokens import email_verification_token



# HELPERS — reusable shortcuts used across multiple tests

def make_user(username="testuser", email="testuser@example.com",
              password="StrongPass123!", verified=True, **kwargs):
    """Create and return a CustomUser. Verified by default."""
    user = CustomUser.objects.create_user(
        username=username,
        email=email,
        password=password,
        **kwargs,
    )
    user.is_verified = verified
    user.save()
    return user


def make_todo(user, description="Buy groceries", hours_from_now=48,
              completion=False, reminder_sent=False, final_reminder_sent=False):
    """Create and return a Todo belonging to the given user."""
    return Todo.objects.create(
        user=user,
        description=description,
        deadline=timezone.now() + timedelta(hours=hours_from_now),
        completion=completion,
        reminder_sent=reminder_sent,
        final_reminder_sent=final_reminder_sent,
    )


def get_tokens(client, username, password):
    """Log in and return the access token string."""
    response = client.post(
        "/api/token/",
        {"username": username, "password": password},
        format="json",
    )
    return response.data.get("access")


def auth_client(user, password="StrongPass123!"):
    """Return an APIClient already authenticated as the given user."""
    client = APIClient()
    token = get_tokens(client, user.username, password)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


def make_verification_link(user):
    """Return (uid, token) for a user's verification link."""
    uid   = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)
    return uid, token


# 1. REGISTRATION

@pytest.mark.django_db
class TestRegistration:

    def test_register_success_returns_201(self):
        """Valid registration data creates a user and returns 201."""
        client = APIClient()
        payload = {
            "username":   "newuser",
            "email":      "newuser@example.com",
            "password":   "StrongPass123!",
            "first_name": "New",
            "last_name":  "User",
            "phone":      "+256700000000",
        }
        response = client.post("/api/register/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_register_creates_user_in_database(self):
        """After registration the user exists in the database."""
        client = APIClient()
        payload = {
            "username":   "dbuser",
            "email":      "dbuser@example.com",
            "password":   "StrongPass123!",
            "first_name": "DB",
            "last_name":  "User",
            "phone":      "+256700000001",
        }
        client.post("/api/register/", payload, format="json")
        assert CustomUser.objects.filter(username="dbuser").exists()

    def test_register_new_user_is_not_verified(self):
        """Newly registered users must have is_verified=False."""
        client = APIClient()
        payload = {
            "username":   "unverified",
            "email":      "unverified@example.com",
            "password":   "StrongPass123!",
            "first_name": "Un",
            "last_name":  "Verified",
            "phone":      "+256700000002",
        }
        client.post("/api/register/", payload, format="json")
        user = CustomUser.objects.get(username="unverified")
        assert user.is_verified is False

    def test_register_returns_message_in_response(self):
        """Response body contains a 'message' key."""
        client = APIClient()
        payload = {
            "username":   "msguser",
            "email":      "msguser@example.com",
            "password":   "StrongPass123!",
            "first_name": "Msg",
            "last_name":  "User",
            "phone":      "+256700000003",
        }
        response = client.post("/api/register/", payload, format="json")
        assert "message" in response.data

    def test_register_duplicate_username_returns_400(self, db):
        """Registering with an already-taken username returns 400."""
        make_user(username="taken")
        client = APIClient()
        payload = {
            "username":   "taken",
            "email":      "other@example.com",
            "password":   "StrongPass123!",
            "first_name": "Other",
            "last_name":  "User",
            "phone":      "+256700000004",
        }
        response = client.post("/api/register/", payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_duplicate_email_returns_400(self, db):
        """Registering with an already-used email returns 400."""
        make_user(username="original", email="shared@example.com")
        client = APIClient()
        payload = {
            "username":   "newguy",
            "email":      "shared@example.com",
            "password":   "StrongPass123!",
            "first_name": "New",
            "last_name":  "Guy",
            "phone":      "+256700000005",
        }
        response = client.post("/api/register/", payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_email_returns_400(self):
        """Registration without email returns 400."""
        client = APIClient()
        response = client.post(
            "/api/register/",
            {"username": "noemail", "password": "StrongPass123!"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_password_returns_400(self):
        """Registration without password returns 400."""
        client = APIClient()
        response = client.post(
            "/api/register/",
            {"username": "nopass", "email": "nopass@example.com"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_empty_payload_returns_400(self):
        """Empty payload returns 400."""
        client = APIClient()
        response = client.post("/api/register/", {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# 2. EMAIL VERIFICATION
# NOTE: mytodoapp.urls is included at "todos/" in the project urls.py, so the
# verify-email route actually lives at /todos/verify-email/<uid>/<token>/,
# NOT /api/verify-email/...

@pytest.mark.django_db
class TestEmailVerification:

    def test_valid_token_returns_200(self):
        """Valid uid + token returns 200 OK."""
        user = make_user(verified=False)
        uid, token = make_verification_link(user)
        client = APIClient()
        response = client.post(f"/todos/verify-email/{uid}/{token}/")
        assert response.status_code == status.HTTP_200_OK

    def test_valid_token_sets_is_verified_true(self):
        """After verification, is_verified flips to True."""
        user = make_user(verified=False)
        uid, token = make_verification_link(user)
        client = APIClient()
        client.post(f"/todos/verify-email/{uid}/{token}/")
        user.refresh_from_db()
        assert user.is_verified is True

    def test_valid_token_returns_success_message(self):
        """Response body contains a success message."""
        user = make_user(verified=False)
        uid, token = make_verification_link(user)
        client = APIClient()
        response = client.post(f"/todos/verify-email/{uid}/{token}/")
        assert "message" in response.data

    def test_invalid_token_returns_400(self):
        """A bad token returns 400."""
        user = make_user(verified=False)
        uid, _ = make_verification_link(user)
        client = APIClient()
        response = client.post(f"/todos/verify-email/{uid}/badtoken/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_uid_returns_400(self):
        """A bad uid returns 400."""
        client = APIClient()
        response = client.post("/todos/verify-email/invaliduid/sometoken/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_token_cannot_be_reused(self):
        """Using a verification link a second time returns 400."""
        user = make_user(verified=False)
        uid, token = make_verification_link(user)
        client = APIClient()
        client.post(f"/todos/verify-email/{uid}/{token}/")   # first use — succeeds
        # After is_verified=True the token is invalid
        response = client.post(f"/todos/verify-email/{uid}/{token}/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_already_verified_user_not_changed(self):
        """Verifying an already-verified user returns 400 and leaves DB unchanged."""
        user = make_user(verified=True)
        uid, token = make_verification_link(user)
        client = APIClient()
        # Token is already invalid because is_verified=True when token was made
        response = client.post(f"/todos/verify-email/{uid}/{token}/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# 3. AUTHENTICATION (JWT)

@pytest.mark.django_db
class TestAuthentication:

    def test_login_success_returns_200(self):
        """Valid credentials return 200."""
        user = make_user()
        client = APIClient()
        response = client.post(
            "/api/token/",
            {"username": user.username, "password": "StrongPass123!"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK

    def test_login_returns_access_token(self):
        """Response contains an access token."""
        user = make_user()
        client = APIClient()
        response = client.post(
            "/api/token/",
            {"username": user.username, "password": "StrongPass123!"},
            format="json",
        )
        assert "access" in response.data

    def test_login_returns_refresh_token(self):
        """Response contains a refresh token."""
        user = make_user()
        client = APIClient()
        response = client.post(
            "/api/token/",
            {"username": user.username, "password": "StrongPass123!"},
            format="json",
        )
        assert "refresh" in response.data

    def test_wrong_password_returns_401(self):
        """Wrong password returns 401."""
        user = make_user()
        client = APIClient()
        response = client.post(
            "/api/token/",
            {"username": user.username, "password": "WrongPassword!"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_nonexistent_user_returns_401(self):
        """Login with a username that does not exist returns 401."""
        client = APIClient()
        response = client.post(
            "/api/token/",
            {"username": "nobody", "password": "SomePass123!"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_request_to_todos_returns_401(self):
        """No token → 401 on any protected endpoint."""
        client = APIClient()
        response = client.get("/todos/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unverified_user_is_blocked_from_todos(self):
        """Authenticated but unverified user gets 403 on todo endpoints."""
        user = make_user(verified=False)
        client = APIClient()
        token = get_tokens(client, user.username, "StrongPass123!")
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = client.get("/todos/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_verified_user_can_access_todos(self):
        """Authenticated and verified user gets 200 on todos list."""
        user = make_user(verified=True)
        client = auth_client(user)
        response = client.get("/todos/")
        assert response.status_code == status.HTTP_200_OK

    def test_token_refresh_returns_new_access_token(self):
        """POST /api/token/refresh/ with a valid refresh token returns a new access token."""
        user = make_user()
        client = APIClient()
        login = client.post(
            "/api/token/",
            {"username": user.username, "password": "StrongPass123!"},
            format="json",
        )
        refresh = login.data["refresh"]
        response = client.post(
            "/api/token/refresh/",
            {"refresh": refresh},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data


# 4. TODOS — CREATE
# NOTE: creation has its own dedicated route: /todos/create/ (TodoCreateView),
# separate from the list route /todos/ (TodoListView).

@pytest.mark.django_db
class TestTodoCreate:

    def setup_method(self):
        self.user   = make_user()
        self.client = auth_client(self.user)

    def test_create_todo_returns_201(self):
        """Valid payload creates a todo and returns 201."""
        payload = {
            "description": "Write unit tests",
            "deadline":    (timezone.now() + timedelta(days=1)).isoformat(),
            "completion":  False,
        }
        response = self.client.post("/todos/create/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_todo_saves_to_database(self):
        """Created todo exists in the database."""
        payload = {
            "description": "Saved todo",
            "deadline":    (timezone.now() + timedelta(days=1)).isoformat(),
            "completion":  False,
        }
        self.client.post("/todos/create/", payload, format="json")
        assert Todo.objects.filter(description="Saved todo").exists()

    def test_create_todo_response_contains_description(self):
        """Response body contains the todo description."""
        payload = {
            "description": "Check response",
            "deadline":    (timezone.now() + timedelta(days=1)).isoformat(),
            "completion":  False,
        }
        response = self.client.post("/todos/create/", payload, format="json")
        assert response.data["description"] == "Check response"

    def test_create_todo_belongs_to_requesting_user(self):
        """Newly created todo is owned by the authenticated user."""
        payload = {
            "description": "Owner check",
            "deadline":    (timezone.now() + timedelta(days=1)).isoformat(),
            "completion":  False,
        }
        response = self.client.post("/todos/create/", payload, format="json")
        todo = Todo.objects.get(id=response.data["id"])
        assert todo.user == self.user

    def test_create_todo_missing_deadline_returns_400(self):
        """Todo without a deadline returns 400."""
        response = self.client.post(
            "/todos/create/",
            {"description": "No deadline"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_todo_missing_description_returns_400(self):
        """Todo without a description returns 400."""
        response = self.client.post(
            "/todos/create/",
            {"deadline": (timezone.now() + timedelta(days=1)).isoformat()},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_unauthenticated_create_returns_401(self):
        """Unauthenticated POST to /todos/create/ returns 401."""
        client = APIClient()
        payload = {
            "description": "Anon todo",
            "deadline":    (timezone.now() + timedelta(days=1)).isoformat(),
        }
        response = client.post("/todos/create/", payload, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# 5. TODOS — READ

@pytest.mark.django_db
class TestTodoRead:

    def setup_method(self):
        self.user   = make_user()
        self.client = auth_client(self.user)
        self.todo   = make_todo(self.user, description="Read me")

    def test_list_todos_returns_200(self):
        """GET /todos/ returns 200."""
        response = self.client.get("/todos/")
        assert response.status_code == status.HTTP_200_OK

    def test_list_todos_contains_users_todo(self):
        """Todo list includes the current user's todo."""
        response = self.client.get("/todos/")
        descriptions = [t["description"] for t in response.data]
        assert "Read me" in descriptions

    def test_list_todos_does_not_contain_other_users_todo(self):
        """Todo list does not include another user's todos."""
        other_user = make_user(username="other", email="other@example.com")
        make_todo(other_user, description="Other user's todo")
        response = self.client.get("/todos/")
        descriptions = [t["description"] for t in response.data]
        assert "Other user's todo" not in descriptions

    def test_retrieve_single_todo_returns_200(self):
        """GET /todos/<id>/ returns 200 for own todo."""
        response = self.client.get(f"/todos/{self.todo.id}/")
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_single_todo_returns_correct_data(self):
        """Retrieved todo has the correct description."""
        response = self.client.get(f"/todos/{self.todo.id}/")
        assert response.data["description"] == "Read me"

    def test_retrieve_other_users_todo_returns_404(self):
        """Trying to GET another user's todo returns 404."""
        other_user = make_user(username="other2", email="other2@example.com")
        other_todo = make_todo(other_user, description="Private")
        response   = self.client.get(f"/todos/{other_todo.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_nonexistent_todo_returns_404(self):
        """GET /todos/99999/ returns 404."""
        response = self.client.get("/todos/99999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND


# 6. TODOS — UPDATE
# NOTE: update has its own dedicated route: /todos/<id>/update/ (TodoUpdateView),
# separate from the detail route /todos/<id>/ (TodoDetailView).

@pytest.mark.django_db
class TestTodoUpdate:

    def setup_method(self):
        self.user   = make_user()
        self.client = auth_client(self.user)
        self.todo   = make_todo(self.user, description="Update me")

    def test_patch_todo_returns_200(self):
        """PATCH /todos/<id>/update/ returns 200."""
        response = self.client.patch(
            f"/todos/{self.todo.id}/update/",
            {"completion": True},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK

    def test_patch_todo_updates_completion(self):
        """PATCH flips completion field in the database."""
        self.client.patch(
            f"/todos/{self.todo.id}/update/",
            {"completion": True},
            format="json",
        )
        self.todo.refresh_from_db()
        assert self.todo.completion is True

    def test_patch_todo_updates_description(self):
        """PATCH updates description correctly."""
        self.client.patch(
            f"/todos/{self.todo.id}/update/",
            {"description": "Updated description"},
            format="json",
        )
        self.todo.refresh_from_db()
        assert self.todo.description == "Updated description"

    def test_put_todo_returns_200(self):
        """PUT /todos/<id>/update/ with full payload returns 200."""
        payload = {
            "description": "Full update",
            "deadline":    (timezone.now() + timedelta(days=3)).isoformat(),
            "completion":  False,
        }
        response = self.client.put(
            f"/todos/{self.todo.id}/update/", payload, format="json"
        )
        assert response.status_code == status.HTTP_200_OK

    def test_put_todo_replaces_description(self):
        """PUT replaces the description in the database."""
        payload = {
            "description": "Fully replaced",
            "deadline":    (timezone.now() + timedelta(days=3)).isoformat(),
            "completion":  False,
        }
        self.client.put(f"/todos/{self.todo.id}/update/", payload, format="json")
        self.todo.refresh_from_db()
        assert self.todo.description == "Fully replaced"

    def test_patch_other_users_todo_returns_404(self):
        """Cannot PATCH another user's todo."""
        other_user = make_user(username="patchother", email="patchother@example.com")
        other_todo = make_todo(other_user)
        response   = self.client.patch(
            f"/todos/{other_todo.id}/update/",
            {"completion": True},
            format="json",
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


# 7. TODOS — DELETE
# NOTE: delete has its own dedicated route: /todos/<id>/delete/ (TodoDeleteView),
# separate from the detail route /todos/<id>/ (TodoDetailView).

@pytest.mark.django_db
class TestTodoDelete:

    def setup_method(self):
        self.user   = make_user()
        self.client = auth_client(self.user)
        self.todo   = make_todo(self.user, description="Delete me")

    def test_delete_todo_returns_204(self):
        """DELETE /todos/<id>/delete/ returns 204 No Content."""
        response = self.client.delete(f"/todos/{self.todo.id}/delete/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_todo_removes_from_database(self):
        """Deleted todo no longer exists in the database."""
        todo_id = self.todo.id
        self.client.delete(f"/todos/{self.todo.id}/delete/")
        assert not Todo.objects.filter(id=todo_id).exists()

    def test_delete_other_users_todo_returns_404(self):
        """Cannot DELETE another user's todo."""
        other_user = make_user(username="delother", email="delother@example.com")
        other_todo = make_todo(other_user)
        response   = self.client.delete(f"/todos/{other_todo.id}/delete/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_todo_returns_404(self):
        """DELETE on a nonexistent ID returns 404."""
        response = self.client.delete("/todos/99999/delete/")
        assert response.status_code == status.HTTP_404_NOT_FOUND


# 8. TODO MODEL PROPERTIES

@pytest.mark.django_db
class TestTodoModelProperties:

    def setup_method(self):
        self.user = make_user()

    def test_is_complete_returns_true_when_completion_is_true(self):
        """is_complete property returns True when completion=True."""
        todo = make_todo(self.user, completion=True)
        assert todo.is_complete is True

    def test_is_complete_returns_false_when_completion_is_false(self):
        """is_complete property returns False when completion=False."""
        todo = make_todo(self.user, completion=False)
        assert todo.is_complete is False

    def test_is_overdue_true_when_deadline_passed_and_incomplete(self):
        """is_overdue returns True when deadline is in the past and incomplete."""
        todo = Todo.objects.create(
            user=self.user,
            description="Overdue",
            deadline=timezone.now() - timedelta(hours=1),
            completion=False,
        )
        assert todo.is_overdue is True

    def test_is_overdue_false_when_deadline_in_future(self):
        """is_overdue returns False when deadline is still in the future."""
        todo = make_todo(self.user, hours_from_now=48)
        assert todo.is_overdue is False

    def test_is_overdue_false_when_completed_even_if_deadline_passed(self):
        """is_overdue returns False when the todo is marked complete."""
        todo = Todo.objects.create(
            user=self.user,
            description="Done late",
            deadline=timezone.now() - timedelta(hours=1),
            completion=True,
        )
        assert todo.is_overdue is False


# 9. REMINDER TASK QUERIES
# NOTE: these tests import get_todos_due_within from mytodoapp.tasks. That
# function isn't in the models.py you shared, so it must exist in a
# mytodoapp/tasks.py module with this signature:
#
#   def get_todos_due_within(hours=0, minutes=0, window_minutes=0, reminder_flag="reminder_sent"):
#       ...returns a QuerySet of Todo objects due within the window, excluding
#          completed todos and todos where the given reminder_flag is already True.
#
# If that module/function doesn't exist yet, these tests will fail with
# ModuleNotFoundError / ImportError rather than an assertion error — that's
# expected until competence 4 (external dependencies / reminder emails) wires
# it up. If you've already built it under a different name or path, update
# the import below to match.

@pytest.mark.django_db
class TestReminderTaskQueries:

    def setup_method(self):
        self.user = make_user()

    # ── 24-hour reminder ─────────────────────────────────────────────────────

    def test_24h_query_finds_todo_due_in_24_hours(self):
        """Todo due in exactly 24 hours is returned by get_todos_due_within."""
        from mytodoapp.tasks import get_todos_due_within
        make_todo(self.user, description="Due in 24h", hours_from_now=24,
                  reminder_sent=False)
        results = get_todos_due_within(hours=24, window_minutes=120,
                                        reminder_flag="reminder_sent")
        assert results.count() == 1

    def test_24h_query_excludes_completed_todo(self):
        """Completed todos are excluded from the 24h reminder query."""
        from mytodoapp.tasks import get_todos_due_within
        make_todo(self.user, description="Done", hours_from_now=24,
                  completion=True, reminder_sent=False)
        results = get_todos_due_within(hours=24, window_minutes=120,
                                        reminder_flag="reminder_sent")
        assert results.count() == 0

    def test_24h_query_excludes_already_reminded_todo(self):
        """Todos already reminded are excluded from the 24h query."""
        from mytodoapp.tasks import get_todos_due_within
        make_todo(self.user, description="Already reminded", hours_from_now=24,
                  reminder_sent=True)
        results = get_todos_due_within(hours=24, window_minutes=120,
                                        reminder_flag="reminder_sent")
        assert results.count() == 0

    def test_24h_query_excludes_overdue_todo(self):
        """Todos whose deadline has already passed are excluded."""
        from mytodoapp.tasks import get_todos_due_within
        Todo.objects.create(
            user=self.user,
            description="Already overdue",
            deadline=timezone.now() - timedelta(hours=1),
            completion=False,
            reminder_sent=False,
        )
        results = get_todos_due_within(hours=24, window_minutes=120,
                                        reminder_flag="reminder_sent")
        assert results.count() == 0

    def test_24h_query_excludes_todo_due_in_48_hours(self):
        """Todo due in 48 hours is outside the 24h window and excluded."""
        from mytodoapp.tasks import get_todos_due_within
        make_todo(self.user, description="Far away", hours_from_now=48,
                  reminder_sent=False)
        results = get_todos_due_within(hours=24, window_minutes=120,
                                        reminder_flag="reminder_sent")
        assert results.count() == 0

    # ── 5-minute reminder ─────────────────────────────────────────────────────

    def test_5min_query_finds_todo_due_in_5_minutes(self):
        """Todo due in exactly 5 minutes is returned by get_todos_due_within."""
        from mytodoapp.tasks import get_todos_due_within
        Todo.objects.create(
            user=self.user,
            description="Due in 5 min",
            deadline=timezone.now() + timedelta(minutes=5),
            completion=False,
            final_reminder_sent=False,
        )
        results = get_todos_due_within(hours=0, minutes=5, window_minutes=2,
                                        reminder_flag="final_reminder_sent")
        assert results.count() == 1

    def test_5min_query_excludes_completed_todo(self):
        """Completed todo is excluded from the 5-minute reminder query."""
        from mytodoapp.tasks import get_todos_due_within
        Todo.objects.create(
            user=self.user,
            description="Done",
            deadline=timezone.now() + timedelta(minutes=5),
            completion=True,
            final_reminder_sent=False,
        )
        results = get_todos_due_within(hours=0, minutes=5, window_minutes=2,
                                        reminder_flag="final_reminder_sent")
        assert results.count() == 0

    def test_5min_query_excludes_already_final_reminded_todo(self):
        """Todos with final_reminder_sent=True are excluded."""
        from mytodoapp.tasks import get_todos_due_within
        Todo.objects.create(
            user=self.user,
            description="Already final reminded",
            deadline=timezone.now() + timedelta(minutes=5),
            completion=False,
            final_reminder_sent=True,
        )
        results = get_todos_due_within(hours=0, minutes=5, window_minutes=2,
                                        reminder_flag="final_reminder_sent")
        assert results.count() == 0

    # ── reminder_sent flag persistence ────────────────────────────────────────

    def test_reminder_sent_flag_is_false_by_default(self):
        """New todos have reminder_sent=False by default."""
        todo = make_todo(self.user)
        assert todo.reminder_sent is False

    def test_final_reminder_sent_flag_is_false_by_default(self):
        """New todos have final_reminder_sent=False by default."""
        todo = make_todo(self.user)
        assert todo.final_reminder_sent is False

    def test_reminder_sent_can_be_set_to_true(self):
        """reminder_sent can be saved as True."""
        todo = make_todo(self.user)
        todo.reminder_sent = True
        todo.save(update_fields=["reminder_sent"])
        todo.refresh_from_db()
        assert todo.reminder_sent is True

    def test_final_reminder_sent_can_be_set_to_true(self):
        """final_reminder_sent can be saved as True."""
        todo = make_todo(self.user)
        todo.final_reminder_sent = True
        todo.save(update_fields=["final_reminder_sent"])
        todo.refresh_from_db()
        assert todo.final_reminder_sent is True