# Smart Resume Analyser App – Final Project Report

**Contributors:** Amank H, Nagesh S  
**Degree:** Bachelor of Computer Applications (BCA)  
**Submission:** Final Year Project  
**Date:** April 2025

---

## Table of Contents
1. Introduction
2. Project Overview
3. Objectives
4. System Architecture
5. Technology Stack
6. Features & Modules
7. Workflow
8. User Interface
9. Backend Logic & Data Flow
10. Database Design
11. Unique & Advanced Features
12. Security Considerations
13. Testing & Validation
14. Challenges Faced
15. Future Scope
16. Conclusion

---

## 1. Introduction

### 1.1 Background
In the modern recruitment landscape, the process of shortlisting candidates often begins with resume screening. Traditionally, this task is manual, time-consuming, and prone to human bias and error. With the rise of automation and artificial intelligence, there is an increasing demand for intelligent systems that can analyze resumes efficiently and objectively, providing not only a score but also personalized recommendations for career advancement. The Smart Resume Analyser App is designed to address these challenges by leveraging Natural Language Processing (NLP), Machine Learning (ML), and web technologies to automate resume analysis and provide actionable guidance to job seekers.

### 1.2 Motivation
The primary motivation behind this project stems from the need to bridge the gap between job seekers and recruiters by offering an unbiased, data-driven evaluation of resumes. Many candidates are unaware of how their resumes are perceived by automated systems or recruiters. By providing comprehensive analysis and feedback, the Smart Resume Analyser App empowers users to improve their employability and make informed career decisions.

### 1.3 Purpose of the Project
The purpose of this project is to create a robust, user-friendly platform that not only analyzes resumes but also offers a holistic suite of career development tools, including skill and course recommendations, resume writing tips, and career guidance. The application aims to be a one-stop solution for both job seekers and administrators, enhancing the overall effectiveness of the recruitment process.

### 1.4 Scope
The scope of this project encompasses the development of a web-based application capable of:
- Parsing and analyzing resumes in PDF format
- Scoring resumes based on predefined criteria
- Providing personalized recommendations for skills, courses, and career paths
- Offering resume writing tips and video resources
- Enabling admin-level analytics and data management

## 2. Project Overview

### 2.1 Project Summary
The Smart Resume Analyser App is an intelligent platform that automates the process of resume evaluation and career guidance. Users can upload their resumes, which are then analyzed using advanced NLP and ML algorithms. The system extracts key information, scores the resume, and provides tailored recommendations for improvement. The application also features an admin panel for managing user data and visualizing analytics.

### 2.2 Key Features
- Automated resume parsing and scoring
- Personalized skill, course, and career recommendations
- Resume writing tips and video suggestions
- Admin dashboard with analytics and data export
- Secure authentication and data handling

### 2.3 Target Audience
- **Job Seekers:** Individuals seeking to improve their resumes and career prospects
- **Recruiters/HR Professionals:** Organizations looking to streamline the resume screening process
- **Educational Institutions:** Colleges and universities aiming to assist students in career preparation

### 2.4 Project Deliverables
- Fully functional web application
- Project documentation and user manual
- Source code with detailed comments
- Final project report (this document)
- Presentation slides and supplementary materials

## 3. Objectives

### 3.1 Primary Objectives
- To develop an automated system for resume analysis and scoring
- To provide personalized recommendations for skills, courses, and career paths
- To offer actionable feedback for resume improvement
- To facilitate data-driven decision-making for administrators

### 3.2 Secondary Objectives
- To enhance user experience through an intuitive web interface
- To ensure data security and privacy
- To maintain extensibility for future enhancements

### 3.3 Learning Outcomes
- Practical application of Python, NLP, and ML in a real-world scenario
- Experience in web development using Streamlit
- Understanding of database integration and data visualization
- Exposure to project management and collaborative development

## 4. System Architecture

### 4.1 High-Level Architecture
The Smart Resume Analyser App follows a modular, layered architecture to ensure scalability, maintainability, and separation of concerns. The main components are:
- **Frontend Layer:** Provides the user interface using Streamlit, handling user interactions and displaying results.
- **Backend Layer:** Handles business logic, including resume parsing, scoring, and recommendation generation.
- **Database Layer:** Stores user data, resume scores, and analytics information using MySQL.
- **Storage Layer:** Manages uploaded resume files and static assets.
- **External Services Layer:** Integrates with third-party APIs for YouTube video recommendations and online course links.

