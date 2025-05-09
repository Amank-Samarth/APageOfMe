import streamlit as st
import nltk
import spacy
import os
import pyresparser.resume_parser
import pandas as pd
import base64
import random
import time
import datetime
from pyresparser import ResumeParser
from pdfminer.high_level import extract_text  # updated from pdfminer.six
from streamlit_tags import st_tags
from PIL import Image
import pymysql
from Courses import (
    ds_course, web_course, android_course, ios_course,
    uiux_course, resume_videos, interview_videos
)
import plotly.express as px
from yt_dlp import YoutubeDL

# Configure environment
os.environ["PAFY_BACKEND"] = "internal"

from dotenv import load_dotenv
load_dotenv()

# Download and load stopwords/model safely
nltk.download('stopwords')
try:
    nlp = spacy.load('en_core_web_sm')
except:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load('en_core_web_sm')

# Set page config
st.set_page_config(
    page_title="Smart Resume Analyzer",
    page_icon='./Logo/SRA_Logo.ico',
)

# Database connection
connection = pymysql.connect(host='localhost', user='yourusername', password='', autocommit=True, port=3307)
cursor = connection.cursor()

# Fetch YouTube video title
def fetch_yt_video(link):
    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'format': 'best',
        }
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            return info_dict.get('title', 'No Title Found')
    except Exception as e:
        return f"Error: {str(e)}"

# Resume to CSV link
def get_table_download_link(df, filename, text):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'

# Extract text from PDF
def pdf_reader(file):
    return extract_text(file)

# Show embedded PDF
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# Recommend courses
def course_recommender(course_list):
    st.subheader("**Courses & Certificates🎓 Recommendations**")
    c = 0
    rec_course = []
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 4)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course

