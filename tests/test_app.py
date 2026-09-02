from app import create_app, db
from app.models import Category


def test_registration_login_and_transaction_flow():
    app = create_app('testing')
    client = app.test_client()
    assert client.post('/auth/register', data={'name': 'Test User', 'email': 'test@example.com', 'password': 'securepass123', 'confirm_password': 'securepass123'}).status_code == 302
    assert client.post('/auth/login', data={'email': 'test@example.com', 'password': 'securepass123'}).status_code == 302
    with app.app_context():
        salary = db.session.query(Category).filter_by(name='Salary', type='income').first()
        assert salary is not None
    response = client.post('/transactions/add', data={'type': 'income', 'amount': '1000', 'category_id': salary.id, 'description': 'Pay', 'date': '2026-09-02', 'payment_method': 'Cash', 'notes': ''})
    assert response.status_code == 302
    assert client.get('/dashboard').status_code == 200
    assert client.get('/reports/export.csv').status_code == 200


def test_protected_routes_redirect():
    app = create_app('testing')
    client = app.test_client()
    assert client.get('/transactions/').status_code == 302
    assert client.get('/budgets/').status_code == 302


def test_savings_goals_and_user_isolation():
    app = create_app('testing')
    first = app.test_client()
    second = app.test_client()
    first.post('/auth/register', data={'name': 'First User', 'email': 'first@example.com', 'password': 'securepass123', 'confirm_password': 'securepass123'})
    first.post('/auth/login', data={'email': 'first@example.com', 'password': 'securepass123'})
    response = first.post('/savings-goals/add', data={'name': 'New Laptop', 'target_amount': '200000', 'current_amount': '75000', 'deadline': '2027-01-01'})
    assert response.status_code == 302
    with app.app_context():
        from app.models import SavingsGoal
        goal = db.session.query(SavingsGoal).one()
        goal_id = goal.id
        assert goal.progress_percent == 37.5
    first.post(f'/savings-goals/{goal_id}/add-money', data={'amount': '25000'})
    with app.app_context():
        assert db.session.get(SavingsGoal, goal_id).current_amount == 100000
    second.post('/auth/register', data={'name': 'Second User', 'email': 'second@example.com', 'password': 'securepass123', 'confirm_password': 'securepass123'})
    second.post('/auth/login', data={'email': 'second@example.com', 'password': 'securepass123'})
    assert second.get('/savings-goals/').status_code == 200
    assert second.post(f'/savings-goals/{goal_id}/delete').status_code == 404
    assert b'New Laptop' not in second.get('/reports/').data
