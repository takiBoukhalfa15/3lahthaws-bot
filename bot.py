import telebot
import random
import time
import threading
import json
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta
import sqlite3
import asyncio
from threading import Timer

# إعداد البوت
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# إعداد قاعدة البيانات
def init_database():
    conn = sqlite3.connect('spyfall_bot.db')
    cursor = conn.cursor()
    
    # جدول المستخدمين
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            balance INTEGER DEFAULT 0,
            bank_account TEXT,
            bank_name TEXT,
            is_banned INTEGER DEFAULT 0,
            ban_reason TEXT,
            items TEXT DEFAULT '{}',
            games_won INTEGER DEFAULT 0,
            games_lost INTEGER DEFAULT 0
        )
    ''')
    
    # جدول الألعاب
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            game_id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            game_state TEXT DEFAULT 'waiting',
            players TEXT DEFAULT '[]',
            spies TEXT DEFAULT '[]',
            game_type TEXT,
            secret_item TEXT,
            game_duration INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            finished_at TIMESTAMP,
            winner TEXT
        )
    ''')
    
    # جدول التصويت
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            vote_id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            voter_id INTEGER,
            target_id INTEGER,
            vote_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # جدول المعاملات المالية
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            transaction_type TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# قوائم الأشياء والأماكن - ضع هنا قوائمك الكاملة
ITEMS = [     "كسكس 🍲", "شخشوخة 🥣", "محاجب 🥞", "رفيس 🍵", "حريرة 🍲", "طاجين 🍖", "ملوخية 🍲", "رشتة 🍜", 
    "لحم حلو 🍖", "دقلة نور 🍌", "زلابية 🍩", "قلب اللوز 🍪", "بغرير 🥞", "سفنج 🍩", "بسبوسة 🍰", 
    "مثوم 🍞", "شربة فريك 🥣", "كعك النقّاش 🍪", "مقرونة 🍝", "عصيدة 🥣", "كليلة 🍲", "فطير 🥐", 
    "خبز الدار 🍞", "خبز المطلوع 🍞", "خبز الفرن 🍞", "كسرة 🥖", "شطيطحة 🥘", "بوقورون 🍽️", 
    "براكوكش 🍲", "كرعين 🍗", "بوزلوف 🍢", "دجاج محمر 🍗", "مشوي 🍖", "كفتة 🍡", "لبنة 🧀", 
    "جبن قريش 🧀", "لبن 🥛", "رايب 🥛", "سمن 🌼", "زيت زيتون 🫒", "زبدة بلدية 🧈", "زيتون أسود 🫒", 
    "زيتون أخضر 🫒", "صلصة مشوية 🌶️", "حمص 🥣", "عدس 🍲", "لوبيا 🌱", "شعير 🌾", "تمور 🌴", 
    "كاوكاو 🥜", "لوز 🌰", "جوز 🌰", "قرفة 🥧", "فلفل أحمر 🌶️", "كمون 🌿", "رند 🌿", "عكري 🍯", 
    "قرنون 🎋", "هميس 🌿", "فريكاسي 🍲", "بريك 🥟", "سفة 🍜", "مروزية 🍖", "مدردرة 🍲", 
    "قاطو اللوز 🍰", "مملحات 🥨", "معجنات 🥐", "طبسيل 🍽️", "سكرية 🍬", "مغرف 🥄", "طبسي 🍲", 
    "قصرية 🥘", "قصعة 🍲", "فخار 🏺", "نحاس ⚙️", "طبل 🥁", "بندير 🥁", "دربوكة 🥁", "ناي 🎶", 
    "قانون 🎶", "رباب 🎻", "مزمار 🎶", "زكرة 🎶", "خمري 🍷", "قندورة 👕", "قشابية 👘", 
    "برنوس 🧥", "فوطا 🛁", "بلوزة 👚", "جبادور 👗", "سروال مدور 👖", "سروال قندريسي 👖", 
    "شاش 🧣", "عمامة 🧕", "شربيل 👡", "سباط بلاستيك 👟", "سكاتش 👟", "شبشب 🥿", "كرافات 👔", 
    "طربوش 🎩", "حرير 🧵", "صوف 🧶", "قطن ☁️", "كتان 🧵", "مقص ✂️", "إبرة 🪡", "مغزل 🧶", 
    "خيط 🧵", "تطريز 🎨", "كروشي 🧶", "خياطة 👗", "زربية 🪞", "بساط 🧺", "سجاد 🧼", 
    "وسادة 🛏️", "غطاء 🛌", "كوفيرطة 🛏️", "لحاف 🛏️", "جلابة 🧥", "حزام حرير 🧣", "حزام شدة 💎", 
    "حرز 🧿", "خميسة ✋", "فضة 🪙", "ذهب 🥇", "خلخال 💍", "سوار 📿", "عقد 💎", "حلق 🧏", 
    "شدة تلمسانية 👘", "شدة قسنطينية 👗", "شدة قبائلية 👘", "خمرة (إبريق) 🍶", "كحل 🧴", 
    "قعدة 🛏️", "طاسة 🥣", "قهوة ☕", "دلّة 🫖", "براد 🫖", "كأس شاي 🍵", "نعناع 🌿", 
    "شاي أحمر 🍵", "قهوة محمصة ☕", "ڨازوز 🥤", "بوقطايف 🍰", "مڨروط 🍪", "نوڨا 🍬", 
    "كاراميل 🍭", "شوكولا 🍫", "علكة 🍬", "طمينة 🍚", "لبان 🌿", "خل 🧴", "قمح 🌾", 
    "ذرة 🌽", "زريعة 🌻", "فول سوداني 🥜", "جلبانة 🥬", "عسل 🍯", "برقوق 🍑", "كرز 🍒", 
    "خوخ 🍑", "تين مجفف 🌰", "شمام 🍈", "رمان 🍎", "دلاح 🍉", "قرعة 🎃", "صبار 🌵", 
    "لب بلدي 🥜", "مربى 🍓", "عصير 🍹", "براد ماء 🚰", "سطل 🪣", "قفة 🧺", "غربال 🪶", 
    "طاجين فخار 🍲", "كسكاس 🍲", "قدر الضغط 🍳", "مقلاة 🍳", "كيس 🛍️", "لوح تقطيع 🔪", 
    "مصفاة 🧂", "مغرف كبير 🥄", "محراك 🔁", "عجانة 🍞", "فرن بلدي 🔥", "طابونة 🧱", 
    "مبخرة 🪔", "فحم 🧱", "فانوس 🏮", "شمعة 🕯️", "زمارة 📯", "بخاخ ماء ورد 🌹", 
    "صابون بلدي 🧼", "صابون غسيل 🧽", "شامبو 🧴", "زيت أركان 🌰", "زيت اللوز 🥥", 
    "زيت السمسم 🌿", "فازلين 🧴", "مراية 🪞", "مشط خشب 💇", "مكنسة 🧹", "شماعة 🧥", 
    "ستارة 🪟", "لحاف صوف 🛌", "كوفيرطة قطن 🛏️", "طقم غسيل 🧺", "مناديل ورقية 🧻", 
    "قماش تقليدي 👘", "قطعة حرير 🧵", "منديل عطري 🌺", "مسبحة 📿", "قرآن 📖", 
    "حامل مصحف 🧎", "مسبح سبسي 🚬", "معطر جو 🌬️", "فواحة كهربائية 💨", "سجادة صلاة 🕌", 
    "حافظة طعام 🍱", "علبة تمر 🌴", "علبة حلويات 🍬", "مجسم جمل 🐫", "مجسم طائرة ✈️", 
    "طابع بريدي 🖋️", "دفتر هوية 📓", "أوراق نقدية 💵", "دنانير 💰", "قندورة عرس 👰", 
    "طرحة قبائلية 🧣", "طرحة قسنطينية 🧕", "طرحة تلمسانية 👑", "بشكير 🧺", "منشفة حمام 🛁", 
    "فوطة مطرزة 🧻", "صينية تقديم 🍽️", "حافظات ماء 💧", "جرة فخار 🏺", "إناء خشب 🪵", 
    "مروحة يدوية 🌬️", "عطر عربي 🌸", "عطر فرنسي 🌺", "علبة طيب 🌼", "سبسي تقليدي 🚬", 
    "مسباح أمازيغي 📿", "خنجر تقليدي ⚔️", "سيف زينة 🗡️", "رمح تقليدي 🏹", "ناي أمازيغي 🎼", 
    "قلال تقليدي 🥁", "دف صوفي 🪘", "لوحة فسيفساء 🎨", "خيمة صحراوية ⛺", "قفطان تقليدي 👗", 
    "بلوزة وهرانية 👚", "شاش شاوي 🧣", "جلابة صحراوية 🧥", "سروال عربي 👖", "تاقيا ⛑️", 
    "سلهام 🧥", "برنوس أبيض 👘", "خيمة أمازيغية ⛺", "خاتم فضة 💍", "حلية أمازيغية 🪙", 
    "إسوارة مطرزة 🧵", "قلادة زينة 💎", "شنطة جلدية 👜", "محفظة نقود 👛", "نظارات تقليدية 🕶️", 
    "مزهرية فخار 🌺", "مبخرة تقليدية 🪔", "علبة ذهبية 📦", "دمية قماش 🧸", "بوق تقليدي 📯", 
    "طبلة قسنطينية 🪘", "مزمار شعبي 🎶", "عود موسيقي 🎸", "غيتار شعبي 🎵", "دف نوبة 🥁", 
    "قبقاب خشب 🥿", "زربية قبائلية 🧶", "زربية الهقار 🪺", "زربية بسكرة 🧺", "سجاد قسنطينة 🧻", 
    "تمثال حجري 🗿", "تمثال صخري 🪨", "سبحة خشب 🌰", "سبحة كهرمان 💠", "مجمرة بخور 🔥", 
    "نقالة تقليدية 🛏️", "قنينة ماء 🍼", "دلو غسيل 🪣", "زجاجة زيت 🫙", "جردل بلاستيك 🚿", 
    "مكواة فحم 🔥", "خزانة خشب 🗄️", "مرآة حائط 🪞", "مشجب ملابس 🪢", "سلة مهملات 🧺", 
    "فرشاة شعر 💇", "فرشاة تنظيف 🧽", "سطل حديد 🪣", "مصباح غاز 🔥", "شمع بلدي 🕯️", 
    "خيوط صوف 🧶", "مئزر تقليدي 🧵", "غطاء رأس نسوي 🧕", "سباط تقليدي 👞", "شنطة يد 👜", 
    "محفظة أوراق 💼", "رزمة نقود 💴", "خاتم عقيق 🟥", "لؤلؤ طبيعي 🦪", "حناء 🌿", 
    "صبغة طبيعية 🎨", "كحل الإثمد 🧴", "علبة مكياج 💄", "ثوب عرس تقليدي 👰", "كرافات عرس 👔", 
    "قميص شدة 👕", "شدة عاصمية 💠", "صندوق عروس 🎁", "حزام جلدي 🧷", "مرش ماء ورد 🌸", 
    "قرط ذهب 💎", "خاتم مزخرف 🧿", "بروش تقليدي 🎀", "طاقية شتوية 🧢", "قفازات جلد 🧤", 
    "حذاء عرس 👠", "زرابي مطرزة 🪟", "مساند زينة 🛋️", "طبل صحراوي 🥁", "كيس هدايا 🎁", 
    "قفة خوص 🧺", "مكنسة تقليدية 🧹", "دلو من الفخار 🪣", "مجسم قبة الشهداء 🏛️", 
    "علم الجزائر 🇩🇿", "جواز سفر جزائري 📘", "بطاقة تعريف وطنية 🪪", "عملة جزائرية 💰", 
    "قرش نحاسي 🪙", "تمثال الأمير عبد القادر 🗿", "صورة المجاهدين 📷", "بندقية قديمة 🔫", 
    "ذخيرة تقليدية 🧨", "تمثال الشيخ بوعمامة 🧔", "منحوتة الطاسيلي 🪨", "نقوش ما قبل التاريخ 🗿", 
    "طابع بريد جزائري ✉️", "قطعة نقدية 🪙", "قلادة تراثية 🧷", "إبرة خياطة 🪡", 
    "صابون الغار 🧼", "زيت الضرو 🪵", "طين تجميلي 🪨"
]

