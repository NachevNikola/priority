import pytest
import json
from flask_jwt_extended import create_access_token
from tests.test_utils import make_request
from src.priority.api.rules.models import Rule, Condition
from src.priority.api.users.models import User


class TestRulesRoutes:

    @pytest.fixture(autouse=True)
    def setup(self, app, client, db):
        self.app = app
        self.client = client

        user1 = User(username="user1", email="user1@example.com")
        user2 = User(username="user2", email="user2@example.com")

        condition1 = Condition(field="category", operator="equals", value="work")
        condition2 = Condition(field="tag", operator="equals", value="priority")
        rule1 = Rule(name="rule1", boost=5, user_id=1, conditions=[condition1])
        rule2 = Rule(name="rule2", boost=10, user_id=1, conditions=[condition1, condition2])
        rule3 = Rule(name="rule3", boost=15, user_id=2, conditions=[condition2])

        db.session.add_all([user1, user2, condition1, condition2, rule1, rule2])
        db.session.commit()

        self.user1 = user1
        self.rule1 = rule1
        self.rule2 = rule2
        self.rule3 = rule3

        self.user1_token = create_access_token(identity=str(user1.id))
        self.user2_token = create_access_token(identity=str(user2.id))

    def test_get_rules_success(self):
        response = make_request(
            self.client,
            "GET",
            "/api/rules/",
            token=self.user1_token
        )

        assert response.status_code == 200
        data = response.get_json()

        assert 'rules' in data
        assert len(data['rules']) == 2

        rule_names = [rule['name'] for rule in data['rules']]

        assert self.rule1.name in rule_names
        assert self.rule2.name in rule_names

    def test_get_rules_unauthorized(self):
        response = make_request(
            self.client,
            "GET",
            "/api/rules/",
        )

        assert response.status_code == 401

    def test_create_rule(self):
        rule_data = {
            'name': 'test rule',
            'boost': 15,
            'conditions': [
                {
                    'field': 'category',
                    'operator': 'equals',
                    'value': 'work'
                },
                {
                    'field': 'created_at',
                    'operator': 'less_than',
                    'value': 'PT5H'
                }
            ]
        }
        response = make_request(
            self.client,
            "POST",
            "/api/rules/",
            token=self.user1_token,
            data=rule_data
        )

        assert response.status_code == 201
        data = response.get_json()

        assert data['name'] == 'test rule'
        assert data['boost'] == 15
        assert len(data['conditions']) == 2

    def test_create_rule_invalid_data(self):
        # without name
        rule_data = {
            'boost': 5,
            'conditions': []
        }

        response = make_request(
            self.client,
            "POST",
            "/api/rules/",
            token=self.user1_token,
            data=rule_data
        )

        assert response.status_code == 422

    def test_get_rule_success(self):
        response = make_request(
            self.client,
            "GET",
            f'/api/rules/{self.rule1.id}',
            token=self.user1_token,
        )

        assert response.status_code == 200
        data = response.get_json()

        assert data['id'] == self.rule1.id
        assert data['name'] == self.rule1.name
        assert data['boost'] == self.rule1.boost

    def test_get_rule_not_found(self):
        response = make_request(
            self.client,
            "GET",
            "/api/rules/999",
            token=self.user1_token,
        )

        assert response.status_code == 404

    def test_get_rule_forbidden(self):
        response = make_request(
            self.client,
            "GET",
            f'/api/rules/{self.rule3.id}',
            token=self.user1_token,

        )

        assert response.status_code == 403

    def test_get_rule_unauthorized(self):
        response = make_request(
            self.client,
            "GET",
            f'/api/rules/{self.rule1.id}',
        )

        assert response.status_code == 401

    def test_update_rule(self):
        update_data = {
            'name': 'updated rule',
            'boost': 25
        }

        response = make_request(
            self.client,
            "PATCH",
            f'/api/rules/{self.rule1.id}',
            token=self.user1_token,
            data=update_data
        )

        assert response.status_code == 200
        data = response.get_json()

        assert data['name'] == 'updated rule'
        assert data['boost'] == 25

    def test_delete_rule(self):
        rule_id = self.rule1.id

        response = make_request(
            self.client,
            "DELETE",
            f'/api/rules/{rule_id}',
            token=self.user1_token,
        )

        assert response.status_code == 204
        assert response.data == b''

        response = make_request(
            self.client,
            "GET",
            f'/api/rules/{rule_id}',
            token=self.user1_token,
        )

        assert response.status_code == 404
