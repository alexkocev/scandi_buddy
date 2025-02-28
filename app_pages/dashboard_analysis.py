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
from dotenv import load_dotenv

# Load environment variables from .env file (optional for local dev)
load_dotenv()

# Set your API keys
CLAUDE_KEY = os.getenv("CLAUDE_KEY_SW")
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
    md_content = re.sub(r"```markdown\n(.*?)\n```", convert_table_to_html, md_content, flags=re.DOTALL)
    md_content = re.sub(r"\|(.+?)\|\n\|(?:-+\|)+\n(.+?)(?=\n\n|\Z)", convert_table_to_html, md_content, flags=re.DOTALL)
    
    return markdown.markdown(md_content)


def convert_table_to_html(match):
    """
    Convert Markdown table into HTML table format.
    """
    table_text = match.group(1) if "```" in match.group(0) else match.group(0)
    rows = [row.strip() for row in table_text.strip().splitlines() if row.strip()]

    if not rows:
        return ""

    headers = [cell.strip() for cell in rows[0].split('|') if cell.strip()]
    data_rows = [
        [cell.strip() for cell in row.split('|') if cell.strip()]
        for row in rows[2:]  # Skip header separator line
    ]

    # Build HTML table
    html_table = '<table style="width:100%; border-collapse:collapse; border:1px solid #ddd;">'
    html_table += '<thead style="background-color:#f2f2f2;"><tr>'
    html_table += ''.join(f'<th style="padding:8px; text-align:left; border:1px solid #ddd;">{header}</th>' for header in headers)
    html_table += '</tr></thead><tbody>'

    for data_row in data_rows:
        html_table += '<tr>'
        html_table += ''.join(f'<td style="padding:8px; text-align:left; border:1px solid #ddd;">{cell}</td>' for cell in data_row)
        html_table += '</tr>'

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
    if uploaded_file is not None:
        st.session_state.pdf_bytes = uploaded_file.read()
        
        try:            
            with st.spinner("Estimation in progress..."):
                # Read PDF and calculate number of pages
                pdf_reader = PdfReader(io.BytesIO(st.session_state.pdf_bytes))
                num_pages = len(pdf_reader.pages)
                if num_pages == 0:
                    st.error("This PDF appears to have no pages.")
                    st.stop()
                    
                estimated_time, estimated_cost = estimate_analysis(num_pages)

            col1, col2 = st.columns(2)
            with col1:
                if num_pages == 1:
                    st.metric(f"Estimated Time for {num_pages} page", estimated_time,
                            help="Includes page analysis but excludes summary generation")
                else:
                    st.metric(f"Estimated Time for {num_pages} pages", estimated_time,
                            help="Includes page analysis but excludes summary generation")   
                      
            with col2:
                if num_pages == 1:
                    st.metric(f"Estimated Cost for {num_pages} page", estimated_cost,
                            help="Based on API usage and complexity")
                else:
                    st.metric(f"Estimated Cost for {num_pages} pages", estimated_cost,
                            help="Based on API usage and complexity")    

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        
        estimated_time, estimated_cost = estimate_analysis(1)

        col1, col2 = st.columns(2)
        with col1:
            st.metric(f"Estimated Time for 1 page", estimated_time,
                    help="Includes page analysis but excludes summary generation")
        with col2:
            st.metric("Estimated Cost for 1 page", estimated_cost,
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



# Check if there is a generated report in the session state and display it
if "output_pdf" in st.session_state and st.session_state.output_pdf:
    st.success("Report generated successfully!")

    # Display Markdown content
    with st.expander("🔍 Show Report", expanded=False):
        if "md_content" in st.session_state and st.session_state.md_content:
            st.markdown(st.session_state.md_content, unsafe_allow_html=True)
        else:
            st.write("No output available. Please run the analysis.")

    with st.expander("🔍 Show Markdown", expanded=False):
        if st.session_state.get("md_content"):
            st.code(st.session_state.md_content)
        else:
            st.write("No output available. Please run the analysis.")         
        

    st.download_button(
        "📄 Download Report",
        data=open(st.session_state.output_pdf, "rb"),
        file_name=f"{st.session_state.get('report_name', 'Dashboard Analysis')} - {st.session_state.get('client_name', '')}.pdf"
        if st.session_state.get('client_name') else f"{st.session_state.get('report_name', 'Dashboard Analysis')}.pdf"
    )
    
    

if run_analysis:
    # Reset session state variables to clear previous outputs
    st.session_state.output_pdf = None
    st.session_state.md_content = None
    st.session_state.report_name = None
    st.session_state.client_name = None


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

            ### Formatting:
            - Please, write the report using markdown.
            - Avoid using number lists unless you want to show a step by step process (rarely used).
            - If using bullet points, use - instead of *
            - Use this template to build tables:
            | Provider | Transactions | Revenue Share |
            |----------|-------------|---------------|
            | Makecommerce | 7,548 (96%) | 678.45K € (94%) |
            | Inbank | <1% | <1% |

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
    
        ### Formatting:
        - Please, write the report using markdown.
        - Avoid using number lists unless you want to show a step by step process (rarely used).
        - If using bullet points, use - instead of *
        - Use this template to build tables:
        | Provider | Transactions | Revenue Share |
        |----------|-------------|---------------|
        | Makecommerce | 7,548 (96%) | 678.45K € (94%) |
        | Inbank | <1% | <1% |


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

            # html_content = markdown.markdown(md_content)
            
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
                    h2 {{
                        font-family: 'Secular One', sans-serif;
                        color: #E04F4F; /* Brand red */
                        margin: 25px 0 15px; /* Top, right/left, bottom */
                    }}

                    h3 {{
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
                        font-size: 12px;

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
            os.remove(pdf_path)

            # Save results to session state
            st.session_state.md_content = md_content
            st.session_state.output_pdf = output_pdf
            st.session_state.report_name = report_name
            st.session_state.client_name = client_name

    
    
            # Notify user and display outputs
            st.write('\n\n')
            st.success("Report generated successfully!")
                # st.download_button(
                    # "📄 Download Report",
                    # data=open(st.session_state.output_pdf, "rb"),
                    # file_name=f"{st.session_state.get('report_name', 'Dashboard Analysis')} - {st.session_state.get('client_name', '')}.pdf"
                    # if st.session_state.get('client_name') else f"{st.session_state.get('report_name', 'Dashboard Analysis')}.pdf"
                # )

            # Display Markdown content
            with st.expander("🔍 Show Report", expanded=False):
                if st.session_state.get("md_content"):
                    st.markdown(st.session_state.md_content, unsafe_allow_html=True)
                else:
                    st.write("No output available. Please run the analysis.")
                    
            with st.expander("🔍 Show Markdown", expanded=False):
                if st.session_state.get("md_content"):
                    st.code(st.session_state.md_content)
                else:
                    st.write("No output available. Please run the analysis.")         
                    
            st.download_button(
                "📄 Download Report",
                data=open(st.session_state.output_pdf, "rb"),
                file_name=f"{report_name} - {client_name}.pdf" if client_name else f"{report_name}.pdf"
            )
            
            # Notify user
            # st.write('\n\n')
            # st.success("Report generated successfully!")
            # st.download_button("📄 Download Report", data=open(st.session_state.output_pdf, "rb"), file_name=f"{report_name} - {client_name}.pdf" if client_name else f"{report_name}.pdf")

            # Final expander to show Markdown output
            # with st.expander("🔍 Show Report", expanded=False):
                # if run_analysis:
                    # if st.session_state.md_content:
                        # st.markdown(st.session_state.md_content, unsafe_allow_html=True)
                    # else:
                        # st.write("No output available. Please run the analysis.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
            
            
        