LOCATIONS = [     "الجزائر العاصمة 🏙️", "وهران 🏙️", "قسنطينة 🏙️", "عنابة 🏙️", "باتنة 🏙️", "بجاية 🏙️", 
    "بسكرة 🏙️", "بشار 🏙️", "البليدة 🏙️", "البويرة 🏙️", "تمنراست 🏙️", "تبسة 🏙️", 
    "تلمسان 🏙️", "تيارت 🏙️", "تيزي وزو 🏙️", "الجلفة 🏙️", "جيجل 🏙️", "سطيف 🏙️", 
    "سعيدة 🏙️", "سكيكدة 🏙️", "سيدي بلعباس 🏙️", "قالمة 🏙️", "المدية 🏙️", "مستغانم 🏙️", 
    "المسيلة 🏙️", "معسكر 🏙️", "ورقلة 🏙️", "البيض 🏙️", "إليزي 🏙️", "برج بوعريريج 🏙️", 
    "بومرداس 🏙️", "الطارف 🏙️", "تندوف 🏙️", "تسمسيلت 🏙️", "الوادي 🏙️", "خنشلة 🏙️", 
    "سوق أهراس 🏙️", "تيبازة 🏙️", "ميلة 🏙️", "عين الدفلى 🏙️", "النعامة 🏙️", "عين تيموشنت 🏙️", 
    "غرداية 🏙️", "غليزان 🏙️", "الونشريس 🏙️", "أولاد جلال 🏙️", "إن صالح 🏙️", "برج باجي مختار 🏙️", 
    "تيميمون 🏙️", "عين الصفراء 🏙️", "عين العنق 🏙️", "إن عيسى 🏙️", "برشطا 🏙️", "قصبة الجزائر 🏙️", 
    "قصبة قسنطينة 🏙️", "قصبة تلمسان 🏙️", "قصبة الطارف 🏙️", "قصبة بومرداس 🏙️", "مقام الشهيد 🏙️", 
    "حديقة التجارب النباتية 🏙️", "حديقة الحامة 🏙️", "حديقة الأوراس 🏙️", "حديقة غابة تيبازة 🏙️", 
    "منتزه الهقار الوطني 🏙️", "منتزه الطاسيلي نجّار 🏙️", "منتزه جرجرة 🏙️", "منتزه الكاف 🏙️", 
    "متنزه شريعة الوطني 🏙️", "متنزه بلزمة الوطني 🏙️", "مرتفعات الشريعة 🏙️", "جبال جرجرة 🏙️", 
    "جبل شلوة 🏙️", "جبل الشعانبي 🏙️", "جبل الشلالات 🏙️", "جبل بشار 🏙️", "جبل إغيل نابير 🏙️", 
    "جبال عمّور 🏙️", "وادي سوف 🏙️", "واحة تمنراست 🏙️", "واحة إيث قزام 🏙️", "واحة تيميمون 🏙️", 
    "واحة جانت 🏙️", "واحة توغرت 🏙️", "واحة إن صالح 🏙️", "وادي ميزاب 🏙️", "وادي الأقط 🏙️", 
    "وادي الحجارة 🏙️", "وادي ملوية 🏙️", "بحيرة الكون 🏙️", "بحيرة رأس الماء 🏙️", "بحيرة تندوف 🏙️", 
    "بحيرة ملوية 🏙️", "بحيرة بوطمة 🏙️", "شاطئ عين الترك 🏙️", "شاطئ سيدي فرج 🏙️", "شاطئ ساليان 🏙️", 
    "شاطئ توريط 🏙️", "شاطئ القالة 🏙️", "شاطئ كاب سهيل 🏙️", "كاب كارون 🏙️", "كابغليون 🏙️", 
    "كاب كاربون 🏙️", "مضيق جيجل 🏙️", "خور يتة 🏙️", "خور الصحراء 🏙️", "قلعة بني حماد 🏙️", 
    "قلعة القليعة 🏙️", "قلعة بني رشيد 🏙️", "قلعة بني عباس 🏙️", "قصر الأبيار 🏙️", "قصر الحمراء تيميمون 🏙️", 
    "قصر المشور 🏙️", "قصر خوموس 🏙️", "مدينة تيبازة الأثرية 🏙️", "مدينة تيمقاد 🏙️", "مدينة دلي إبراهيم 🏙️", 
    "مدينة جميلة الأثرية 🏙️", "مدينة إل كيلّا 🏙️", "مدينة عين بومهدي 🏙️", "مغارات عشّاش 🏙️", 
    "مغارات مستغانم 🏙️", "مغارات باتنة 🏙️", "وادي يسر 🏙️", "وادي كامو 🏙️", "وادي رقراق 🏙️", 
    "طريق القاف 🏙️", "طريق الحرير الجزائري 🏙️", "رصيف الوحدة 🏙️", "حديقة الطيور وهران 🏙️", 
    "محمية غابة متيجة 🏙️", "محمية الزبون 🏙️", "محمية سيدي مخلوف 🏙️", "نبع عين الشطا 🏙️", 
    "نبع عين الدفلى 🏙️", "عين الصافح 🏙️", "عين قزام الأثرية 🏙️", "محطة قطار الجزائر 🏙️", 
    "محطة ترام الجزائر 🏙️", "مطار هواري بومدين 🏙️", "مطار وهران 🏙️", "مطار عنابة 🏙️", 
    "مطار قسنطينة 🏙️", "مطار تلمسان 🏙️", "مطار غرداية 🏙️", "محطة حافلات الجزائر 🏙️", 
    "محطة حافلات وهران 🏙️", "ثكنة ابن باديس 🏙️", "ثكنة المرسى 🏙️", "متحف الباي 🏙️", 
    "متحف باردو 🏙️", "متحف المجاهد 🏙️", "متحف الفنون الجميلة 🏙️", "متحف تيبازة 🏙️", 
    "متحف تلمسان 🏙️", "متحف باتنة 🏙️", "متحف وهران 🏙️", "متحف بجاية 🏙️", "متحف بشار 🏙️", 
    "أكاديمية الفنون 🏙️", "المدرسة القرآنية بالقصبة 🏙️", "المدرسة العتيقة تلمسان 🏙️", 
    "المدرسة الصادقية 🏙️", "المدرسة الشهابية 🏙️", "المدرسة الأمير عبد القادر 🏙️", 
    "الكلية المركزية 🏙️", "جامعة الجزائر 🏙️", "جامعة وهران 🏙️", "جامعة قسنطينة 🏙️", 
    "جامعة باتنة 🏙️", "جامعة تلمسان 🏙️", "جامعة ورقلة 🏙️", "جامعة تمنراست 🏙️", 
    "جامعة غرداية 🏙️", "جامعة بجاية 🏙️", "جامعة بومرداس 🏙️", "معهد البريد 🏙️", 
    "معهد جغرافي 🏙️", "معهد الفنون 🏙️", "معهد الفلاحة 🏙️", "معهد النفط 🏙️", 
    "المعهد الوطني للبحث الزراعي 🏙️", "محطة الطاقة الحرارية غار بوڨرة 🏙️", "مجمع سوناطراك 🏙️", 
    "مفاعل أبحاث نووي 🏙️", "سد شارف 🏙️", "سد تاجموت 🏙️", "سد بومرداس 🏙️", "سد بني هارون 🏙️", 
    "سد عين دليلة 🏙️", "سد بوقايد 🏙️", "سكة حديد الشرق 🏙️", "سكة حديد الغرب 🏙️", 
    "تطوان جبال الأوراس 🏙️", "قناة الحامة 🏙️", "قناة الجزائر 🏙️", "قناة وهران 🏙️", 
    "برج الاتصالات الجزائر 🏙️", "برج زموري 🏙️", "شارع ديدوش مراد 🏙️", "شارع الإخوة عميروش 🏙️", 
    "شارع ابن سينا 🏙️", "شارع العربي بن مهيدي 🏙️", "كازينو الدالية 🏙️", "قاعة رياضية الجزائر 🏙️", 
    "قاعة مؤتمرات وهران 🏙️", "مركز المؤتمرات الجزائر 🏙️", "ملعب 5 جويلية 🏙️", 
    "ملعب مصطفى تشاكر 🏙️", "ملعب الشهيد حملاوي 🏙️", "ملعب وهران الجديد 🏙️", 
    "ملعب عنابة الدولي 🏙️", "ملعب مصطفى بن جنات 🏙️", "ملعب باتنة 🏙️", "قصر رياض الأفراح 🏙️", 
    "قاعة حفلات الجزائر 🏙️", "دار الأوبرا الجزائر 🏙️", "دار الثقافة وهران 🏙️", 
    "دار الثقافة تلمسان 🏙️", "دار الثقافة باتنة 🏙️", "دار الثقافة برج بوعريريج 🏙️", 
    "مكتبة تاشفين القسنطينية 🏙️", "مكتبة الولاية الجزائر 🏙️", "مكتبة وهران العامة 🏙️", 
    "حدائق سكيكدة 🏙️", "حدائق باتنة 🏙️", "حدائق وادي سوف 🏙️", "حدائق تيزي وزو 🏙️", 
    "حدائق بومرداس 🏙️", "حدائق تلمسان 🏙️", "حدائق قسنطينة 🏙️", "حدائق عنابة 🏙️", 
    "حدائق وهران 🏙️", "حدائق الجزائر العاصمة 🏙️", "مهرجان الراي وهران 🏙️", 
    "مهرجان الجزائر الدولي للفيلم 🏙️", "مهرجان الموسيقى الأندلسية 🏙️", "مهرجان تميمون 🏙️", 
    "مهرجان تيميتار 🏙️", "مهرجان الصحراء تمنراست 🏙️", "مهرجان ورقلة 🏙️", "مهرجان بجاية 🏙️", 
    "مهرجان سكيكدة 🏙️", "مهرجان عنابة 🏙️", "مهرجان باتنة 🏙️", "مهرجان سطيف 🏙️", 
    "مهرجان تيارت 🏙️", "ملتقى الشعر الجزائري 🏙️", "مهرجان الفيديو كليب الجزائر 🏙️", 
    "بازار القصبة 🏙️", "بازار وهران 🏙️", "بازار تلمسان 🏙️", "بازار باتنة 🏙️", 
    "بازار بجاية 🏙️", "بازار سطيف 🏙️", "بازار عنابة 🏙️", "بازار قسنطينة 🏙️", "بازار تمنراست 🏙️"
]

