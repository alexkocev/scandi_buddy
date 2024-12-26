import streamlit as st
import base64
import requests
import io
import json
from datetime import datetime
import os
import markdown
import re
from weasyprint import HTML
import time as time
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
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


st.title("🦉")
st.header("Tracking Report Creator")
st.markdown("💡 Provide all Notion pages and Excel requirements sheets from a client, and let the Buddy generate a tracking report.")


st.write("")
st.write("")




# Excel file
col1, col2 = st.columns([3, .5])
with col1:
    uploaded_excel = st.file_uploader(
        "Upload the Excel requirements file (xlsx)", 
        type=["xlsx"],
        accept_multiple_files=True
        )

with col2:
    st.write("")
    st.write("")
    st.write("")
    
    st.link_button(label="Help", 
                   url="https://www.loom.com/share/79ec5c89500d494e93567256eabc251f?sid=645dacc4-0b56-43e5-9272-10ad462af59c",
                   help="How to download all excel files from Requirements",
                   icon="🤔")
    

# Notion pages
col1, col2 = st.columns([3, .5])
with col1:
    uploaded_notion_files = st.file_uploader(
        "Upload your Notion pages (select multiple if needed) (md)",
        type=["md"],
        accept_multiple_files=True
    )
with col2:
    st.write("")
    st.write("")
    st.write("")
    st.link_button(label="Help",
                   url="(https://www.loom.com/share/65212eb31dcb47679df7f913e09c7579?sid=cbd21cb5-590f-497b-8000-10f60dc29af9",
                   help="How to download all Notion pages from a client using Markdown format",
                   icon="🤔")




# Parameters
with st.expander("⚙️ Additional Parameters", expanded=False):
    custom_request = st.text_area(
        "Custom request (optional)",
        value="",
        placeholder="Add a section on GTM setup.",
        height=130
    )

    # Emoji Toggle
    add_emoji = st.checkbox("Add Emojis to the Report?", value=False)


st.write("")
st.write("")
st.write("")
st.write("")


def markdown_to_html(md_content):
    # Replace Markdown tables with proper HTML tables
    # md_content = re.sub(r"\|(.+?)\|\n\|(?:-+\|)+\n(.+?)(?=\n\n|\Z)", convert_table_to_html, md_content, flags=re.DOTALL)

    # Replace numbered lists with bullet points while keeping structure
    # md_content = re.sub(r"(\d+)\.\s+\*\*(.+?)\*\*", r"<ul><li><strong>\2</strong></li></ul>", md_content)
    # md_content = re.sub(r"(\d+)\.\s+(.+)", r"<li>\2</li>", md_content)

    # Remove '```markdown' code block artifacts
    md_content = re.sub(r"```(?:markdown)?\n(.*?)\n```", r"```\1```", md_content, flags=re.DOTALL)

    # Replace code blocks with <pre><code> for clean indentation and syntax highlighting
    md_content = re.sub(r"```(.*?)\n(.*?)```", r"<pre><code class='\1'>\2</code></pre>", md_content, flags=re.DOTALL)

    # Remove stray '```' left behind
    md_content = re.sub(r"```", "", md_content)

    # Properly handle checkboxes for lists ([ ] or [x])
    md_content = re.sub(r"- \[ \] (.+)", r'<li><input type="checkbox" disabled> \1</li>', md_content)
    md_content = re.sub(r"- \[x\] (.+)", r'<li><input type="checkbox" disabled checked> \1</li>', md_content)
    md_content = re.sub(r"(<li><input.*?</li>)", r"<ul>\1</ul>", md_content, flags=re.DOTALL)




    # Clean up unintended bullet points from headers (e.g., `- Header`)
    # md_content = re.sub(r"^\s*-\s+(?=\*\*)", "", md_content, flags=re.MULTILINE)
    # md_content = re.sub(r"^\s*-\s+(?=#)", "", md_content, flags=re.MULTILINE)
   
    # Convert Markdown to HTML
    # html_content = markdown.markdown(md_content, extensions=['tables']) 
    html_content = markdown.markdown(md_content, extensions=["tables", "fenced_code", "nl2br"])

    # return markdown.markdown(md_content)
    return html_content

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




def combine_uploaded_markdown_files(file_tuples):
    """
    Combine the content of multiple markdown files (already read into memory) into one string.
    file_tuples should be a list of (filename, bytes_content).
    """
    combined_content = ""
    for name, file_bytes in file_tuples:
        if name.endswith(".md"):
            content = file_bytes.decode("utf-8")
            combined_content += f"### {name}\n\n{content}\n\n---\n\n"
    return combined_content


def excel_sheets_to_text(excel_file_tuples):
    """
    Converts all sheets from multiple Excel files (in memory) into a structured text format.
    excel_file_tuples should be a list of (filename, bytes_content).
    """
    combined_text = ""
    for name, file_bytes in excel_file_tuples:
        excel_data = pd.read_excel(io.BytesIO(file_bytes), sheet_name=None)
        for sheet_name, data in excel_data.items():
            combined_text += f"### Excel File: {name} - Sheet: {sheet_name}\n\n"
            sheet_text = data.to_csv(index=False, sep=",")
            combined_text += sheet_text + "\n\n---\n\n"
    return combined_text



