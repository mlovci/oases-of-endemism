import os
import re
import markdown

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Oases of Endemism: Ecological Conservation & Analysis</title>
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <!-- FontAwesome for Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        /* Color Tokens & Variables */
        :root {
            --bg-color: #0f172a;
            --text-color: #e2e8f0;
            --text-muted: #94a3b8;
            --container-bg: rgba(30, 41, 59, 0.6);
            --border-color: rgba(255, 255, 255, 0.08);
            --header-text: #f8fafc;
            --accent-primary: #10b981; /* Emerald */
            --accent-secondary: #0ea5e9; /* Sky Blue */
            --accent-hover: #059669;
            --alert-note-bg: rgba(59, 130, 246, 0.15);
            --alert-note-border: #3b82f6;
            --alert-warning-bg: rgba(245, 158, 11, 0.15);
            --alert-warning-border: #f59e0b;
            --code-bg: #1e293b;
            --code-color: #cbd5e1;
            --sidebar-bg: rgba(15, 23, 42, 0.8);
            --shadow-color: rgba(0, 0, 0, 0.3);
            --font-main: 'Inter', sans-serif;
            --font-header: 'Outfit', sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
            --transition-speed: 0.3s;
        }

        [data-theme="light"] {
            --bg-color: #f8fafc;
            --text-color: #334155;
            --text-muted: #64748b;
            --container-bg: rgba(255, 255, 255, 0.85);
            --border-color: rgba(0, 0, 0, 0.06);
            --header-text: #0f172a;
            --accent-primary: #059669; /* Dark Emerald */
            --accent-secondary: #0284c7; /* Dark Sky Blue */
            --accent-hover: #047857;
            --alert-note-bg: rgba(59, 130, 246, 0.08);
            --alert-note-border: #2563eb;
            --alert-warning-bg: rgba(245, 158, 11, 0.08);
            --alert-warning-border: #d97706;
            --code-bg: #f1f5f9;
            --code-color: #1e293b;
            --sidebar-bg: rgba(241, 245, 249, 0.9);
            --shadow-color: rgba(0, 0, 0, 0.08);
        }

        /* Basic Reset */
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: var(--font-main);
            color: var(--text-color);
            background-color: var(--bg-color);
            line-height: 1.6;
            display: flex;
            min-height: 100vh;
            transition: background-color var(--transition-speed), color var(--transition-speed);
        }

        /* Sidebar Styling */
        aside {
            width: 320px;
            background-color: var(--sidebar-bg);
            border-right: 1px solid var(--border-color);
            padding: 40px 24px;
            display: flex;
            flex-direction: column;
            position: fixed;
            top: 0;
            bottom: 0;
            left: 0;
            z-index: 100;
            backdrop-filter: blur(12px);
            transition: background-color var(--transition-speed), border-color var(--transition-speed);
        }

        .sidebar-header {
            margin-bottom: 40px;
        }

        .sidebar-header h1 {
            font-family: var(--font-header);
            font-size: 24px;
            font-weight: 700;
            color: var(--header-text);
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }

        .sidebar-header p {
            font-size: 13px;
            color: var(--text-muted);
            line-height: 1.4;
        }

        .meta-list {
            margin-bottom: auto;
        }

        .meta-item {
            margin-bottom: 20px;
            font-size: 13px;
        }

        .meta-label {
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            font-size: 10px;
            letter-spacing: 1px;
            margin-bottom: 4px;
        }

        .meta-value {
            color: var(--header-text);
            font-family: var(--font-header);
            font-weight: 500;
        }
        
        .meta-value a {
            color: var(--accent-secondary);
            text-decoration: none;
            transition: color 0.2s;
        }
        
        .meta-value a:hover {
            color: var(--accent-primary);
            text-decoration: underline;
        }

        .theme-switch-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-top: 20px;
            border-top: 1px solid var(--border-color);
        }

        .theme-label {
            font-size: 13px;
            font-weight: 500;
            color: var(--text-color);
        }

        .theme-toggle-btn {
            background: none;
            border: 1px solid var(--border-color);
            color: var(--header-text);
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: background-color 0.2s, border-color 0.2s;
        }

        .theme-toggle-btn:hover {
            background-color: var(--border-color);
        }

        /* Main Content Styling */
        main {
            margin-left: 320px;
            flex: 1;
            padding: 60px 80px;
            max-width: 1200px;
            display: flex;
            flex-direction: column;
            gap: 40px;
        }

        /* Navigation Tabs */
        .nav-tabs {
            display: flex;
            gap: 8px;
            padding: 6px;
            background-color: var(--code-bg);
            border-radius: 12px;
            align-self: flex-start;
            border: 1px solid var(--border-color);
        }

        .tab-btn {
            background: none;
            border: none;
            color: var(--text-muted);
            font-family: var(--font-header);
            font-weight: 600;
            font-size: 14px;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            transition: background-color 0.2s, color 0.2s;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .tab-btn:hover {
            color: var(--header-text);
        }

        .tab-btn.active {
            background-color: var(--bg-color);
            color: var(--accent-primary);
            box-shadow: 0 4px 6px -1px var(--shadow-color);
        }

        /* Content Sections */
        .content-section {
            display: none;
            background-color: var(--container-bg);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 48px;
            backdrop-filter: blur(12px);
            box-shadow: 0 10px 30px -10px var(--shadow-color);
            animation: fadeIn 0.4s ease;
        }

        .content-section.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Markdown Styling */
        h1, h2, h3, h4 {
            font-family: var(--font-header);
            color: var(--header-text);
            margin-top: 1.8em;
            margin-bottom: 0.6em;
            line-height: 1.3;
        }

        h1 { font-size: 36px; font-weight: 800; border-bottom: 1.5px solid var(--border-color); padding-bottom: 12px; margin-top: 0; }
        h2 { font-size: 26px; font-weight: 700; border-bottom: 1px solid var(--border-color); padding-bottom: 8px; }
        h3 { font-size: 20px; font-weight: 600; }
        h4 { font-size: 16px; font-weight: 600; }

        p {
            margin-bottom: 1.4em;
            font-size: 15px;
            color: var(--text-color);
        }

        ul, ol {
            margin-bottom: 1.5em;
            padding-left: 24px;
            font-size: 15px;
        }

        li {
            margin-bottom: 0.6em;
        }

        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 2.5em 0;
            font-size: 14px;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px var(--shadow-color);
        }

        th, td {
            padding: 14px 18px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }

        th {
            background-color: var(--code-bg);
            color: var(--header-text);
            font-family: var(--font-header);
            font-weight: 600;
        }

        tr:last-child td {
            border-bottom: none;
        }

        tr:hover td {
            background-color: rgba(255, 255, 255, 0.02);
        }
        
        [data-theme="light"] tr:hover td {
            background-color: rgba(0, 0, 0, 0.01);
        }

        /* Fenced Code & Monospace */
        code {
            font-family: var(--font-mono);
            font-size: 13.5px;
            background-color: var(--code-bg);
            color: var(--code-color);
            padding: 2px 6px;
            border-radius: 4px;
        }

        pre {
            background-color: var(--code-bg);
            padding: 20px;
            border-radius: 12px;
            overflow-x: auto;
            margin: 1.5em 0;
            border: 1px solid var(--border-color);
        }

        pre code {
            padding: 0;
            background-color: transparent;
            color: var(--code-color);
            display: block;
        }

        /* Images & Visual Cards */
        img {
            max-width: 100%;
            height: auto;
            border-radius: 12px;
            display: block;
            margin: 1.5em auto;
            border: 1px solid var(--border-color);
            box-shadow: 0 10px 20px -10px var(--shadow-color);
            cursor: pointer;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        img:hover {
            transform: scale(1.02);
            box-shadow: 0 15px 30px -15px var(--shadow-color);
        }

        /* Inline Figures Captions */
        img + em, p > img + em {
            display: block;
            text-align: center;
            font-size: 13px;
            color: var(--text-muted);
            margin-top: -10px;
            margin-bottom: 20px;
            font-style: italic;
        }

        /* Alert/Callout Blocks */
        blockquote {
            border-left: 4px solid var(--accent-secondary);
            background-color: var(--code-bg);
            padding: 16px 20px;
            margin: 1.5em 0;
            border-radius: 0 12px 12px 0;
        }

        blockquote p {
            margin-bottom: 0;
            font-style: italic;
        }

        /* Lightbox Container */
        .lightbox {
            display: none;
            position: fixed;
            z-index: 1000;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(8px);
            justify-content: center;
            align-items: center;
            cursor: zoom-out;
            animation: fadeIn 0.2s ease;
        }

        .lightbox img {
            max-width: 90%;
            max-height: 90%;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
            cursor: default;
        }

        .lightbox-caption {
            position: absolute;
            bottom: 30px;
            color: #fff;
            font-family: var(--font-header);
            font-size: 16px;
            font-weight: 500;
            text-align: center;
            background: rgba(0, 0, 0, 0.6);
            padding: 8px 24px;
            border-radius: 20px;
        }

        /* Responsive Design */
        @media (max-width: 1024px) {
            body {
                flex-direction: column;
            }
            aside {
                position: relative;
                width: 100%;
                border-right: none;
                border-bottom: 1px solid var(--border-color);
                padding: 30px;
            }
            main {
                margin-left: 0;
                padding: 40px 24px;
            }
        }
    </style>
    <!-- MathJax for LaTeX equations -->
    <script>
        window.MathJax = {
            tex: {
                inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
                displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
                processEscapes: true
            }
        };
    </script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>

    <!-- Sidebar Panel -->
    <aside>
        <div class="sidebar-header">
            <h1>Oases of Endemism</h1>
            <p>Regional aquifer desert springs serve as biodiversity hotspots in the Great Basin & Mojave Deserts.</p>
        </div>

        <div class="meta-list">
            <div class="meta-item">
                <div class="meta-label">Primary Author</div>
                <div class="meta-value">Matthew J. Forrest</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Original Publication</div>
                <div class="meta-value">Limnology and Oceanography (2026)</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">DOI / Citation</div>
                <div class="meta-value"><a href="https://doi.org/10.1002/lno.70414" target="_blank">10.1002/lno.70414</a></div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Interactive Platform</div>
                <div class="meta-value">Google DeepMind Antigravity</div>
            </div>
        </div>

        <div class="theme-switch-container">
            <span class="theme-label">Switch Theme</span>
            <button class="theme-toggle-btn" id="theme-toggle">
                <i class="fa-solid fa-moon"></i> <span>Dark Mode</span>
            </button>
        </div>
    </aside>

    <!-- Main Content Panel -->
    <main>
        <!-- Navigation Bar -->
        <nav class="nav-tabs">
            <button class="tab-btn active" onclick="switchTab('results-tab')">
                <i class="fa-solid fa-chart-line"></i> Scientific Findings
            </button>
            <button class="tab-btn" onclick="switchTab('methods-tab')">
                <i class="fa-solid fa-gears"></i> Methodology
            </button>
            <button class="tab-btn" onclick="switchTab('walkthrough-tab')">
                <i class="fa-solid fa-clipboard-check"></i> Verification Log
            </button>
        </nav>

        <!-- Findings Section (results.md) -->
        <section id="results-tab" class="content-section active">
            {RESULTS_HTML}
        </section>

        <!-- Methodology Section (methods.md) -->
        <section id="methods-tab" class="content-section">
            {METHODS_HTML}
        </section>

        <!-- Verification Section (walkthrough.md) -->
        <section id="walkthrough-tab" class="content-section">
            {WALKTHROUGH_HTML}
        </section>
    </main>

    <!-- Full Screen Lightbox -->
    <div class="lightbox" id="lightbox" onclick="closeLightbox()">
        <img src="" alt="" onclick="event.stopPropagation()">
        <div class="lightbox-caption" id="lightbox-caption"></div>
    </div>

    <!-- JavaScript Navigation Logic -->
    <script>
        function switchTab(tabId) {
            // Hide all sections
            document.querySelectorAll('.content-section').forEach(section => {
                section.classList.remove('active');
            });
            // Deactivate all buttons
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });

            // Show target section
            document.getElementById(tabId).classList.add('active');
            
            // Find the active tab button and highlight it
            const activeIndex = ['results-tab', 'methods-tab', 'walkthrough-tab'].indexOf(tabId);
            document.querySelectorAll('.tab-btn')[activeIndex].classList.add('active');

            // Scroll window to top of content
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        // Theme Toggle Logic
        const themeToggle = document.getElementById('theme-toggle');
        const htmlElement = document.documentElement;

        themeToggle.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-theme') || 'dark';
            let newTheme = 'dark';
            if (currentTheme === 'dark') {
                newTheme = 'light';
                themeToggle.innerHTML = '<i class="fa-solid fa-sun"></i> <span>Light Mode</span>';
            } else {
                newTheme = 'dark';
                themeToggle.innerHTML = '<i class="fa-solid fa-moon"></i> <span>Dark Mode</span>';
            }
            htmlElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });

        // Set default theme from localStorage
        const savedTheme = localStorage.getItem('theme') || 'dark';
        htmlElement.setAttribute('data-theme', savedTheme);
        if (savedTheme === 'light') {
            themeToggle.innerHTML = '<i class="fa-solid fa-sun"></i> <span>Light Mode</span>';
        }

        // Lightbox Logic for Images
        document.querySelectorAll('img').forEach(img => {
            img.addEventListener('click', () => {
                const lightbox = document.getElementById('lightbox');
                const lightboxImg = lightbox.querySelector('img');
                const caption = document.getElementById('lightbox-caption');

                lightboxImg.src = img.src;
                caption.textContent = img.alt || img.getAttribute('title') || 'Interactive Figure';
                lightbox.style.display = 'flex';
            });
        });

        function closeLightbox() {
            document.getElementById('lightbox').style.display = 'none';
        }
    </script>