### 4.2 Component Diagram
```
[User] <--> [Streamlit Web UI] <--> [Backend Logic (Python)] <--> [MySQL Database]
                                              |                     |
                                              v                     v
                                  [Resume Parsing & NLP]     [File Storage]
                                              |
                                              v
                                  [External APIs: YouTube, Courses]
```

### 4.3 Data Flow Diagram
1. User accesses the web app via Streamlit.
2. User uploads their resume (PDF).
3. Resume is parsed for key information (skills, education, experience, etc.).
4. App calculates a resume score and recommends improvements.
5. Personalized career fields, skills, and courses are suggested.
6. YouTube videos relevant to the user's profile are recommended.
7. Admin can access analytics and download user data.

### 4.4 Detailed Architecture Explanation
- **User Interface:** Built with Streamlit, the UI is designed for simplicity and accessibility, allowing users to upload resumes, view results, and interact with recommendations effortlessly.
- **Resume Parsing:** Utilizes pyresparser and pdfminer.six to extract structured data (skills, education, experience) from PDF resumes, handling various formats and templates.
- **NLP Processing:** Employs NLTK and spaCy for tokenization, stopword removal, and entity recognition, enabling accurate extraction and analysis of resume content.
- **Scoring Engine:** Applies ML algorithms (KNN in the original Classifier.py) to evaluate resumes based on multiple parameters (skills match, experience, education, etc.).
- **Recommendation System:** Matches user profiles with relevant career fields, skills, and courses using curated datasets (Courses.py) and logic based on extracted data.
- **Database Integration:** Stores all user interactions, resume scores, and recommendations in a MySQL database for persistence and analytics.
- **Admin Panel:** Provides administrators with access to user data, analytics dashboards, and data export functionality.
- **External Integrations:** Fetches YouTube video titles and links using yt-dlp and presents curated online courses for further learning.

### 4.5 Advantages of the Architecture
- **Scalability:** Modular design allows for easy addition of new features
- **Maintainability:** Clear separation of frontend, backend, and data layers
- **Extensibility:** Supports integration with additional APIs and services
- **User-Centric:** Focused on delivering actionable insights and recommendations

## 5. Technology Stack
- **Languages:** Python 3.6+
- **Libraries:**
  - Streamlit (web UI)
  - NLTK, spaCy (NLP)
  - pyresparser (resume parsing)
  - pdfminer.six (PDF extraction)
  - pandas (data handling)
  - plotly (visualization)
  - pymysql (MySQL connection)
  - PIL (image processing)
  - yt-dlp (YouTube video info)
  - streamlit-tags (UI tags)
- **Database:** MySQL (XAMPP or similar)
- **Other:** Virtual environment, requirements.txt for reproducibility

## 6. Features & Modules
### User Features
- Resume upload (PDF)
- Resume parsing and information extraction
- Resume scoring (based on ML/NLP analysis)
- Personalized career recommendations
- Resume writing tips
- Recommended courses and skills
- YouTube video recommendations

### Admin Features
- Admin login (username: machine_learning_hub, password: mlhub123)
- View all uploaded resumes and user data
- Download user data as CSV
- Visual analytics (charts, graphs)

### Core Modules
- `App.py`: Main application logic, UI, backend integration
- `Courses.py`: Contains curated course and video lists
- `requirements.txt`: Dependency management
- `Uploaded_Resumes/`: Stores user-uploaded resumes
- `Logo/`: App branding assets

## 7. Workflow
1. User accesses the web app via Streamlit.
2. User uploads their resume (PDF).
3. Resume is parsed for key information (skills, education, experience, etc.).
4. App calculates a resume score and recommends improvements.
5. Personalized career fields, skills, and courses are suggested.
6. YouTube videos relevant to the user's profile are recommended.
7. Admin can access analytics and download user data.

## 8. User Interface
- Clean, modern Streamlit UI
- Logo and branding (custom icons/images)
- Interactive widgets for uploading, selecting, and viewing recommendations
- Embedded PDF viewer for resume preview
- Visualizations (Plotly charts)
- Screenshots: `sc1.png` (User), `sc2.png` (Admin)

## 9. Backend Logic & Data Flow
- **Resume Parsing:** Uses pyresparser and pdfminer.six to extract structured data from PDFs
- **NLP Processing:** NLTK and spaCy for stopwords, entity recognition, and text analysis
- **Scoring:** ML logic (KNN algorithm in original Classifier.py) to rate resumes
- **Recommendations:** Logic to match user profile with relevant careers, skills, and courses (from Courses.py)
- **Database:** Stores user data, resume scores, and recommendations
- **YouTube Integration:** yt-dlp fetches video titles and links for recommendations