# -- Estimation Logic for Chunks --
def estimate_analysis(num_chunks):
    cost_per_chunk = 0.054
    time_per_chunk = 18.55  # seconds

    total_cost = num_chunks * cost_per_chunk
    total_time = num_chunks * time_per_chunk

    if total_time < 60:
        time_display = f"{total_time:.2f} seconds"
    elif total_time < 3600:
        time_display = f"{total_time/60:.2f} minutes"
    else:
        time_display = f"{total_time/3600:.2f} hours"

    cost_display = f"${total_cost:.2f}"
    return time_display, cost_display

formatted_chunks = None
estimator_container = st.container(border=True)

with estimator_container:
    # estimation_progress_bar = st.empty()

    if uploaded_excel and uploaded_notion_files:
        st.session_state.excel_files = [(f.name, f.read()) for f in uploaded_excel]
        st.session_state.notion_files = [(f.name, f.read()) for f in uploaded_notion_files]

        try:
            with st.spinner("Estimation in progress..."):
                # estimation_progress_bar.progress(10, text="Estimation in progress...")
                # Combine markdown and excel content
                combined_message = combine_uploaded_markdown_files(st.session_state.notion_files)
                # estimation_progress_bar.progress(20, text="Estimation in progress...")
                all_sheets_text = excel_sheets_to_text(st.session_state.excel_files)
                # estimation_progress_bar.progress(40, text="Estimation in progress...")
                combined_input = combined_message + "\n" + all_sheets_text
                # estimation_progress_bar.progress(60, text="Estimation in progress...")
                # Split the text into chunks
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=60000,  
                    chunk_overlap=500,  
                )
                chunks = text_splitter.split_text(combined_input)
                # estimation_progress_bar.progress(80, text="Estimation in progress...")
                formatted_chunks = [f"Section {i+1}:\n{c.strip()}" for i,c in enumerate(chunks)]
                st.session_state.formatted_chunks = formatted_chunks
                num_chunks = len(st.session_state.formatted_chunks)
                # Estimate cost/time
                estimated_time, estimated_cost = estimate_analysis(num_chunks)
                # estimation_progress_bar.progress(100, text="Estimation complete")
            

            if num_chunks == 1:
                st.success(f"Estimation for 1 chunk")
            else:
                st.success(f"Estimation for {num_chunks} chunks")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Estimated Time", estimated_time, help="Time to process all chunks")
            with col2:
                st.metric("Estimated Cost", estimated_cost, help="Based on API usage")
        
        except Exception as e:
            st.error(f"An error occurred: {e}")
            
    else:
        
        estimated_time, estimated_cost = estimate_analysis(1)
        st.success(f"Estimation for 1 chunk")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Estimated Time", estimated_time, help="Time to process all chunks")
        with col2:
            st.metric("Estimated Cost", estimated_cost, help="Based on API usage")
        








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
                st.error(f"""No way, max attempts reached. Come back and retry in a few minutes \n
                         Error after {max_attempts} attempts: {str(e)} """)
                return f"Error after {max_attempts} attempts: {str(e)}"



# Create a placeholder for the progress bar
progress_placeholder = st.empty()

