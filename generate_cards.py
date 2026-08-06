from bs4 import BeautifulSoup
import json
import re

# Load comp.html file containing all 713 rows
try:
    with open('comp.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
except FileNotFoundError:
    print("Error: comp.html not found.")
    exit()

companies = {}
rows = soup.find_all('tr')[1:]

for row in rows:
    cols = row.find_all('td')
    if len(cols) < 6:
        continue
    name = cols[0].get_text(strip=True)
    role = cols[1].get_text(strip=True)
    ctc = cols[2].get_text(strip=True)
    deadline = cols[4].get_text(strip=True)
    link_tag = cols[5].find('a')
    link = link_tag['href'] if link_tag else '#'
    
    # Sanitize zero-width spaces in links
    link = link.replace('\u200b', '').replace('\u200c', '').replace('\u200d', '').replace('\ufeff', '')

    if name not in companies:
        companies[name] = {'ctc': ctc, 'deadline': deadline, 'roles': []}
    
    if not any(r['link'] == link for r in companies[name]['roles']):
        companies[name]['roles'].append({'title': role, 'link': link})

sorted_names = sorted(companies.keys(), key=lambda s: s.lower())

total_jds = sum(len(c['roles']) for c in companies.values())
total_companies = len(sorted_names)

# Track counts for CTC tiers
tier_counts = {
    'all': total_companies,
    'super-dream': 0, # >= 30 LPA
    'dream': 0,       # 20-30 LPA
    'high': 0,        # 10-20 LPA
    'standard': 0,    # < 10 LPA
    'tbd': 0          # Undisclosed / Not specified
}

cards_html = ""
for name in sorted_names:
    data = companies[name]
    first_letter = name[0].upper() if name[0].isalpha() else "#"
    
    # Determine CTC tier and numeric value
    ctc_text = data['ctc']
    try:
        numbers = re.findall(r'\d+\.?\d*', ctc_text.replace(',', ''))
        ctc_val = float(numbers[0]) if numbers else 0.0
    except:
        ctc_val = 0.0

    if ctc_val >= 30.0:
        ctc_tier = "super-dream"
        badge_style = "bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300 border-purple-300 dark:border-purple-700"
    elif ctc_val >= 20.0:
        ctc_tier = "dream"
        badge_style = "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300 border-emerald-300 dark:border-emerald-700"
    elif ctc_val >= 10.0:
        ctc_tier = "high"
        badge_style = "bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300 border-blue-200 dark:border-blue-800"
    elif ctc_val > 0.0:
        ctc_tier = "standard"
        badge_style = "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border-slate-200 dark:border-slate-700"
    else:
        ctc_tier = "tbd"
        badge_style = "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300 border-amber-200 dark:border-amber-700"

    tier_counts[ctc_tier] += 1

    # Combined search payload
    all_roles_str = " ".join([r['title'] for r in data['roles']])
    search_payload = f"{name} {all_roles_str} {ctc_text}".lower()
    compact_payload = re.sub(r'\s+', '', search_payload)

    role_count_badge = f'<span class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300">{len(data["roles"])} Roles</span>' if len(data['roles']) > 1 else ''

    cards_html += f'''
    <div class="company-card group bg-white dark:bg-slate-800/90 rounded-[2rem] p-6 border border-slate-200/80 dark:border-slate-700/80 shadow-sm hover:shadow-2xl hover:border-blue-500/80 transition-all duration-300 flex flex-col justify-between h-full backdrop-blur-sm" 
         data-search="{search_payload}" data-compact="{compact_payload}" data-letter="{first_letter}" data-ctc-val="{ctc_val}" data-ctc-tier="{ctc_tier}">
        <div>
            <div class="flex justify-between items-start mb-5 gap-2">
                <div class="w-12 h-12 bg-slate-100 dark:bg-slate-700/80 rounded-2xl flex items-center justify-center border border-slate-200/60 dark:border-slate-600/60 group-hover:bg-blue-600 group-hover:border-blue-600 transition-all shadow-xs">
                    <i class="fas fa-building text-slate-400 dark:text-slate-400 group-hover:text-white text-xl transition-colors"></i>
                </div>
                <div class="flex flex-col items-end gap-1">
                    <span class="px-3 py-1 text-[11px] font-extrabold tracking-wide rounded-xl border {badge_style} shadow-xs">
                        {ctc_text}
                    </span>
                    {role_count_badge}
                </div>
            </div>
            
            <h3 class="text-xl font-extrabold text-slate-900 dark:text-white mb-2 tracking-tight line-clamp-1" title="{name}">{name}</h3>
            <p class="text-xs text-blue-600 dark:text-blue-400 font-bold mb-4 leading-snug line-clamp-2" title="{data['roles'][0]['title']}">{data['roles'][0]['title']}</p>
            
            <div class="flex items-center gap-2.5 text-[11px] text-slate-500 dark:text-slate-400 mb-6 bg-slate-50 dark:bg-slate-900/60 w-fit px-3.5 py-1.5 rounded-xl border border-slate-200/70 dark:border-slate-700/70">
                <i class="far fa-calendar-alt text-blue-500"></i>
                <span>Deadline: <span class="text-slate-800 dark:text-slate-200 font-bold">{data['deadline']}</span></span>
            </div>
        </div>

        <div class="space-y-3 pt-2">'''
    
    if len(data['roles']) > 1:
        cards_html += f'''
            <div class="relative">
                <select onchange="if(this.value) window.open(this.value, '_blank')" class="w-full appearance-none bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 text-xs font-semibold rounded-xl px-3.5 py-2.5 outline-none focus:ring-2 focus:ring-blue-500 transition-all cursor-pointer">
                    <option value="" class="bg-white dark:bg-slate-900 text-slate-400">Select Department / Role ({len(data['roles'])})</option>'''
        for r in data['roles']:
            cards_html += f'<option value="{r["link"]}" class="bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-100">{r["title"]}</option>'
        cards_html += '''</select>
                <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3.5 text-slate-400">
                    <i class="fas fa-chevron-down text-[10px]"></i>
                </div>
            </div>'''
    
    cards_html += f'''
            <a href="{data['roles'][0]['link']}" target="_blank" class="flex items-center justify-center gap-2 w-full py-3.5 bg-slate-900 dark:bg-blue-600 text-white text-xs font-extrabold rounded-xl hover:bg-blue-600 dark:hover:bg-blue-500 shadow-md transition-all active:scale-[0.98]">
                <span>View Primary JD</span> <i class="fas fa-external-link-alt text-[10px]"></i>
            </a>
        </div>
    </div>'''

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ#"
alpha_html = "".join([f'<button onclick="filterByLetter(\'{l}\')" class="alpha-btn w-full py-2.5 flex items-center justify-center rounded-xl font-extrabold text-slate-500 dark:text-slate-400 hover:text-blue-600 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-all text-xs tracking-wider">{l}</button>' for l in alphabet])

template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PlacementHub | Company Directory & CTC Packages</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {{ darkMode: 'class' }}
    </script>
    <style>
        body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
        .alpha-btn.active {{ background-color: #2563eb !important; color: white !important; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35); }}
        .ctc-btn.active {{ border-color: #2563eb !important; background-color: #eff6ff !important; color: #1d4ed8 !important; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15); }}
        .dark .ctc-btn.active {{ background-color: #1e3a8a !important; color: #93c5fd !important; border-color: #3b82f6 !important; }}
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-thumb {{ background: #cbd5e1; border-radius: 10px; }}
        .dark ::-webkit-scrollbar-thumb {{ background: #334155; }}
    </style>
</head>
<body class="antialiased bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors duration-300 min-h-screen">

    <!-- Header Navigation -->
    <header class="sticky top-0 z-50 border-b border-slate-200/80 dark:border-slate-800/80 bg-white/80 dark:bg-slate-950/80 backdrop-blur-md px-6 md:px-10 py-4">
        <div class="max-w-[1650px] mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
            <div class="flex items-center gap-4">
                <a href="index.html" class="flex items-center gap-3 group">
                    <div class="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center shadow-md group-hover:scale-105 transition-transform">
                        <i class="fas fa-graduation-cap text-white text-lg"></i>
                    </div>
                    <div>
                        <h1 class="text-xl font-extrabold tracking-tight text-slate-900 dark:text-white leading-none">Placement<span class="text-blue-600">Hub</span></h1>
                        <span class="text-[10px] font-bold text-slate-400 tracking-wider uppercase">Directory & CTC Filters</span>
                    </div>
                </a>

                <div class="hidden lg:flex items-center gap-2 ml-4 text-xs font-semibold bg-slate-100 dark:bg-slate-900 px-3.5 py-1.5 rounded-full border border-slate-200/70 dark:border-slate-800">
                    <span class="text-blue-600 dark:text-blue-400 font-extrabold">{total_jds}</span> JDs across 
                    <span class="text-emerald-600 dark:text-emerald-400 font-extrabold">{total_companies}</span> Companies
                </div>
            </div>
            
            <div class="flex items-center gap-3 w-full md:w-auto">
                <div class="relative group flex-grow md:w-[420px]">
                    <i class="fas fa-search absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-blue-500 transition-colors"></i>
                    <input type="text" id="searchInput" onkeyup="runFilters()" placeholder="Search company, role, CTC (e.g. 'Apple 36 LPA')..." 
                        class="w-full pl-11 pr-10 py-3 bg-slate-100 dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white dark:focus:bg-slate-900 transition-all text-xs font-semibold">
                    <button onclick="clearSearch()" id="clearBtn" class="hidden absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
                        <i class="fas fa-times-circle"></i>
                    </button>
                </div>

                <a href="comp.html" class="px-3.5 py-3 bg-slate-100 dark:bg-slate-900 hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-2xl border border-slate-200/80 dark:border-slate-800 text-xs font-extrabold flex items-center gap-2 transition-all whitespace-nowrap" title="Switch to Table View">
                    <i class="fas fa-table-list text-blue-500"></i> <span class="hidden sm:inline">Table View</span>
                </a>

                <a href="notices.html" class="px-3.5 py-3 bg-amber-50 dark:bg-amber-950/40 hover:bg-amber-100 dark:hover:bg-amber-900/60 text-amber-800 dark:text-amber-300 rounded-2xl border border-amber-200 dark:border-amber-800 text-xs font-extrabold flex items-center gap-2 transition-all whitespace-nowrap">
                    <i class="fas fa-bullhorn text-amber-600 dark:text-amber-400"></i> <span class="hidden sm:inline">Notices</span>
                </a>

                <button onclick="toggleTheme()" class="w-11 h-11 rounded-2xl border border-slate-200/80 dark:border-slate-800 flex items-center justify-center text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-900 transition-all shrink-0">
                    <i id="themeIcon" class="fas fa-moon"></i>
                </button>
            </div>
        </div>
    </header>

    <!-- Main Container -->
    <div class="flex max-w-[1650px] mx-auto">
        <!-- Sidebar A-Z Filter -->
        <aside class="w-24 hidden lg:flex flex-col border-r border-slate-200/80 dark:border-slate-800/80 sticky top-[77px] h-[calc(100vh-77px)] overflow-y-auto py-6 px-4">
            <button onclick="filterByLetter('ALL')" class="alpha-btn active w-full py-3 flex items-center justify-center rounded-xl font-extrabold text-xs mb-4">ALL</button>
            <div class="space-y-1">{alpha_html}</div>
        </aside>

        <!-- Main Content Area -->
        <main class="flex-grow p-6 md:p-10">
            <!-- Package Filter Bar ("Filter Packages") -->
            <div class="bg-white dark:bg-slate-900/90 rounded-3xl p-5 md:p-6 border border-slate-200/80 dark:border-slate-800 shadow-sm mb-8">
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
                    <div>
                        <h2 class="text-base font-extrabold text-slate-900 dark:text-white flex items-center gap-2">
                            <i class="fas fa-filter text-blue-600"></i> Filter Packages (CTC Ranges)
                        </h2>
                        <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Select a salary tier to filter companies by CTC package offer.</p>
                    </div>
                    <div class="text-xs font-extrabold text-slate-500 dark:text-slate-400">
                        Showing <span id="visibleCount" class="text-blue-600 dark:text-blue-400 font-extrabold text-sm">{total_companies}</span> companies
                    </div>
                </div>

                <!-- CTC Filter Pill Buttons -->
                <div class="flex flex-wrap gap-2.5">
                    <button onclick="filterByCtc('all')" id="ctc-btn-all" class="ctc-btn active px-4 py-2.5 rounded-2xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-extrabold text-xs transition-all flex items-center gap-2">
                        <span>All Packages</span>
                        <span class="px-2 py-0.5 rounded-full bg-slate-200/80 dark:bg-slate-700 text-[10px]">{total_companies}</span>
                    </button>
                    <button onclick="filterByCtc('super-dream')" id="ctc-btn-super-dream" class="ctc-btn px-4 py-2.5 rounded-2xl border border-purple-200 dark:border-purple-800/60 bg-purple-50/50 dark:bg-purple-950/30 text-purple-800 dark:text-purple-300 font-extrabold text-xs transition-all flex items-center gap-2">
                        <span>🚀 Super Dream (30+ LPA)</span>
                        <span class="px-2 py-0.5 rounded-full bg-purple-200/60 dark:bg-purple-900/60 text-[10px]">{tier_counts['super-dream']}</span>
                    </button>
                    <button onclick="filterByCtc('dream')" id="ctc-btn-dream" class="ctc-btn px-4 py-2.5 rounded-2xl border border-emerald-200 dark:border-emerald-800/60 bg-emerald-50/50 dark:bg-emerald-950/30 text-emerald-800 dark:text-emerald-300 font-extrabold text-xs transition-all flex items-center gap-2">
                        <span>⭐ Dream (20 - 30 LPA)</span>
                        <span class="px-2 py-0.5 rounded-full bg-emerald-200/60 dark:bg-emerald-900/60 text-[10px]">{tier_counts['dream']}</span>
                    </button>
                    <button onclick="filterByCtc('high')" id="ctc-btn-high" class="ctc-btn px-4 py-2.5 rounded-2xl border border-blue-200 dark:border-blue-800/60 bg-blue-50/50 dark:bg-blue-950/30 text-blue-800 dark:text-blue-300 font-extrabold text-xs transition-all flex items-center gap-2">
                        <span>💼 High (10 - 20 LPA)</span>
                        <span class="px-2 py-0.5 rounded-full bg-blue-200/60 dark:bg-blue-900/60 text-[10px]">{tier_counts['high']}</span>
                    </button>
                    <button onclick="filterByCtc('standard')" id="ctc-btn-standard" class="ctc-btn px-4 py-2.5 rounded-2xl border border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/50 text-slate-700 dark:text-slate-300 font-extrabold text-xs transition-all flex items-center gap-2">
                        <span>📌 Standard (< 10 LPA)</span>
                        <span class="px-2 py-0.5 rounded-full bg-slate-200 dark:bg-slate-700 text-[10px]">{tier_counts['standard']}</span>
                    </button>
                </div>
            </div>

            <!-- Cards Grid -->
            <div id="companyGrid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">{cards_html}</div>
            
            <!-- Empty State -->
            <div id="noResults" class="hidden flex-col items-center justify-center py-32 text-slate-400">
                <div class="w-20 h-20 bg-slate-100 dark:bg-slate-900 rounded-3xl flex items-center justify-center mb-4">
                    <i class="fas fa-search text-3xl text-slate-300 dark:text-slate-700"></i>
                </div>
                <p class="text-lg font-bold text-slate-700 dark:text-slate-300">No matching companies found</p>
                <p class="text-xs text-slate-400 mt-1">Try clearing your CTC package filter or search query.</p>
                <button onclick="resetFilters()" class="mt-5 px-5 py-2.5 bg-blue-600 text-white rounded-xl text-xs font-bold shadow-md hover:bg-blue-500 transition-all">
                    Reset All Filters
                </button>
            </div>
        </main>
    </div>

    <!-- Script Section -->
    <script>
        let currentLetter = 'ALL';
        let currentCtcTier = 'all';

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

        if (localStorage.getItem('theme') === 'dark') {{
            document.documentElement.classList.add('dark');
            document.getElementById('themeIcon').className = 'fas fa-sun';
        }}

        function clearSearch() {{
            document.getElementById('searchInput').value = '';
            runFilters();
        }}

        function resetFilters() {{
            document.getElementById('searchInput').value = '';
            filterByCtc('all');
            filterByLetter('ALL');
        }}

        function runFilters() {{
            const searchInput = document.getElementById('searchInput').value.toLowerCase().trim();
            const compactQuery = searchInput.replace(/\\s+/g, '');
            const clearBtn = document.getElementById('clearBtn');
            clearBtn.style.display = searchInput ? 'block' : 'none';

            const cards = document.querySelectorAll('.company-card');
            let foundCount = 0;

            cards.forEach(card => {{
                const searchData = card.getAttribute('data-search');
                const compactData = card.getAttribute('data-compact');
                const cardLetter = card.getAttribute('data-letter');
                const cardTier = card.getAttribute('data-ctc-tier');

                const matchesSearch = !searchInput || searchData.includes(searchInput) || (compactQuery.length >= 2 && compactData.includes(compactQuery));
                const matchesLetter = (currentLetter === 'ALL' || cardLetter === currentLetter);
                const matchesCtc = (currentCtcTier === 'all' || cardTier === currentCtcTier);

                if (matchesSearch && matchesLetter && matchesCtc) {{
                    card.style.display = "flex";
                    foundCount++;
                }} else {{
                    card.style.display = "none";
                }}
            }});

            document.getElementById('visibleCount').innerText = foundCount;
            document.getElementById('noResults').style.display = foundCount > 0 ? "none" : "flex";
        }}

        function filterByCtc(tier) {{
            currentCtcTier = tier;
            document.querySelectorAll('.ctc-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            const activeBtn = document.getElementById(`ctc-btn-${{tier}}`);
            if (activeBtn) activeBtn.classList.add('active');

            runFilters();
        }}

        function filterByLetter(letter) {{
            currentLetter = letter;
            document.querySelectorAll('.alpha-btn').forEach(btn => {{
                btn.classList.remove('active');
                if (btn.innerText === letter) btn.classList.add('active');
            }});
            runFilters();
        }}

        // Handle URL Parameters (e.g. ?tier=dream or ?tier=super-dream)
        window.addEventListener('DOMContentLoaded', () => {{
            const urlParams = new URLSearchParams(window.location.search);
            const tierParam = urlParams.get('tier');
            if (tierParam && ['all', 'super-dream', 'dream', 'high', 'standard'].includes(tierParam)) {{
                filterByCtc(tierParam);
            }}
        }});
    </script>
</body>
</html>'''

with open('companies_new.html', 'w', encoding='utf-8') as f:
    f.write(template)

print(f"Generated companies_new.html with Package Filtering for {total_companies} companies.")