# متجر البوت
SHOP_ITEMS = {
    "تبون": {"price": 100000000, "emoji": "🇩🇿"},
    "شنڤريحة": {"price": 200000000, "emoji": "🎭"},
    "شاب بيلو": {"price": 300000000, "emoji": "🎵"},
    "ديدين كلاش": {"price": 400000000, "emoji": "🎬"},
    "ايناس عبدلي": {"price": 500000000, "emoji": "🎪"},
    "ريفكا": {"price": 600000000, "emoji": "🎨"},
    "كريم": {"price": 700000000, "emoji": "⚽"},
    "عادل ميكسيك": {"price": 800000000, "emoji": "🎤"},
    "مراد طهاري": {"price": 900000000, "emoji": "🏆"}
}

# البنوك المتاحة
BANKS = ["بدر", "الهلال", "أويحي"]

# متغيرات عامة
games = {}
user_states = {}
voting_sessions = {}
game_timers = {}
DEVELOPER_USERNAME = "V_b_L_o"

# وظائف المساعدة
def get_user_data(user_id):
    conn = sqlite3.connect('spyfall_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def create_user(user_id, username, first_name):
    conn = sqlite3.connect('spyfall_bot.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO users (user_id, username, first_name, balance, items) 
        VALUES (?, ?, ?, 0, '{}')
    """, (user_id, username, first_name))
    conn.commit()
    conn.close()

def update_user_balance(user_id, amount):
    conn = sqlite3.connect('spyfall_bot.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def get_user_balance(user_id):
    conn = sqlite3.connect('spyfall_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def is_user_banned(user_id):
    conn = sqlite3.connect('spyfall_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result and result[0] == 1

def ban_user(user_id, reason="غير محدد"):
    conn = sqlite3.connect('spyfall_bot.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_banned = 1, ban_reason = ? WHERE user_id = ?", (reason, user_id))
    conn.commit()
    conn.close()

def unban_user(user_id):
    conn = sqlite3.connect('spyfall_bot.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_banned = 0, ban_reason = NULL WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def is_admin(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except:
        return False

def is_bot_admin(chat_id):
    try:
        member = bot.get_chat_member(chat_id, bot.get_me().id)
        return member.status in ['administrator', 'creator']
    except:
        return False

def get_user_items(user_id):
    conn = sqlite3.connect('spyfall_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT items FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return json.loads(result[0])
    return {}

def update_user_items(user_id, items):
    conn = sqlite3.connect('spyfall_bot.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET items = ? WHERE user_id = ?", (json.dumps(items), user_id))
    conn.commit()
    conn.close()

def get_user_bank_info(user_id):
    conn = sqlite3.connect('spyfall_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT bank_account, bank_name FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def update_user_bank(user_id, bank_account, bank_name):
    conn = sqlite3.connect('spyfall_bot.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET bank_account = ?, bank_name = ? WHERE user_id = ?", (bank_account, bank_name, user_id))
    conn.commit()
    conn.close()

def calculate_max_spies(total_players):
    """حساب عدد الجواسيس المسموح حسب العدد الكلي للاعبين"""
    if total_players >= 3 and total_players <= 5:
        return 1
    elif total_players >= 6 and total_players <= 8:
        return 2
    elif total_players >= 9 and total_players <= 11:
        return 3
    else:
        return int(total_players / 3)

def send_welcome_message(chat_id):
    """إرسال رسالة الترحيب عند إضافة البوت للمجموعة"""
    text = "👋 شكرًا لإضافتي!\nاضغط على /newgame للبدء."
    bot.send_message(chat_id, text)

def generate_account_number():
    """توليد رقم حساب بنكي"""
    return f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"

def add_transaction(user_id, amount, transaction_type, description):
    """إضافة معاملة مالية"""
    conn = sqlite3.connect('spyfall_bot.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (user_id, amount, transaction_type, description)
        VALUES (?, ?, ?, ?)
    """, (user_id, amount, transaction_type, description))
    conn.commit()
    conn.close()

def end_game_timer(chat_id):
    """انتهاء وقت اللعبة"""
    if chat_id in games and games[chat_id]['status'] == 'playing':
        # الجواسيس يفوزون إذا انتهى الوقت
        spies_win(chat_id)

def spies_win(chat_id):
    """فوز الجواسيس"""
    game = games[chat_id]
    
    # فيديو فوز الجواسيس
    video_url = "https://raw.githubusercontent.com/username/repository/main/spy_win.mp4"
    
    text = "🎉 فاز الجاسوس!\n"
    text += f"الموقع/الشيء: {game['secret_item']}\n\n"
    text += "🏆 **نتائج اللعبة:**\n"
    
    # عرض النتائج
    for player_id, player_name in game['players']:
        if player_id in game['spies']:
            text += f"🕵️ {player_name} - جاسوس (فاز) 🎉\n"
            # إضافة الأموال للجاسوس
            update_user_balance(player_id, 2000000000)
            add_transaction(player_id, 2000000000, "game_win", "فوز كجاسوس")
        else:
            text += f"👤 {player_name} - لاعب عادي (خسر) 😞\n"
    
    text += "\n💰 حصل الجاسوس على جائزة مالية 2,000,000,000 د.ج\n"
    text += f"عاقبوا اللاعبين بما تريدون، وإذا لم يطبقوا الحكم، ارسلوا أسمائهم لـ @{DEVELOPER_USERNAME} ليخرجهم من اللعبة نهائيًا."
    
    try:
        bot.send_video(chat_id, video_url, caption=text)
    except:
        bot.send_message(chat_id, text)
    
    # إنهاء اللعبة
    games[chat_id]['status'] = 'finished'

def players_win(chat_id):
    """فوز اللاعبين"""
    game = games[chat_id]
    
    # فيديو فوز اللاعبين
    video_url = "https://raw.githubusercontent.com/username/repository/main/players_win.mp4"
    
    text = "🎊 فاز اللاعبون!\n"
    text += f"الموقع/الشيء: {game['secret_item']}\n\n"
    text += "🏆 **نتائج اللعبة:**\n"
    
    # عرض النتائج
    for player_id, player_name in game['players']:
        if player_id in game['spies']:
            text += f"🕵️ {player_name} - جاسوس (خسر) 😞\n"
        else:
            text += f"👤 {player_name} - لاعب عادي (فاز) 🎉\n"
            # إضافة الأموال للاعب
            update_user_balance(player_id, 100000)
            add_transaction(player_id, 100000, "game_win", "فوز كلاعب عادي")
    
    text += "\n💸 كل لاعب حصل على 100,000 د.ج\n"
    text += f"عاقبوا الجاسوس بما تريدون، وإذا لم تُطبق العقوبة، ارسلوا اسمه لـ @{DEVELOPER_USERNAME} ليُقصى نهائيًا."
    
    try:
        bot.send_video(chat_id, video_url, caption=text)
    except:
        bot.send_message(chat_id, text)
    
    # إنهاء اللعبة
    games[chat_id]['status'] = 'finished'

# بدء البوت
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    # إنشاء المستخدم في قاعدة البيانات
    create_user(user_id, username, first_name)
    
    # التحقق من الحظر
    if is_user_banned(user_id):
        bot.send_message(message.chat.id, f"🚫 أنت مقصي من اللعبة\nاتصل بالمطور للإفراج عنك\nالمطور: @{DEVELOPER_USERNAME}")
        return
    
    # إذا كان في المجموعة، أرسل رسالة الترحيب
    if message.chat.type in ['group', 'supergroup']:
        send_welcome_message(message.chat.id)
        return
    
    # إرسال الصورة والنص في الخاص
    photo_url = "https://pin.it/2qzWrzyQO"
    
    text = """🕵️‍♂️ لعبة Spyfall هي لعبة اجتماعية قصيرة (3–30 لاعبين)
يجتهد فيها "الجاسوس" في تخمين مكان سري،
بينما يحاول الآخرون كشفه بأسئلة ذكية،
أو ينتصر الجاسوس إذا ظل خفيًا أو خمن المكان.
🔗 رابط المجموعة: https://t.me/+0ipdbPwuF304OWRk
👨‍💻 المطور: @V_b_L_o"""
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("اضغط هنا باه تفهم", callback_data="rules"))
    keyboard.add(InlineKeyboardButton("اضفني لمجموعتك لبدأ اللعبة", url="http://t.me/spy_spy_bbot?startgroup=new"))
    
    try:
        bot.send_photo(message.chat.id, photo_url, caption=text, reply_markup=keyboard)
    except:
        bot.send_message(message.chat.id, text, reply_markup=keyboard)