# Create a button to trigger the analysis
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
        background-color: #D03F3F; 
        color: white; 
    }
    </style>
    """,
    unsafe_allow_html=True
)

with col2:
    run_analysis = st.button("Run Analysis")


if run_analysis:
    if "formatted_chunks" not in st.session_state:
        st.error("Please upload both Excel files and Notion pages before launching the analysis.")
        st.stop()

    try:
        formatted_chunks = st.session_state.formatted_chunks
        num_chunks = len(formatted_chunks)
        
        # Generate a unique folder for each analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        user_folder = f"temp_analysis/{timestamp}"
        os.makedirs(user_folder, exist_ok=True)

        # Analyze each chunk
        chunk_analyses = []
        total_steps = num_chunks + 1
        for i, chunk in enumerate(formatted_chunks, 1):
            progress = i / total_steps
            progress_placeholder.progress(progress, text=f"Analyzing chunk {i}...")

            chunk_analysis_prompt = f"""
            Analyze the following chunk of data in detail:

            {chunk}

            ### Analysis Requirements:
            1. **Contextual Insights**:
            - Identify the main themes, patterns, and anomalies within this chunk.
            - Highlight any key metrics, trends, or figures that stand out.

            2. **Relevance and Challenges**:
            - Evaluate how the information in this chunk contributes to the broader project goals.
            - Note any inconsistencies, gaps, or challenges present in the data.

            3. **Recommendations**:
            - Provide actionable recommendations based on the analysis.
            - Suggest tools, methods, or adjustments that could enhance the data's utility.

            4. **Cross-Chapter Connection**:
            - Indicate potential links or overlaps with other sections of the dataset.
            - Highlight any dependencies or contextual connections.

            {f'- Custom request is: {custom_request}' if custom_request else ''}
            {f'- This is the first chunk of the analysis. Please extract the following and display as follows: Client Name: ... - Report Name: .... If either of these is not clearly provided, mention that it is unavailable.' if i == 1 else ''}

            ### Formatting:
            - Use clear markdown with subheadings.
            - Maintain a professional tone.
            - Keep within 1,000 tokens for the response.
            """

            chunk_payload = {
                'model': 'claude-3-5-sonnet-20241022',
                'max_tokens': 8192,
                'messages': [
                    {
                        'role': 'user',
                        'content': chunk_analysis_prompt
                    }
                ]
            }

            response = process_with_retry(headers, chunk_payload)
            if isinstance(response, str) and response.startswith("Error"):
                st.error("Processing failed for a chunk.")
                continue
            else:
                chunk_analyses.append(response)

        # Prepare the final analysis
        combined_chunk_insights = "\n\n".join(chunk_analyses)

        # Extract client_name and report_name from the first chunk analysis if possible
        # Assuming first chunk analysis might contain "Client Name:" and "Report Name:"
        first_chunk_analysis = chunk_analyses[0] if chunk_analyses else ""
        client_name_match = re.search(r"Client Name:\s*([^\n]+)", first_chunk_analysis, re.IGNORECASE)
        report_name_match = re.search(r"Report Name:\s*([^\n]+)", first_chunk_analysis, re.IGNORECASE)

        client_name = client_name_match.group(1).strip() if client_name_match else ""
        report_name = report_name_match.group(1).strip() if report_name_match else "Dashboard Analysis"

        progress_placeholder.progress(num_chunks / total_steps, text="Combining final report...")

        final_analysis_prompt=f"""
        Combine the detailed analyses from the individual chunks into a comprehensive final report.

        ### Output Requirements:
        1. **Executive Summary**:
        - Concisely summarize the project's objectives, key findings, and insights derived from the data.

        2. **Integrated Data Insights**:
        - Synthesize findings from all chunks, highlighting major themes, trends, and gaps.
        - Include any cross-chunk dependencies or overarching insights.

        3. **Strategic Recommendations**:
        - Provide actionable strategies based on the combined analyses.
        - Suggest next steps, tools, or methodologies to address identified challenges.

        4. **Visualization and Presentation**:
        - Propose key visualizations (e.g., charts, graphs) that could illustrate the findings effectively.
        - Describe the data and insights these visualizations should convey.

        5. **Comprehensive Report**:
        - Adhere to the provided template structure.
        - Ensure the final markdown document is between 100,000 and 200,000 characters.


        ### Notes:
        - Use markdown formatting with appropriate headings and subheadings.
        - Maintain a cohesive narrative throughout the report.
        - Output length: 100,000 to 200,000 characters
        - Do not include extra instructions like "I'll help combine these analyses..." or "[End of Report]" in the final output.
        - Emoji Usage: {'Enabled' if add_emoji else 'Disabled'}
        {f'- Custom request is: {custom_request}' if custom_request else ''}

        ----
        ### Analysis from each Chunk:
        {combined_chunk_insights}
        """

        final_analysis_payload = {
            'model': 'claude-3-5-sonnet-20241022',
            'max_tokens': 8192,
            'messages': [
                {
                    'role': 'user',
                    'content': final_analysis_prompt
                }
            ]
        }

        final_response = process_with_retry(headers, final_analysis_payload)
        if isinstance(final_response, str) and final_response.startswith("Error"):
            st.error("Processing failed for final analysis.")
        else:
            # Final progress update to 100%
            progress_placeholder.progress(1.0, text="Generating PDF report...")
                        
            # Generate PDF report
            logo_path = os.path.abspath("./images/SW_logo.jpeg")
            output_pdf = os.path.join(user_folder, f"{report_name}.pdf")
            
            md_content = final_response
            # Remove any extraneous lines if needed
            # (In case the model added any disclaimers)
            # E.g., ensure no "End of Report" line:
            md_content = re.sub(r"(?i)\[End of Report\]", "", md_content)
            # html_content = markdown.markdown(md_content, output_format="html5")
            html_content = markdown_to_html(md_content)

            # st.write('md_content')
            # st.code(md_content)
            
            # st.write('html_content')
            # st.code(html_content)
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
                    






                    body {{
                        font-family: 'Inter', 'Liberation Sans', 'DejaVu Sans', sans-serif;
                        font-size: 12px;
                        line-height: 1.4;
                        color: #10132C;
                        margin: 20px;
                        background-color: #FFFFFF;
                    }}
                    h1 {{
                        font-family: 'Secular One', sans-serif;
                        color: #10132C;
                        margin: 30px 0 20px;
                    }}
                    h2, h3 {{
                        font-family: 'Secular One', sans-serif;
                        color: #E04F4F;
                        margin: 25px 0 15px;
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
                        top: -40px;
                        right: -40px;
                    }}
                    .header {{
                        position: absolute;
                        top: -35px;
                        left: -20px;
                        font-size: 10px;
                        color: #E04F4F;
                    }}
                    .footer {{
                        position: fixed;
                        bottom: -30px;
                        left: 0;
                        right: 0;
                        text-align: center;
                        font-size: 10px;
                        color: #9B9CA8;
                    }}
                    hr {{
                        border: 1px solid #E04F4F;
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
