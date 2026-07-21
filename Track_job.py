<!DOCTYPE html>
<html lang="en" class="h-full">

<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Dashboard · Ledger</title>
  <script>
    // Apply stored theme before Tailwind/paint to avoid a light-mode flash
    (function () {
      try {
        const stored = localStorage.getItem('ledger-theme');
        const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        const isDark = stored ? stored === 'dark' : prefersDark;
        if (isDark) document.documentElement.classList.add('dark');
      } catch (e) { /* ignore */ }
    })();
  </script>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = { darkMode: 'class' };
  </script>
  <style>
    .card-drag-over {
      outline: 2px dashed #a3a3a3;
      outline-offset: -2px;
      background: #f9fafb;
    }

    .dark .card-drag-over {
      background: #1c1c1c;
      outline-color: #525252;
    }

    .dragging {
      opacity: 0.35;
    }

    [draggable="true"] * {
      pointer-events: none;
    }

    [draggable="true"] .card-actions,
    [draggable="true"] .card-actions * {
      pointer-events: auto;
    }

    .col-applied {
      border-top: 2px solid #94a3b8;
    }

    .col-interview {
      border-top: 2px solid #3b82f6;
    }

    .col-offer {
      border-top: 2px solid #10b981;
    }

    .col-rejected {
      border-top: 2px solid #ef4444;
    }

    .dot-applied {
      background: #94a3b8;
    }

    .dot-interview {
      background: #3b82f6;
    }

    .dot-offer {
      background: #10b981;
    }

    .dot-rejected {
      background: #ef4444;
    }

    .sort-btn {
      font-size: 12px;
      padding: 4px 12px;
      border-radius: 20px;
      text-decoration: none;
      font-weight: 500;
      color: #737373;
      background: white;
      border: 1px solid #e5e5e5;
      transition: all .15s;
    }

    .sort-btn.active {
      background: black;
      color: white;
      border-color: black;
    }

    .dark .sort-btn {
      background: #171717;
      border-color: #333333;
      color: #a3a3a3;
    }

    .dark .sort-btn.active {
      background: #f5f5f5;
      color: #0a0a0a;
      border-color: #f5f5f5;
    }

    .interview-badge, .deadline-badge, .salary-badge {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 10px;
      font-weight: 500;
      border-radius: 9999px;
      padding: 2px 8px;
      white-space: nowrap;
    }

    .interview-badge {
      color: #3b82f6;
      background: #eff6ff;
      border: 1px solid #bfdbfe;
    }

    .dark .interview-badge {
      color: #93c5fd;
      background: rgba(59, 130, 246, 0.12);
      border: 1px solid rgba(59, 130, 246, 0.35);
    }

    .deadline-badge {
      color: #d97706;
      background: #fffbeb;
      border: 1px solid #fde68a;
    }

    .dark .deadline-badge {
      color: #fcd34d;
      background: rgba(217, 119, 6, 0.12);
      border: 1px solid rgba(217, 119, 6, 0.35);
    }

    .deadline-badge.urgent {
      color: #dc2626;
      background: #fef2f2;
      border: 1px solid #fecaca;
    }

    .dark .deadline-badge.urgent {
      color: #fca5a5;
      background: rgba(220, 38, 38, 0.14);
      border: 1px solid rgba(220, 38, 38, 0.4);
    }

    .salary-badge {
      color: #059669;
      background: #ecfdf5;
      border: 1px solid #a7f3d0;
    }

    .dark .salary-badge {
      color: #6ee7b7;
      background: rgba(5, 150, 105, 0.12);
      border: 1px solid rgba(5, 150, 105, 0.35);
    }
  </style>
</head>

