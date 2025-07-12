import pytest
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

@pytest.mark.django_db
@pytest.mark.unit
def test_create_custom_user():
    user = CustomUser.objects.create_user(
        email='test@example.com',
        password='testpassword',
        first_name='John',
        last_name='Doe',
        external_id='auth_id_123'
    )
    assert user.email == 'test@example.com'
    assert user.first_name == 'John'
    assert user.last_name == 'Doe'
    assert user.external_id == 'auth_id_123'
    assert user.is_active
    assert not user.is_staff
    assert not user.is_superuser
    assert user.check_password('testpassword')

@pytest.mark.django_db
@pytest.mark.unit
def test_create_custom_superuser():
    admin_user = CustomUser.objects.create_superuser(
        email='admin@example.com',
        password='adminpassword'
    )
    assert admin_user.email == 'admin@example.com'
    assert admin_user.is_active
    assert admin_user.is_staff
    assert admin_user.is_superuser
    assert admin_user.check_password('adminpassword')

@pytest.mark.django_db
@pytest.mark.unit
def test_create_user_no_email_raises_error():
    with pytest.raises(ValueError, match="The Email must be set"):
        CustomUser.objects.create_user(email=None, password='testpassword')

@pytest.mark.django_db
@pytest.mark.unit
def test_user_full_name():
    user = CustomUser.objects.create_user(
        email='name@example.com',
        password='password',
        first_name='Jane',
        last_name='Smith'
    )
    assert user.full_name == 'Jane Smith'

    user_no_last = CustomUser.objects.create_user(
        email='first@example.com',
        password='password',
        first_name='First'
    )
    assert user_no_last.full_name == 'First'

    user_no_first = CustomUser.objects.create_user(
        email='last@example.com',
        password='password',
        last_name='Last'
    )
    assert user_no_first.full_name == 'Last'

    user_no_name = CustomUser.objects.create_user(
        email='none@example.com',
        password='password'
    )
    assert user_no_name.full_name == ''