# قواعد اللعبة
@bot.callback_query_handler(func=lambda call: call.data == "rules")
def send_rules(call):
    rules_text = """📜 **قواعد اللعبة:**
[●] ممنوع شخص يتسأل مرتين ورا بعض
[●] أي لاعب يقدر دايما يبدأ تصويت على لاعب تاني شك فيه، والأغلبية تفوز
[●] لو الأغلبية شكوا في لاعب، حقهم يعرفوا كان جاسوس ولا لأ، ولو كان جاسوس يطرد
[●] لا يُحتسب صوت أي لاعب خرج بالتصويت حتى لو ما كانش جاسوس
[●] كل دور هيكون فيه عدد فرص حسب عدد اللعيبة، والفرصة بتضيع مع كل لعيب بيطرد وهو مش جاسوس
[●] لو الوقت خلص قبل ما الجواسيس كلهم يتطردوا، 🕒 الجواسيس يكسبوا
[●] محدش عارف مين جاسوس ومين لأ، فكر كويس وخلي أسئلتك ذكية ومش بتفضح المكان أو الأكلة
[●] لو الجاسوس عرف المكان أو الأكلة، ممكن يوقف الدور في أي وقت ويعلن تخمينه:
– لو صح ➡️ تنتهي الدور بفوز الجواسيس
– لو غلط ➡️ يطرد والدور يكمل عادي
[●] هدف الجواسيس: إنهم ما يتعرفوش ويعرفوا المكان أو الأكلة قبل ما الوقت يخلص
[●] هدف الباقي: إكتشاف كل الجواسيس قبل ما الوقت يخلص
[●] الجاسوس هي لعبة لـ 3 أو أكثر، مكونة من فرقتين:
– فريق يعرف المكان/الاكلـة
– فريق جواسيس مش عارفينه"""
    
    bot.send_message(call.message.chat.id, rules_text, parse_mode='Markdown')

