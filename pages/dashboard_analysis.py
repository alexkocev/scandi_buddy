import streamlit as st
import base64
import requests
import io
# from PyPDF2 import PdfReader, PdfWriter
from pypdf import PdfReader, PdfWriter

import json
from datetime import datetime
import os
import markdown
import re
from weasyprint import HTML
import time as time

# Set your API keys
secrets_path = "./secrets.json"
with open(secrets_path, "r") as f:
    secrets = json.load(f)
CLAUDE_KEY = secrets["CLAUDE_KEY"]
url = 'https://api.anthropic.com/v1/messages'
headers = {
    'Content-Type': 'application/json',
    'x-api-key': CLAUDE_KEY,
    'anthropic-version': '2023-06-01',
    'anthropic-beta': 'pdfs-2024-09-25'
}

st.title("🦋")
st.header("Looker Studio Dashboard Analyzer")
st.markdown("💡 Upload your Looker Studio PDF dashboard to analyze and generate a report.")

st.write("")
st.write("")

# File uploader
col1, col2 = st.columns([3, .5])
with col1:
    uploaded_file = st.file_uploader("Upload your Looker Studio dashboard (PDF)", type="pdf")

with col2:
    st.write("")
    st.write("")
    st.write("")
    st.link_button("Help", 
                   "https://www.loom.com/share/c542db5ff8994ff996cb9102c911984a?sid=c6b22478-1c69-4397-86d5-21d368f162ff",
                   help="How to download a Looker Studio Dashboard as PDF",
                   icon="🤔")

    


# -- PARAMETERS --
with st.expander("⚙️ Additional Parameters", expanded=False):
    
    # Report Example
    analysis_example = st.text_area(
        "Analysis Example (optional)",
        value="",
        placeholder="""
1. Key Performance Indicators
2. Trend Analysis
3. Comparative Insights
4. Actionable Recommendations
        """.strip(),
        height=130
    )

    # Report Type Dropdown
    report_type = st.selectbox(
        "Select the Report Type (optional)",
        ["", "Weekly performance", "Monthly performance", "Yearly performance"],
        placeholder="Weekly performance",
        index=0
    )

    # Emoji Toggle
    add_emoji = st.checkbox("Add Emojis to the Report?", value=False) 
    



st.write("")
st.write("")
st.write("")
st.write("")

def markdown_to_html(md_content):
    # Replace Markdown tables with proper HTML tables
    md_content = re.sub(r"\|(.+?)\|\n\|(?:-+\|)+\n(.+?)(?=\n\n|\Z)", convert_table_to_html, md_content, flags=re.DOTALL)

    # Replace numbered lists with bullet points while keeping structure
    md_content = re.sub(r"(\d+)\.\s+\*\*(.+?)\*\*", r"<ul><li><strong>\2</strong></li></ul>", md_content)
    md_content = re.sub(r"(\d+)\.\s+(.+)", r"<li>\2</li>", md_content)

    return markdown.markdown(md_content)

def convert_table_to_html(match):
    # Extract headers and rows
    headers = [h.strip() for h in match.group(1).strip().split('|') if h.strip()]
    rows = [
        [cell.strip() for cell in row.split('|') if cell.strip()]
        for row in match.group(2).strip().splitlines()
    ]
    
    # Build HTML table
    html_table = '<table><thead><tr>'
    html_table += ''.join(f'<th>{header}</th>' for header in headers)
    html_table += '</tr></thead><tbody>'
    
    for row in rows:
        if len(row) != len(headers):
            # Pad rows with empty cells to match headers
            row += [''] * (len(headers) - len(row))
        html_table += '<tr>' + ''.join(f'<td>{cell}</td>' for cell in row) + '</tr>'
    
    html_table += '</tbody></table>'
    return html_table


