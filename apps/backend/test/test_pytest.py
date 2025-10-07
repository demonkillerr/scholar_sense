import pytest
import requests
import os

BASE_URL = "http://localhost:5000"

@pytest.mark.parametrize("file_path", ["tests/sample_paper.pdf"])
def test_upload_and_analyze_file(file_path):
    assert os.path.exists(file_path), f"Test file not found: {file_path}"
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert 'result' in data and 'file_info' in data['result']
    saved_filename = data['result']['file_info']['saved_filename']
    
    payload = {"file_path": saved_filename}
    response = requests.post(f"{BASE_URL}/analyze", json=payload)
    assert response.status_code == 200
    result = response.json().get("result", {})
    assert "document" in result
    assert "sentiment" in result

@pytest.mark.parametrize("filename", ["20250317024808_Optimising_DNNs1.pdf"])
def test_analyze_existing_file(filename):
    payload = {"file_path": filename}
    response = requests.post(f"{BASE_URL}/analyze", json=payload)
    assert response.status_code == 200
    result = response.json().get("result", {})
    assert "document" in result
    assert "sentiment" in result

@pytest.mark.parametrize("topic", ["AI", "climate change", "video games"])
def test_analyze_topic_only(topic):
    payload = {"topic": topic}
    response = requests.post(f"{BASE_URL}/analyse", json=payload)
    assert response.status_code == 200
    result = response.json().get("result", {})
    assert "topic" in result
    assert "sentiment" in result
    assert "keywords" in result