# بدء لعبة جديدة
@bot.message_handler(commands=['newgame'])
def new_game(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # التحقق من الحظر
    if is_user_banned(user_id):
        bot.send_message(chat_id, f"🚫 أنت مقصي من اللعبة\nاتصل بالمطور للإفراج عنك\nالمطور: @{DEVELOPER_USERNAME}")
        return
    
    # التحقق من أن البوت إدمن
    if not is_bot_admin(chat_id):
        bot.send_message(chat_id, "⚠️ لا استطيع اكمال اللعبة الا عند رفعي ادمن")
        return
    
    # التحقق من وجود لعبة جارية
    if chat_id in games and games[chat_id]['status'] in ['waiting', 'joining', 'playing']:
        bot.send_message(chat_id, "⚠️ لا يمكن بداية لعبة جديدة حتى تكمل البارتية")
        return
    
    # إنشاء لعبة جديدة
    games[chat_id] = {
        'status': 'waiting',
        'players': [],
        'spies': [],
        'secret_item': None,
        'game_type': None,
        'duration': 0,
        'votes': {},
        'join_time': time.time(),
        'normal_players': 0,
        'spy_count': 0
    }
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔵 أبدا اللعبة", callback_data=f"start_game_{chat_id}"))
    keyboard.add(InlineKeyboardButton("🟠 كيفاه تتعلب هذي اللعبة", callback_data="rules"))
    keyboard.add(InlineKeyboardButton("🟣 انضم للقناة للمزيد من المتعة", url="https://t.me/+0ipdbPwuF304OWRk"))
    
    bot.send_message(chat_id, "🤔 حاب تبدا تلعب؟", reply_markup=keyboard)

# بدء اللعبة
@bot.callback_query_handler(func=lambda call: call.data.startswith("start_game_"))
def start_game(call):
    chat_id = int(call.data.split("_")[2])
    
    if chat_id not in games:
        bot.answer_callback_query(call.id, "❌ لا توجد لعبة متاحة")
        return
    
    games[chat_id]['status'] = 'joining'
    
    # حذف الرسالة السابقة
    bot.delete_message(chat_id, call.message.message_id)
    
    # إرسال زر الانضمام
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🟢 انضم للعبة", callback_data=f"join_game_{chat_id}"))
    
    bot.send_message(chat_id, "🎮 **اللعبة بدأت!**\nاضغط على الزر للانضمام\n⏳ مدة الانضمام: دقيقة ونصف", reply_markup=keyboard)
    
    # تايمر دقيقة ونصف للانضمام
    Timer(90, lambda: end_joining_phase(chat_id)).start()

# الانضمام للعبة
@bot.callback_query_handler(func=lambda call: call.data.startswith("join_game_"))
def join_game(call):
    chat_id = int(call.data.split("_")[2])
    user_id = call.from_user.id
    username = call.from_user.first_name
    
    if chat_id not in games:
        bot.answer_callback_query(call.id, "❌ لا توجد لعبة متاحة")
        return
    
    if games[chat_id]['status'] != 'joining':
        bot.answer_callback_query(call.id, "❌ فترة الانضمام انتهت")
        return
    
    # التحقق من الحظر
    if is_user_banned(user_id):
        bot.answer_callback_query(call.id, f"🚫 أنت مقصي من اللعبة")
        return
    
    # التحقق من أن اللاعب ليس مسجلاً مسبقاً
    for player_id, player_name in games[chat_id]['players']:
        if player_id == user_id:
            bot.answer_callback_query(call.id, "⚠️ أنت مسجل مسبقاً")
            return
    
    # إضافة اللاعب
    games[chat_id]['players'].append((user_id, username))
    
    # تحديث الرسالة
    player_count = len(games[chat_id]['players'])
    text = f"🎮 **اللعبة بدأت!**\nاضغط على الزر للانضمام\n⏳ مدة الانضمام: دقيقة ونصف\n\n👥 **اللاعبون المسجلون:** ({player_count})\n"
    
    for i, (pid, pname) in enumerate(games[chat_id]['players'], 1):
        text += f"{i}. {pname}\n"
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🟢 انضم للعبة", callback_data=f"join_game_{chat_id}"))
    
    bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=keyboard)
    bot.answer_callback_query(call.id, f"✅ تم تسجيلك في اللعبة")

