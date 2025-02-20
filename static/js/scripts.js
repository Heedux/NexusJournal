// حساب سعر الخروج
function calculateExitPrice() {
    const entryPrice = parseFloat(document.getElementById('entryPrice').value);
    const pips = parseFloat(document.getElementById('pips').value);
    
    if (!isNaN(entryPrice) && !isNaN(pips)) {
        const exitPrice = entryPrice + (pips * 0.0001);
        document.getElementById('exitPrice').value = exitPrice.toFixed(4);
    } else {
        document.getElementById('exitPrice').value = '';
    }
}

// دالة لتغيير اللغة
function changeLanguage(lang) {
    const elements = {
        headerTitle: { ar: "Journal Trading المتطور", en: "Advanced Journal Trading" },
        headerDescription: { ar: "قم بتسجيل تداولاتك وتحليل أدائك بسهولة", en: "Record your trades and analyze your performance easily" },
        initialPortfolioLabel: { ar: "المبلغ الأولي:", en: "Initial Portfolio:" },
        entryTimeLabel: { ar: "وقت الدخول:", en: "Entry Time:" },
        entryPriceLabel: { ar: "سعر الدخول:", en: "Entry Price:" },
        pipsLabel: { ar: "عدد الـ Pips:", en: "Number of Pips:" },
        exitPriceLabel: { ar: "سعر الخروج:", en: "Exit Price:" },
        stopLossLabel: { ar: "Stop Loss (%):", en: "Stop Loss (%):" },
        currencyPairLabel: { ar: "العملة:", en: "Currency:" },
        strategyLabel: { ar: "الاستراتيجية:", en: "Strategy:" },
        lotSizeLabel: { ar: "حجم اللوت:", en: "Lot Size:" },
        killzoneLabel: { ar: "منطقة التداول:", en: "Trading Zone:" },
        submitButton: { ar: "إضافة تداول", en: "Add Trade" },
        tradesTableHeader: { ar: "سجل التداولات", en: "Trades Log" },
        timeHeader: { ar: "الوقت", en: "Time" },
        entryPriceHeader: { ar: "سعر الدخول", en: "Entry Price" },
        exitPriceHeader: { ar: "سعر الخروج", en: "Exit Price" },
        currencyHeader: { ar: "العملة", en: "Currency" },
        strategyHeader: { ar: "الاستراتيجية", en: "Strategy" },
        lotSizeHeader: { ar: "حجم اللوت", en: "Lot Size" },
        zoneHeader: { ar: "المنطقة", en: "Zone" },
        profitLossHeader: { ar: "الربح/الخسارة", en: "Profit/Loss" },
        actionsHeader: { ar: "الإجراءات", en: "Actions" },
        exportExcel: { ar: "Excel", en: "Excel" },
        exportPDF: { ar: "PDF", en: "PDF" },
        exportChart: { ar: "رسم بياني", en: "Chart" },
        chartsButton: { ar: "الذهاب إلى الرسوم البيانية", en: "Go to Charts" },
        currencyUnit: { ar: "دولار", en: "USD" },
        languageLabel: { ar: "اختر اللغة:", en: "Choose Language:" },
        deleteButton: { ar: "حذف", en: "Delete" }
    };

    // تغيير النصوص بناءً على اللغة المختارة
    Object.entries(elements).forEach(([id, text]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = text[lang];
        }
    });

    // تغيير النصوص في خيارات المبلغ الأولي
    const initialPortfolioSelect = document.getElementById('initialPortfolio');
    if (initialPortfolioSelect) {
        for (let option of initialPortfolioSelect.options) {
            const value = option.value;
            option.text = `${value} ${elements.currencyUnit[lang]}`;
        }
    }

    // تغيير النصوص في خيارات منطقة التداول
    const killzoneOptions = {
        LONDON: { ar: "لندن", en: "London" },
        NYW: { ar: "نيويورك", en: "New York" },
        ASIA: { ar: "آسيا", en: "Asia" }
    };

    const killzoneSelect = document.getElementById('killzone');
    if (killzoneSelect) {
        for (let option of killzoneSelect.options) {
            option.text = killzoneOptions[option.value][lang];
        }
    }

    // تغيير النصوص في زر الحذف
    const deleteButtons = document.querySelectorAll('button[onclick^="deleteTrade"]');
    deleteButtons.forEach(button => {
        button.textContent = elements.deleteButton[lang];
    });

    // تغيير اتجاه الصفحة بناءً على اللغة
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = lang;
}

