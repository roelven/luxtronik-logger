import pytest
import json
import sqlite3
from datetime import datetime, timedelta
from unittest.mock import patch, call
from src.storage import DataStorage

class TestDataStorage:
    def test_add_to_buffer(self):
        storage = DataStorage(":memory:")
        test_data = {"temp": 45.0, "pressure": 2.1}
        
        storage.add(datetime.now(), test_data)
        assert len(storage.buffer) == 1
        assert storage.buffer[0]["data"] == test_data
    
    @patch("sqlite3.connect")
    def test_flush(self, mock_connect):
        mock_conn = mock_connect.return_value.__enter__.return_value
        storage = DataStorage(":memory:")
        
        test_time = datetime.now()
        test_data = {"temp": 45.0}
        storage.add(test_time, test_data)
        
        storage.flush()
        assert len(storage.buffer) == 0
        
        # Check the INSERT call specifically
        insert_calls = [call for call in mock_conn.execute.mock_calls 
                      if call[1][0].startswith("INSERT")]
        assert len(insert_calls) == 1
    
    @patch("sqlite3.connect")
    def test_query(self, mock_connect):
        mock_conn = mock_connect.return_value.__enter__.return_value
        mock_cursor = mock_conn.execute.return_value
        
        test_time = datetime.now().timestamp()
        test_data = {"temp": 45.0}
        mock_cursor.fetchall.return_value = [(test_time, json.dumps(test_data))]
        
        storage = DataStorage(":memory:")
        results = storage.query(datetime.now() - timedelta(hours=1), datetime.now())
        
        # Verify the query was made with correct parameters
        query_calls = [c for c in mock_conn.execute.mock_calls 
                     if len(c[1]) > 0 and c[1][0].startswith("SELECT")]
        assert len(query_calls) == 1
        
        # Mock should return our test data
        assert len(results) == 1
        assert results[0]["data"] == test_data
    
    @patch("sqlite3.connect")
    def test_init_db(self, mock_connect):
        mock_conn = mock_connect.return_value.__enter__.return_value
        
        storage = DataStorage(":memory:")
        
        # Verify CREATE TABLE was called
        create_table_calls = [call for call in mock_conn.execute.mock_calls 
                           if call[1][0].strip().startswith("CREATE TABLE")]
        assert len(create_table_calls) == 1