# انتهاء فترة الانضمام
def end_joining_phase(chat_id):
    if chat_id not in games or games[chat_id]['status'] != 'joining':
        return
    
    player_count = len(games[chat_id]['players'])
    
    if player_count < 3:
        bot.send_message(chat_id, "❌ عدد اللاعبين غير كافي (الحد الأدنى 3 لاعبين)")
        games[chat_id]['status'] = 'cancelled'
        return
    
    # طلب نوع اللعبة
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("📦 اشياء", callback_data=f"game_type_items_{chat_id}"))
    keyboard.add(InlineKeyboardButton("📍 اماكن", callback_data=f"game_type_locations_{chat_id}"))
    
    bot.send_message(chat_id, "واش حابين؟", reply_markup=keyboard)
    games[chat_id]['status'] = 'selecting_type'

# اختيار نوع اللعبة
@bot.callback_query_handler(func=lambda call: call.data.startswith("game_type_"))
def select_game_type(call):
    parts = call.data.split("_")
    game_type = parts[2]
    chat_id = int(parts[3])
    
    if chat_id not in games:
        bot.answer_callback_query(call.id, "❌ لا توجد لعبة متاحة")
        return
    
    games[chat_id]['game_type'] = game_type
    bot.delete_message(chat_id, call.message.message_id)
    
    # طلب عدد الأشخاص العاديين
    user_states[call.from_user.id] = {'state': 'waiting_normal_players', 'chat_id': chat_id}
    bot.send_message(chat_id, "📝 كم عدد الأشخاص العاديين؟\n(من 3 إلى 30)")

# اختيار عدد الجواسيس
@bot.callback_query_handler(func=lambda call: call.data.startswith("spies_count_"))
def select_spies_count(call):
    parts = call.data.split("_")
    spy_count = int(parts[2])
    chat_id = int(parts[3])
    
    if chat_id not in games:
        bot.answer_callback_query(call.id, "❌ لا توجد لعبة متاحة")
        return
    
    games[chat_id]['spy_count'] = spy_count
    bot.delete_message(chat_id, call.message.message_id)
    
    # طلب مدة اللعبة
    user_states[call.from_user.id] = {'state': 'waiting_duration', 'chat_id': chat_id}
    bot.send_message(chat_id, "📝 كم دقيقة تريدون هذه البارتية؟\n(من 1 إلى 15)")

# معالجة الرسائل النصية
@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text
    
    # التحقق من حالة المستخدم
    if user_id in user_states:
        state = user_states[user_id]['state']
        
        if state == 'waiting_normal_players':
            try:
                normal_players = int(text)
                if normal_players < 3 or normal_players > 30:
                    bot.send_message(chat_id, "❌ العدد يجب أن يكون بين 3 و 30")
                    return
                
                games[chat_id]['normal_players'] = normal_players
                max_spies = calculate_max_spies(normal_players)
                
                # إنشاء أزرار عدد الجواسيس
                keyboard = InlineKeyboardMarkup()
                for i in range(1, max_spies + 1):
                    keyboard.add(InlineKeyboardButton(f"{i} جاسوس", callback_data=f"spies_count_{i}_{chat_id}"))
                
                bot.delete_message(chat_id, message.message_id)
                bot.send_message(chat_id, f"📝 كم عدد الجواسيس؟\n(الحد الأقصى: {max_spies})", reply_markup=keyboard)
                del user_states[user_id]
                
            except ValueError:
                bot.send_message(chat_id, "❌ يرجى إدخال رقم صحيح")
        
        elif state == 'waiting_duration':
            try:
                duration = int(text)
                if duration < 1 or duration > 15:
                    bot.send_message(chat_id, "❌ المدة يجب أن تكون بين 1 و 15 دقيقة")
                    return
                
                games[chat_id]['duration'] = duration
                bot.delete_message(chat_id, message.message_id)
                
                # بدء اللعبة
                start_actual_game(chat_id)
                del user_states[user_id]
                
            except ValueError:
                bot.send_message(chat_id, "❌ يرجى إدخال رقم صحيح")
        
        elif state == 'waiting_bank_choice':
            if text in BANKS:
                bank_account = generate_account_number()
                update_user_bank(user_id, bank_account, text)
                bot.send_message(chat_id, f"✅ تم فتح الحساب\n🏦 البنك: {text}\n💳 رقم الحساب: {bank_account}\n💰 الرصيد: 0 د.ج")
                del user_states[user_id]
            else:
                bot.send_message(chat_id, "❌ اختر بنك من القائمة المتاحة")
        
        elif state == 'waiting_transfer_account':
            try:
                # التحقق من صيغة رقم الحساب
                if len(text) == 9 and text[4] == '-':
                    transfer_data = user_states[user_id]['transfer_data']
                    amount = transfer_data['amount']
                    
                    # خصم العمولة 15%
                    commission = int(amount * 0.15)
                    final_amount = amount - commission
                    
                    # تحديث الأرصدة
                    update_user_balance(user_id, -amount)
                    add_transaction(user_id, -amount, "transfer", f"تحويل إلى {text}")
                    
                    bot.send_message(chat_id, f"✅ تم التحويل بنجاح\n💰 المبلغ: {final_amount:,} د.ج\n💳 إلى الحساب: {text}\n📊 العمولة: {commission:,} د.ج")
                    del user_states[user_id]
                else:
                    bot.send_message(chat_id, "❌ صيغة رقم الحساب غير صحيحة (مثال: 1234-5678)")
            except:
                bot.send_message(chat_id, "❌ حدث خطأ في التحويل")
    
    # معالجة الأوامر المالية
    elif text.startswith("شراء"):
        handle_purchase(message)
    elif text.startswith("بيع"):
        handle_sell(message)
    elif text.startswith("فارسي"):
        handle_transfer(message)
    elif text == "ممتلكاتي":
        show_user_items(message)
    elif text == "حلي بونكا":
        open_bank_account(message)

