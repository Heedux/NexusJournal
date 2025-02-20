import datetime
from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
import logging
import sqlite3
from flask_cors import CORS
import calendar


app = Flask(__name__)
CORS(app)  # أضف هذا السطر
app = Flask(__name__)
app.secret_key = '2002'  # مفتاح سري للجلسة
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.logger.setLevel(logging.INFO)

# إعداد SQLAlchemy وإدارة الجلسات
db = SQLAlchemy(app)
Session(app)
def init_db():
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS trades
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entryTime TEXT NOT NULL,
                    entryPrice REAL NOT NULL,
                    exitPrice REAL NOT NULL,
                    pips REAL,
                    currencyPair TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    lotSize REAL NOT NULL,
                    initialPortfolio REAL NOT NULL,
                    killzone TEXT NOT NULL,
                    stopLoss REAL NOT NULL,
                    newsImpact TEXT NOT NULL,
                    profitLoss REAL NOT NULL,
                    remainingPortfolio REAL NOT NULL)''')  # تأكد من صحة الأعمدة
        conn.commit()
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        conn.close()

init_db()  # استدعاء الدالة عند التشغيل
# قاموس الرسائل باللغتين العربية والإنجليزية
MESSAGES = {
    'ar': {
        'add_trade_success': "تمت إضافة التداول بنجاح!",
        'add_trade_error': "حدث خطأ أثناء الإضافة",
        'db_error': "خطأ في قاعدة البيانات",
        'unexpected_error': "حدث خطأ غير متوقع",
        'get_trades_error': "فشل في جلب البيانات",
        'update_success': "تم التحديث بنجاح!",
        'update_error': "حدث خطأ أثناء التحديث",
        'delete_success': "تم الحذف بنجاح!",
        'delete_error': "حدث خطأ أثناء الحذف",
        'analysis_error': "حدث خطأ أثناء التحليل",
        'export_error': "حدث خطأ أثناء التصدير",
        'chart_error': "حدث خطأ أثناء إنشاء الرسم",
    },
    'en': {
        'add_trade_success': "Trade added successfully!",
        'add_trade_error': "An error occurred while adding the trade",
        'db_error': "Database error",
        'unexpected_error': "An unexpected error occurred",
        'get_trades_error': "Failed to fetch data",
        'update_success': "Updated successfully!",
        'update_error': "An error occurred while updating",
        'delete_success': "Deleted successfully!",
        'delete_error': "An error occurred while deleting",
        'analysis_error': "An error occurred during analysis",
        'export_error': "An error occurred during export",
        'chart_error': "An error occurred while generating the chart",
    }
}

# نموذج قاعدة البيانات
class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entryTime = db.Column(db.String, nullable=False)
    entryPrice = db.Column(db.Float, nullable=False)
    exitPrice = db.Column(db.Float, nullable=False)
    pips = db.Column(db.Float)
    currencyPair = db.Column(db.String, nullable=False)
    strategy = db.Column(db.String, nullable=False)
    lotSize = db.Column(db.Float, nullable=False)
    initialPortfolio = db.Column(db.Float, nullable=False)
    killzone = db.Column(db.String, nullable=False)
    stopLoss = db.Column(db.Float, nullable=False)
    newsImpact = db.Column(db.String, nullable=False)
    profitLoss = db.Column(db.Float, nullable=False)
    remainingPortfolio = db.Column(db.Float, nullable=False)

# إنشاء الجداول في قاعدة البيانات
with app.app_context():
    db.create_all()

# ---------------------------
# Routes الأساسية
# ---------------------------
@app.route('/')
def index():
    # تعيين اللغة الافتراضية إذا لم يتم تعيينها
    if 'lang' not in session:
        session['lang'] = 'ar'  # اللغة الافتراضية هي العربية
    return render_template('index.html', lang=session['lang'])

@app.route('/set_lang/<lang>')
def set_lang(lang):
    session['lang'] = lang
    return redirect(url_for('index'))

@app.route('/charts')
def charts():
    return render_template('charts.html', lang=session.get('lang', 'ar'))

# ---------------------------
# إدارة التداولات (CRUD)
# ---------------------------
@app.route('/add_trade', methods=['POST'])
def add_trade():
    try:
        data = request.get_json()
        
        # التحقق من الحقول الأساسية
        required_fields = ['entryTime', 'entryPrice', 'exitPrice', 'currencyPair', 'strategy', 'lotSize']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"الحقل {field} مطلوب"}), 400
        
        # حساب القيم التلقائية
        pips = (data['exitPrice'] - data['entryPrice']) * 10000
        profit_loss = (data['exitPrice'] - data['entryPrice']) * data['lotSize'] * 100000
        initial_portfolio = float(data.get('initialPortfolio', 5000))
        remaining_portfolio = initial_portfolio + profit_loss
        
        # إدخال البيانات في قاعدة البيانات
        new_trade = Trade(
            entryTime=data['entryTime'],
            entryPrice=data['entryPrice'],
            exitPrice=data['exitPrice'],
            pips=pips,
            currencyPair=data['currencyPair'],
            strategy=data['strategy'],
            lotSize=data['lotSize'],
            initialPortfolio=initial_portfolio,
            killzone=data.get('killzone', 'LONDON'),
            stopLoss=data.get('stopLoss', 1.0),
            newsImpact=data.get('newsImpact', 'Neutral'),
            profitLoss=profit_loss,
            remainingPortfolio=remaining_portfolio
        )
        db.session.add(new_trade)
        db.session.commit()
        
        return jsonify({"message": MESSAGES[session.get('lang', 'ar')]['add_trade_success']}), 201
        
    except Exception as e:
        app.logger.error(f"خطأ عام: {str(e)}")
        return jsonify({"error": MESSAGES[session.get('lang', 'ar')]['unexpected_error']}), 500

@app.route('/get_trades', methods=['GET'])
def get_trades():
    try:
        trades = Trade.query.all()
        trades_data = [{
            "id": trade.id,
            "entryTime": trade.entryTime,
            "entryPrice": trade.entryPrice,
            "exitPrice": trade.exitPrice,
            "pips": trade.pips,
            "currencyPair": trade.currencyPair,
            "strategy": trade.strategy,
            "lotSize": trade.lotSize,
            "initialPortfolio": trade.initialPortfolio,
            "killzone": trade.killzone,
            "stopLoss": trade.stopLoss,
            "newsImpact": trade.newsImpact,
            "profitLoss": trade.profitLoss,
            "remainingPortfolio": trade.remainingPortfolio
        } for trade in trades]
        return jsonify(trades_data), 200
    except Exception as e:
        app.logger.error(f"خطأ في جلب التداولات: {str(e)}")
        return jsonify({"error": MESSAGES[session.get('lang', 'ar')]['get_trades_error']}), 500

@app.route('/update_trade/<int:trade_id>', methods=['PUT'])
def update_trade(trade_id):
    try:
        data = request.get_json()
        trade = Trade.query.get_or_404(trade_id)
        
        trade.entryTime = data['entryTime']
        trade.entryPrice = data['entryPrice']
        trade.exitPrice = data['exitPrice']
        trade.pips = data['pips']
        trade.currencyPair = data['currencyPair']
        trade.strategy = data['strategy']
        trade.lotSize = data['lotSize']
        trade.initialPortfolio = data['initialPortfolio']
        trade.killzone = data['killzone']
        trade.stopLoss = data['stopLoss']
        trade.newsImpact = data['newsImpact']
        trade.profitLoss = data['profitLoss']
        trade.remainingPortfolio = data['remainingPortfolio']
        
        
        db.session.commit()
        return jsonify({"message": MESSAGES[session.get('lang', 'ar')]['update_success']}), 200
    except Exception as e:
        app.logger.error(f"خطأ في التحديث: {str(e)}")
        return jsonify({"error": MESSAGES[session.get('lang', 'ar')]['update_error']}), 500

@app.route('/delete_trade/<int:trade_id>', methods=['DELETE'])
def delete_trade(trade_id):
    try:
        trade = Trade.query.get_or_404(trade_id)
        db.session.delete(trade)
        db.session.commit()
        return jsonify({"message": MESSAGES[session.get('lang', 'ar')]['delete_success']}), 200
    except Exception as e:
        app.logger.error(f"خطأ في الحذف: {str(e)}")
        return jsonify({"error": MESSAGES[session.get('lang', 'ar')]['delete_error']}), 500

# ---------------------------
# التحليلات والتقارير
# ---------------------------
@app.route('/analyze_strategies')
def analyze_strategies():
    try:
        strategies = db.session.query(Trade.strategy, db.func.count(Trade.id)).group_by(Trade.strategy).all()
        analysis = {strategy: count for strategy, count in strategies}
        return jsonify(analysis), 200
    except Exception as e:
        app.logger.error(f"خطأ في التحليل: {str(e)}")
        return jsonify({"error": MESSAGES[session.get('lang', 'ar')]['analysis_error']}), 500

# ---------------------------
# تصدير البيانات
# ---------------------------
@app.route('/export_excel')
def export_excel():
    try:
        trades = Trade.query.all()
        df = pd.DataFrame([{
            "id": trade.id,
            "entryTime": trade.entryTime,
            "entryPrice": trade.entryPrice,
            "exitPrice": trade.exitPrice,
            "pips": trade.pips,
            "currencyPair": trade.currencyPair,
            "strategy": trade.strategy,
            "lotSize": trade.lotSize,
            "initialPortfolio": trade.initialPortfolio,
            "killzone": trade.killzone,
            "stopLoss": trade.stopLoss,
            "newsImpact": trade.newsImpact,
            "profitLoss": trade.profitLoss,
            "remainingPortfolio": trade.remainingPortfolio
        } for trade in trades])
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Trades', index=False)
        output.seek(0)
        return send_file(output, download_name='trades.xlsx', as_attachment=True)
    except Exception as e:
        app.logger.error(f"خطأ في التصدير: {str(e)}")
        return jsonify({"error": MESSAGES[session.get('lang', 'ar')]['export_error']}), 500

@app.route('/export_pdf')
def export_pdf():
    try:
        trades = Trade.query.all()
        df = pd.DataFrame([{
            "id": trade.id,
            "entryTime": trade.entryTime,
            "entryPrice": trade.entryPrice,
            "exitPrice": trade.exitPrice,
            "pips": trade.pips,
            "currencyPair": trade.currencyPair,
            "strategy": trade.strategy,
            "lotSize": trade.lotSize,
            "initialPortfolio": trade.initialPortfolio,
            "killzone": trade.killzone,
            "stopLoss": trade.stopLoss,
            "newsImpact": trade.newsImpact,
            "profitLoss": trade.profitLoss,
            "remainingPortfolio": trade.remainingPortfolio
        } for trade in trades])
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        
        columns = df.columns
        for col in columns:
            pdf.cell(40, 10, str(col), border=1)
        pdf.ln()
        
        for _, row in df.iterrows():
            for col in columns:
                pdf.cell(40, 10, str(row[col]), border=1)
            pdf.ln()
            
        output = BytesIO()
        pdf.output(output)
        output.seek(0)
        return send_file(output, download_name='trades.pdf', as_attachment=True)
    except Exception as e:
        app.logger.error(f"خطأ في التصدير: {str(e)}")
        return jsonify({"error": MESSAGES[session.get('lang', 'ar')]['export_error']}), 500

@app.route('/export_chart')
def export_chart():
    try:
        strategies = db.session.query(Trade.strategy, db.func.count(Trade.id)).group_by(Trade.strategy).all()
        df = pd.DataFrame(strategies, columns=['strategy', 'count'])
        
        plt.figure(figsize=(10,6))
        plt.bar(df['strategy'], df['count'], color='#3498db')
        plt.title('توزيع الاستراتيجيات المستخدمة')
        plt.xlabel('الاستراتيجية')
        plt.ylabel('عدد التداولات')
        plt.xticks(rotation=45)
        
        img = BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        return send_file(img, mimetype='image/png')
    except Exception as e:
        app.logger.error(f"خطأ في إنشاء الرسم: {str(e)}")
        return jsonify({"error": MESSAGES[session.get('lang', 'ar')]['chart_error']}), 500
@app.route('/get_strategy_profits', methods=['GET'])
def get_strategy_profits():
    try:
        strategies = db.session.query(Trade.strategy, db.func.sum(Trade.profitLoss)).group_by(Trade.strategy).all()
        strategy_profits = {strategy: profit for strategy, profit in strategies}
        return jsonify(strategy_profits), 200
    except Exception as e:
        app.logger.error(f"خطأ في حساب أرباح الاستراتيجيات: {str(e)}")
        return jsonify({"error": "حدث خطأ أثناء جلب البيانات"}), 500
@app.route('/get_strategy_profits_data', methods=['GET'])
def get_strategy_profits_data():
    try:
        strategies = db.session.query(Trade.strategy, db.func.sum(Trade.profitLoss)).group_by(Trade.strategy).all()
        strategy_profits = {strategy: float(profit) for strategy, profit in strategies}
        return jsonify(strategy_profits), 200
    except Exception as e:
        app.logger.error(f"خطأ في حساب أرباح الاستراتيجيات: {str(e)}")
        return jsonify({"error": "حدث خطأ أثناء جلب البيانات"}), 500
@app.route('/get_monthly_performance', methods=['GET'])
def get_monthly_performance():
    try:
        trades = db.session.query(Trade.entryTime, Trade.profitLoss).all()
        
        monthly_data = {}
        
        for entryTime, profitLoss in trades:
            date_obj = datetime.strptime(entryTime, '%Y-%m-%d %H:%M:%S')  # تحويل النص إلى تاريخ
            month_year = f"{calendar.month_name[date_obj.month]} {date_obj.year}"  # استخراج اسم الشهر والسنة
            
            if month_year in monthly_data:
                monthly_data[month_year] += profitLoss
            else:
                monthly_data[month_year] = profitLoss

        return jsonify(monthly_data), 200
    except Exception as e:
        app.logger.error(f"خطأ في حساب الأداء الشهري: {str(e)}")
        return jsonify({"error": "حدث خطأ أثناء جلب البيانات"}), 500
# ---------------------------
# تشغيل التطبيق
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)