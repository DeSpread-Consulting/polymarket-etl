// Supabase Configuration (config.js에서 가져옴)
const SUPABASE_URL = typeof CONFIG !== 'undefined' ? CONFIG.SUPABASE_URL : '';
const SUPABASE_ANON_KEY = typeof CONFIG !== 'undefined' ? CONFIG.SUPABASE_ANON_KEY : '';

// State
let supabaseClient = null;
let allEvents = [];
let currentDate = new Date();

// Filter state
let filters = {
    tags: [],
    timeRemaining: 'all',
    minVolume: 0,
    minLiquidity: 0
};

// Temp filter state (for modal)
let tempFilters = { ...filters };

// All available tags with counts
let allTags = {};

// Category to Emoji mapping
const categoryEmojis = {
    'Sports': '⚽',
    'Crypto': '💰',
    'Politics': '🏛️',
    'Pop Culture': '🎬',
    'Science': '🔬',
    'Business': '💼',
    'Technology': '💻',
    'Gaming': '🎮',
    'Music': '🎵',
    'default': '📊'
};

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 앱 시작');

    initTheme();
    initSupabase();
    setupEventListeners();
    await loadData();
    renderCalendar();
});

function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
}

function initSupabase() {
    if (!SUPABASE_URL || SUPABASE_URL === 'YOUR_SUPABASE_URL') {
        console.warn('Supabase URL이 설정되지 않았습니다.');
        return;
    }
    try {
        supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
        console.log('✅ Supabase 클라이언트 생성 완료');
    } catch (e) {
        console.error('❌ Supabase 클라이언트 생성 실패:', e);
    }
}

function setupEventListeners() {
    // Theme toggle
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            toggleTheme();
        });
    }

    // Month navigation
    document.getElementById('prevMonth').addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar();
    });

    document.getElementById('nextMonth').addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar();
    });

    // Today button
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            if (e.target.dataset.view === 'today') {
                currentDate = new Date();
                renderCalendar();
            }
        });
    });

    // Search
    document.getElementById('searchInput').addEventListener('input', (e) => {
        renderCalendar(e.target.value);
    });

    // Filter row click -> open filter modal
    document.getElementById('filtersRow').addEventListener('click', (e) => {
        // clearFilters 버튼 클릭 시 모달 열지 않음
        if (e.target.closest('#clearFilters') || e.target.closest('.remove-tag')) {
            return;
        }
        openFilterModal();
    });

    // Filter modal events
    document.getElementById('filterModalClose').addEventListener('click', closeFilterModal);
    document.getElementById('filterModalOverlay').addEventListener('click', (e) => {
        if (e.target === e.currentTarget) closeFilterModal();
    });

    // Filter options
    setupFilterOptions('timeRemainingOptions', 'timeRemaining');
    setupFilterOptions('minVolumeOptions', 'minVolume');
    setupFilterOptions('minLiquidityOptions', 'minLiquidity');

    // Tag search
    document.getElementById('tagSearchInput').addEventListener('input', (e) => {
        renderFilterTags(e.target.value);
    });

    // Show less tags toggle
    document.getElementById('showLessTags').addEventListener('click', (e) => {
        e.stopPropagation();
        const tagsContainer = document.getElementById('filterTags');
        tagsContainer.classList.toggle('collapsed');
        const btn = document.getElementById('showLessTags');
        btn.textContent = tagsContainer.classList.contains('collapsed') ? 'Show More' : 'Show Less';
    });

    // Apply/Reset filters
    document.getElementById('applyFilters').addEventListener('click', applyFilters);
    document.getElementById('resetFilters').addEventListener('click', resetFilters);
    document.getElementById('clearFilters').addEventListener('click', (e) => {
        e.stopPropagation();
        clearAllFilters();
    });

    // Event modal
    document.getElementById('modalClose').addEventListener('click', closeModal);
    document.getElementById('modalOverlay').addEventListener('click', (e) => {
        if (e.target === e.currentTarget) closeModal();
    });

    // Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModal();
            closeFilterModal();
        }
    });
}