## 10. Database Design
- MySQL database holds user records, resume scores, timestamps, recommended fields, skills, and courses
- Connection via PyMySQL
- Data can be exported as CSV for further analysis

## 11. Unique & Advanced Features
- Automated, intelligent resume scoring
- Personalized, data-driven recommendations
- Real-time YouTube video fetching and display
- Downloadable analytics for admin
- Embedded PDF preview
- Multi-section UI for users and admins

## 12. Security Considerations
- Admin authentication for sensitive data access
- File upload validation (PDF only)
- Database credentials (to be secured in production)

## 13. Testing & Validation
- Manual testing of all user/admin flows
- Validation of resume parsing accuracy
- Verification of recommendation logic
- UI/UX tested on multiple browsers

## 14. Challenges Faced
- Handling diverse resume formats
- Ensuring accurate information extraction
- Integrating multiple third-party libraries
- Managing dependencies and environment compatibility
- Ensuring smooth database connectivity

## 15. Future Scope
- Support for more file formats (DOCX, etc.)
- Enhanced ML models for better scoring
- Integration with job portals
- Mobile-friendly UI
- Improved security (OAuth, encrypted credentials)

## 16. Final Remarks and Functional Overview

The Smart Resume Analyser App stands as a comprehensive, innovative solution that leverages the power of Python, Natural Language Processing (NLP), and modern web technologies to address the evolving needs of job seekers, recruiters, and educational institutions. Through its intelligent automation and user-centric design, the application transforms the traditional resume evaluation process into a streamlined, data-driven, and insightful experience.

### Core Functionality and Features

#### 1. Automated Resume Parsing and Scoring
- **Functionality:** Users upload their resumes in PDF format. The system employs advanced NLP and ML algorithms (via pyresparser, pdfminer, NLTK, spaCy) to extract structured information such as skills, education, work experience, and contact details.
- **Use:** Saves time for both candidates and recruiters by instantly processing resumes and providing an objective evaluation.

#### 2. Personalized Recommendations
- **Functionality:** Based on the extracted data, the app suggests relevant career paths, in-demand skills, and curated online courses (from platforms like Coursera, Udemy, LinkedIn Learning, etc.).
- **Use:** Empowers users to identify gaps in their profiles and take actionable steps to enhance their employability.

#### 3. Resume Writing Tips and Video Resources
- **Functionality:** The app provides targeted tips for improving resume quality and recommends YouTube videos for further guidance, fetched dynamically using the yt-dlp library.
- **Use:** Offers practical, multimedia learning resources, making the process interactive and engaging for all types of learners.

#### 4. Admin Dashboard and Analytics
- **Functionality:** Dedicated admin login enables access to all user data, resume analytics, and downloadable CSV reports. Visualizations (using Plotly) present trends and insights for better decision-making.
- **Use:** Facilitates efficient management, monitoring, and reporting for recruiters, placement officers, or educators.

#### 5. Secure Data Management
- **Functionality:** User data and resumes are securely stored, and admin access is protected by authentication. File uploads are validated, and sensitive operations are restricted.
- **Use:** Ensures privacy and integrity of user information, which is critical in the recruitment domain.

#### 6. Intuitive, Accessible User Interface
- **Functionality:** Built with Streamlit, the UI is modern, responsive, and easy to navigate. Features include drag-and-drop resume upload, embedded PDF preview, and interactive widgets.
- **Use:** Lowers the barrier for users of all technical backgrounds, making the app widely accessible.

### Practical Uses and Impact
- **For Job Seekers:** Provides immediate, actionable feedback on resume quality and career readiness, helping users stand out in competitive job markets.
- **For Recruiters/HR:** Automates the initial screening process, reducing manual workload and improving the quality of shortlisted candidates.
- **For Educational Institutions:** Assists students in preparing industry-ready resumes and guides them toward relevant upskilling opportunities.

### Conclusion

The Smart Resume Analyser App exemplifies the integration of technology and practical problem-solving in the field of career development. By automating resume analysis, offering personalized recommendations, and supporting both users and administrators with robust tools, the application delivers significant value to all stakeholders. Its modular, extensible design ensures that it can evolve to meet future requirements, making it not just a project, but a foundation for ongoing innovation in employability solutions.

*This report covers all aspects of the project as required for the final year BCA submission. For any queries, please contact the contributors.*
