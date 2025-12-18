from bs4 import BeautifulSoup

# Load your existing manual HTML file
try:
    with open('comp.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
except FileNotFoundError:
    print("Error: comp.html not found.")
    exit()

companies = {}
rows = soup.find_all('tr')[1:] 

for row in rows:
    cols = row.find_all('td')
    if len(cols) < 6: continue
    name = cols[0].get_text(strip=True)
    role = cols[1].get_text(strip=True)
    ctc = cols[2].get_text(strip=True)
    deadline = cols[4].get_text(strip=True)
    link = cols[5].find('a')['href']

    if name not in companies:
        companies[name] = {'ctc': ctc, 'deadline': deadline, 'roles': []}
    companies[name]['roles'].append({'title': role, 'link': link})

sorted_names = sorted(companies.keys())

cards_html = ""
for name in sorted_names:
    data = companies[name]
    first_letter = name[0].upper() if name[0].isalpha() else "#"
    
    try:
        ctc_val = float(''.join(c for c in data['ctc'].split()[0] if c.isdigit() or c == '.'))
        is_high_ctc = ctc_val >= 25.0
    except:
        is_high_ctc = False

    badge_style = "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 border-green-200 dark:border-green-800" if is_high_ctc else "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 border-blue-200 dark:border-blue-800"
    
    # Combined search data for faster filtering
    search_payload = f"{name} {' '.join([r['title'] for r in data['roles']])} {data['ctc']}".lower()

    cards_html += f'''
    <div class="company-card group bg-white dark:bg-slate-800 rounded-[2rem] p-6 border border-slate-200 dark:border-slate-700 shadow-sm hover:shadow-2xl hover:border-blue-500 transition-all duration-300 flex flex-col justify-between h-full" 
         data-search="{search_payload}" data-letter="{first_letter}">
        <div>
            <div class="flex justify-between items-start mb-6">
                <div class="w-12 h-12 bg-slate-100 dark:bg-slate-700 rounded-2xl flex items-center justify-center border border-slate-200 dark:border-slate-600 group-hover:bg-blue-600 transition-all">
                    <i class="fas fa-building text-slate-400 dark:text-slate-500 group-hover:text-white text-xl"></i>
                </div>
                <span class="px-3 py-1 text-[11px] font-bold tracking-widest uppercase rounded-lg border {badge_style}">
                    {data['ctc']}
                </span>
            </div>
            
            <h3 class="text-xl font-bold text-slate-900 dark:text-white mb-2 tracking-tight line-clamp-1">{name}</h3>
            <p class="text-sm text-blue-600 dark:text-blue-400 font-semibold mb-4 leading-tight">{data['roles'][0]['title']}</p>
            
            <div class="flex items-center gap-3 text-[12px] text-slate-500 dark:text-slate-400 mb-8 bg-slate-50 dark:bg-slate-900/50 w-fit px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700">
                <i class="far fa-calendar-alt text-blue-500"></i>
                <span>Ends: <span class="text-slate-900 dark:text-slate-200 font-bold">{data['deadline']}</span></span>
            </div>
        </div>

        <div class="space-y-4">'''
    
    if len(data['roles']) > 1:
        cards_html += f'''
            <div class="relative">
                <select onchange="window.open(this.value)" class="w-full appearance-none bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 text-[12px] font-bold rounded-xl px-4 py-3 outline-none focus:border-blue-500 transition-all cursor-pointer">
                    <option value="" class="bg-white dark:bg-slate-900">View Roles ({len(data['roles'])})</option>'''
        for r in data['roles']:
            cards_html += f'<option value="{r["link"]}" class="bg-white dark:bg-slate-900">{r["title"]}</option>'
        cards_html += '''</select>
                <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-slate-400">
                    <i class="fas fa-chevron-down text-[10px]"></i>
                </div>
            </div>'''
    
    cards_html += f'''
            <a href="{data['roles'][0]['link']}" target="_blank" class="flex items-center justify-center gap-3 w-full py-4 bg-slate-900 dark:bg-blue-600 text-white text-sm font-bold rounded-xl hover:bg-slate-800 dark:hover:bg-blue-500 shadow-lg transition-all active:scale-95">
                Explore JD <i class="fas fa-external-link-alt text-[10px]"></i>
            </a>
        </div>
    </div>'''

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ#"
alpha_html = "".join([f'<button onclick="filterLetter(\'{l}\')" class="alpha-btn w-full py-3.5 flex items-center justify-center rounded-2xl font-bold text-slate-400 dark:text-slate-500 hover:text-blue-600 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-all text-sm tracking-widest">{l}</button>' for l in alphabet])

template = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PlacementHub | Directory</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {{ darkMode: 'class' }}
    </script>
    <style>
        body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
        .alpha-btn.active {{ background-color: #2563eb !important; color: white !important; box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3); }}
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-thumb {{ background: #cbd5e1; border-radius: 10px; }}
        .dark ::-webkit-scrollbar-thumb {{ background: #334155; }}
    </style>
</head>
<body class="antialiased bg-slate-50 dark:bg-slate-950 transition-colors duration-300">

    <header class="sticky top-0 z-50 border-b border-slate-200 dark:border-slate-800 bg-white/90 dark:bg-slate-950/90 backdrop-blur-md px-8 py-5">
        <div class="max-w-[1600px] mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
            <div class="flex items-center gap-4">
                <div class="w-11 h-11 bg-blue-600 rounded-2xl flex items-center justify-center shadow-lg">
                    <i class="fas fa-graduation-cap text-white text-xl"></i>
                </div>
                <h1 class="text-2xl font-extrabold tracking-tight text-slate-900 dark:text-white">Placement<span class="text-blue-600">Hub</span></h1>
            </div>
            
            <div class="flex items-center gap-4 w-full md:w-fit">
                <button onclick="toggleTheme()" class="w-12 h-12 rounded-2xl border border-slate-200 dark:border-slate-800 flex items-center justify-center text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-900 transition-all">
                    <i id="themeIcon" class="fas fa-moon"></i>
                </button>
                
                <div class="relative group w-full md:w-[450px]">
                    <i class="fas fa-search absolute left-5 top-1/2 -translate-y-1/2 text-slate-400"></i>
                    <input type="text" id="searchInput" onkeyup="runFilters()" placeholder="Search company or role (e.g. 'Apple SDE')..." 
                        class="w-full pl-14 pr-6 py-4 bg-slate-100 dark:bg-slate-900 border-none rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 transition-all text-sm font-semibold dark:text-white">
                </div>
            </div>
        </div>
    </header>

    <div class="flex max-w-[1600px] mx-auto">
        <aside class="w-32 hidden md:flex flex-col border-r border-slate-200 dark:border-slate-800 sticky top-[92px] h-[calc(100vh-92px)] overflow-y-auto py-10 px-6">
            <button onclick="filterByLetter('ALL')" class="alpha-btn active w-full py-4 flex items-center justify-center rounded-2xl font-bold text-xs mb-10">ALL</button>
            <div class="space-y-2">{alpha_html}</div>
        </aside>

        <main class="flex-grow p-8 md:p-12">
            <div id="companyGrid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">{cards_html}</div>
            <div id="noResults" class="hidden flex-col items-center justify-center py-40 text-slate-400">
                <i class="fas fa-search text-6xl mb-6 opacity-20"></i>
                <p class="text-xl font-bold">No results found</p>
            </div>
        </main>
    </div>

    <script>
        let currentLetter = 'ALL';

        // THEME TOGGLE
        function toggleTheme() {{
            const html = document.documentElement;
            const icon = document.getElementById('themeIcon');
            if (html.classList.contains('dark')) {{
                html.classList.remove('dark');
                icon.className = 'fas fa-moon';
                localStorage.setItem('theme', 'light');
            }} else {{
                html.classList.add('dark');
                icon.className = 'fas fa-sun';
                localStorage.setItem('theme', 'dark');
            }}
        }}

        // LOAD THEME
        if (localStorage.getItem('theme') === 'dark') {{
            document.documentElement.classList.add('dark');
            document.getElementById('themeIcon').className = 'fas fa-sun';
        }}

        // MASTER FILTERING LOGIC
        function runFilters() {{
            const searchInput = document.getElementById('searchInput').value.toLowerCase();
            const cards = document.querySelectorAll('.company-card');
            let foundCount = 0;

            cards.forEach(card => {{
                const cardSearchData = card.getAttribute('data-search');
                const cardLetter = card.getAttribute('data-letter');
                
                const matchesSearch = cardSearchData.includes(searchInput);
                const matchesLetter = (currentLetter === 'ALL' || cardLetter === currentLetter);

                if (matchesSearch && matchesLetter) {{
                    card.style.display = "flex";
                    foundCount++;
                }} else {{
                    card.style.display = "none";
                }}
            }});

            document.getElementById('noResults').style.display = foundCount > 0 ? "none" : "flex";
        }}

        function filterByLetter(letter) {{
            currentLetter = letter;
            
            // UI Update for buttons
            document.querySelectorAll('.alpha-btn').forEach(btn => {{
                btn.classList.remove('active');
                if (btn.innerText === letter) btn.classList.add('active');
            }});

            runFilters();
        }}
    </script>
</body>
</html>'''

with open('companies_new.html', 'w', encoding='utf-8') as f:
    f.write(template)