function setupFilterOptions(containerId, filterKey) {
    const container = document.getElementById(containerId);
    container.querySelectorAll('.filter-option').forEach(btn => {
        btn.addEventListener('click', () => {
            container.querySelectorAll('.filter-option').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            tempFilters[filterKey] = btn.dataset.value === 'all' ? 'all' : parseInt(btn.dataset.value);
        });
    });
}

function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

async function loadData() {
    console.log('📥 데이터 로드 시작');

    if (!supabaseClient) {
        console.log('⚠️ Supabase 없음 - 데모 데이터 사용');
        allEvents = generateDemoData();
        extractTags();
        updateStats();
        return;
    }

    try {
        const PAGE_SIZE = 1000;
        let allData = [];
        let offset = 0;
        let hasMore = true;

        while (hasMore) {
            const { data, error } = await supabaseClient
                .from('poly_events')
                .select('*')
                .order('end_date', { ascending: true })
                .range(offset, offset + PAGE_SIZE - 1);

            if (error) throw error;

            if (data && data.length > 0) {
                allData = allData.concat(data);
                console.log(`📦 ${allData.length}건 로드됨...`);
                offset += PAGE_SIZE;
                hasMore = data.length === PAGE_SIZE;
            } else {
                hasMore = false;
            }
        }

        console.log('✅ 데이터 로드 성공:', allData.length, '건');
        allEvents = allData;
        extractTags();
        updateStats();
    } catch (error) {
        console.error('❌ 데이터 로드 실패:', error);
        allEvents = generateDemoData();
        extractTags();
        updateStats();
    }
}

function extractTags() {
    allTags = {};
    allEvents.forEach(event => {
        if (event.tags && Array.isArray(event.tags)) {
            event.tags.forEach(tag => {
                if (tag) {
                    allTags[tag] = (allTags[tag] || 0) + 1;
                }
            });
        }
    });

    // Sort by count
    const sortedTags = Object.entries(allTags)
        .sort((a, b) => b[1] - a[1])
        .reduce((obj, [key, value]) => {
            obj[key] = value;
            return obj;
        }, {});

    allTags = sortedTags;
    document.getElementById('tagCount').textContent = `(${Object.keys(allTags).length})`;
}

function generateDemoData() {
    const categories = ['Sports', 'Crypto', 'Politics', 'Pop Culture', 'Science', 'Business'];
    const demoTags = ['Sports', 'Games', 'Soccer', 'Politics', 'Basketball', 'Crypto', 'NCAA', 'Trump', 'Elections'];
    const demoEvents = [];
    const now = new Date();

    for (let i = 0; i < 500; i++) {
        const endDate = new Date(now);
        endDate.setDate(endDate.getDate() + Math.floor(Math.random() * 60) - 10);

        const prob = Math.random();
        const eventTags = [];
        const numTags = Math.floor(Math.random() * 3);
        for (let j = 0; j < numTags; j++) {
            eventTags.push(demoTags[Math.floor(Math.random() * demoTags.length)]);
        }

        demoEvents.push({
            id: `demo-${i}`,
            title: `Demo Market ${i + 1}`,
            slug: `demo-market-${i + 1}`,
            end_date: endDate.toISOString(),
            volume: Math.random() * 10000000,
            volume_24hr: Math.random() * 500000,
            probs: [prob.toFixed(2), (1 - prob).toFixed(2)],
            outcomes: ['Yes', 'No'],
            category: categories[Math.floor(Math.random() * categories.length)],
            tags: eventTags
        });
    }

    return demoEvents;
}