// إضافة تداول
document.getElementById('tradeForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const tradeData = {
        entryTime: document.getElementById('entryTime').value,
        entryPrice: parseFloat(document.getElementById('entryPrice').value),
        exitPrice: parseFloat(document.getElementById('exitPrice').value),
        currencyPair: document.getElementById('currencyPair').value,
        strategy: document.getElementById('strategy').value,
        lotSize: parseFloat(document.getElementById('lotSize').value),
        initialPortfolio: parseFloat(document.getElementById('initialPortfolio').value),
        killzone: document.getElementById('killzone').value,
        stopLoss: parseFloat(document.getElementById('stopLoss').value),
        pips: (parseFloat(document.getElementById('exitPrice').value) - parseFloat(document.getElementById('entryPrice').value)) * 10000,
        profitLoss: (parseFloat(document.getElementById('exitPrice').value) - parseFloat(document.getElementById('entryPrice').value)) * parseFloat(document.getElementById('lotSize').value) * 100000
    };

    try {
        const response = await fetch('/add_trade', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(tradeData)
        });
        
        const result = await response.json();
        alert(result.message);
        loadTrades();
    } catch (error) {
        console.error('Error:', error);
        alert('حدث خطأ أثناء الإضافة');
    }
});

// تحميل التداولات
async function loadTrades() {
    try {
        const response = await fetch('/get_trades');
        const trades = await response.json();
        
        const tbody = document.querySelector('#tradesTable tbody');
        tbody.innerHTML = '';
        
        trades.forEach(trade => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${trade.entryTime}</td>
                <td>${trade.entryPrice.toFixed(4)}</td>
                <td>${trade.exitPrice.toFixed(4)}</td>
                <td>${trade.currencyPair}</td>
                <td>${trade.strategy}</td>
                <td>${trade.lotSize}</td>
                <td>${trade.killzone}</td>
                <td class="${trade.profitLoss >= 0 ? 'profit' : 'loss'}">
                    ${trade.profitLoss.toFixed(2)} ${document.getElementById('currencyUnit').textContent}
                </td>
                <td>
                    <button onclick="deleteTrade(${trade.id})">${document.getElementById('deleteButton').textContent}</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading trades:', error);
    }
}

// حذف تداول
async function deleteTrade(tradeId) {
    if (confirm('هل أنت متأكد من الحذف؟')) {
        try {
            const response = await fetch(`/delete_trade/${tradeId}`, {
                method: 'DELETE'
            });
            const result = await response.json();
            alert(result.message);
            loadTrades();
        } catch (error) {
            console.error('Error:', error);
        }
    }
}
async function loadTrades() {
    try {
        const response = await fetch('/get_trades');
        const trades = await response.json();
        console.log("Trades from API:", trades); // Debugging

        const tbody = document.querySelector('#tradesTable tbody');
        tbody.innerHTML = '';

        trades.forEach(trade => {
            const row = `
                <tr>
                    <td>${trade.entryTime}</td>
                    <td>${trade.entryPrice.toFixed(4)}</td>
                    <td>${trade.exitPrice.toFixed(4)}</td>
                    <td>${trade.currencyPair}</td>
                    <td>${trade.strategy}</td>
                    <td>${trade.lotSize}</td>
                    <td>${trade.killzone}</td>
                    <td class="${trade.profitLoss >= 0 ? 'profit' : 'loss'}">
                        ${trade.profitLoss.toFixed(2)} $
                    <td>
                    <button onclick="deleteTrade(${trade.id})">delete</button>
                    </td>
                </tr>
            
            `;
            tbody.innerHTML += row;
        });
    } catch (error) {
        console.error("Error loading trades:", error);
    }
}
// تحديث المحفظة
function updatePortfolio() {
    loadTrades();
}

// التحميل الأولي
window.onload = function() {
    loadTrades();

    // تعيين اللغة الافتراضية بناءً على لغة المتصفح
    const userLanguage = navigator.language || navigator.userLanguage;
    if (userLanguage.startsWith('en')) {
        document.getElementById('language').value = 'en';
        changeLanguage('en');
    } else {
        changeLanguage('ar');
    }
};