<body class="h-full bg-white text-[#37352f] dark:bg-neutral-900 dark:text-neutral-100 transition-colors">

  <nav class="border-b border-neutral-100 dark:border-neutral-800 py-4 bg-white/80 dark:bg-neutral-900/80 backdrop-blur-md sticky top-0 z-50">
    <div class="mx-auto max-w-7xl px-4 flex justify-between items-center">
      <div class="flex items-center gap-6">
        <a href="{{ url_for('index') }}" class="font-bold text-lg tracking-tight">Ledger</a>
        <a href="{{ url_for('archived') }}"
          class="text-sm font-medium text-neutral-400 hover:text-black dark:hover:text-white transition-colors">Archived</a>
      </div>
      <div class="flex items-center gap-4">
        <label class="relative inline-flex items-center cursor-pointer" title="Toggle dark mode">
          <input type="checkbox" id="darkModeToggle" onchange="toggleDarkMode()" class="sr-only peer">
          <div class="w-11 h-6 bg-neutral-300 dark:bg-neutral-700 rounded-full peer-checked:bg-black dark:peer-checked:bg-white transition-colors"></div>
          <div class="absolute left-[3px] top-[3px] w-[18px] h-[18px] bg-white dark:bg-neutral-900 rounded-full shadow transition-transform peer-checked:translate-x-5">
          </div>
        </label>

        <div class="relative">
          <button id="profileMenuBtn" onclick="toggleProfileMenu()"
            class="w-8 h-8 rounded-full bg-neutral-100 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 flex items-center justify-center hover:border-black dark:hover:border-white transition-colors overflow-hidden">
            {% if profile_pic %}
            <img src="{{ profile_pic }}" alt="Profile" class="w-full h-full object-cover" />
            {% else %}
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round" class="text-neutral-400">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
            {% endif %}
          </button>

          <div id="profileMenu"
            class="hidden absolute right-0 mt-2 w-40 rounded-xl border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 shadow-lg overflow-hidden z-50">
            <a href="{{ url_for('profile') }}"
              class="block px-4 py-2.5 text-sm text-[#37352f] dark:text-neutral-100 hover:bg-neutral-50 dark:hover:bg-neutral-700 transition-colors no-underline">Profile</a>
            <a href="{{ url_for('logout') }}"
              class="block px-4 py-2.5 text-sm text-red-500 hover:bg-neutral-50 dark:hover:bg-neutral-700 transition-colors no-underline border-t border-neutral-100 dark:border-neutral-700">Logout</a>
          </div>
        </div>
      </div>
    </div>
  </nav>

  <main class="mx-auto max-w-7xl px-4 py-8">

    <div class="mb-6">
      <h1 class="text-3xl font-semibold mb-1">Dashboard</h1>
      <p class="text-neutral-500 text-sm">
        {{ jobs_by_status.values() | map('length') | sum }} application{{ '' if (jobs_by_status.values() | map('length')
        | sum) == 1 else 's' }} tracked — drag a card to update its stage.
      </p>
    </div>

    <!-- Stats bar -->
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 mb-6">
      <div class="rounded-2xl bg-neutral-50 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 px-5 py-4">
        <p class="text-xs text-neutral-400 uppercase tracking-widest mb-1">Total</p>
        <p class="text-2xl font-semibold">{{ total_applied }}</p>
        <p class="text-xs text-neutral-400 mt-1">applications</p>
      </div>
      <div class="rounded-2xl bg-neutral-50 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 px-5 py-4">
        <p class="text-xs text-neutral-400 uppercase tracking-widest mb-1">Response</p>
        <p class="text-2xl font-semibold text-amber-500">{{ response_rate | round | int }}%</p>
        <p class="text-xs text-neutral-400 mt-1">heard back</p>
      </div>
      <div class="rounded-2xl bg-neutral-50 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 px-5 py-4">
        <p class="text-xs text-neutral-400 uppercase tracking-widest mb-1">Interview</p>
        <p class="text-2xl font-semibold text-blue-500">{{ interview_rate | round | int }}%</p>
        <p class="text-xs text-neutral-400 mt-1">got interviews</p>
      </div>
      <div class="rounded-2xl bg-neutral-50 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 px-5 py-4">
        <p class="text-xs text-neutral-400 uppercase tracking-widest mb-1">Offer rate</p>
        <p class="text-2xl font-semibold text-emerald-500">{{ offer_rate | round | int }}%</p>
        <p class="text-xs text-neutral-400 mt-1">received offers</p>
      </div>
      <div class="rounded-2xl bg-neutral-50 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 px-5 py-4">
        <p class="text-xs text-neutral-400 uppercase tracking-widest mb-1">Rejected</p>
        <p class="text-2xl font-semibold text-red-500">{{ rejected_rate | round | int }}%</p>
        <p class="text-xs text-neutral-400 mt-1">rejection rate</p>
      </div>
    </div>

    <!-- Add form -->
    <div class="rounded-2xl border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 p-4 shadow-sm mb-4">
      <p class="text-xs font-medium text-neutral-500 uppercase tracking-wider mb-3">Add Application</p>
      <form method="post" action="{{ url_for('add_job') }}" class="flex flex-wrap gap-3 items-end">
        <input name="company" placeholder="Company" required
          class="flex-1 min-w-[140px] rounded-xl bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 px-3 py-2 text-sm text-black dark:text-neutral-100 outline-none focus:border-black dark:focus:border-white" />
        <input name="role" placeholder="Role / title" required
          class="flex-1 min-w-[140px] rounded-xl bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 px-3 py-2 text-sm text-black dark:text-neutral-100 outline-none focus:border-black dark:focus:border-white" />
        <select name="status"
          class="w-[130px] rounded-xl bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 px-3 py-2 text-sm text-black dark:text-neutral-100 outline-none focus:border-black dark:focus:border-white">
          <option value="Applied">Applied</option>
          <option value="Interview">Interview</option>
          <option value="Offer">Offer</option>
          <option value="Rejected">Rejected</option>
        </select>
        <input name="url" type="url" placeholder="Job URL (optional)"
          class="flex-1 min-w-[160px] rounded-xl bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 px-3 py-2 text-sm text-black dark:text-neutral-100 outline-none focus:border-black dark:focus:border-white" />
        <input name="notes" placeholder="Notes (optional)"
          class="flex-1 min-w-[160px] rounded-xl bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 px-3 py-2 text-sm text-black dark:text-neutral-100 outline-none focus:border-black dark:focus:border-white" />
        <label class="w-[150px]">
          <span class="block text-[10px] text-neutral-400 uppercase tracking-wider mb-1">Interview date</span>
          <input name="interview_date" type="date"
            class="w-full rounded-xl bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 px-3 py-2 text-sm text-black dark:text-neutral-100 outline-none focus:border-black dark:focus:border-white" />
        </label>
        <label class="w-[150px]">
          <span class="block text-[10px] text-neutral-400 uppercase tracking-wider mb-1">Apply-by deadline</span>
          <input name="deadline" type="date"
            class="w-full rounded-xl bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 px-3 py-2 text-sm text-black dark:text-neutral-100 outline-none focus:border-black dark:focus:border-white" />
        </label>
        <label class="w-[130px]">
          <span class="block text-[10px] text-neutral-400 uppercase tracking-wider mb-1">Salary</span>
          <input name="salary" placeholder="e.g. 90k"
            class="w-full rounded-xl bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 px-3 py-2 text-sm text-black dark:text-neutral-100 outline-none focus:border-black dark:focus:border-white" />
        </label>
        <button type="submit"
          class="rounded-xl bg-black dark:bg-white text-white dark:text-black px-4 py-2 text-sm font-semibold hover:bg-neutral-800 dark:hover:bg-neutral-200 transition-colors whitespace-nowrap">Add</button>
      </form>
    </div>

    <!-- Search + Sort -->
    <div class="flex items-center gap-4 mb-6 flex-wrap">
      <form method="get" action="{{ url_for('index') }}" class="relative flex-none w-80">
        <input type="text" name="q" value="{{ search_query }}" placeholder="Search company or role..."
          autocomplete="off"
          class="w-full rounded-xl bg-neutral-50 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 pl-9 pr-8 py-2 text-sm text-black dark:text-neutral-100 outline-none focus:border-black dark:focus:border-white"
          oninput="clearTimeout(window.__t); window.__t = setTimeout(() => this.form.submit(), 380);" />
        <svg class="absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" width="13" height="13"
          viewBox="0 0 24 24" fill="none" stroke="#a3a3a3" stroke-width="2.2">
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        {% if search_query %}
        <a href="{{ url_for('index') }}"
          class="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 text-sm no-underline">✕</a>
        {% endif %}
      </form>
      <div class="flex items-center gap-2">
        <span class="text-xs text-neutral-400 uppercase tracking-wider">Sort</span>
        <a href="{{ url_for('index', q=search_query, sort='newest') }}"
          class="sort-btn {{ 'active' if sort == 'newest' else '' }}">Newest</a>
        <a href="{{ url_for('index', q=search_query, sort='oldest') }}"
          class="sort-btn {{ 'active' if sort == 'oldest' else '' }}">Oldest</a>
      </div>
      <a href="{{ url_for('export_csv') }}"
        class="ml-auto inline-flex items-center gap-1.5 text-xs font-medium text-neutral-500 dark:text-neutral-400 border border-neutral-200 dark:border-neutral-700 rounded-full px-3 py-1.5 hover:text-black dark:hover:text-white hover:border-black dark:hover:border-white transition-colors no-underline">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
          stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="7 10 12 15 17 10" />
          <line x1="12" y1="15" x2="12" y2="3" />
        </svg>
        Export CSV
      </a>
    </div>

    <!-- Kanban Board -->
    <div class="flex md:grid md:grid-cols-4 gap-4 overflow-x-auto snap-x snap-mandatory -mx-4 px-4 md:mx-0 md:px-0 md:overflow-visible pb-3 md:pb-0">
      {% set columns = [
      ('Applied', 'applied'),
      ('Interview', 'interview'),
      ('Offer', 'offer'),
      ('Rejected', 'rejected')
      ] %}

      {% for status, cls in columns %}
      <div class="col-{{ cls }} rounded-2xl border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 shadow-sm flex flex-col flex-shrink-0 w-[85vw] snap-center md:w-auto"
        style="min-height:480px;">

        <div class="px-4 py-3 border-b border-neutral-100 dark:border-neutral-700 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="dot-{{ cls }} w-2 h-2 rounded-full inline-block flex-shrink-0"></span>
            <span class="text-sm font-semibold">{{ status }}</span>
          </div>
          <span
            class="text-xs text-neutral-400 bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-full px-2 py-0.5 font-mono">
            {{ jobs_by_status[status] | length if jobs_by_status[status] else 0 }}
          </span>
        </div>

        <div class="flex-1 p-3 flex flex-col gap-2" data-status="{{ status }}"
          ondragover="event.preventDefault(); this.classList.add('card-drag-over')"
          ondragleave="this.classList.remove('card-drag-over')" ondrop="handleDrop(event, '{{ status }}')">

          {% if jobs_by_status[status] %}
          {% for job in jobs_by_status[status] %}

          {% if edit_id == job.id %}
          <div class="rounded-xl border border-black dark:border-white bg-neutral-50 dark:bg-neutral-900 p-3">
            <form method="post" action="{{ url_for('edit_job', job_id=job.id) }}" class="flex flex-col gap-2">
              <input name="company" value="{{ job.company }}" required
                class="rounded-lg bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 px-2 py-1.5 text-xs text-black dark:text-neutral-100 outline-none focus:border-black dark:focus:border-white" />
              <input name="role" value="{{ job.role }}" required
                class="rounded-lg bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 px-2 py-1.5 text-xs text-black dark:text-neutral-100 outline-none focus:border-black dark:focus:border-white" />
              <select name="status"
                class="rounded-lg bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 px-2 py-1.5 text-xs text-black dark:text-neutral-100 outline-none focus:border-black dark:focus:border-white">
                {% for s in ['Applied','Interview','Offer','Rejected'] %}
                <option value="{{ s }}" {% if s==job.status %}selected{% endif %}>{{ s }}</option>
                {% endfor %}
              </select>
              <input name="url" value="{{ job.url or '' }}" placeholder="Job URL"
                class="rounded-lg bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 px-2 py-1.5 text-xs text-black dark:text-neutral-100 outline-none focus:border-black dark:focus:border-white" />
              <input name="notes" value="{{ job.notes or '' }}" placeholder="Notes"
                class="rounded-lg bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 px-2 py-1.5 text-xs text-black dark:text-neutral-100 outline-none focus:border-black dark:focus:border-white" />
              <label class="flex flex-col gap-1">
                <span class="text-[10px] text-neutral-400 uppercase tracking-wider">Interview date</span>
                <input name="interview_date" type="date" value="{{ job.interview_date or '' }}"
                  class="rounded-lg bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 px-2 py-1.5 text-xs text-black dark:text-neutral-100 outline-none focus:border-black dark:focus:border-white" />
              </label>
              <label class="flex flex-col gap-1">
                <span class="text-[10px] text-neutral-400 uppercase tracking-wider">Apply-by deadline</span>
                <input name="deadline" type="date" value="{{ job.deadline or '' }}"
                  class="rounded-lg bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 px-2 py-1.5 text-xs text-black dark:text-neutral-100 outline-none focus:border-black dark:focus:border-white" />
              </label>
              <label class="flex flex-col gap-1">
                <span class="text-[10px] text-neutral-400 uppercase tracking-wider">Salary</span>
                <input name="salary" value="{{ job.salary or '' }}" placeholder="e.g. 90k"
                  class="rounded-lg bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 px-2 py-1.5 text-xs text-black dark:text-neutral-100 outline-none focus:border-black dark:focus:border-white" />
              </label>
              <div class="flex gap-2 mt-1">
                <button type="submit"
                  class="flex-1 bg-black dark:bg-white text-white dark:text-black rounded-lg py-1.5 text-xs font-semibold hover:bg-neutral-800 dark:hover:bg-neutral-200 transition-colors">Save</button>
                <a href="{{ url_for('index', q=search_query) }}"
                  class="flex-1 bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 text-neutral-500 rounded-lg py-1.5 text-xs font-medium text-center hover:bg-neutral-50 dark:hover:bg-neutral-700 transition-colors">Cancel</a>
              </div>
            </form>
          </div>

          {% else %}
          {% set stage_days = (job.status_changed_at or job.date_applied) | days_since %}
          {% set dl_days = (job.deadline | days_until) if job.deadline else none %}
          <div draggable="true" data-id="{{ job.id }}"
            class="rounded-xl border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-900 p-3 cursor-grab hover:shadow-md transition-shadow">

            {% if job.url %}
            <a href="{{ job.url }}" target="_blank" rel="noopener noreferrer" class="block mb-2 no-underline">
              <p class="font-semibold text-sm text-blue-600 dark:text-blue-400 underline underline-offset-2 mb-0.5">{{ job.company }} ↗</p>
              <p class="text-xs text-neutral-500">{{ job.role }}</p>
            </a>
            {% else %}
            <div class="mb-2">
              <p class="font-semibold text-sm text-[#37352f] dark:text-neutral-100 mb-0.5">{{ job.company }}</p>
              <p class="text-xs text-neutral-500">{{ job.role }}</p>
            </div>
            {% endif %}

            <div class="flex flex-wrap gap-1 mb-2">
              {% if job.interview_date %}
              <span class="interview-badge">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"
                  stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="4" width="18" height="18" rx="2" />
                  <line x1="16" y1="2" x2="16" y2="6" />
                  <line x1="8" y1="2" x2="8" y2="6" />
                  <line x1="3" y1="10" x2="21" y2="10" />
                </svg>
                {{ job.interview_date }}
              </span>
              {% endif %}

              {% if job.deadline %}
              <span class="deadline-badge {{ 'urgent' if dl_days is not none and dl_days <= 3 else '' }}">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"
                  stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="9" />
                  <polyline points="12 7 12 12 15 14" />
                </svg>
                {% if dl_days is not none and dl_days < 0 %}Deadline passed
                {% elif dl_days is not none and dl_days == 0 %}Due today
                {% else %}Apply by {{ job.deadline }}{% endif %}
              </span>
              {% endif %}

              {% if job.salary %}
              <span class="salary-badge">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"
                  stroke-linecap="round" stroke-linejoin="round">
                  <line x1="12" y1="1" x2="12" y2="23" />
                  <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
                </svg>
                {{ job.salary }}
              </span>
              {% endif %}
            </div>

            {% if job.notes %}
            <p class="text-xs text-neutral-400 mb-2 border-l-2 border-neutral-200 dark:border-neutral-700 pl-2 leading-relaxed">{{ job.notes }}
            </p>
            {% endif %}

            <div class="flex items-center justify-between mt-2 pt-2 border-t border-neutral-100 dark:border-neutral-700">
              <span class="text-[10px] text-neutral-400 font-mono whitespace-nowrap">
                {{ job.date_applied }}{% if stage_days is not none %} · {{ stage_days }}d in stage{% endif %}
              </span>
              <div class="flex gap-1 card-actions">
                <a href="{{ url_for('index', edit_id=job.id, q=search_query) }}"
                  class="text-[11px] text-neutral-400 px-2 py-0.5 border border-neutral-200 dark:border-neutral-700 rounded hover:text-black dark:hover:text-white hover:border-black dark:hover:border-white transition-colors no-underline">Edit</a>
                <form method="post" action="{{ url_for('archive_job', job_id=job.id) }}" style="margin:0;">
                  <button
                    class="text-[11px] text-neutral-400 px-2 py-0.5 border border-neutral-200 dark:border-neutral-700 rounded hover:text-red-500 hover:border-red-300 transition-colors cursor-pointer bg-white dark:bg-neutral-900">Archive</button>
                </form>
              </div>
            </div>
          </div>
          {% endif %}

          {% endfor %}
          {% else %}
          <p class="text-xs text-neutral-300 text-center py-8">
            {% if search_query %}No matches{% else %}No applications{% endif %}
          </p>
          {% endif %}

        </div>
      </div>
      {% endfor %}

    </div>
  </main>

  <script>
    function toggleProfileMenu() {
      document.getElementById('profileMenu').classList.toggle('hidden');
    }
    document.addEventListener('click', function (e) {
      const menu = document.getElementById('profileMenu');
      const btn = document.getElementById('profileMenuBtn');
      if (!menu.contains(e.target) && !btn.contains(e.target)) {
        menu.classList.add('hidden');
      }
    });

    let draggedId = null;
    document.addEventListener('dragstart', function (e) {
      const card = e.target.closest('[data-id]');
      if (!card) return;
      draggedId = card.dataset.id;
      setTimeout(() => card.style.opacity = '0.35', 0);
    });
    document.addEventListener('dragend', function (e) {
      const card = e.target.closest('[data-id]');
      if (card) card.style.opacity = '1';
      draggedId = null;
    });
    function handleDrop(e, newStatus) {
      e.preventDefault();
      e.currentTarget.classList.remove('card-drag-over');
      if (!draggedId) return;
      fetch('/update-status/' + draggedId, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'status=' + encodeURIComponent(newStatus)
      }).then(() => window.location.reload());
    }

    function toggleDarkMode() {
      const checkbox = document.getElementById('darkModeToggle');
      const isDark = checkbox.checked;
      document.documentElement.classList.toggle('dark', isDark);
      localStorage.setItem('ledger-theme', isDark ? 'dark' : 'light');
    }
    // Sync the switch position with whatever theme was already applied (from the head script)
    document.getElementById('darkModeToggle').checked = document.documentElement.classList.contains('dark');
  </script>

</body>

</html>