function updateStats() {
    const activeMarkets = allEvents.length;
    const totalVolume = allEvents.reduce((sum, e) => sum + (parseFloat(e.volume) || 0), 0);
    const volume24hr = allEvents.reduce((sum, e) => sum + (parseFloat(e.volume_24hr) || 0), 0);

    document.getElementById('activeMarkets').textContent = formatNumber(activeMarkets);
    document.getElementById('totalVolume').textContent = formatCurrency(totalVolume);
    document.getElementById('volume24hr').textContent = formatCurrency(volume24hr);
    document.getElementById('totalLiquidity').textContent = formatCurrency(totalVolume * 0.1);
}

function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

function formatCurrency(num) {
    if (num >= 1000000000) return (num / 1000000000).toFixed(1) + 'B';
    if (num >= 1000000) return (num / 1000000).toFixed(0) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(0) + 'K';
    return num.toFixed(0);
}

// Filter Modal Functions
function openFilterModal() {
    tempFilters = JSON.parse(JSON.stringify(filters));
    renderFilterTags();
    syncFilterUI();
    document.getElementById('filterModalOverlay').classList.add('active');
}

function closeFilterModal() {
    document.getElementById('filterModalOverlay').classList.remove('active');
}

function renderFilterTags(searchQuery = '') {
    const container = document.getElementById('filterTags');
    container.innerHTML = '';

    const query = searchQuery.toLowerCase();
    const filteredTags = Object.entries(allTags)
        .filter(([tag]) => tag.toLowerCase().includes(query));

    filteredTags.forEach(([tag, count]) => {
        const chip = document.createElement('button');
        chip.className = `tag-chip${tempFilters.tags.includes(tag) ? ' active' : ''}`;
        chip.innerHTML = `${tag} <span class="tag-count">${count}</span>`;
        chip.addEventListener('click', () => {
            if (tempFilters.tags.includes(tag)) {
                tempFilters.tags = tempFilters.tags.filter(t => t !== tag);
                chip.classList.remove('active');
            } else {
                tempFilters.tags.push(tag);
                chip.classList.add('active');
            }
        });
        container.appendChild(chip);
    });
}

function syncFilterUI() {
    // Time remaining
    document.querySelectorAll('#timeRemainingOptions .filter-option').forEach(btn => {
        const value = btn.dataset.value === 'all' ? 'all' : parseInt(btn.dataset.value);
        btn.classList.toggle('active', tempFilters.timeRemaining === value);
    });

    // Min Volume
    document.querySelectorAll('#minVolumeOptions .filter-option').forEach(btn => {
        const value = parseInt(btn.dataset.value);
        btn.classList.toggle('active', tempFilters.minVolume === value);
    });

    // Min Liquidity
    document.querySelectorAll('#minLiquidityOptions .filter-option').forEach(btn => {
        const value = parseInt(btn.dataset.value);
        btn.classList.toggle('active', tempFilters.minLiquidity === value);
    });
}

function applyFilters() {
    filters = JSON.parse(JSON.stringify(tempFilters));
    closeFilterModal();
    updateActiveFiltersDisplay();
    renderCalendar();
}

function resetFilters() {
    tempFilters = {
        tags: [],
        timeRemaining: 'all',
        minVolume: 0,
        minLiquidity: 0
    };
    renderFilterTags();
    syncFilterUI();
}

function clearAllFilters() {
    filters = {
        tags: [],
        timeRemaining: 'all',
        minVolume: 0,
        minLiquidity: 0
    };
    updateActiveFiltersDisplay();
    renderCalendar();
}

