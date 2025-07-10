"""
Tests for file upload service and endpoints.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Mock configuration before importing file service
with patch('services.file_service.get_config') as mock_config:
    mock_security = MagicMock()
    mock_security.max_file_size = 10 * 1024 * 1024  # 10MB
    mock_config.return_value.security = mock_security
    
    from services.file_service import (
        FileService,
        FileValidationError,
        FileProcessingError,
        get_file_service
    )


class TestFileService:
    """Test file service functionality"""
    
    @patch('services.file_service.get_config')
    def setup_method(self, mock_config):
        """Setup test environment"""
        # Mock configuration to avoid needing actual config file
        mock_security = MagicMock()
        mock_security.max_file_size = 10 * 1024 * 1024  # 10MB
        mock_config.return_value.security = mock_security
        self.file_service = FileService()
    
    def test_validate_file_size_limit(self):
        """Test file size validation"""
        # Test empty file
        with pytest.raises(FileValidationError, match="Empty file not allowed"):
            self.file_service.validate_file(b"", "test.txt", "text/plain")
        
        # Test oversized file
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        with pytest.raises(FileValidationError, match="File size exceeds limit"):
            self.file_service.validate_file(large_content, "large.txt", "text/plain")
    
    def test_validate_filename(self):
        """Test filename validation"""
        content = b"test content"
        
        # Test empty filename
        with pytest.raises(FileValidationError, match="Invalid filename"):
            self.file_service.validate_file(content, "", "text/plain")
        
        # Test long filename
        long_name = "x" * 300 + ".txt"
        with pytest.raises(FileValidationError, match="Invalid filename"):
            self.file_service.validate_file(content, long_name, "text/plain")
    
    def test_validate_file_extension(self):
        """Test file extension validation"""
        content = b"test content"
        
        # Test invalid extension
        with pytest.raises(FileValidationError, match="Unsupported file extension"):
            self.file_service.validate_file(content, "test.exe", "application/octet-stream")
        
        # Test valid extensions
        valid_files = [
            ("test.pdf", "application/pdf"),
            ("test.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
            ("test.txt", "text/plain")
        ]
        
        # Note: These will fail full validation due to content, but should pass extension check
        for filename, content_type in valid_files:
            try:
                self.file_service.validate_file(content, filename, content_type)
            except FileValidationError as e:
                # Should fail on content validation, not extension
                assert "Unsupported file extension" not in str(e)
    
    def test_security_scan(self):
        """Test security scanning"""
        # Test dangerous patterns
        dangerous_contents = [
            b"<script>alert('xss')</script>",
            b"javascript:void(0)",
            b"#!/bin/bash\nrm -rf /",
            b"<?php system($_GET['cmd']); ?>"
        ]
        
        for content in dangerous_contents:
            with pytest.raises(FileValidationError, match="Suspicious content detected"):
                self.file_service.validate_file(content, "test.txt", "text/plain")
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        test_cases = [
            ("normal_file.txt", "normal_file.txt"),
            ("file with spaces.txt", "file with spaces.txt"),
            ("file<>:\"/\\|?*.txt", "file_________.txt"),
            ("very_long_filename_" + "x" * 100 + ".txt", "very_long_filename_" + "x" * 73 + ".txt")
        ]
        
        for input_name, expected in test_cases:
            result = self.file_service._sanitize_filename(input_name)
            assert result == expected
    
    def test_detect_resume_sections(self):
        """Test resume section detection"""
        sample_resume = """
        John Doe
        Software Engineer
        john.doe@email.com
        
        PROFESSIONAL SUMMARY
        Experienced software engineer with 5 years of experience.
        
        WORK EXPERIENCE
        Senior Developer at Tech Corp (2020-2023)
        - Developed web applications
        - Led team of 3 developers
        
        EDUCATION
        BS Computer Science, University of Tech (2018)
        
        TECHNICAL SKILLS
        Python, JavaScript, React, Node.js
        
        PROJECTS
        Personal portfolio website
        Open source contributions
        """
        
        sections = self.file_service._detect_resume_sections(sample_resume)
        
        assert 'experience' in sections
        assert 'education' in sections
        assert 'skills' in sections
        assert 'summary' in sections
        assert 'projects' in sections
        
        # Check content
        assert 'Tech Corp' in sections['experience']
        assert 'Computer Science' in sections['education']
        assert 'Python' in sections['skills']
    
    def test_validate_text_file(self):
        """Test text file validation"""
        # Mock the magic detection to use mimetypes fallback
        with patch('services.file_service.MAGIC_AVAILABLE', False):
            # Valid text content
            valid_text = b"This is a valid resume with enough content to pass validation."
            result = self.file_service.validate_file(valid_text, "resume.txt", "text/plain")
            assert result == "txt"
            
            # Invalid text (too short)
            short_text = b"short"
            with pytest.raises(FileValidationError, match="appears to be empty or too short"):
                self.file_service.validate_file(short_text, "short.txt", "text/plain")
    
    def test_save_file_success(self):
        """Test successful file saving"""
        content = b"This is a test resume with sufficient content for validation."
        filename = "test_resume.txt"
        content_type = "text/plain"
        
        with patch('services.file_service.MAGIC_AVAILABLE', False):
            file_info = self.file_service.save_file(content, filename, content_type)
            
            assert file_info.file_id.startswith("file_")
            assert file_info.original_filename == filename
            assert file_info.file_size == len(content)
            assert file_info.content_type == content_type
            assert file_info.file_format == "txt"
            assert file_info.temp_path.exists()
            
            # Cleanup
            self.file_service.cleanup_file(file_info)
    
    def test_cleanup_file(self):
        """Test file cleanup"""
        content = b"Test content for cleanup validation and file management testing."
        
        with patch('services.file_service.MAGIC_AVAILABLE', False):
            file_info = self.file_service.save_file(content, "cleanup_test.txt", "text/plain")
            
            # File should exist
            assert file_info.temp_path.exists()
            
            # Cleanup should succeed
            success = self.file_service.cleanup_file(file_info)
            assert success is True
            
            # File should not exist
            assert not file_info.temp_path.exists()
    
    def test_extract_text_content(self):
        """Test text extraction from text file"""
        content = b"Sample resume content with various sections and information."
        
        with patch('services.file_service.MAGIC_AVAILABLE', False):
            file_info = self.file_service.save_file(content, "extract_test.txt", "text/plain")
            
            try:
                extracted = self.file_service.extract_text(file_info)
                
                assert extracted.text == content.decode('utf-8')
                assert extracted.word_count == len(content.decode('utf-8').split())
                assert extracted.extraction_method == "text"
                assert 'encoding' in extracted.metadata
                
            finally:
                self.file_service.cleanup_file(file_info)
    
    def test_file_service_singleton(self):
        """Test file service singleton pattern"""
        service1 = get_file_service()
        service2 = get_file_service()
        assert service1 is service2


class TestFileUploadEndpoints:
    """Test file upload API endpoints"""
    
    def test_supported_formats_endpoint(self):
        """Test supported formats endpoint"""
        from api.files import get_supported_formats
        
        # This is an async function, but we can test the structure
        import asyncio
        result = asyncio.run(get_supported_formats())
        
        assert 'supported_formats' in result
        assert 'pdf' in result['supported_formats']
        assert 'docx' in result['supported_formats']
        assert 'txt' in result['supported_formats']
        assert 'limitations' in result
        assert 'security_features' in result


class TestFileValidation:
    """Test file validation scenarios"""
    
    def test_pdf_validation_structure(self):
        """Test PDF structure validation"""
        file_service = FileService()
        
        # Invalid PDF content
        fake_pdf = b"Not a real PDF file content"
        with pytest.raises(FileValidationError, match="PDF validation failed"):
            file_service._validate_pdf(fake_pdf)
    
    def test_docx_validation_structure(self):
        """Test DOCX structure validation"""
        file_service = FileService()
        
        # Invalid DOCX content
        fake_docx = b"Not a real DOCX file content"
        with pytest.raises(FileValidationError, match="DOCX validation failed"):
            file_service._validate_docx(fake_docx)
    
    def test_text_encoding_detection(self):
        """Test text encoding detection"""
        file_service = FileService()
        
        # Valid UTF-8 text
        utf8_text = "Hello world! This is a test résumé with unicode characters.".encode('utf-8')
        file_service._validate_text(utf8_text)  # Should not raise
        
        # Invalid text (binary data)
        binary_data = b"\x00\x01\x02\x03This is not valid text"
        with pytest.raises(FileValidationError, match="contains binary data"):
            file_service._validate_text(binary_data)


class TestFileCleanup:
    """Test file cleanup functionality"""
    
    def test_cleanup_old_files(self):
        """Test cleanup of old files"""
        file_service = FileService()
        
        # Create test file in temp directory
        test_file = file_service.temp_dir / "file_test_old_file.txt"
        test_file.write_text("test content")
        
        # Set old modification time
        old_time = os.path.getctime(test_file) - (25 * 3600)  # 25 hours ago
        os.utime(test_file, (old_time, old_time))
        
        # Cleanup should remove the file
        cleaned_count = file_service.cleanup_old_files(max_age_hours=24)
        
        assert cleaned_count >= 1
        assert not test_file.exists()


if __name__ == "__main__":
    # Simple test runner for development
    import sys
    
    print("Running file service tests...")
    
    try:
        # Mock configuration for test runner
        with patch('services.file_service.get_config') as mock_config:
            mock_security = MagicMock()
            mock_security.max_file_size = 10 * 1024 * 1024  # 10MB
            mock_config.return_value.security = mock_security
            
            # Test file service initialization
            file_service = FileService()
            print("✓ FileService initialization: PASS")
            
            # Test filename sanitization
            sanitized = file_service._sanitize_filename("test<>file.txt")
            assert sanitized == "test__file.txt"
            print("✓ Filename sanitization: PASS")
            
            # Test section detection
            sample_text = "EXPERIENCE\nSoftware Engineer\nEDUCATION\nComputer Science"
            sections = file_service._detect_resume_sections(sample_text)
            assert 'experience' in sections
            assert 'education' in sections
            print("✓ Resume section detection: PASS")
            
            # Test singleton pattern
            service1 = get_file_service()
            service2 = get_file_service()
            assert service1 is service2
            print("✓ Singleton pattern: PASS")
            
            # Test supported formats endpoint
            import asyncio
            from api.files import get_supported_formats
            result = asyncio.run(get_supported_formats())
            assert 'supported_formats' in result
            print("✓ Supported formats endpoint: PASS")
        
        print("\n✅ All file service tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)