# Estimation box
def estimate_analysis(num_pages):
    BASE_TIME_PER_PAGE = 23  # seconds per page
    BASE_COST_PER_PAGE = 0.0215  # $ per page

    total_analysis_time = num_pages * BASE_TIME_PER_PAGE
    total_cost = num_pages * BASE_COST_PER_PAGE

    if total_analysis_time < 60:
        time_display = f"{total_analysis_time:.1f} seconds"
    elif total_analysis_time < 3600:
        time_display = f"{total_analysis_time / 60:.1f} minutes"
    else:
        time_display = f"{total_analysis_time / 3600:.1f} hours"

    cost_display = f"${total_cost:.2f}"
    return time_display, cost_display

estimator_container = st.container(border=True)

with estimator_container:
    estimation_progress_bar = st.empty()
    if uploaded_file is not None:
        
        try:
            st.session_state.pdf_bytes = uploaded_file.read()
            estimation_progress_bar.progress(10, text="Calculating number of pages...")
            # Read PDF and calculate number of pages
            pdf_reader = PdfReader(io.BytesIO(st.session_state.pdf_bytes))
            num_pages = len(pdf_reader.pages)
            if num_pages == 0:
                st.error("This PDF appears to have no pages.")
                st.stop()
            estimation_progress_bar.progress(50, text="Estimation in progress...")
            estimated_time, estimated_cost = estimate_analysis(num_pages)
            estimation_progress_bar.progress(100, text="Estimation complete.")

            if num_pages == 1:
                st.markdown("<small>🔢  Estimation for 1 page</small>", unsafe_allow_html=True)
            else:
                st.markdown(f"<small>🔢  Estimation for {num_pages} pages</small>", unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Estimated Time", estimated_time,
                        help="Includes page analysis but excludes summary generation")
            with col2:
                st.metric("Estimated Cost", estimated_cost,
                        help="Based on API usage and complexity")

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        
        st.markdown("<small>🔢  Estimation for 1 page</small>", unsafe_allow_html=True)
        estimated_time, estimated_cost = estimate_analysis(1)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Estimated Time", estimated_time,
                    help="Includes page analysis but excludes summary generation")
        with col2:
            st.metric("Estimated Cost", estimated_cost,
                    help="Based on API usage and complexity")
            








st.write("")
st.write("")
st.write("")
st.write("")


def process_with_retry(headers, payload, max_attempts=3, retry_delay=30):
    attempt = 0
    while attempt < max_attempts:
        try:
            response = requests.post(url, headers=headers, json=payload)
            response_json = response.json()
            if 'content' in response_json and response_json['content']:
                return response_json['content'][0]['text']
            else:
                raise ValueError(f"Unexpected response format: {response_json}")
        except Exception as e:
            attempt += 1
            if attempt < max_attempts:
                st.error(f"""Oooops we have an error, let's retry in {retry_delay} seconds... \n
                         Error on attempt {attempt}: {str(e)}""")
                time.sleep(retry_delay)
            else:
                st.error(f"""No way, max attempts reached. Come back an retry in few minutes \n
                         Error after {max_attempts} attempts: {str(e)} """)
                return f"Error after {max_attempts} attempts: {str(e)}"



# Create a placeholder for the progress bar
progress_placeholder = st.empty()

# Use Streamlit's button in the centered div
col1, col2, col3 = st.columns([1, 1, 1])

# Custom CSS for the button
st.markdown(
    """
    <style>
    div.stButton > button {
        background-color: #E04F4F;
        color: white;
        border: none;
        padding: 0.5em 1em;
        border-radius: 10px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
    }
    div.stButton > button:hover {
        background-color: #D03F3F; /* Slightly darker shade for hover effect */
        color: white; /* Ensure font color remains white */
    }
    </style>
    """,
    unsafe_allow_html=True
)

with col2:
    run_analysis = st.button("Run Analysis")
    