function updateActiveFiltersDisplay() {
    const container = document.getElementById('activeFilters');
    const clearBtn = document.getElementById('clearFilters');
    container.innerHTML = '';

    let hasFilters = false;

    // Tags
    filters.tags.forEach(tag => {
        hasFilters = true;
        const tagEl = document.createElement('span');
        tagEl.className = 'filter-tag';
        tagEl.innerHTML = `${tag} <span class="remove-tag" data-type="tag" data-value="${tag}">×</span>`;
        container.appendChild(tagEl);
    });

    // Time remaining
    if (filters.timeRemaining !== 'all') {
        hasFilters = true;
        const tagEl = document.createElement('span');
        tagEl.className = 'filter-tag';
        tagEl.innerHTML = `< ${filters.timeRemaining} days <span class="remove-tag" data-type="timeRemaining">×</span>`;
        container.appendChild(tagEl);
    }

    // Min Volume
    if (filters.minVolume > 0) {
        hasFilters = true;
        const tagEl = document.createElement('span');
        tagEl.className = 'filter-tag';
        tagEl.innerHTML = `Vol > $${formatCurrency(filters.minVolume)} <span class="remove-tag" data-type="minVolume">×</span>`;
        container.appendChild(tagEl);
    }

    // Min Liquidity
    if (filters.minLiquidity > 0) {
        hasFilters = true;
        const tagEl = document.createElement('span');
        tagEl.className = 'filter-tag';
        tagEl.innerHTML = `Liq > $${formatCurrency(filters.minLiquidity)} <span class="remove-tag" data-type="minLiquidity">×</span>`;
        container.appendChild(tagEl);
    }

    if (!hasFilters) {
        container.innerHTML = '<span class="filter-placeholder">Click to add filters</span>';
    }

    clearBtn.style.display = hasFilters ? 'block' : 'none';

    // Add remove handlers
    container.querySelectorAll('.remove-tag').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const type = btn.dataset.type;
            const value = btn.dataset.value;

            if (type === 'tag') {
                filters.tags = filters.tags.filter(t => t !== value);
            } else if (type === 'timeRemaining') {
                filters.timeRemaining = 'all';
            } else if (type === 'minVolume') {
                filters.minVolume = 0;
            } else if (type === 'minLiquidity') {
                filters.minLiquidity = 0;
            }

            updateActiveFiltersDisplay();
            renderCalendar();
        });
    });
}

function getFilteredEvents(searchQuery = '') {
    let filtered = [...allEvents];
    const now = new Date();

    // Apply tag filter
    if (filters.tags.length > 0) {
        filtered = filtered.filter(e =>
            e.tags && filters.tags.some(tag => e.tags.includes(tag))
        );
    }

    // Apply time remaining filter
    if (filters.timeRemaining !== 'all') {
        const days = parseInt(filters.timeRemaining);
        const maxDate = new Date(now.getTime() + days * 24 * 60 * 60 * 1000);
        filtered = filtered.filter(e => {
            const endDate = new Date(e.end_date);
            return endDate <= maxDate && endDate >= now;
        });
    }

    // Apply min volume filter
    if (filters.minVolume > 0) {
        filtered = filtered.filter(e => parseFloat(e.volume) >= filters.minVolume);
    }

    // Apply min liquidity filter (using volume * 0.1 as approximate liquidity)
    if (filters.minLiquidity > 0) {
        filtered = filtered.filter(e => parseFloat(e.volume) * 0.1 >= filters.minLiquidity);
    }

    // Apply search
    if (searchQuery) {
        const query = searchQuery.toLowerCase();
        filtered = filtered.filter(e =>
            e.title?.toLowerCase().includes(query) ||
            e.category?.toLowerCase().includes(query)
        );
    }

    return filtered;
}

