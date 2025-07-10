"""
Tests for resume parser utilities.
"""

import pytest
from utils.parsers import ResumeParser, ParsedResume, get_resume_parser


class TestResumeParser:
    """Test resume parser functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.parser = ResumeParser()
    
    def test_basic_parsing(self):
        """Test basic resume parsing"""
        sample_resume = """
        John Doe
        Software Engineer
        john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe
        
        PROFESSIONAL SUMMARY
        Experienced software engineer with 5 years of experience in web development.
        
        WORK EXPERIENCE
        Senior Software Engineer at Tech Corp
        January 2020 - Present | San Francisco, CA
        • Developed web applications using Python and React
        • Led team of 3 developers
        • Implemented CI/CD pipelines using Jenkins
        
        Software Developer at StartupCo
        June 2018 - December 2019 | Remote
        • Built REST APIs using Flask and PostgreSQL
        • Collaborated with product team on feature development
        
        EDUCATION
        Bachelor of Science in Computer Science
        University of Technology | 2018
        GPA: 3.8
        
        TECHNICAL SKILLS
        Python, JavaScript, React, Node.js, PostgreSQL, Docker, Git
        
        PROJECTS
        Personal Portfolio Website
        Built responsive portfolio using React and hosted on AWS
        Technologies: React, AWS, Node.js
        
        Open Source Contributions
        Contributed to various Python libraries on GitHub
        """
        
        parsed = self.parser.parse_resume(sample_resume)
        
        # Test contact info
        assert parsed.contact_info.email == "john.doe@email.com"
        assert parsed.contact_info.phone == "(555) 123-4567"
        assert parsed.contact_info.linkedin == "linkedin.com/in/johndoe"
        
        # Test summary
        assert parsed.summary is not None
        assert "5 years of experience" in parsed.summary
        
        # Test work experience
        assert len(parsed.work_experience) == 2
        
        first_job = parsed.work_experience[0]
        assert first_job.company == "Tech Corp"
        assert first_job.position == "Senior Software Engineer"
        assert first_job.start_date == "January 2020"
        assert first_job.end_date == "Present"
        assert "Python" in first_job.technologies
        assert "React" in first_job.technologies
        
        # Test education
        assert len(parsed.education) == 1
        education = parsed.education[0]
        assert education.degree == "Bachelor of Science in Computer Science"
        assert education.institution == "University of Technology"
        assert education.graduation_date == "2018"
        assert education.gpa == "3.8"
        
        # Test skills
        assert "Python" in parsed.skills
        assert "JavaScript" in parsed.skills
        assert "React" in parsed.skills
        
        # Test projects
        assert len(parsed.projects) >= 1
        project = parsed.projects[0]
        assert "Portfolio" in project.name
        assert "React" in project.technologies
    
    def test_contact_info_extraction(self):
        """Test contact information extraction"""
        test_cases = [
            {
                'text': 'Contact: john.smith@company.com',
                'expected_email': 'john.smith@company.com'
            },
            {
                'text': 'Phone: (555) 123-4567',
                'expected_phone': '(555) 123-4567'
            },
            {
                'text': 'LinkedIn: linkedin.com/in/john-smith',
                'expected_linkedin': 'linkedin.com/in/john-smith'
            },
            {
                'text': 'GitHub: github.com/johnsmith',
                'expected_github': 'github.com/johnsmith'
            }
        ]
        
        for case in test_cases:
            contact = self.parser._extract_contact_info(case['text'])
            
            if 'expected_email' in case:
                assert contact.email == case['expected_email']
            if 'expected_phone' in case:
                assert contact.phone == case['expected_phone']
            if 'expected_linkedin' in case:
                assert contact.linkedin == case['expected_linkedin']
            if 'expected_github' in case:
                assert contact.github == case['expected_github']
    
    def test_section_detection(self):
        """Test resume section detection"""
        sample_text = """
        Header Information
        
        PROFESSIONAL SUMMARY
        This is the summary section.
        
        WORK EXPERIENCE
        This is the experience section.
        
        EDUCATION
        This is the education section.
        
        SKILLS
        This is the skills section.
        """
        
        sections = self.parser._extract_sections(sample_text)
        
        assert 'summary' in sections
        assert 'experience' in sections
        assert 'education' in sections
        assert 'skills' in sections
        
        assert "summary section" in sections['summary']
        assert "experience section" in sections['experience']
    
    def test_work_experience_parsing(self):
        """Test work experience parsing"""
        experience_text = """
        Senior Developer at TechCorp
        January 2020 - Present
        • Developed web applications
        • Led development team
        • Technologies: Python, React, PostgreSQL
        
        Junior Developer at StartupCo
        June 2018 - December 2019
        • Built REST APIs
        • Worked with product team
        """
        
        experiences = self.parser._extract_work_experience(experience_text)
        
        assert len(experiences) >= 1
        
        first_exp = experiences[0]
        assert "TechCorp" in first_exp.company or "Senior Developer" in first_exp.position
        assert any(tech in ["Python", "React", "PostgreSQL"] for tech in first_exp.technologies)
    
    def test_education_parsing(self):
        """Test education parsing"""
        education_text = """
        Bachelor of Science in Computer Science
        University of Technology
        Graduated: 2018
        GPA: 3.8
        
        Master of Business Administration
        Business School
        2020
        """
        
        education_list = self.parser._extract_education(education_text)
        
        assert len(education_list) >= 1
        
        # Check first education entry
        first_edu = education_list[0]
        assert "Bachelor" in first_edu.degree or "Computer Science" in str(first_edu.field_of_study)
    
    def test_skills_extraction(self):
        """Test skills extraction"""
        skills_text = "Python, JavaScript, React, Node.js, PostgreSQL, Docker"
        full_text = "I have experience with Python and React development."
        
        skills = self.parser._extract_skills(skills_text, full_text)
        
        assert "Python" in skills
        assert "JavaScript" in skills
        assert "React" in skills
    
    def test_technology_pattern_matching(self):
        """Test technology pattern matching"""
        sample_text = """
        I have experience with Python, JavaScript, React, and Node.js.
        I've worked with PostgreSQL databases and Docker containers.
        Cloud experience includes AWS and Azure.
        """
        
        matches = self.parser.tech_pattern.findall(sample_text)
        
        assert "Python" in matches
        assert "JavaScript" in matches
        assert "React" in matches
        assert "PostgreSQL" in matches
        assert "Docker" in matches
        assert "AWS" in matches
    
    def test_empty_resume_handling(self):
        """Test handling of empty or invalid resume"""
        with pytest.raises(ValueError, match="Resume text cannot be empty"):
            self.parser.parse_resume("")
        
        with pytest.raises(ValueError, match="Resume text cannot be empty"):
            self.parser.parse_resume("   ")
    
    def test_minimal_resume(self):
        """Test parsing of minimal resume"""
        minimal_resume = """
        Jane Smith
        jane@email.com
        
        Software Engineer with experience in web development.
        """
        
        parsed = self.parser.parse_resume(minimal_resume)
        
        assert parsed.contact_info.email == "jane@email.com"
        assert parsed.raw_text == minimal_resume
    
    def test_section_header_detection(self):
        """Test section header detection"""
        test_cases = [
            ("EXPERIENCE", "experience"),
            ("Work Experience", "experience"),
            ("Professional Experience:", "experience"),
            ("EDUCATION", "education"),
            ("Educational Background", "education"),
            ("SKILLS", "skills"),
            ("Technical Skills", "skills"),
            ("SUMMARY", "summary"),
            ("Professional Summary", "summary"),
            ("Not a header - this is too long to be a section header", None),
            ("Regular text", None)
        ]
        
        for header_text, expected_section in test_cases:
            result = self.parser._detect_section_header(header_text)
            assert result == expected_section
    
    def test_projects_extraction(self):
        """Test project extraction"""
        projects_text = """
        Personal Portfolio Website
        Built a responsive portfolio using React and Node.js
        URL: https://example.com
        
        E-commerce Platform
        Developed full-stack application with payment integration
        Technologies: Python, Django, PostgreSQL
        """
        
        projects = self.parser._extract_projects(projects_text)
        
        assert len(projects) >= 1
        
        first_project = projects[0]
        assert "Portfolio" in first_project.name
        assert "React" in first_project.technologies or "Node.js" in first_project.technologies
    
    def test_parser_singleton(self):
        """Test parser singleton pattern"""
        parser1 = get_resume_parser()
        parser2 = get_resume_parser()
        assert parser1 is parser2


class TestIntegration:
    """Integration tests for resume parsing"""
    
    def test_full_resume_parsing_workflow(self):
        """Test complete resume parsing workflow"""
        full_resume = """
        ALEX JOHNSON
        Senior Full-Stack Developer
        
        📧 alex.johnson@techmail.com | 📱 (555) 987-6543
        🔗 linkedin.com/in/alexjohnson | 💻 github.com/alexjohnson
        📍 San Francisco, CA
        
        PROFESSIONAL SUMMARY
        Passionate full-stack developer with 7+ years of experience building scalable web applications.
        Expert in modern JavaScript frameworks and cloud technologies.
        
        WORK EXPERIENCE
        
        Senior Full-Stack Developer | TechStartup Inc.
        March 2021 - Present | San Francisco, CA
        • Architected and developed microservices using Node.js and Docker
        • Led frontend development using React and TypeScript
        • Implemented CI/CD pipelines reducing deployment time by 60%
        • Mentored 2 junior developers and conducted code reviews
        • Technologies: React, Node.js, TypeScript, PostgreSQL, Docker, AWS
        
        Full-Stack Developer | WebSolutions LLC
        June 2019 - February 2021 | Remote
        • Built responsive web applications serving 100k+ users
        • Developed REST APIs using Express.js and MongoDB
        • Integrated third-party payment systems (Stripe, PayPal)
        • Technologies: JavaScript, React, Express.js, MongoDB, Redis
        
        Junior Developer | LocalTech Company
        January 2017 - May 2019 | Oakland, CA
        • Maintained legacy PHP applications
        • Migrated database from MySQL to PostgreSQL
        • Collaborated with design team on UI/UX improvements
        
        EDUCATION
        
        Master of Science in Computer Science
        Stanford University | 2016
        Specialization: Software Engineering
        GPA: 3.9/4.0
        
        Bachelor of Science in Computer Science
        UC Berkeley | 2014
        Magna Cum Laude
        
        TECHNICAL SKILLS
        
        Frontend: React, Vue.js, Angular, TypeScript, HTML5, CSS3, Sass
        Backend: Node.js, Python, Java, PHP, Express.js, Django, Spring Boot
        Databases: PostgreSQL, MongoDB, MySQL, Redis, DynamoDB
        Cloud & DevOps: AWS, Docker, Kubernetes, Jenkins, GitHub Actions
        Tools: Git, Webpack, Jest, Cypress, Postman, Figma
        
        PROJECTS
        
        TaskManager Pro
        Full-stack project management application with real-time collaboration
        • Built with React, Node.js, Socket.io, and PostgreSQL
        • Implemented JWT authentication and role-based access control
        • Deployed on AWS with auto-scaling groups
        URL: https://taskmanager-pro.herokuapp.com
        
        Open Source Contributions
        Active contributor to React ecosystem libraries
        • Contributed to React Router with 50+ GitHub stars
        • Maintained personal utility library with 200+ downloads/month
        
        CERTIFICATIONS
        AWS Certified Solutions Architect - Associate (2022)
        Google Cloud Professional Developer (2021)
        
        LANGUAGES
        English (Native)
        Spanish (Conversational)
        French (Basic)
        """
        
        parser = ResumeParser()
        parsed = parser.parse_resume(full_resume)
        
        # Verify comprehensive parsing
        assert parsed.contact_info.email == "alex.johnson@techmail.com"
        assert parsed.contact_info.phone == "(555) 987-6543"
        assert parsed.contact_info.linkedin == "linkedin.com/in/alexjohnson"
        assert parsed.contact_info.github == "github.com/alexjohnson"
        
        assert "7+ years of experience" in parsed.summary
        
        assert len(parsed.work_experience) >= 2
        assert len(parsed.education) >= 2
        assert len(parsed.skills) >= 10
        assert len(parsed.projects) >= 1
        assert len(parsed.certifications) >= 1
        assert len(parsed.languages) >= 2
        
        # Check specific data
        senior_role = next((exp for exp in parsed.work_experience if "Senior" in exp.position), None)
        if senior_role:
            assert "TechStartup" in senior_role.company or "Senior" in senior_role.position
            assert "React" in senior_role.technologies
            assert "Node.js" in senior_role.technologies
        
        masters_degree = next((edu for edu in parsed.education if "Master" in edu.degree), None)
        if masters_degree:
            assert "Stanford" in masters_degree.institution
        
        assert "React" in parsed.skills
        assert "Node.js" in parsed.skills
        assert "AWS" in parsed.skills


if __name__ == "__main__":
    # Simple test runner for development
    import sys
    
    print("Running resume parser tests...")
    
    try:
        parser = ResumeParser()
        print("✓ ResumeParser initialization: PASS")
        
        # Test basic contact extraction
        contact = parser._extract_contact_info("john@example.com | (555) 123-4567")
        assert contact.email == "john@example.com"
        assert "555" in contact.phone and "123-4567" in contact.phone
        print("✓ Contact info extraction: PASS")
        
        # Test section detection
        sections = parser._extract_sections("SUMMARY\nThis is summary\nEXPERIENCE\nThis is experience")
        assert 'summary' in sections
        assert 'experience' in sections
        print("✓ Section detection: PASS")
        
        # Test technology extraction
        matches = parser.tech_pattern.findall("I use Python, React, and AWS")
        assert "Python" in matches
        assert "React" in matches
        assert "AWS" in matches
        print("✓ Technology pattern matching: PASS")
        
        # Test full parsing
        sample = """
        John Doe
        john@email.com
        
        SUMMARY
        Software engineer with Python experience.
        
        EXPERIENCE
        Developer at TechCorp
        2020-2023
        """
        
        parsed = parser.parse_resume(sample)
        assert parsed.contact_info.email == "john@email.com"
        # Summary might be None if too short, check sections instead
        assert 'summary' in parsed.sections
        print("✓ Full resume parsing: PASS")
        
        # Test singleton
        parser1 = get_resume_parser()
        parser2 = get_resume_parser()
        assert parser1 is parser2
        print("✓ Parser singleton: PASS")
        
        print("\n✅ All resume parser tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)