# بدء اللعبة الفعلية
def start_actual_game(chat_id):
    game = games[chat_id]
    
    # إرسال رسالة للاعبين
    bot.send_message(chat_id, "ارسل لي كلمة start في الخاص لترى دورك")
    
    # اختيار العنصر السري
    if game['game_type'] == 'items':
        game['secret_item'] = random.choice(ITEMS)
    else:
        game['secret_item'] = random.choice(LOCATIONS)
    
    # اختيار الجواسيس
    all_players = game['players'].copy()
    random.shuffle(all_players)
    game['spies'] = [player[0] for player in all_players[:game['spy_count']]]
    
    # إرسال الأدوار في الخاص
    for player_id, player_name in game['players']:
        try:
            if player_id in game['spies']:
                # رسالة للجاسوس
                spy_photo = "https://pin.it/2Xv5gZUHU"
                text = f"🕵️‍♂️ أنت الجاسوس!\nاعرف كيفاه تلعب وتجاوب، ماتخليهمش يكشفوك!"
                try:
                    bot.send_photo(player_id, spy_photo, caption=text)
                except:
                    bot.send_message(player_id, text)
            else:
                # رسالة للاعب العادي
                text = f"🚫🕵️ أنت ماكش جاسوس\n{game['game_type']}: {game['secret_item']}"
                bot.send_message(player_id, text)
        except:
            # إذا لم يستطع إرسال الرسالة للمستخدم
            pass
    
    # بدء اللعبة
    game['status'] = 'playing'
    bot.send_message(chat_id, "📢 صَيَّبو مدينا الأدوار، ابداو تلعبو! 🎲🕰️")
    
    # تشغيل تايمر اللعبة
    game_duration = game['duration'] * 60  # تحويل إلى ثواني
    Timer(game_duration - 40, lambda: start_voting_phase(chat_id)).start()
    Timer(game_duration, lambda: end_game_timer(chat_id)).start()

# مرحلة التصويت
def start_voting_phase(chat_id):
    if chat_id not in games or games[chat_id]['status'] != 'playing':
        return
    
    game = games[chat_id]
    bot.send_message(chat_id, "⏰ أرسلت لكم التصويت في الخاص")
    
    # إرسال أزرار التصويت للاعبين
    for player_id, player_name in game['players']:
        try:
            keyboard = InlineKeyboardMarkup()
            for target_id, target_name in game['players']:
                if target_id != player_id:  # لا يمكن التصويت لنفسه
                    keyboard.add(InlineKeyboardButton(target_name, callback_data=f"vote_{target_id}_{chat_id}"))
            
            bot.send_message(player_id, "على من تصوت أنه الجاسوس؟", reply_markup=keyboard)
        except:
            pass

# التصويت
@bot.callback_query_handler(func=lambda call: call.data.startswith("vote_"))
def handle_vote(call):
    parts = call.data.split("_")
    target_id = int(parts[1])
    chat_id = int(parts[2])
    voter_id = call.from_user.id
    
    if chat_id not in games:
        bot.answer_callback_query(call.id, "❌ لا توجد لعبة متاحة")
        return
    
    game = games[chat_id]
    
    # التحقق من أن المصوت لاعب في اللعبة
    voter_in_game = False
    target_name = ""
    voter_name = ""
    
    for player_id, player_name in game['players']:
        if player_id == voter_id:
            voter_in_game = True
            voter_name = player_name
        if player_id == target_id:
            target_name = player_name
    
    if not voter_in_game:
        bot.answer_callback_query(call.id, "❌ أنت لست في اللعبة")
        return
    
    # التحقق من عدم التصويت المسبق
    if voter_id in game['votes']:
        bot.answer_callback_query(call.id, "⚠️ لقد صوتت مسبقاً")
        return
    
    # تسجيل التصويت
    game['votes'][voter_id] = target_id
    bot.answer_callback_query(call.id, f"✅ تم تسجيل صوتك ضد {target_name}")
    
    # إرسال في المجموعة
    bot.send_message(chat_id, f"{voter_name} صوت لإعدام {target_name} 🗳️")
    
    # التحقق من اكتمال التصويت
    if len(game['votes']) == len(game['players']):
        calculate_vote_results(chat_id)

# حساب نتائج التصويت
def calculate_vote_results(chat_id):
    game = games[chat_id]
    
    # حساب الأصوات
    vote_counts = {}
    for voter_id, target_id in game['votes'].items():
        vote_counts[target_id] = vote_counts.get(target_id, 0) + 1
    
    # العثور على الأكثر حصولاً على الأصوات
    max_votes = max(vote_counts.values())
    most_voted = [player_id for player_id, votes in vote_counts.items() if votes == max_votes]
    
    # تحديد الفائز
    if len(most_voted) == 1:
        eliminated_id = most_voted[0]
        eliminated_name = ""
        
        for player_id, player_name in game['players']:
            if player_id == eliminated_id:
                eliminated_name = player_name
                break
        
        # التحقق من أن المطرود جاسوس
        if eliminated_id in game['spies']:
            bot.send_message(chat_id, f"🎉 تم إعدام {eliminated_name} وكان جاسوساً!")
            game['spies'].remove(eliminated_id)
            
            # التحقق من فوز اللاعبين
            if len(game['spies']) == 0:
                players_win(chat_id)
            else:
                bot.send_message(chat_id, f"🔄 اللعبة مستمرة، باقي {len(game['spies'])} جاسوس")
        else:
            bot.send_message(chat_id, f"💀 تم إعدام {eliminated_name} ولم يكن جاسوساً!")
            # الجواسيس يفوزون
            spies_win(chat_id)
    else:
        bot.send_message(chat_id, "🤝 تعادل في التصويت، الجواسيس يفوزون!")
        spies_win(chat_id)

