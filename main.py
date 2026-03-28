
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
import time
import random

def human_delay(min_seconds=1.5, max_seconds=4.5):
    """إضافة تأخير زمني عشوائي لمحاكاة السلوك البشري وتجنب الحظر"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def make_textmenu(widget):
    """إنشاء قائمة سياق (كليك يمين) للنسخ واللصق"""
    menu = tk.Menu(widget, tearoff=0)
    menu.add_command(label="قص", command=lambda: widget.event_generate("<<Cut>>"))
    menu.add_command(label="نسخ", command=lambda: widget.event_generate("<<Copy>>"))
    menu.add_command(label="لصق", command=lambda: widget.event_generate("<<Paste>>"))
    
    def show_menu(e):
        menu.tk_popup(e.x_root, e.y_root)
        
    widget.bind("<Button-3>", show_menu) # ربط القائمة بالنقر بزر الماوس الأيمن

def save_results():
    results = results_text.get('1.0', tk.END)
    if not results.strip():
        messagebox.showerror("خطأ", "لا توجد نتائج لحفظها.")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                               filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(results)
        messagebox.showinfo("نجاح", f"تم حفظ النتائج في {file_path}")

def start_scraping():
    email = email_entry.get()
    password = password_entry.get()
    page_url = page_url_entry.get()
    proxy = proxy_entry.get().strip() # جلب قيمة البروكسي

    if not email or not password or not page_url:
        messagebox.showerror("خطأ", "يرجى ملء جميع الحقول الإلزامية")
        return

    try:
        # إعداد خيارات المتصفح لتخطي الحماية
        options = uc.ChromeOptions()
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        
        # إضافة إعدادات البروكسي إذا تم توفيرها
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
        
        driver = uc.Chrome(options=options)

        driver.get("https://www.facebook.com")
        human_delay(2, 4)

        email_field = driver.find_element(By.ID, "email")
        # كتابة البريد الإلكتروني كإنسان (حرف بحرف)
        for char in email:
            email_field.send_keys(char)
            time.sleep(random.uniform(0.05, 0.2))
        human_delay(1, 2)

        password_field = driver.find_element(By.ID, "pass")
        for char in password:
            password_field.send_keys(char)
            time.sleep(random.uniform(0.05, 0.2))
        human_delay(1, 2)

        password_field.send_keys(Keys.RETURN)
        human_delay(5, 8) # انتظر حتى يتم تحميل الصفحة الرئيسية

        driver.get(page_url)
        human_delay(4, 7)

        try:
            community_link = driver.find_element(By.PARTIAL_LINK_TEXT, "Community")
            community_link.click()
            human_delay(3, 5)
        except:
            try:
                people_link = driver.find_element(By.PARTIAL_LINK_TEXT, "People")
                people_link.click()
                human_delay(3, 5)
            except Exception as e:
                messagebox.showerror("خطأ", "لم يتم العثور على قسم المجتمع أو الأشخاص.")
                driver.quit()
                return

        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        while scroll_attempts < 20: # وضع حد أقصى للتمرير لتجنب الحظر
            # تمرير سلس (Smooth Scrolling) بدلاً من القفز المباشر
            driver.execute_script("window.scrollBy(0, window.innerHeight * 0.8);")
            human_delay(1.5, 3.5)
            
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                # حاول التمرير مرة أخرى للتأكد من أنه لم يكن مجرد تأخير في التحميل
                human_delay(3, 5)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
            last_height = new_height
            scroll_attempts += 1

        members = driver.find_elements(By.XPATH, "//div[@role='listitem']//a")
        member_names = [member.text for member in members if member.text]

        results_text.delete('1.0', tk.END)
        for name in member_names:
            results_text.insert(tk.END, name + "\n")

        messagebox.showinfo("نجاح", f"تم استخراج {len(member_names)} عضو بنجاح!")
        driver.quit()

    except Exception as e:
        messagebox.showerror("خطأ في Selenium", str(e))

root = tk.Tk()
root.title("أداة استخراج أعضاء فيسبوك")

# ... (نفس الواجهة السابقة)

tk.Label(root, text="البريد الإلكتروني:").grid(row=0, column=0, padx=10, pady=5)
email_entry = tk.Entry(root, width=50)
email_entry.grid(row=0, column=1, padx=10, pady=5)
make_textmenu(email_entry)

tk.Label(root, text="كلمة المرور:").grid(row=1, column=0, padx=10, pady=5)
password_entry = tk.Entry(root, show="*", width=50)
password_entry.grid(row=1, column=1, padx=10, pady=5)
make_textmenu(password_entry)

tk.Label(root, text="رابط الصفحة:").grid(row=2, column=0, padx=10, pady=5)
page_url_entry = tk.Entry(root, width=50)
page_url_entry.grid(row=2, column=1, padx=10, pady=5)
make_textmenu(page_url_entry)

tk.Label(root, text="البروكسي (اختياري - IP:Port):").grid(row=3, column=0, padx=10, pady=5)
proxy_entry = tk.Entry(root, width=50)
proxy_entry.grid(row=3, column=1, padx=10, pady=5)
make_textmenu(proxy_entry)

start_button = tk.Button(root, text="بدء الاستخراج", command=start_scraping)
start_button.grid(row=4, column=0, columnspan=2, pady=10)

results_text = scrolledtext.ScrolledText(root, width=70, height=20)
results_text.grid(row=5, column=0, columnspan=2, padx=10, pady=10)
make_textmenu(results_text)

save_button = tk.Button(root, text="حفظ النتائج", command=save_results)
save_button.grid(row=6, column=0, columnspan=2, pady=10)

root.mainloop()