</body>
</html>
"""

def read_md(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def convert_to_html(md_text):
    # Enable extensions: tables, fenced_code, toc
    html = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'toc'])
    
    # Replace absolute image paths in both formats:
    # 1. /path/to/Oases of Endemism/figures/name.png
    html = re.sub(
        r'src=".*?/Oases of Endemism/figures/([a-zA-Z0-9_\-\.]+)\.png"',
        r'src="figures/\1.png"',
        html
    )
    html = re.sub(
        r'href=".*?/Oases of Endemism/figures/([a-zA-Z0-9_\-\.]+)\.png"',
        r'href="figures/\1.png"',
        html
    )
    
    # 2. file:///path/to/Oases of Endemism/figures/name.png
    html = re.sub(
        r'src="file:///.*?/Oases of Endemism/figures/([a-zA-Z0-9_\-\.]+)\.png"',
        r'src="figures/\1.png"',
        html
    )
    html = re.sub(
        r'href="file:///.*?/Oases of Endemism/figures/([a-zA-Z0-9_\-\.]+)\.png"',
        r'href="figures/\1.png"',
        html
    )
    
    # 3. Brain directory figure paths conversion
    html = re.sub(
        r'src=".*?/\.gemini/antigravity-ide/brain/[a-zA-Z0-9_\-]+/figures/([a-zA-Z0-9_\-\.]+)\.png"',
        r'src="figures/\1.png"',
        html
    )
    html = re.sub(
        r'href=".*?/\.gemini/antigravity-ide/brain/[a-zA-Z0-9_\-]+/figures/([a-zA-Z0-9_\-\.]+)\.png"',
        r'href="figures/\1.png"',
        html
    )
    
    # 4. PDF and Excel links translation (file:/// or absolute)
    html = re.sub(
        r'href="(?:file:///.*?/Oases of Endemism/|.*?/Oases of Endemism/)figures/([a-zA-Z0-9_\-\.]+)\.pdf"',
        r'href="figures/\1.pdf"',
        html
    )
    html = re.sub(
        r'href="(?:file:///.*?/Oases of Endemism/|.*?/Oases of Endemism/)([a-zA-Z0-9_\-\.]+)\.xlsx"',
        r'href="\1.xlsx"',
        html
    )
    
    # 5. Clean up raw file scheme links to other markdown files (making them relative)
    html = re.sub(
        r'href="file:///.*?/Oases of Endemism/([a-zA-Z0-9_\-\.]+)\.md"',
        r'href="#\1"',  # Link to section/tab conceptually
        html
    )
    
    return html

def main():
    print("Compiling markdown articles to publication.html...")
    
    # Load markdown documents
    results_md = read_md('results.md')
    methods_md = read_md('methods.md')
    walkthrough_md = read_md('walkthrough.md')
    
    # Convert markdown to HTML
    results_html = convert_to_html(results_md)
    methods_html = convert_to_html(methods_md)
    walkthrough_html = convert_to_html(walkthrough_md)
    
    # Format template using replace() to avoid CSS/JS brace escaping issues
    compiled_html = HTML_TEMPLATE.replace('{RESULTS_HTML}', results_html)
    compiled_html = compiled_html.replace('{METHODS_HTML}', methods_html)
    compiled_html = compiled_html.replace('{WALKTHROUGH_HTML}', walkthrough_html)
    
    output_paths = ['publication.html', 'index.html']
    for output_path in output_paths:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(compiled_html)
        print(f"Publication compiled successfully: {output_path}")

if __name__ == '__main__':
    main()