# أوامر المتجر والبنك
def handle_purchase(message):
    user_id = message.from_user.id
    text = message.text
    
    # استخراج اسم العنصر
    parts = text.split()
    if len(parts) < 3:
        bot.send_message(message.chat.id, "❌ صيغة الأمر: شراء [العدد] [اسم العنصر]")
        return
    
    try:
        quantity = int(parts[1])
        item_name = " ".join(parts[2:])
    except ValueError:
        bot.send_message(message.chat.id, "❌ العدد يجب أن يكون رقم")
        return
    
    if item_name not in SHOP_ITEMS:
        bot.send_message(message.chat.id, "❌ هذا العنصر غير متوفر في المتجر")
        return
    
    total_cost = SHOP_ITEMS[item_name]["price"] * quantity
    user_balance = get_user_balance(user_id)
    
    if user_balance < total_cost:
        bot.send_message(message.chat.id, f"❌ رصيدك غير كافي\nالمطلوب: {total_cost:,} د.ج\nرصيدك: {user_balance:,} د.ج")
        return
    
    # إتمام الشراء
    update_user_balance(user_id, -total_cost)
    
    # إضافة العنصر للمخزون
    user_items = get_user_items(user_id)
    user_items[item_name] = user_items.get(item_name, 0) + quantity
    update_user_items(user_id, user_items)
    
    add_transaction(user_id, -total_cost, "purchase", f"شراء {quantity} {item_name}")
    
    remaining_balance = get_user_balance(user_id)
    emoji = SHOP_ITEMS[item_name]["emoji"]
    
    bot.send_message(message.chat.id, f"✅ لقد اشتريت {quantity} {item_name} {emoji} بسعر {total_cost:,} د.ج 💵\nتبقى لديك {remaining_balance:,} د.ج")

def handle_sell(message):
    user_id = message.from_user.id
    text = message.text
    
    # استخراج اسم العنصر
    parts = text.split()
    if len(parts) < 3:
        bot.send_message(message.chat.id, "❌ صيغة الأمر: بيع [العدد] [اسم العنصر]")
        return
    
    try:
        quantity = int(parts[1])
        item_name = " ".join(parts[2:])
    except ValueError:
        bot.send_message(message.chat.id, "❌ العدد يجب أن يكون رقم")
        return
    
    if item_name not in SHOP_ITEMS:
        bot.send_message(message.chat.id, "❌ هذا العنصر غير متوفر في المتجر")
        return
    
    user_items = get_user_items(user_id)
    if item_name not in user_items or user_items[item_name] < quantity:
        bot.send_message(message.chat.id, f"❌ ليس لديك {quantity} من {item_name}")
        return
    
    # حساب سعر البيع (75% من سعر الشراء)
    sell_price = int(SHOP_ITEMS[item_name]["price"] * 0.75) * quantity
    
    # إتمام البيع
    update_user_balance(user_id, sell_price)
    
    user_items[item_name] -= quantity
    if user_items[item_name] == 0:
        del user_items[item_name]
    
    update_user_items(user_id, user_items)
    add_transaction(user_id, sell_price, "sell", f"بيع {quantity} {item_name}")
    
    bot.send_message(message.chat.id, f"✅ تم بيع {quantity} {item_name}\nاسترجعت {sell_price:,} د.ج (75% من سعر الشراء)")

def show_user_items(message):
    user_id = message.from_user.id
    user_items = get_user_items(user_id)
    
    if not user_items:
        bot.send_message(message.chat.id, "📦 لا تملك أي عناصر")
        return
    
    text = "🏆 **ممتلكاتي:**\n\n"
    for item, quantity in user_items.items():
        emoji = SHOP_ITEMS.get(item, {}).get("emoji", "📦")
        text += f"{emoji} {item}: {quantity}\n"
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

def open_bank_account(message):
    user_id = message.from_user.id
    
    # التحقق من وجود حساب مسبق
    bank_info = get_user_bank_info(user_id)
    if bank_info and bank_info[0]:
        bot.send_message(message.chat.id, f"💳 لديك حساب مسبق\n🏦 البنك: {bank_info[1]}\n📱 رقم الحساب: {bank_info[0]}")
        return
    
    # عرض البنوك المتاحة
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for bank in BANKS:
        keyboard.add(KeyboardButton(bank))
    
    bot.send_message(message.chat.id, "اختر البونكا:", reply_markup=keyboard)
    user_states[user_id] = {'state': 'waiting_bank_choice'}

def handle_transfer(message):
    user_id = message.from_user.id
    text = message.text
    
    # استخراج المبلغ
    parts = text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ صيغة الأمر: فارسي [المبلغ]")
        return
    
    try:
        amount = int(parts[1])
    except ValueError:
        bot.send_message(message.chat.id, "❌ المبلغ يجب أن يكون رقم")
        return
    
    user_balance = get_user_balance(user_id)
    if user_balance < amount:
        bot.send_message(message.chat.id, f"❌ رصيدك غير كافي\nرصيدك: {user_balance:,} د.ج")
        return
    
    # طلب رقم الحساب
    user_states[user_id] = {
        'state': 'waiting_transfer_account',
        'transfer_data': {'amount': amount}
    }
    
    bot.send_message(message.chat.id, f"💸 ارسل رقم حساب المستفيد لتحويل {amount:,} د.ج\n💼 العمولة: 15%")

# أوامر المطور
@bot.message_handler(commands=['ban'])
def ban_user_command(message):
    if message.from_user.username != DEVELOPER_USERNAME:
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ صيغة الأمر: /ban [user_id] [السبب]")
        return
    
    try:
        target_user_id = int(parts[1])
        reason = " ".join(parts[2:]) if len(parts) > 2 else "غير محدد"
        
        ban_user(target_user_id, reason)
        bot.send_message(message.chat.id, f"✅ تم حظر المستخدم {target_user_id}")
    except ValueError:
        bot.send_message(message.chat.id, "❌ ID المستخدم يجب أن يكون رقم")

@bot.message_handler(commands=['unban'])
def unban_user_command(message):
    if message.from_user.username != DEVELOPER_USERNAME:
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ صيغة الأمر: /unban [user_id]")
        return
    
    try:
        target_user_id = int(parts[1])
        unban_user(target_user_id)
        bot.send_message(message.chat.id, f"✅ تم إلغاء حظر المستخدم {target_user_id}")
    except ValueError:
        bot.send_message(message.chat.id, "❌ ID المستخدم يجب أن يكون رقم")

# معالجة إضافة البوت للمجموعة
@bot.message_handler(content_types=['new_chat_members'])
def new_member(message):
    for member in message.new_chat_members:
        if member.id == bot.get_me().id:
            send_welcome_message(message.chat.id)

# تشغيل البوت
if __name__ == '__main__':
    init_database()
    print("🚀 البوت يعمل...")
    bot.polling(none_stop=True)