function renderCalendar(searchQuery = '') {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'];
    document.getElementById('currentMonth').textContent = `${monthNames[month]} ${year}`;

    const firstDay = new Date(year, month, 1);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());

    const filtered = getFilteredEvents(searchQuery);

    // Group events by date
    const eventsByDate = {};
    filtered.forEach(event => {
        if (event.end_date) {
            const dateKey = event.end_date.split('T')[0];
            if (!eventsByDate[dateKey]) {
                eventsByDate[dateKey] = [];
            }
            eventsByDate[dateKey].push(event);
        }
    });

    const calendarDays = document.getElementById('calendarDays');
    calendarDays.innerHTML = '';

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    for (let i = 0; i < 42; i++) {
        const date = new Date(startDate);
        date.setDate(date.getDate() + i);

        const dateKey = date.toISOString().split('T')[0];
        const dayEvents = eventsByDate[dateKey] || [];
        const isOtherMonth = date.getMonth() !== month;
        const isToday = date.getTime() === today.getTime();
        const isPast = date.getTime() < today.getTime();

        const dayEl = document.createElement('div');
        let className = 'calendar-day';
        if (isOtherMonth) className += ' other-month';
        if (isToday) className += ' today';
        if (isPast) className += ' past-day';
        dayEl.className = className;

        const headerHtml = `
            <div class="day-header">
                <span class="day-number">${date.getDate()}</span>
                ${dayEvents.length > 0 ? `<span class="event-count">${dayEvents.length}</span>` : ''}
            </div>
        `;

        const maxVisible = 3;
        const visibleEvents = dayEvents.slice(0, maxVisible);
        const remainingCount = dayEvents.length - maxVisible;

        let eventsHtml = '<div class="day-events">';
        visibleEvents.forEach(event => {
            const emoji = categoryEmojis[event.category] || categoryEmojis.default;
            const prob = getMainProb(event);
            const probClass = prob < 30 ? 'low' : prob < 70 ? 'mid' : '';

            eventsHtml += `
                <div class="event-item" onclick="openEventLink('${event.slug}')" title="${event.title}">
                    <span class="event-emoji">${emoji}</span>
                    <span class="event-title">${truncate(event.title, 15)}</span>
                    <span class="event-prob ${probClass}">${prob}%</span>
                </div>
            `;
        });

        if (remainingCount > 0) {
            eventsHtml += `<div class="more-events" onclick="showDayEvents('${dateKey}')">+${remainingCount} more</div>`;
        }
        eventsHtml += '</div>';

        dayEl.innerHTML = headerHtml + eventsHtml;
        calendarDays.appendChild(dayEl);
    }
}

function getMainProb(event) {
    if (!event.probs || !Array.isArray(event.probs)) return 50;
    const prob = parseFloat(event.probs[0]);
    return Math.round(prob * 100);
}

function truncate(str, length) {
    if (!str) return '';
    return str.length > length ? str.substring(0, length) + '...' : str;
}

function openEventLink(slug) {
    if (slug) {
        window.open(`https://polymarket.com/event/${slug}`, '_blank');
    }
}

function showDayEvents(dateKey) {
    const filtered = getFilteredEvents(document.getElementById('searchInput').value);
    const dayEvents = filtered.filter(e => e.end_date?.startsWith(dateKey));

    const date = new Date(dateKey + 'T00:00:00');
    const dateStr = date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    document.getElementById('modalDate').textContent = `Events on ${dateStr}`;

    const modalBody = document.getElementById('modalBody');
    modalBody.innerHTML = '';

    dayEvents.forEach(event => {
        const emoji = categoryEmojis[event.category] || categoryEmojis.default;
        const prob = getMainProb(event);
        const probClass = prob < 30 ? 'low' : prob < 70 ? 'mid' : '';

        const eventEl = document.createElement('div');
        eventEl.className = 'modal-event-item';
        eventEl.onclick = () => openEventLink(event.slug);
        eventEl.innerHTML = `
            <span class="modal-event-emoji">${emoji}</span>
            <div class="modal-event-content">
                <div class="modal-event-title">${event.title}</div>
                <div class="modal-event-category">${event.category || 'Uncategorized'}</div>
            </div>
            <span class="modal-event-prob ${probClass}">${prob}%</span>
        `;
        modalBody.appendChild(eventEl);
    });

    document.getElementById('modalOverlay').classList.add('active');
}

function closeModal() {
    document.getElementById('modalOverlay').classList.remove('active');
}

// Global functions for onclick handlers
window.openEventLink = openEventLink;
window.showDayEvents = showDayEvents;
