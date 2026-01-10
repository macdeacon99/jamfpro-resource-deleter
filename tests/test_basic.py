import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from jamf_resource_deleter import JamfResourceDeleter
from jamf_resource_deleter.models import OperationStatus


@pytest.fixture
def mock_client():
    return Mock()


@pytest.fixture
def deleter(mock_client, tmp_path):
    return JamfResourceDeleter(mock_client, backup_dir=str(tmp_path))


def test_delete_resource_success(deleter, mock_client):
    # Setup mock
    mock_client.classic.computers.delete_by_id.return_value = True

    # Execute
    result = deleter.delete_resource(
        "unusedComputers", resource_id=123, resource_name="Test Computer"
    )

    # Assert
    assert result.status == OperationStatus.SUCCESS
    assert result.resource_id == 123
    mock_client.classic.computers.delete_by_id.assert_called_once_with(123)
