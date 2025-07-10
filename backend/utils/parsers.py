"""
Resume Parser Utilities

Advanced text extraction and analysis for resume files.
Provides structured parsing, section detection, and content analysis.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ContactInfo:
    """Contact information extracted from resume"""
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None

@dataclass
class WorkExperience:
    """Work experience entry"""
    company: str
    position: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[str] = None
    description: List[str] = None
    technologies: List[str] = None
    
    def __post_init__(self):
        if self.description is None:
            self.description = []
        if self.technologies is None:
            self.technologies = []

@dataclass
class Education:
    """Education entry"""
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    graduation_date: Optional[str] = None
    gpa: Optional[str] = None
    location: Optional[str] = None

@dataclass
class Project:
    """Project entry"""
    name: str
    description: str
    technologies: List[str] = None
    url: Optional[str] = None
    
    def __post_init__(self):
        if self.technologies is None:
            self.technologies = []

@dataclass
class ParsedResume:
    """Complete parsed resume structure"""
    raw_text: str
    contact_info: ContactInfo
    summary: Optional[str] = None
    work_experience: List[WorkExperience] = None
    education: List[Education] = None
    skills: List[str] = None
    projects: List[Project] = None
    certifications: List[str] = None
    languages: List[str] = None
    sections: Dict[str, str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.work_experience is None:
            self.work_experience = []
        if self.education is None:
            self.education = []
        if self.skills is None:
            self.skills = []
        if self.projects is None:
            self.projects = []
        if self.certifications is None:
            self.certifications = []
        if self.languages is None:
            self.languages = []
        if self.sections is None:
            self.sections = {}
        if self.metadata is None:
            self.metadata = {}


class ResumeParser:
    """Advanced resume parser with structured data extraction"""
    
    # Common section headers
    SECTION_PATTERNS = {
        'contact': [
            r'contact\s+information?',
            r'personal\s+information?',
            r'contact\s+details?'
        ],
        'summary': [
            r'(?:professional\s+)?summary',
            r'(?:professional\s+)?profile',
            r'objective',
            r'about\s+me',
            r'overview',
            r'career\s+summary'
        ],
        'experience': [
            r'(?:work\s+|professional\s+|employment\s+)?experience',
            r'work\s+history',
            r'career\s+history',
            r'professional\s+background',
            r'employment'
        ],
        'education': [
            r'education(?:al\s+background)?',
            r'academic\s+background',
            r'qualifications?',
            r'degrees?',
            r'university',
            r'college'
        ],
        'skills': [
            r'(?:technical\s+)?skills?',
            r'core\s+competencies',
            r'expertise',
            r'proficiencies',
            r'technologies',
            r'programming\s+languages?'
        ],
        'projects': [
            r'projects?',
            r'personal\s+projects?',
            r'portfolio',
            r'achievements?',
            r'accomplishments?'
        ],
        'certifications': [
            r'certifications?',
            r'certificates?',
            r'licenses?',
            r'credentials?'
        ],
        'languages': [
            r'languages?',
            r'language\s+skills?',
            r'linguistic\s+skills?'
        ]
    }
    
    # Common technology patterns
    TECH_PATTERNS = [
        # Programming languages
        r'\b(?:Python|Java|JavaScript|TypeScript|C\+\+|C#|PHP|Ruby|Go|Rust|Swift|Kotlin|Scala|R|MATLAB|Perl)\b',
        # Web technologies
        r'\b(?:React|Angular|Vue\.js|Node\.js|Express|Django|Flask|Laravel|Spring|ASP\.NET)\b',
        # Databases
        r'\b(?:MySQL|PostgreSQL|MongoDB|Redis|SQLite|Oracle|SQL\s+Server|Cassandra|DynamoDB)\b',
        # Cloud/DevOps
        r'\b(?:AWS|Azure|Google\s+Cloud|Docker|Kubernetes|Jenkins|Git|GitHub|GitLab|CI/CD)\b',
        # Data/ML
        r'\b(?:TensorFlow|PyTorch|Scikit-learn|Pandas|NumPy|Apache\s+Spark|Hadoop|Tableau)\b'
    ]
    
    def __init__(self):
        """Initialize the resume parser"""
        self.tech_pattern = re.compile('|'.join(self.TECH_PATTERNS), re.IGNORECASE)
    
    def parse_resume(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> ParsedResume:
        """
        Parse resume text into structured data.
        
        Args:
            text: Raw resume text
            metadata: Optional metadata from file extraction
            
        Returns:
            ParsedResume object with structured data
        """
        if not text or not text.strip():
            raise ValueError("Resume text cannot be empty")
        
        # Clean and normalize text
        cleaned_text = self._clean_text(text)
        
        # Extract sections
        sections = self._extract_sections(cleaned_text)
        
        # Parse structured data
        contact_info = self._extract_contact_info(cleaned_text)
        summary = self._extract_summary(sections.get('summary', ''))
        work_experience = self._extract_work_experience(sections.get('experience', ''))
        education = self._extract_education(sections.get('education', ''))
        skills = self._extract_skills(sections.get('skills', ''), cleaned_text)
        projects = self._extract_projects(sections.get('projects', ''))
        certifications = self._extract_certifications(sections.get('certifications', ''))
        languages = self._extract_languages(sections.get('languages', ''))
        
        return ParsedResume(
            raw_text=text,
            contact_info=contact_info,
            summary=summary,
            work_experience=work_experience,
            education=education,
            skills=skills,
            projects=projects,
            certifications=certifications,
            languages=languages,
            sections=sections,
            metadata=metadata or {}
        )
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Normalize line breaks first
        text = re.sub(r'\r\n?', '\n', text)
        
        # Remove common resume artifacts
        text = re.sub(r'(?:page\s+\d+(?:\s+of\s+\d+)?)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'(?:confidential|proprietary)', '', text, flags=re.IGNORECASE)
        
        # Clean up excessive whitespace within lines (but preserve line breaks)
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            # Remove excessive whitespace within the line
            cleaned_line = re.sub(r'\s+', ' ', line.strip())
            cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines).strip()
    
    def _extract_sections(self, text: str) -> Dict[str, str]:
        """Extract major resume sections"""
        sections = {}
        lines = text.split('\n')
        current_section = 'header'
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a section header
            detected_section = self._detect_section_header(line)
            
            if detected_section:
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = detected_section
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _detect_section_header(self, line: str) -> Optional[str]:
        """Detect if a line is a section header"""
        line_lower = line.lower().strip()
        
        # Skip very long lines (likely not headers)
        if len(line) > 100:
            return None
        
        # Check each section pattern
        for section_name, patterns in self.SECTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(f'^{pattern}s?:?$', line_lower):
                    return section_name
                # Also check if pattern is at start or end of line
                if re.search(f'^{pattern}', line_lower) or re.search(f'{pattern}$', line_lower):
                    # Additional validation: ensure line is relatively short and contains the keyword prominently
                    if len(line.strip()) < 50 and any(keyword in line_lower for keyword in pattern.split()):
                        return section_name
        
        return None
    
    def _extract_contact_info(self, text: str) -> ContactInfo:
        """Extract contact information"""
        contact = ContactInfo()
        
        # Email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if email_match:
            contact.email = email_match.group()
        
        # Phone (various formats)
        phone_patterns = [
            r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
            r'\b(?:\+?1[-.\s]?)?([0-9]{3})[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
        ]
        for pattern in phone_patterns:
            phone_match = re.search(pattern, text)
            if phone_match:
                contact.phone = phone_match.group()
                break
        
        # LinkedIn
        linkedin_match = re.search(r'(?:linkedin\.com/in/|linkedin\.com/pub/)([A-Za-z0-9_-]+)', text, re.IGNORECASE)
        if linkedin_match:
            contact.linkedin = f"linkedin.com/in/{linkedin_match.group(1)}"
        
        # GitHub
        github_match = re.search(r'(?:github\.com/)([A-Za-z0-9_-]+)', text, re.IGNORECASE)
        if github_match:
            contact.github = f"github.com/{github_match.group(1)}"
        
        # Website/Portfolio
        website_match = re.search(r'https?://(?:www\.)?([A-Za-z0-9.-]+\.[A-Za-z]{2,})', text)
        if website_match and 'linkedin' not in website_match.group().lower() and 'github' not in website_match.group().lower():
            contact.website = website_match.group()
        
        return contact
    
    def _extract_summary(self, summary_text: str) -> Optional[str]:
        """Extract and clean professional summary"""
        if not summary_text:
            return None
        
        # Clean up the summary
        summary = re.sub(r'\s+', ' ', summary_text).strip()
        
        # Remove section headers if they got included
        summary = re.sub(r'^(?:professional\s+)?(?:summary|profile|objective)[:.]?\s*', '', summary, flags=re.IGNORECASE)
        
        # Return if has substantial content
        if len(summary) > 20:
            return summary
        
        return None
    
    def _extract_work_experience(self, experience_text: str) -> List[WorkExperience]:
        """Extract work experience entries"""
        if not experience_text:
            return []
        
        experiences = []
        
        # Split into potential entries (look for company/position patterns)
        entries = self._split_experience_entries(experience_text)
        
        for entry in entries:
            exp = self._parse_experience_entry(entry)
            if exp:
                experiences.append(exp)
        
        return experiences
    
    def _split_experience_entries(self, text: str) -> List[str]:
        """Split experience text into individual entries"""
        # Look for common patterns that indicate new entries
        entry_patterns = [
            r'\n(?=[A-Z][A-Za-z\s,&]+(?:Inc|LLC|Corp|Company|Corporation|Ltd|Group|Technologies|Solutions|Systems|Software|Services))',
            r'\n(?=[A-Z][A-Za-z\s]+\s+(?:at|@)\s+[A-Z][A-Za-z\s]+)',
            r'\n(?=(?:Senior|Junior|Lead|Principal|Staff|Associate|Assistant)?\s*[A-Z][A-Za-z\s]+(?:Engineer|Developer|Manager|Analyst|Specialist|Consultant|Director))'
        ]
        
        # Try to split by patterns
        for pattern in entry_patterns:
            splits = re.split(pattern, text)
            if len(splits) > 1:
                return [split.strip() for split in splits if split.strip()]
        
        # Fallback: split by double newlines or significant breaks
        entries = re.split(r'\n\s*\n', text)
        return [entry.strip() for entry in entries if entry.strip()]
    
    def _parse_experience_entry(self, entry_text: str) -> Optional[WorkExperience]:
        """Parse a single work experience entry"""
        if not entry_text or len(entry_text) < 20:
            return None
        
        lines = [line.strip() for line in entry_text.split('\n') if line.strip()]
        if not lines:
            return None
        
        # Try to extract company and position from first few lines
        company = None
        position = None
        dates = None
        location = None
        
        # Pattern 1: "Position at Company"
        at_match = re.search(r'^(.+?)\s+at\s+(.+?)(?:\s*[\(,]([^)]+)[\),])?', lines[0], re.IGNORECASE)
        if at_match:
            position = at_match.group(1).strip()
            company = at_match.group(2).strip()
            if at_match.group(3):
                dates = at_match.group(3).strip()
        
        # Pattern 2: First line is position, second is company
        elif len(lines) > 1:
            position = lines[0]
            # Look for company indicators in second line
            if any(indicator in lines[1].lower() for indicator in ['inc', 'llc', 'corp', 'company', 'ltd', 'group']):
                company = lines[1]
            else:
                # Maybe first line contains both
                parts = lines[0].split(' - ')
                if len(parts) >= 2:
                    position = parts[0].strip()
                    company = parts[1].strip()
        
        if not company and not position:
            return None
        
        # Extract dates
        date_patterns = [
            r'(\d{1,2}/\d{4})\s*[-–]\s*(\d{1,2}/\d{4}|present|current)',
            r'(\w+\s+\d{4})\s*[-–]\s*(\w+\s+\d{4}|present|current)',
            r'(\d{4})\s*[-–]\s*(\d{4}|present|current)'
        ]
        
        start_date = None
        end_date = None
        
        for line in lines[:3]:  # Check first 3 lines for dates
            for pattern in date_patterns:
                date_match = re.search(pattern, line, re.IGNORECASE)
                if date_match:
                    start_date = date_match.group(1)
                    end_date = date_match.group(2)
                    break
            if start_date:
                break
        
        # Extract description (bullet points or paragraphs)
        description = []
        for line in lines[1:]:  # Skip first line
            # Skip lines that look like dates or locations
            if re.search(r'\d{4}|present|current', line, re.IGNORECASE):
                continue
            if re.search(r'^[A-Z][a-z]+,\s+[A-Z]{2}$', line):  # City, State
                location = line
                continue
            
            # Clean bullet points
            clean_line = re.sub(r'^[•·▪▫◦‣⁃]\s*', '', line)
            if clean_line and len(clean_line) > 10:
                description.append(clean_line)
        
        # Extract technologies
        technologies = []
        full_text = ' '.join(lines)
        tech_matches = self.tech_pattern.findall(full_text)
        technologies.extend(tech_matches)
        
        return WorkExperience(
            company=company or "Unknown Company",
            position=position or "Unknown Position", 
            start_date=start_date,
            end_date=end_date,
            location=location,
            description=description,
            technologies=list(set(technologies))  # Remove duplicates
        )
    
    def _extract_education(self, education_text: str) -> List[Education]:
        """Extract education entries"""
        if not education_text:
            return []
        
        education_list = []
        entries = re.split(r'\n\s*\n', education_text)
        
        for entry in entries:
            entry = entry.strip()
            if not entry or len(entry) < 10:
                continue
            
            lines = [line.strip() for line in entry.split('\n') if line.strip()]
            
            # Try to parse education entry
            institution = None
            degree = None
            field_of_study = None
            graduation_date = None
            gpa = None
            
            # Look for degree patterns
            degree_patterns = [
                r'(Bachelor(?:\'s)?|Master(?:\'s)?|PhD|Doctor(?:ate)?|Associate)?\s*(?:of\s+)?(Science|Arts|Engineering|Business|Fine Arts|Philosophy)',
                r'(B\.?S\.?|M\.?S\.?|Ph\.?D\.?|M\.?B\.?A\.?|B\.?A\.?)',
                r'(Bachelor|Master|PhD|Doctorate)\s+(?:of\s+|in\s+)?([A-Za-z\s]+)'
            ]
            
            for line in lines:
                for pattern in degree_patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        degree = match.group().strip()
                        # Look for field of study in the same line
                        in_match = re.search(r'in\s+([A-Za-z\s]+)', line, re.IGNORECASE)
                        if in_match:
                            field_of_study = in_match.group(1).strip()
                        break
                if degree:
                    break
            
            # Look for institution
            for line in lines:
                if any(keyword in line.lower() for keyword in ['university', 'college', 'institute', 'school']):
                    institution = line
                    break
            
            # Look for graduation date
            for line in lines:
                date_match = re.search(r'\b(19|20)\d{2}\b', line)
                if date_match:
                    graduation_date = date_match.group()
                    break
            
            # Look for GPA
            for line in lines:
                gpa_match = re.search(r'GPA:?\s*([0-9.]+)', line, re.IGNORECASE)
                if gpa_match:
                    gpa = gpa_match.group(1)
                    break
            
            if institution or degree:
                education_list.append(Education(
                    institution=institution or "Unknown Institution",
                    degree=degree or "Unknown Degree",
                    field_of_study=field_of_study,
                    graduation_date=graduation_date,
                    gpa=gpa
                ))
        
        return education_list
    
    def _extract_skills(self, skills_text: str, full_text: str) -> List[str]:
        """Extract technical and professional skills"""
        skills = set()
        
        # Extract from skills section
        if skills_text:
            # Split by common delimiters
            skill_items = re.split(r'[,;|\n•·▪▫◦‣⁃]', skills_text)
            for item in skill_items:
                clean_skill = item.strip()
                if clean_skill and len(clean_skill) > 1 and len(clean_skill) < 50:
                    skills.add(clean_skill)
        
        # Extract technologies from full text
        tech_matches = self.tech_pattern.findall(full_text)
        skills.update(tech_matches)
        
        # Common skill keywords
        skill_keywords = [
            'Machine Learning', 'Data Analysis', 'Web Development', 'Mobile Development',
            'DevOps', 'Cloud Computing', 'Database Design', 'API Development',
            'Project Management', 'Agile', 'Scrum', 'Leadership', 'Team Management'
        ]
        
        for keyword in skill_keywords:
            if keyword.lower() in full_text.lower():
                skills.add(keyword)
        
        return sorted(list(skills))
    
    def _extract_projects(self, projects_text: str) -> List[Project]:
        """Extract project entries"""
        if not projects_text:
            return []
        
        projects = []
        entries = re.split(r'\n\s*\n', projects_text)
        
        for entry in entries:
            entry = entry.strip()
            if not entry or len(entry) < 20:
                continue
            
            lines = [line.strip() for line in entry.split('\n') if line.strip()]
            
            # First line is usually the project name
            name = lines[0]
            
            # Rest is description
            description = ' '.join(lines[1:]) if len(lines) > 1 else name
            
            # Extract technologies
            technologies = []
            tech_matches = self.tech_pattern.findall(entry)
            technologies.extend(tech_matches)
            
            # Look for URLs
            url_match = re.search(r'https?://[^\s]+', entry)
            url = url_match.group() if url_match else None
            
            projects.append(Project(
                name=name,
                description=description,
                technologies=list(set(technologies)),
                url=url
            ))
        
        return projects
    
    def _extract_certifications(self, cert_text: str) -> List[str]:
        """Extract certifications"""
        if not cert_text:
            return []
        
        # Split by common delimiters
        cert_items = re.split(r'[,;\n•·▪▫◦‣⁃]', cert_text)
        certifications = []
        
        for item in cert_items:
            clean_cert = item.strip()
            if clean_cert and len(clean_cert) > 3:
                certifications.append(clean_cert)
        
        return certifications
    
    def _extract_languages(self, lang_text: str) -> List[str]:
        """Extract language skills"""
        if not lang_text:
            return []
        
        # Split by common delimiters
        lang_items = re.split(r'[,;\n•·▪▫◦‣⁃]', lang_text)
        languages = []
        
        for item in lang_items:
            # Remove proficiency indicators
            clean_lang = re.sub(r'\s*\([^)]*\)', '', item).strip()
            clean_lang = re.sub(r'\s*[-–]\s*\w+$', '', clean_lang).strip()
            
            if clean_lang and len(clean_lang) > 1:
                languages.append(clean_lang)
        
        return languages


# Global parser instance
_parser_instance = None

def get_resume_parser() -> ResumeParser:
    """Get resume parser singleton instance"""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = ResumeParser()
    return _parser_instance