if run_analysis:
    if "pdf_bytes" not in st.session_state:
        st.error("Please upload a PDF file before launching analysis.")
        st.stop()

    try:
        # Generate a unique folder for each analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        user_folder = f"temp_analysis/{timestamp}"
        os.makedirs(user_folder, exist_ok=True)

        pdf_path = os.path.join(user_folder, uploaded_file.name)
        with open(pdf_path, "wb") as f:
            f.write(st.session_state.pdf_bytes)


        # -- Split PDF into individual page base64 encodings -- 
        pdf_reader = PdfReader(io.BytesIO(st.session_state.pdf_bytes))
        page_base64_list = []
        for page in pdf_reader.pages:
            # Save page to a bytes buffer
            page_bytes_io = io.BytesIO()
            page_writer = PdfWriter()
            page_writer.add_page(page)
            page_writer.write(page_bytes_io)
            page_bytes_io.seek(0)
            
            # Convert to base64
            page_base64 = base64.b64encode(page_bytes_io.getvalue()).decode('utf-8')
            page_base64_list.append(page_base64)
            

        # -- Analyze PDF pages and compile results --
        page_analyses = []
        client_name = ""
        report_name = None

        # Total number of pages for progress calculation
        total_pages = len(page_base64_list)
        # Total steps: pages + 1 for summary step
        total_steps = total_pages + 1
        
        
        for i, page_base64 in enumerate(page_base64_list, 1):
            # Calculate progress percentage
            progress = i / total_steps
            # Update the progress bar via the placeholder
            progress_placeholder.progress(progress, text=f"Analyzing page {i}...")
            
            
            prompt = f"""
            Analyze this PDF page {i} in depth.
                    
            Report Type: {report_type}
            Emoji Usage: {'Enabled' if add_emoji else 'Disabled'}

            {f'Analysis Example: {analysis_example}' if analysis_example else ''}

            {f'This is the first page of a Looker Studio report. Please extract the following and display as follows: Client Name: ... - Report Name: .... If either of these is not clearly provided, mention that it is unavailable.' if i == 1 else ''}

            Please focus on key insights, trends, and notable information.
            """
                
            page_payload = {
                'model': 'claude-3-5-sonnet-20241022',
                'max_tokens': 2048,
                'messages': [
                    {
                        'role': 'user',
                        'content': [
                            {
                                'type': 'document',
                                'source': {
                                    'type': 'base64',
                                    'media_type': 'application/pdf',
                                    'data': page_base64
                                }
                            },
                            {
                                'type': 'text',
                                'text': prompt
                            }
                        ]
                    }
                ]
            }

            response = process_with_retry(headers, page_payload)
            if isinstance(response, str) and response.startswith("Error"):
                st.error("Processing failed for a page.")
                continue
            else:
                page_analyses.append(response)

            
            # Try to extract client name from first page
            if i == 1:

                try:
                    # Extract client name and report name using regex
                    client_name_match = re.search(r"Client Name:\s*([^\n]+)", page_analyses, re.IGNORECASE)
                    report_name_match = re.search(r"Report Name:\s*([^\n]+)", page_analyses, re.IGNORECASE)

                    client_name = client_name_match.group(1).strip() if client_name_match else ""
                    report_name = report_name_match.group(1).strip() if report_name_match else "Dashboard Analysis"
                except:
                    client_name = ""
                    report_name = "Dashboard Analysis"          

        # Add progress for the summary step
        progress = total_pages / total_steps
        progress_placeholder.progress(progress, text="Summarizing all findings...")

        # Summarize all page analyses
        summary_prompt = f"""Build a comprehensive report based on the following page analyses:

        {chr(10).join(page_analyses)}

        Report Type: {report_type}
        Emoji Usage: {'Enabled' if add_emoji else 'Disabled'}

        Provide a comprehensive overview that captures key insights across all pages.
        Please, write the report using markdown.
        """

        final_analysis_payload = {
            'model': 'claude-3-5-sonnet-20241022',
            'max_tokens': 4096,
            'messages': [
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': summary_prompt
                        }
                    ]
                }
            ]
        }


        response = process_with_retry(headers, final_analysis_payload)
        if isinstance(response, str) and response.startswith("Error"):
            st.error("Processing failed for the final analysis")
        
        else:
            # Prepare JSON output
            response_data = {
                "client_name": client_name,
                "report_name": report_name,
                "page_analyses": page_analyses,
                "summary": response
            }
            
            # Final progress update to 100%
            progress_placeholder.progress(1.0, text="Analysis completed.")

            # Generate PDF report
            logo_path = os.path.abspath("./images/SW_logo.jpeg")
            client_name = response_data.get("client_name", "")
            report_name = response_data["report_name"]
            output_pdf = os.path.join(user_folder, f"{report_name}.pdf")
            md_content = response_data["summary"]            
            # html_content = markdown.markdown(md_content, output_format="html5")
            html_content = markdown_to_html(md_content)

            # Prepare the HTML Template
            html_template = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Report</title>
                <style>
                
                


                    /* Custom Fonts . Alex, delete if not needed */
                    @font-face {{
                        font-family: 'Inter';
                        src: url('./fonts/inter.ttf') format('truetype');
                        font-weight: normal;
                    }}
                    @font-face {{
                        font-family: 'Secular One';
                        src: url('./fonts/SecularOne.ttf') format('truetype');
                        font-weight: normal;
                    }}
                    @font-face {{
                        font-family: 'Noto Emoji';
                        src: url('./fonts/NotoColorEmoji.ttf') format('truetype');
                    }}
                    


                    /* General Styles */
                    body {{
                        font-family: 'Inter', 'Liberation Sans', 'DejaVu Sans', sans-serif;
                        font-size: 12px; /* Smaller font size */
                        line-height: 1.4;
                        color: #10132C; /* Brand black */
                        margin: 20px;
                        background-color: #FFFFFF; /* White background */
                    }}
                    h1 {{
                        font-family: 'Secular One', sans-serif;
                        color: #10132C; /* Brand red */
                        margin: 30px 0 20px;  /* Top, right/left, bottom */
                    }}
                    h2, h3 {{
                        font-family: 'Secular One', sans-serif;
                        color: #E04F4F; /* Brand red */
                        margin: 25px 0 15px; /* Top, right/left, bottom */
                    }}




                    ul {{
                        margin-left: 20px;
                        list-style-type: disc;
                    }}
                    li {{
                        margin-bottom: 5px;
                    }}
                    strong {{
                        color: #10132C;
                    }}
                    
                    


                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin: 20px 0;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                    }}
                    th {{
                        background-color: #f2f2f2;
                        font-weight: bold;
                    }}
                    tr:nth-child(even) {{
                        background-color: #f9f9f9;
                    }}
                    tr:hover {{
                        background-color: #d9f7ff;
                    }}
                                        
                                        
                    
                    img {{
                        max-width: 100px;
                        max-height: 100px;
                    }}
                    .logo {{
                        position: absolute;
                        top: -40px; /* Closer to the top */
                        right: -40px; /* Closer to the right */
                    }}
                    .header {{
                        position: absolute;
                        top: -35px; /* Closer to the top */
                        left: -20px; /* Closer to the left */
                        font-size: 10px;
                        color: #E04F4F; /* Brand red */
                    }}
                    .footer {{
                        position: fixed;
                        bottom: -30px; /* Closer to the bottom */
                        left: 0;
                        right: 0;
                        text-align: center;
                        font-size: 10px;
                        color: #9B9CA8; /* Grey */
                    }}
                    hr {{
                        border: 1px solid #E04F4F; /* Brand red */
                        margin: 20px 0;
                    }}
                    



                </style>
            </head>
            <body>
                <!-- Header -->
                <div class="header">
                    {f'{report_name} - {client_name}' if client_name else f'{report_name}'}
                </div>

                <!-- Logo -->
                <div class="logo">
                    <img src="{logo_path}" alt="Company Logo">
                </div>

                <!-- Content -->
                <div class="content">
                    {html_content}
                </div>
                
                <!-- Footer -->
                <div class="footer">
                    © 2024 Scandiweb | www.scandiweb.com
                </div>
            </body>
            </html>
            """
            
            html_file = os.path.join(user_folder, "temp_report.html")
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html_template)
            HTML(html_file).write_pdf(output_pdf)

            # Cleanup temp files
            os.remove(html_file)

            # Notify user
            st.write('\n\n')
            st.success("PDF generated successfully!")
            st.download_button("Download Report", data=open(output_pdf, "rb"), file_name=f"{report_name}.pdf")


    except Exception as e:
        st.error(f"An error occurred: {e}")
            
            
        