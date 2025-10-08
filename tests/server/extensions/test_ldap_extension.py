def test_ldap_manager_success(ldap_manager_instance):
    """LDAP authentication succeeds for a valid user with correct password."""
    manager = ldap_manager_instance
    manager.app.config["LDAP_BIND_DIRECT_CREDENTIALS"] = True

    def mock_direct_bind(username, password):
        return True  # simulate valid credentials

    def mock_authenticate(username, password):
        return None  # not used, but ensures no fallback

    manager._direct_bind = mock_direct_bind
    manager.ldap_manager.authenticate = mock_authenticate

    assert manager.ldap_authorized("testuser", "password123") is True


def test_ldap_manager_wrong_password(ldap_manager_instance):
    """LDAP auth fails when the password is incorrect."""
    manager = ldap_manager_instance
    manager.app.config["LDAP_BIND_DIRECT_CREDENTIALS"] = True

    def mock_direct_bind(username, password):
        return False  # simulate failed direct bind

    def mock_authenticate(username, password):
        return None  # simulate fallback also failing

    manager._direct_bind = mock_direct_bind
    manager.ldap_manager.authenticate = mock_authenticate

    assert manager.ldap_authorized("testuser", "wrongpass") is False


def test_ldap_manager_unknown_user(ldap_manager_instance):
    """LDAP authentication fails for a non-existent user."""
    manager = ldap_manager_instance
    manager.app.config["LDAP_BIND_DIRECT_CREDENTIALS"] = False

    def mock_authenticate(username, password):
        return None  # simulate no LDAP match

    manager.ldap_manager.authenticate = mock_authenticate
    assert manager.ldap_authorized("unknownuser", "password123") is False


def test_ldap_manager_fallback_to_search_bind(ldap_manager_instance):
    """
     Test LDAP authentication fallback behavior.

    Steps simulated:
    1. Direct bind fails (LDAP_BIND_DIRECT_CREDENTIALS=True).
    2. Fallback to search+bind via flask-ldap3-login succeeds.
    3. Group membership check is skipped (LDAP_GROUP_DN=None).

    Asserts that ldap_authorized() ultimately returns True.
    """
    manager = ldap_manager_instance
    manager.app.config["LDAP_BIND_DIRECT_CREDENTIALS"] = True

    # Simulate direct bind failure
    def mock_direct_bind(username, password):
        return False

    # Simulate successful search+bind result
    class FakeResult:
        status = True
        user_dn = "uid=testuser,ou=people,dc=planetexpress,dc=com"

    def mock_authenticate(username, password):
        return FakeResult()

    manager._direct_bind = mock_direct_bind
    manager.ldap_manager.authenticate = mock_authenticate

    # group check will be skipped since LDAP_GROUP_DN is None
    manager.app.config["LDAP_GROUP_DN"] = None

    assert manager.ldap_authorized("testuser", "password123") is True