# Insert record into DB
def insert_data(name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills, courses):
    DB_table_name = 'user_data'
    insert_sql = "INSERT INTO " + DB_table_name + """
    VALUES (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = (name, email, str(res_score), timestamp, str(no_of_pages), reco_field, cand_level, skills, recommended_skills, courses)
    cursor.execute(insert_sql, rec_values)
    connection.commit()

# Improved fallback name extraction for diverse resume formats
import re

def extract_name_fallback(resume_text):
    blacklist = {
        'india', 'aug', 'july', 'june', 'may', 'march', 'april', 'feb', 'dec', 'nov', 'oct', 'sept', 'jan',
        'resume', 'curriculum', 'vitae', 'address', 'contact', 'email', 'phone',
        'languages', 'english', 'skills', 'education', 'profile', 'summary', 'experience', 'projects',
        'personal', 'details', 'interests', 'objective', 'career', 'declaration', 'hobbies', 'references'
    }
    lines = resume_text.split('\n')[:20]  # Look at more lines
    # Prefer uppercase/title case lines not in blacklist
    for line in lines:
        words = line.strip().split()
        # Accept names like "Nagesh S" (second word can be 1 letter)
        if (2 <= len(words) <= 4 and
            all(w.isalpha() for w in words) and
            not any(w.lower() in blacklist for w in words)):
            if len(words[-1]) == 1 or line.strip().isupper() or line.strip().istitle():
                return line.strip()
    # Try NER as backup
    for line in lines:
        doc = nlp(line)
        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                words = ent.text.strip().split()
                if (2 <= len(words) <= 4 and
                    all(w.isalpha() for w in words) and
                    not any(w.lower() in blacklist for w in words)):
                    if len(words[-1]) == 1 or ent.text.strip().isupper() or ent.text.strip().istitle():
                        return ent.text.strip()
    # Regex for patterns like "NAGESH S"
    for line in lines:
        if re.match(r'^[A-Z][a-z]+ [A-Z]$', line.strip()) or re.match(r'^[A-Z]+ [A-Z]$', line.strip()):
            return line.strip()
    return None

import requests
from urllib.parse import urlencode, urlparse, parse_qs

# LinkedIn API Credentials from environment variables
LINKEDIN_CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
LINKEDIN_CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
LINKEDIN_REDIRECT_URI = os.getenv('LINKEDIN_REDIRECT_URI')

# LinkedIn API endpoints
LINKEDIN_AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
LINKEDIN_JOBS_API = "https://api.linkedin.com/v2/jobSearch"

# Helper: Get LinkedIn OAuth2 URL
def get_linkedin_auth_url():
    params = {
        'response_type': 'code',
        'client_id': LINKEDIN_CLIENT_ID,
        'redirect_uri': LINKEDIN_REDIRECT_URI,
        'scope': 'r_liteprofile r_emailaddress openid w_member_social',
        # Note: 'r_jobs' is not a public scope; job search is partner-only
    }
    return f"{LINKEDIN_AUTH_URL}?{urlencode(params)}"

# Helper: Exchange code for access token
def get_linkedin_access_token(auth_code):
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': LINKEDIN_REDIRECT_URI,
        'client_id': LINKEDIN_CLIENT_ID,
        'client_secret': LINKEDIN_CLIENT_SECRET,
    }
    response = requests.post(LINKEDIN_TOKEN_URL, data=data, timeout=10)
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        st.error(f"LinkedIn token error: {response.text}")
        return None

# Helper: Fetch jobs using Adzuna API
ADZUNA_APP_ID = os.getenv('ADZUNA_APP_ID')
ADZUNA_APP_KEY = os.getenv('ADZUNA_APP_KEY')
ADZUNA_COUNTRY = 'in'  # Change to 'us', 'gb', etc. for other regions

def fetch_public_jobs(skills, location=None):
    job_results = []
    try:
        if not skills:
            skills = ["Software Engineer"]
        query = " ".join(skills[:3])  # Use top 3 skills for search
        url = (
            f"https://api.adzuna.com/v1/api/jobs/{ADZUNA_COUNTRY}/search/1?app_id={ADZUNA_APP_ID}&app_key={ADZUNA_APP_KEY}"
            f"&results_per_page=5&what={query}"
        )
        if location:
            url += f"&where={location}"
        # st.info(f"Adzuna API URL: {url}")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for job in data.get('results', []):
                job_results.append({
                    'title': job.get('title'),
                    'company': job.get('company', {}).get('display_name', 'N/A'),
                    'location': job.get('location', {}).get('display_name', 'N/A'),
                    'link': job.get('redirect_url'),
                })
        else:
            st.error(f'Could not fetch jobs from Adzuna. Status code: {response.status_code}. Response: {response.text}. URL: {url}')
    except Exception as e:
        st.error(f'Error fetching jobs from Adzuna API: {str(e)}. URL: {url}. Showing mock data.')
    # No fallback mock data; only return real Adzuna jobs
    return job_results


# Streamlit section for LinkedIn jobs
def job_applications_section(resume_data):
    st.markdown("## Real-Time Job Listings Based on Your Resume")
    # Extract skills and location from resume data
    skills = resume_data.get('skills', [])
    location = resume_data.get('location', None)
    jobs = fetch_public_jobs(skills, location)
    if not jobs:
        st.warning("No jobs found at this time. Please check back later.")
    else:
        for job in jobs:
            st.markdown(f"**{job['title']}** at *{job['company']}*  ")
            st.markdown(f"Location: {job['location']}")
            st.markdown(f"[View Job Posting]({job['link']})", unsafe_allow_html=True)
            st.markdown("---")
    # Auto-refresh every 10 minutes
    st.markdown("<script>setTimeout(function(){window.location.reload();}, 600000);</script>", unsafe_allow_html=True)


# def run():
#     st.title("Smart Resume Analyzer")
#     ...  (rest of logic)
def run():
    st.title("Smart Resume Analyser")
    st.sidebar.markdown("# Choose User")
    activities = ["Normal User", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)
    # link = '[©Developed by Spidy20](http://github.com/spidy20)'
    # st.sidebar.markdown(link, unsafe_allow_html=True)
    img = Image.open('./Logo/SRA_Logo.jpg')
    img = img.resize((250, 250))
    st.image(img)

    # Create the DB
    db_sql = """CREATE DATABASE IF NOT EXISTS SRA;"""
    cursor.execute(db_sql)
    connection.select_db("sra")

    # Create table
    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                        (ID INT NOT NULL AUTO_INCREMENT,
                         Name varchar(100) NOT NULL,
                         Email_ID VARCHAR(50) NOT NULL,
                         resume_score VARCHAR(8) NOT NULL,
                         Timestamp VARCHAR(50) NOT NULL,
                         Page_no VARCHAR(5) NOT NULL,
                         Predicted_Field VARCHAR(25) NOT NULL,
                         User_level VARCHAR(30) NOT NULL,
                         Actual_skills VARCHAR(300) NOT NULL,
                         Recommended_skills VARCHAR(300) NOT NULL,
                         Recommended_courses VARCHAR(600) NOT NULL,
                         PRIMARY KEY (ID));
                        """
    cursor.execute(table_sql)
    if choice == 'Normal User':
        # st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>* Upload your resume, and get smart recommendation based on it."</h4>''',
        #             unsafe_allow_html=True)
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            # with st.spinner('Uploading your Resume....'):
            #     time.sleep(4)
            save_image_path = './Uploaded_Resumes/' + pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            if resume_data:
                ## Get the whole resume data
                resume_text = pdf_reader(save_image_path)
                # Check if the extracted name is valid
                name = resume_data.get('name')
                suspicious = False
                if name:
                    words = name.split()
                    blacklist = {
                        'india', 'aug', 'july', 'june', 'may', 'march', 'april', 'feb', 'dec', 'nov', 'oct', 'sept', 'jan',
                        'resume', 'curriculum', 'vitae', 'address', 'contact', 'email', 'phone',
                        'languages', 'english', 'skills', 'education', 'profile', 'summary', 'experience', 'projects',
                        'personal', 'details', 'interests', 'objective', 'career', 'declaration', 'hobbies', 'references'
                    }
                    # Accept if last word is 1 letter (for initials)
                    if (len(words) < 2 or len(words) > 4 or not all(w.isalpha() for w in words) or any(w.lower() in blacklist for w in words)):
                        suspicious = True
                if not name or suspicious:
                    fallback_name = extract_name_fallback(resume_text)
                    if fallback_name:
                        resume_data['name'] = fallback_name
                    else:
                        resume_data['name'] = st.text_input("Couldn't extract name reliably. Please enter your name:")
                else:
                    # Always ask for confirmation if name is suspicious or single word
                    resume_data['name'] = st.text_input("Is this your name? If not, please correct:", value=resume_data['name'])

                st.header("**Resume Analysis**")
                st.success("Hello " + resume_data['name'])
                st.subheader("**Your Basic info**")
                try:
                    st.text('Name: ' + resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Resume pages: ' + str(resume_data['no_of_pages']))
                except:
                    pass

                cand_level = ''
                if resume_data['no_of_pages'] == 1:
                    cand_level = "Fresher"
                    st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>You are looking Fresher.</h4>''',
                                unsafe_allow_html=True)
                elif resume_data['no_of_pages'] == 2:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',
                                unsafe_allow_html=True)
                elif resume_data['no_of_pages'] >= 3:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',
                                unsafe_allow_html=True)

                st.subheader("**Skills Recommendation💡**")
                ## Skill shows
                keywords = st_tags(label='### Skills that you have',
                                   text='See our skills recommendation',
                                   value=resume_data['skills'], key='1')

                ##  recommendation
                ds_keyword = ['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep Learning', 'flask',
                              'streamlit']
                web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress',
                               'javascript', 'angular js', 'c#', 'flask']
                android_keyword = ['android', 'android development', 'flutter', 'kotlin', 'xml', 'kivy']
                ios_keyword = ['ios', 'ios development', 'swift', 'cocoa', 'cocoa touch', 'xcode']
                uiux_keyword = ['ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping', 'wireframes',
                                'storyframes', 'adobe photoshop', 'photoshop', 'editing', 'adobe illustrator',
                                'illustrator', 'adobe after effects', 'after effects', 'adobe premier pro',
                                'premier pro', 'adobe indesign', 'indesign', 'wireframe', 'solid', 'grasp',
                                'user research', 'user experience']

                recommended_skills = []
                reco_field = ''
                rec_course = ''

                ## Courses recommendation
                for i in resume_data['skills']:
                    ## Data science recommendation
                    if i.lower() in ds_keyword:
                        print(i.lower())
                        reco_field = 'Data Science'
                        st.success("** Our analysis says you are looking for Data Science Jobs.**")
                        recommended_skills = ['Data Visualization', 'Predictive Analysis', 'Statistical Modeling',
                                              'Data Mining', 'Clustering & Classification', 'Data Analytics',
                                              'Quantitative Analysis', 'Web Scraping', 'ML Algorithms', 'Keras',
                                              'Pytorch', 'Probability', 'Scikit-learn', 'Tensorflow', "Flask",
                                              'Streamlit']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='2')
                        st.markdown(
                            '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                            unsafe_allow_html=True)
                        rec_course = course_recommender(ds_course)
                        break

                    ## Web development recommendation
                    elif i.lower() in web_keyword:
                        print(i.lower())
                        reco_field = 'Web Development'
                        st.success("** Our analysis says you are looking for Web Development Jobs **")
                        recommended_skills = ['React', 'Django', 'Node JS', 'React JS', 'php', 'laravel', 'Magento',
                                              'wordpress', 'Javascript', 'Angular JS', 'c#', 'Flask', 'SDK']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='3')
                        st.markdown(
                            '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                            unsafe_allow_html=True)
                        rec_course = course_recommender(web_course)
                        break

                    ## Android App Development
                    elif i.lower() in android_keyword:
                        print(i.lower())
                        reco_field = 'Android Development'
                        st.success("** Our analysis says you are looking for Android App Development Jobs **")
                        recommended_skills = ['Android', 'Android development', 'Flutter', 'Kotlin', 'XML', 'Java',
                                              'Kivy', 'GIT', 'SDK', 'SQLite']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='4')
                        st.markdown(
                            '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                            unsafe_allow_html=True)
                        rec_course = course_recommender(android_course)
                        break

                    ## IOS App Development
                    elif i.lower() in ios_keyword:
                        print(i.lower())
                        reco_field = 'IOS Development'
                        st.success("** Our analysis says you are looking for IOS App Development Jobs **")
                        recommended_skills = ['IOS', 'IOS Development', 'Swift', 'Cocoa', 'Cocoa Touch', 'Xcode',
                                              'Objective-C', 'SQLite', 'Plist', 'StoreKit', "UI-Kit", 'AV Foundation',
                                              'Auto-Layout']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='5')
                        st.markdown(
                            '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                            unsafe_allow_html=True)
                        rec_course = course_recommender(ios_course)
                        break

                    ## Ui-UX Recommendation
                    elif i.lower() in uiux_keyword:
                        print(i.lower())
                        reco_field = 'UI-UX Development'
                        st.success("** Our analysis says you are looking for UI-UX Development Jobs **")
                        recommended_skills = ['UI', 'User Experience', 'Adobe XD', 'Figma', 'Zeplin', 'Balsamiq',
                                              'Prototyping', 'Wireframes', 'Storyframes', 'Adobe Photoshop', 'Editing',
                                              'Illustrator', 'After Effects', 'Premier Pro', 'Indesign', 'Wireframe',
                                              'Solid', 'Grasp', 'User Research']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='6')
                        st.markdown(
                            '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                            unsafe_allow_html=True)
                        rec_course = course_recommender(uiux_course)
                        break

                #
                ## Insert into table
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date + '_' + cur_time)

                ### Resume writing recommendation
                st.subheader("**Resume Tips & Ideas💡**")
                resume_score = 0
                if 'Objective' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Objective</h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add your career objective, it will give your career intension to the Recruiters.</h4>''',
                        unsafe_allow_html=True)

                if 'Declaration' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Delcaration✍/h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Declaration✍. It will give the assurance that everything written on your resume is true and fully acknowledged by you</h4>''',
                        unsafe_allow_html=True)

                if 'Hobbies' or 'Interests' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies⚽</h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Hobbies⚽. It will show your persnality to the Recruiters and give the assurance that you are fit for this role or not.</h4>''',
                        unsafe_allow_html=True)

                if 'Achievements' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements🏅 </h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Achievements🏅. It will show that you are capable for the required position.</h4>''',
                        unsafe_allow_html=True)

                if 'Projects' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects👨‍💻 </h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Projects👨‍💻. It will show that you have done work related the required position or not.</h4>''',
                        unsafe_allow_html=True)

                st.subheader("**Resume Score📝**")
                st.markdown(
                    """
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: #d73b5c;
                        }
                    </style>""",
                    unsafe_allow_html=True,
                )
                my_bar = st.progress(0)
                score = 0
                for percent_complete in range(resume_score):
                    score += 1
                    time.sleep(0.1)
                    my_bar.progress(percent_complete + 1)
                # Email must be present for DB insert; force user input if missing
                email = resume_data.get('email')
                while not email:
                    email = st.text_input("Email could not be extracted. Please enter your email to proceed:")
                    if email:
                        resume_data['email'] = email
                        break
                    st.warning("Email is required to save your data. Please enter a valid email above.")
                    st.stop()
                # Now safe to insert
                insert_data(resume_data['name'], resume_data['email'], str(resume_score), timestamp,
                            str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']),
                            str(recommended_skills), str(rec_course))

                ## Resume writing video
                st.header("**Bonus Video for Resume Writing Tips💡**")
                resume_vid = random.choice(resume_videos)
                res_vid_title = fetch_yt_video(resume_vid)
                st.subheader("✅ **" + res_vid_title + "**")
                st.video(resume_vid)

                ## Interview Preparation Video
                st.header("**Bonus Video for Interview👨‍💼 Tips💡**")
                interview_vid = random.choice(interview_videos)
                int_vid_title = fetch_yt_video(interview_vid)
                st.subheader("✅ **" + int_vid_title + "**")
                st.video(interview_vid)

                # --- Job Application Section after Bonus Videos ---
                st.header("Current Job Applications as per Your Interest")
                st.markdown("These openings are curated based on your resume and interests. Click on a job to view details and apply directly.")
                job_applications_section(resume_data)

                connection.commit()
            else:
                st.error('Something went wrong..')
    else:
        ## Admin Side
        st.success('Welcome to Admin Side')
        # st.sidebar.subheader('**ID / Password Required!**')

        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')
        if st.button('Login'):
            if ad_user == 'machine_learning_hub' and ad_password == 'mlhub123':
                st.success("Welcome, Admin. You have successfully logged in.")
                # Display Data
                cursor.execute('''SELECT*FROM user_data''')
                data = cursor.fetchall()
                st.header("**User's👨‍💻 Data**")
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Resume Score', 'Timestamp', 'Total Page',
                                                 'Predicted Field', 'User Level', 'Actual Skills', 'Recommended Skills',
                                                 'Recommended Course'])
                st.dataframe(df)
                st.markdown(get_table_download_link(df, 'User_Data.csv', 'Download Report'), unsafe_allow_html=True)
                ## Admin Side Data
                query = 'select * from user_data;'
                plot_data = pd.read_sql(query, connection)

                ## Pie chart for predicted field recommendations
                st.subheader("📈 **Pie-Chart for Predicted Field Recommendations**")
                fig = px.pie(plot_data, names='Predicted_Field', title='Predicted Field according to the Skills')
                st.plotly_chart(fig)

                ### Pie chart for User's👨‍💻 Experienced Level
                st.subheader("📈 ** Pie-Chart for User's👨‍💻 Experienced Level**")
                fig = px.pie(plot_data, names='User_level', title="Pie-Chart📈 for User's👨‍💻 Experienced Level")
                st.plotly_chart(fig)

            else:
                st.error("Wrong ID & Password Provided")

run()