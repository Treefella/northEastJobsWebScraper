import tkinter as tk
from tkinter import ttk, messagebox
import requests
from bs4 import BeautifulSoup
import urllib3
import threading
import webbrowser

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class JobScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('North East Jobs Scraper')
        self.root.geometry('1200x700')

        self.jobs_data = []

        self.setup_ui()

    def setup_ui(self):
        # Top frame for controls
        control_frame = ttk.Frame(self.root, padding='10')
        control_frame.pack(fill='x')

        ttk.Label(control_frame, text='North East Jobs Scraper', font=('Arial', 14, 'bold')).pack(side='left')

        self.status_label = ttk.Label(control_frame, text='Ready')
        self.status_label.pack(side='right', padx=10)

        self.fetch_btn = ttk.Button(control_frame, text='Fetch Jobs', command=self.start_fetch)
        self.fetch_btn.pack(side='right')

        # Progress bar
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(fill='x', padx=10)

        # Table frame
        table_frame = ttk.Frame(self.root, padding='10')
        table_frame.pack(fill='both', expand=True)

        # Create treeview with columns
        columns = ('title', 'salary', 'location', 'category', 'closing', 'contract')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', selectmode='browse')

        # Define column headings and widths
        self.tree.heading('title', text='Job Title')
        self.tree.heading('salary', text='Salary')
        self.tree.heading('location', text='Location')
        self.tree.heading('category', text='Category')
        self.tree.heading('closing', text='Closing Date')
        self.tree.heading('contract', text='Contract')

        self.tree.column('title', width=350, minwidth=200)
        self.tree.column('salary', width=180, minwidth=100)
        self.tree.column('location', width=200, minwidth=100)
        self.tree.column('category', width=150, minwidth=100)
        self.tree.column('closing', width=100, minwidth=80)
        self.tree.column('contract', width=100, minwidth=80)

        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid layout for table
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Bind double-click to open job link
        self.tree.bind('<Double-1>', self.open_job_link)

        # Details frame at bottom
        details_frame = ttk.LabelFrame(self.root, text='Job Description', padding='10')
        details_frame.pack(fill='x', padx=10, pady=5)

        self.description_text = tk.Text(details_frame, height=5, wrap='word')
        self.description_text.pack(fill='x')

        # Bind selection to show description
        self.tree.bind('<<TreeviewSelect>>', self.show_description)

        # Bottom status bar
        status_frame = ttk.Frame(self.root, padding='5')
        status_frame.pack(fill='x')

        self.jobs_count_label = ttk.Label(status_frame, text='Jobs: 0')
        self.jobs_count_label.pack(side='left')

        ttk.Label(status_frame, text='Double-click a job to open in browser').pack(side='right')

    def start_fetch(self):
        self.fetch_btn.config(state='disabled')
        self.status_label.config(text='Fetching jobs...')
        self.progress.start()

        # Run in thread to keep UI responsive
        thread = threading.Thread(target=self.fetch_jobs, daemon=True)
        thread.start()

    def fetch_jobs(self):
        try:
            url = 'https://www.northeastjobs.org.uk/alljobs'
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

            resp = requests.get(url, headers=headers, verify=False, timeout=30)
            soup = BeautifulSoup(resp.text, 'html.parser')

            job_cards = soup.select('div.job-card-sub')
            self.jobs_data = []

            for card in job_cards:
                # Job title and link
                title_elem = card.select_one('h5.card-title a')
                title = title_elem.get_text(strip=True) if title_elem else 'N/A'
                link = title_elem['href'] if title_elem else ''

                # Closing date
                closing_date = card.select_one('span.font-weight-bold')
                closing = closing_date.get_text(strip=True) if closing_date else 'N/A'

                # Extract details from card body
                details = {}
                card_body = card.select_one('div.card-body')
                if card_body:
                    labels = card_body.select('span.item_label')
                    for label in labels:
                        key = label.get_text(strip=True).rstrip(':')
                        value_elem = label.find_next_sibling('span')
                        value = value_elem.get_text(strip=True) if value_elem else 'N/A'
                        details[key] = value

                # Short description
                desc_elem = card.select_one("[id*='lblShortDescription']")
                description = desc_elem.get_text(strip=True) if desc_elem else 'N/A'

                self.jobs_data.append({
                    'title': title,
                    'salary': details.get('Salary', 'N/A'),
                    'location': details.get('Employment Location', 'N/A'),
                    'category': details.get('Job category', 'N/A'),
                    'closing': closing,
                    'contract': details.get('Contract Type', 'N/A'),
                    'description': description,
                    'link': link
                })

            # Update UI from main thread
            self.root.after(0, self.update_table)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror('Error', f'Failed to fetch jobs: {e}'))
            self.root.after(0, self.reset_ui)

    def update_table(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add new items
        for job in self.jobs_data:
            self.tree.insert('', 'end', values=(
                job['title'],
                job['salary'],
                job['location'],
                job['category'],
                job['closing'],
                job['contract']
            ))

        self.jobs_count_label.config(text=f"Jobs: {len(self.jobs_data)}")
        self.reset_ui()

    def reset_ui(self):
        self.progress.stop()
        self.fetch_btn.config(state='normal')
        self.status_label.config(text='Ready')

    def show_description(self, event):
        selection = self.tree.selection()
        if selection:
            idx = self.tree.index(selection[0])
            if idx < len(self.jobs_data):
                self.description_text.delete('1.0', 'end')
                self.description_text.insert('1.0', self.jobs_data[idx]['description'])

    def open_job_link(self, event):
        selection = self.tree.selection()
        if selection:
            idx = self.tree.index(selection[0])
            if idx < len(self.jobs_data) and self.jobs_data[idx]['link']:
                webbrowser.open(self.jobs_data[idx]['link'])


if __name__ == '__main__':
    root = tk.Tk()
    app = JobScraperGUI(root)
    root.mainloop()
