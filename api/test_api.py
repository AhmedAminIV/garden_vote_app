import requests
from unittest.mock import patch

@patch('requests.post')
def test_post(mock_post):
    mock_post.return_value.status_code = 200
    response = requests.post("http://api/api/vote", data={"vote": "a"})
    assert response.status_code == 200

if __name__ == '__main__':
    unittest.main()
